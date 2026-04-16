import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.config import settings
from app.db import WikiPage, OperationLog
from app.services.llm import llm_service

class QueryService:
    def __init__(self, db: Session, user_id: Optional[int] = None):
        self.db = db
        self.user_id = user_id
        self.wiki_dir = settings.WIKI_DIR
        self.index_path = self.wiki_dir / "index.md"

    def get_relevant_pages(self, question: str, limit: int = 5) -> List[WikiPage]:
        all_pages = self.db.query(WikiPage).filter(WikiPage.status == "active").all()

        question_lower = question.lower()
        scored = []
        for page in all_pages:
            score = 0
            title_lower = page.title.lower()
            if any(word in title_lower for word in question_lower.split()):
                score += 2
            if any(word in title_lower for word in question_lower.split()[:3]):
                score += 1
            scored.append((page, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [p[0] for p in scored[:limit]]

    def get_page_content(self, page: WikiPage) -> str:
        file_path = Path(page.file_path)
        if not file_path.exists():
            return ""
        return file_path.read_text(encoding='utf-8')

    def parse_frontmatter(self, content: str) -> Dict[str, Any]:
        import re
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return {}

        frontmatter = {}
        for line in match.group(1).split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()
        return frontmatter

    def extract_main_content(self, content: str) -> str:
        import re
        return re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)

    async def query(self, question: str) -> Dict[str, Any]:
        result = {
            "question": question,
            "answer": "",
            "sources": [],
            "pages_used": [],
            "confidence": 0.0
        }

        try:
            relevant_pages = self.get_relevant_pages(question)

            if not relevant_pages:
                result["answer"] = "抱歉，知识库中没有找到与您问题相关的内容。"
                self._log_query(result)
                return result

            context_parts = []
            for page in relevant_pages:
                content = self.get_page_content(page)
                main_content = self.extract_main_content(content)

                context_parts.append(f"=== {page.title} ===\n{main_content[:1000]}")
                result["pages_used"].append(page.title)

            context = "\n\n".join(context_parts)

            llm_response = await llm_service.query_knowledge(question, context)

            result["answer"] = llm_response.get("answer", "抱歉，无法生成回答。")
            result["sources"] = llm_response.get("sources", result["pages_used"])
            result["confidence"] = llm_response.get("confidence", 0.5)

            self._log_query(result)

        except Exception as e:
            result["answer"] = f"处理查询时出错: {str(e)}"

        return result

    def _log_query(self, result: Dict[str, Any]):
        log = OperationLog(
            operation="query",
            status="success",
            details=json.dumps(result, ensure_ascii=False),
            operator_id=self.user_id
        )
        self.db.add(log)
        self.db.commit()

    def get_query_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        logs = self.db.query(OperationLog).filter(
            OperationLog.operation == "query"
        ).order_by(OperationLog.created_at.desc()).limit(limit).all()

        history = []
        for log in logs:
            details = json.loads(log.details) if log.details else {}
            history.append({
                "question": details.get("question", ""),
                "answer": details.get("answer", ""),
                "timestamp": log.created_at.isoformat() if log.created_at else None
            })
        return history