"""检索模块 - 从Wiki知识库检索相关知识（LLM辅助查询版）"""
import os
from typing import List
import anthropic
from .wiki_kb import WikiKnowledgeBase, RetrievedEntry, WikiEntry


class Retriever:
    """
    检索器

    关键设计：使用 LLM 辅助查询，而非简单的关键字匹配
    LLM 读取 index.md 理解 Wiki 结构，然后决定需要查询哪些页面
    """

    def __init__(self, wiki_kb: WikiKnowledgeBase, top_k: int = 5):
        self.wiki_kb = wiki_kb
        self.top_k = top_k

        # 初始化 LLM 客户端
        base_url = os.environ.get("ANTHROPIC_BASE_URL", "https://api.minimaxi.com/anthropic")
        auth_token = os.environ.get("ANTHROPIC_AUTH_TOKEN", "")

        if auth_token:
            self.client = anthropic.Anthropic(
                base_url=base_url,
                api_key=auth_token,
            )
        else:
            self.client = None

    def retrieve(self, intent) -> List[RetrievedEntry]:
        """
        根据意图检索相关知识

        正确的 LLM Wiki Query 流程：
        1. LLM 读取 index.md（理解 Wiki 结构）
        2. LLM 决定需要哪些页面（基于 intent）
        3. 读取选定页面

        Args:
            intent: UserIntent对象

        Returns:
            检索结果列表（按置信度排序）
        """
        all_results: List[RetrievedEntry] = []

        # 1. 首先获取高置信度的相关实体页面
        if intent.artifact:
            artifact_page = self.wiki_kb.get_page(intent.artifact)
            if artifact_page:
                all_results.append(RetrievedEntry(
                    entry=artifact_page,
                    score=1.0,
                    highlight=f"直接匹配: {artifact_page.title}"
                ))

            related = self.wiki_kb.search(intent.artifact)
            for r in related:
                if r.entry.title != intent.artifact:
                    all_results.append(r)

        # 2. 获取风格/方法论相关页面（concepts）
        if intent.style:
            style_page = self.wiki_kb.get_page(intent.style)
            if style_page:
                all_results.append(RetrievedEntry(
                    entry=style_page,
                    score=0.9,
                    highlight=f"风格匹配: {style_page.title}"
                ))

            style_results = self.wiki_kb.search(intent.style)
            for r in style_results:
                if r.entry.title != intent.style and r.entry.category == "concepts":
                    all_results.append(r)

        # 3. 获取脚本结构相关页面（如果需要脚本）
        if intent.intent_type == "脚本":
            script_page = self.wiki_kb.get_page("短视频脚本结构")
            if script_page:
                all_results.append(RetrievedEntry(
                    entry=script_page,
                    score=0.85,
                    highlight=f"结构匹配: {script_page.title}"
                ))

        # 4. 去重（根据 title）
        seen_titles = set()
        unique_results = []
        for r in all_results:
            if r.entry.title not in seen_titles:
                seen_titles.add(r.entry.title)
                unique_results.append(r)

        # 5. 按置信度排序
        unique_results.sort(key=lambda x: x.entry.confidence, reverse=True)

        return unique_results[:self.top_k]

    def get_context_for_query(self, question: str) -> dict:
        """
        为 LLM 生成查询上下文（供 LLM 辅助查询用）

        这个方法返回 LLM 需要的信息，让 LLM 决定查询哪些页面
        """
        index_content = self.wiki_kb.read_index()

        all_pages = self.wiki_kb.list_pages()

        high_conf_pages = self.wiki_kb.get_high_confidence_pages(threshold=0.7)

        return {
            "index": index_content,
            "total_pages": len(all_pages),
            "pages_by_category": {
                "entities": [p.title for p in all_pages if p.category == "entities"],
                "concepts": [p.title for p in all_pages if p.category == "concepts"],
            },
            "high_confidence_pages": [p.title for p in high_conf_pages],
            "user_question": question
        }

    def retrieve_with_llm(self, intent, user_question: str = None) -> List[RetrievedEntry]:
        """
        使用 LLM 辅助查询（真正调用 LLM）

        流程：
        1. 读取 index.md 理解 Wiki 结构
        2. 将上下文发送给 LLM，让 LLM 决定需要查询哪些页面
        3. 读取 LLM 指定的页面
        4. 返回检索结果

        Args:
            intent: UserIntent对象
            user_question: 用户原始问题（可选，用于 LLM 理解上下文）

        Returns:
            检索结果列表
        """
        if not self.client:
            # 没有 LLM 配置，回退到规则匹配
            return self.retrieve(intent)

        # 1. 构建 LLM 上下文
        context = self.get_context_for_query(user_question or f"{intent.artifact or ''} {intent.style or ''} {intent.intent_type or ''}")

        # 2. 构建提示词
        prompt = f"""你是一个 Wiki 知识库查询助手。用户想要查询与以下意图相关的 Wiki 页面：

用户意图：
- 素材/文物: {intent.artifact or '未指定'}
- 风格: {intent.style or '未指定'}
- 意图类型: {intent.intent_type or '未指定'}
- 时长: {intent.duration or '60'}秒

Wiki 知识库结构：
{context['index']}

请根据用户意图，从 Wiki 中选择最相关的页面返回。
返回格式：以 JSON 数组形式返回页面标题，例如：["青铜面具", "悬疑叙事技巧"]

只返回 JSON 数组，不要包含其他内容。"""

        # 3. 调用 LLM
        response = self.client.messages.create(
            model="MiniMax-M2.7",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # 4. 解析 LLM 响应（处理 MiniMax 的 ThinkingBlock）
        llm_response = ""
        for block in response.content:
            if hasattr(block, 'text'):
                llm_response = block.text.strip()
                break

        # 提取 JSON 数组
        import json
        import re

        # 尝试找到 JSON 数组
        json_match = re.search(r'\[.*\]', llm_response, re.DOTALL)
        if json_match:
            try:
                selected_pages = json.loads(json_match.group())
            except json.JSONDecodeError:
                selected_pages = []
        else:
            selected_pages = []

        # 5. 读取选定的页面
        results = []
        for page_title in selected_pages:
            page = self.wiki_kb.get_page(page_title)
            if page:
                results.append(RetrievedEntry(
                    entry=page,
                    score=page.confidence,
                    highlight=f"LLM选择: {page.title}"
                ))

        # 按置信度排序
        results.sort(key=lambda x: x.entry.confidence, reverse=True)

        return results[:self.top_k]
