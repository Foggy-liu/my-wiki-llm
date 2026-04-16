import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.config import settings
from app.db import WikiPage, OperationLog

class PublishService:
    def __init__(self, db: Session, operator_id: Optional[int] = None):
        self.db = db
        self.operator_id = operator_id
        self.wiki_dir = settings.WIKI_DIR
        self.output_dir = settings.WIKI_ROOT.parent / "output"

    def get_active_pages(self) -> List[WikiPage]:
        return self.db.query(WikiPage).filter(
            WikiPage.status == "active"
        ).all()

    def generate_markdown(self, page: WikiPage) -> str:
        content = self._read_page_content(page)
        return content

    def generate_html(self, page: WikiPage) -> str:
        content = self._read_page_content(page)

        html = content
        html = html.replace('# ', '<h1>').replace('\n', '</h1>\n', 1)
        html = html.replace('## ', '<h2>').replace('\n## ', '</h2>\n<h2>')
        html = html.replace('**', '<strong>', 1).replace('**', '</strong>', 1)
        html = html.replace('\n- ', '\n<li>')
        html = f"<html><body>{html}</body></html>"

        return html

    def _read_page_content(self, page: WikiPage) -> str:
        file_path = Path(page.file_path)
        if not file_path.exists():
            return ""
        return file_path.read_text(encoding='utf-8')

    def publish(self, format: str = "markdown") -> Dict[str, Any]:
        result = {
            "format": format,
            "pages_published": 0,
            "output_dir": str(self.output_dir),
            "timestamp": datetime.now().isoformat()
        }

        self.output_dir.mkdir(parents=True, exist_ok=True)

        pages = self.get_active_pages()

        for page in pages:
            if format == "markdown":
                content = self.generate_markdown(page)
                output_path = self.output_dir / f"{page.title}.md"
            else:
                content = self.generate_html(page)
                output_path = self.output_dir / f"{page.title}.html"

            output_path.write_text(content, encoding='utf-8')
            result["pages_published"] += 1

        index_content = "# 发布索引\n\n"
        index_content += f"生成时间: {result['timestamp']}\n\n"
        index_content += "## 页面列表\n\n"
        for page in pages:
            ext = "md" if format == "markdown" else "html"
            index_content += f"- [{page.title}]({page.title}.{ext})\n"

        (self.output_dir / f"index.{ext}").write_text(index_content, encoding='utf-8')

        log = OperationLog(
            operation="publish",
            status="success",
            details=json.dumps(result, ensure_ascii=False),
            operator_id=self.operator_id
        )
        self.db.add(log)
        self.db.commit()

        return result