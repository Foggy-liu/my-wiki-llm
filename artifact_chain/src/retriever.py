"""检索模块 - 从Wiki知识库检索相关知识（LLM辅助查询版）"""
from typing import List
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
