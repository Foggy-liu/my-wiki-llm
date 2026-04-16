import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.config import settings
from app.db import WikiPage, OperationLog, OperationType, OperationStatus
from app.services.llm import llm_service

class IngestService:
    def __init__(self, db: Session, operator_id: Optional[int] = None):
        self.db = db
        self.operator_id = operator_id
        self.raw_dir = settings.RAW_DIR
        self.wiki_dir = settings.WIKI_DIR

    def get_pending_files(self) -> List[Path]:
        pending = []
        for subdir in ["papers", "articles", "transcripts", "docs"]:
            subdir_path = self.raw_dir / subdir
            if subdir_path.exists():
                for file_path in subdir_path.rglob("*"):
                    if file_path.is_file() and not file_path.name.startswith('.'):
                        pending.append(file_path)
        return pending

    def read_file_content(self, file_path: Path) -> str:
        suffix = file_path.suffix.lower()
        if suffix in ['.md', '.txt']:
            return file_path.read_text(encoding='utf-8')
        elif suffix == '.pdf':
            return f"[PDF content from {file_path.name}]"
        else:
            return f"[Content from {file_path.name}]"

    def extract_wikilinks(self, content: str) -> List[str]:
        pattern = r'\[\[([^\]]+)\]\]'
        return re.findall(pattern, content)

    def ensure_wiki_page(self, title: str, category: str = "entities") -> Path:
        category_dir = self.wiki_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)

        safe_title = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', title)
        safe_title = safe_title.strip()[:100]
        file_path = category_dir / f"{safe_title}.md"

        if not file_path.exists():
            frontmatter = f"""---
title: {title}
category: {category}
created: {datetime.now().strftime('%Y-%m-%d')}
updated: {datetime.now().strftime('%Y-%m-%d')}
sources: []
description:
confidence: 0.5
status: active
---

## {title}

<!-- Page created automatically via Ingest -->
"""
            file_path.write_text(frontmatter, encoding='utf-8')

            db_page = WikiPage(
                title=title,
                category=category,
                file_path=str(file_path),
                confidence=0.5,
                status="active"
            )
            self.db.add(db_page)
            self.db.commit()

        return file_path

    def update_wiki_page(self, page: WikiPage, content: str, sources: List[str]):
        file_path = Path(page.file_path)
        if not file_path.exists():
            return

        existing_content = file_path.read_text(encoding='utf-8')

        import re
        updated_content = re.sub(
            r'^sources:.*$',
            f'sources:\n' + '\n'.join(f'  - "[[{s}]]"' for s in sources),
            existing_content,
            flags=re.MULTILINE
        )
        updated_content = re.sub(
            r'^updated:.*$',
            f'updated: {datetime.now().strftime("%Y-%m-%d")}',
            updated_content,
            flags=re.MULTILINE
        )

        file_path.write_text(updated_content, encoding='utf-8')
        page.updated_at = datetime.utcnow()
        self.db.commit()

    async def ingest_file(self, file_path: Path) -> Dict[str, Any]:
        result = {
            "file": str(file_path),
            "status": "success",
            "entities_created": [],
            "links_updated": [],
            "error": None
        }

        try:
            content = self.read_file_content(file_path)
            entities = await llm_service.extract_entities(content)

            for entity in entities:
                title = entity.get("title", "")
                category = entity.get("category", "entities")
                description = entity.get("description", "")
                properties = entity.get("properties", {})
                sources = entity.get("sources", [str(file_path)])

                page_path = self.ensure_wiki_page(title, category)

                page = self.db.query(WikiPage).filter(
                    WikiPage.file_path == str(page_path)
                ).first()

                if page:
                    self.update_wiki_page(page, content, sources)
                    result["links_updated"].append(title)
                else:
                    page_content = f"""---
title: {title}
category: {category}
created: {datetime.now().strftime('%Y-%m-%d')}
updated: {datetime.now().strftime('%Y-%m-%d')}
sources:
"""
                    for s in sources:
                        page_content += f"  - \"[[{s}]]\"\n"
                    page_content += f"""description: {description}
confidence: 0.75
status: active
---

## {title}

"""
                    for key, value in properties.items():
                        page_content += f"- **{key}:** {value}\n"

                    page_content += f"\n## 来源\n"
                    for s in sources:
                        page_content += f"- [[{s}]]\n"

                    page_path.write_text(page_content, encoding='utf-8')

                    db_page = WikiPage(
                        title=title,
                        category=category,
                        file_path=str(page_path),
                        confidence=0.75,
                        status="active"
                    )
                    self.db.add(db_page)
                    self.db.commit()
                    result["entities_created"].append(title)

            await self._update_index()
            self._log_operation("ingest", "success", result)

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            self._log_operation("ingest", "failed", result)

        return result

    async def _update_index(self):
        index_path = self.wiki_dir / "index.md"

        pages = self.db.query(WikiPage).all()

        by_category = {}
        for page in pages:
            if page.category not in by_category:
                by_category[page.category] = []
            by_category[page.category].append(page)

        content = """---
title: Wiki Index
category: index
created: 2026-04-16
updated: {updated}
---

# 文物 IP 知识库

## 目录

| 分类 | 页面数 | 最近更新 |
|------|--------|----------|
""".format(updated=datetime.now().strftime('%Y-%m-%d'))

        for cat in ["entities", "concepts", "summaries", "comparisons", "synthesis"]:
            cat_pages = by_category.get(cat, [])
            recent = max([p.updated_at for p in cat_pages], default="-")
            if recent != "-":
                recent = recent.strftime('%Y-%m-%d')
            content += f"| {cat} | {len(cat_pages)} | {recent} |\n"

        content += "\n## 所有页面\n\n"
        for cat in ["entities", "concepts", "summaries", "comparisons", "synthesis"]:
            cat_pages = by_category.get(cat, [])
            if cat_pages:
                content += f"### {cat}\n"
                for p in cat_pages:
                    content += f"- [[{p.title}]]\n"

        index_path.write_text(content, encoding='utf-8')

    def _log_operation(self, operation: str, status: str, details: Dict):
        log = OperationLog(
            operation=operation,
            status=status,
            details=json.dumps(details, ensure_ascii=False),
            operator_id=self.operator_id
        )
        self.db.add(log)
        self.db.commit()

    async def run(self) -> List[Dict[str, Any]]:
        pending = self.get_pending_files()
        results = []
        for file_path in pending:
            result = await self.ingest_file(file_path)
            results.append(result)
        return results