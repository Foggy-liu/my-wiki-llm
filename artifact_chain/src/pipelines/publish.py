"""Publish Pipeline - 从 Wiki 生成交付物"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import List
from datetime import datetime


@dataclass
class PublishResult:
    """Publish 操作结果"""
    output_path: str
    format: str
    platform: str
    source_pages: List[str]
    lifecycle_updates: List[dict]
    log_entry: str


class PublishPipeline:
    """
    Publish 流程

    明确需求 → 定位源材料 → 生成草稿 →
    格式适配 → 用户审核 → 记录log
    """

    def __init__(self, wiki_kb, output_dir: str = "output"):
        self.wiki_kb = wiki_kb
        self.output_dir = Path(output_dir)

        # 初始化 LLM 客户端
        base_url = os.environ.get("ANTHROPIC_BASE_URL", "https://api.minimaxi.com/anthropic")
        auth_token = os.environ.get("ANTHROPIC_AUTH_TOKEN", "")
        if auth_token:
            import anthropic
            self.llm_client = anthropic.Anthropic(
                base_url=base_url,
                api_key=auth_token,
            )
        else:
            self.llm_client = None

    def publish(self, requirement: str, topic: str, format: str = "post",
                platform: str = "sora") -> PublishResult:
        """
        发布交付物

        Args:
            requirement: 用户需求描述
            topic: 主题
            format: 格式 (post/report/slides/tutorial/newsletter)
            platform: 平台 (sora/kling/runway/text)

        Returns:
            PublishResult
        """
        # 1. 定位源材料（通过 Query）
        from .query import QueryPipeline
        query_pipe = QueryPipeline(self.wiki_kb)
        query_result = query_pipe.query(topic)

        # 2. 生成内容（LLM 辅助）
        content = self._generate_content_with_llm(requirement, topic, query_result.consulted_pages, format, platform)

        # 3. 保存到 output
        output_path = self._save_output(content, topic, format)

        # 4. 更新 lifecycle
        lifecycle_updates = []
        for page_title in query_result.consulted_pages:
            self.wiki_kb.update_access(page_title)
            lifecycle_updates.append({"page": page_title, "action": "publish_used"})

        # 5. 记录 log
        log_entry = self._create_log_entry(topic, format, platform,
                                           query_result.consulted_pages, str(output_path))
        self.wiki_kb.append_log(log_entry)

        return PublishResult(
            output_path=str(output_path),
            format=format,
            platform=platform,
            source_pages=query_result.consulted_pages,
            lifecycle_updates=lifecycle_updates,
            log_entry=log_entry
        )

    def _generate_content_with_llm(self, requirement: str, topic: str,
                                    pages: List[str], format: str, platform: str) -> str:
        """使用 LLM 生成交付内容"""
        # 读取页面内容
        page_contents = []
        for page_title in pages:
            page = self.wiki_kb.get_page(page_title)
            if page:
                page_contents.append(f"## {page.title}\n\n{page.content}")

        if not page_contents:
            return self._generate_content_fallback(requirement, pages, format)

        pages_text = "\n\n".join(page_contents)

        # 根据格式构建不同的提示词
        format_prompts = {
            "post": f"撰写一篇关于 {topic} 的社交媒体帖子（短视频配套文案），长度 200-400 字。",
            "report": f"撰写一份关于 {topic} 的分析报告，长度 500-800 字，包含背景、分析和结论。",
            "slides": f"为 {topic} 创建演示文稿大纲，包含 5-8 个幻灯片要点。",
            "tutorial": f"撰写 {topic} 的教程指南，包含步骤说明和示例。",
            "newsletter": f"撰写 {topic} 的通讯文章，包含关键信息和行动号召。",
        }

        format_instruction = format_prompts.get(format, f"撰写关于 {topic} 的内容")

        prompt = f"""你是一个内容创作助手。请根据以下 Wiki 知识库的内容，为用户需求生成交付物。

用户需求：{requirement}
主题：{topic}
格式：{format}
平台：{platform}

格式要求：{format_instruction}

知识库内容：
{pages_text}

请生成符合格式要求的交付物内容。使用 [[页面标题]] 引用相关知识。

输出格式为 Markdown。"""

        if self.llm_client:
            try:
                response = self.llm_client.messages.create(
                    model="MiniMax-M2.7",
                    max_tokens=4096,
                    messages=[{"role": "user", "content": prompt}]
                )

                for block in response.content:
                    if hasattr(block, 'text'):
                        return block.text.strip()

            except Exception as e:
                print(f"LLM content generation failed: {e}")

        return self._generate_content_fallback(requirement, pages, format)

    def _generate_content_fallback(self, requirement: str, pages: List[str], format: str) -> str:
        """简单拼接回退方案"""
        content_lines = [
            f"# {requirement}",
            "",
            f"**主题**: {requirement}",
            f"**格式**: {format}",
            "",
            "## 源材料",
        ]

        for page_title in pages:
            page = self.wiki_kb.get_page(page_title)
            if page:
                content_lines.append(f"- [[{page_title}]]")

        content_lines.extend([
            "",
            "## 内容",
            "",
            "(基于知识库内容生成)"
        ])

        return "\n".join(content_lines)

    def _save_output(self, content: str, topic: str, format: str) -> Path:
        """保存输出文件"""
        format_dir = self.output_dir / f"{format}s"
        format_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{topic[:20]}_{datetime.now().strftime('%Y%m%d%H%M%S')}.md"
        output_path = format_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return output_path

    def _create_log_entry(self, topic: str, format: str, platform: str,
                          pages: List[str], output_path: str) -> str:
        """创建日志条目"""
        now = datetime.now().strftime("%Y-%m-%d")
        pages_str = ", ".join([f"[[{p}]]" for p in pages]) if pages else "None"

        return f"## [{now}] publish | {format} | {topic}\n- Output: {output_path}\n- wiki_deps: {pages_str}\n"
