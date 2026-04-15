"""Query Pipeline - LLM 辅助查询"""

import os
import re
import json
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class QueryResult:
    """Query 操作结果"""
    answer: str
    consulted_pages: List[str]
    citations: List[str]
    lifecycle_updates: List[dict]
    log_entry: str
    ask_archive: bool = False


class QueryPipeline:
    """
    Query 流程（LLM 辅助）

    用户提问 → LLM 读取 index.md → LLM 选择页面 → 读取页面 →
    综合回答 → 更新 lifecycle → 记录 log
    """

    def __init__(self, wiki_kb, llm_client=None):
        self.wiki_kb = wiki_kb
        self.llm_client = llm_client
        if llm_client is None:
            # 初始化 LLM 客户端（如果未提供）
            base_url = os.environ.get("ANTHROPIC_BASE_URL", "https://api.minimaxi.com/anthropic")
            auth_token = os.environ.get("ANTHROPIC_AUTH_TOKEN", "")
            if auth_token:
                import anthropic
                self.llm_client = anthropic.Anthropic(
                    base_url=base_url,
                    api_key=auth_token,
                )

    def query(self, question: str) -> QueryResult:
        """
        LLM 辅助查询

        Args:
            question: 用户问题

        Returns:
            QueryResult
        """
        # 1. LLM 读取 index.md（理解 Wiki 结构）
        index_content = self.wiki_kb.read_index()

        # 2. LLM 选择页面
        selected_titles = self._select_pages_with_llm(question, index_content)

        # 3. 读取选定页面
        pages = []
        for title in selected_titles:
            page = self.wiki_kb.get_page(title)
            if page:
                pages.append(page)

        # 4. LLM 综合回答
        answer = self._synthesize_with_llm(question, pages)

        # 5. 提取引用
        citations = [f"[[{p.title}]]" for p in pages]

        # 6. 更新 lifecycle
        lifecycle_updates = []
        for page in pages:
            self.wiki_kb.update_access(page.title)
            lifecycle_updates.append({"page": page.title, "action": "access"})

        # 7. 记录 log
        log_entry = self._create_log_entry(question, selected_titles)
        self.wiki_kb.append_log(log_entry)

        return QueryResult(
            answer=answer,
            consulted_pages=selected_titles,
            citations=citations,
            lifecycle_updates=lifecycle_updates,
            log_entry=log_entry,
            ask_archive=False
        )

    def _select_pages_with_llm(self, question: str, index_content: str) -> List[str]:
        """
        使用 LLM 选择需要查询的页面

        Args:
            question: 用户问题
            index_content: index.md 内容

        Returns:
            选中的页面标题列表
        """
        if not self.llm_client:
            # 没有 LLM，回退到关键字匹配
            return self._select_pages_fallback(question)

        prompt = f"""你是一个 Wiki 知识库查询助手。用户想要查询与以下问题相关的 Wiki 页面：

用户问题：{question}

Wiki 知识库结构：
{index_content}

请根据用户问题，从 Wiki 中选择最相关的页面返回。
返回格式：以 JSON 数组形式返回页面标题，例如：["青铜面具", "悬疑叙事技巧"]

只返回 JSON 数组，不要包含其他内容。"""

        try:
            response = self.llm_client.messages.create(
                model="MiniMax-M2.7",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            # 解析 LLM 响应
            llm_response = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    llm_response = block.text.strip()
                    break

            # 提取 JSON 数组
            json_match = re.search(r'\[.*\]', llm_response, re.DOTALL)
            if json_match:
                selected = json.loads(json_match.group())
                return selected[:10]  # 限制数量

        except Exception as e:
            print(f"LLM page selection failed: {e}")

        # 回退到关键字匹配
        return self._select_pages_fallback(question)

    def _select_pages_fallback(self, question: str) -> List[str]:
        """关键字匹配回退方案"""
        selected = []
        question_lower = question.lower()
        all_pages = self.wiki_kb.list_pages()

        for page in all_pages:
            if any(kw in page.title.lower() or kw in question_lower
                   for kw in [page.title.lower()]):
                if page.title not in selected:
                    selected.append(page.title)

        return selected[:5]

    def _synthesize_with_llm(self, question: str, pages: list) -> str:
        """
        使用 LLM 综合多页面内容回答问题

        Args:
            question: 用户问题
            pages: 页面列表

        Returns:
            综合回答
        """
        if not pages:
            return "抱歉，知识库中没有找到相关信息。"

        if not self.llm_client:
            # 没有 LLM，回退到简单拼接
            return self._synthesize_fallback(question, pages)

        # 构建页面内容摘要
        page_summaries = []
        for page in pages:
            page_summaries.append(f"## {page.title}\n\n{page.content[:500]}")

        pages_text = "\n\n".join(page_summaries)

        prompt = f"""你是一个 Wiki 知识库问答助手。请根据以下页面内容回答用户问题。

用户问题：{question}

相关页面内容：
{pages_text}

请根据以上内容，综合回答用户问题。如果页面内容不足以回答，请说明。

回答要求：
1. 综合多个页面的信息
2. 使用 [[页面标题]] 格式引用相关页面
3. 回答简洁有条理"""

        try:
            response = self.llm_client.messages.create(
                model="MiniMax-M2.7",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )

            for block in response.content:
                if hasattr(block, 'text'):
                    return block.text.strip()

        except Exception as e:
            print(f"LLM synthesis failed: {e}")

        return self._synthesize_fallback(question, pages)

    def _synthesize_fallback(self, question: str, pages: list) -> str:
        """简单拼接回退方案"""
        answers = []
        for page in pages:
            answers.append(f"## {page.title}\n\n{page.content[:300]}...")
        return "\n\n".join(answers)

    def _create_log_entry(self, question: str, pages: List[str]) -> str:
        """创建日志条目"""
        now = datetime.now().strftime("%Y-%m-%d")
        pages_str = ", ".join([f"[[{p}]]" for p in pages]) if pages else "None"
        return f"## [{now}] query | {question}\n- Consulted: {pages_str}\n"
