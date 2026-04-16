import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.config import settings
from app.db import WikiPage, OperationLog, PageStatus

class LintIssue:
    def __init__(self, issue_type: str, severity: str, page: str, description: str, auto_fix: bool = False):
        self.issue_type = issue_type
        self.severity = severity
        self.page = page
        self.description = description
        self.auto_fix = auto_fix

class LintService:
    def __init__(self, db: Session, operator_id: Optional[int] = None):
        self.db = db
        self.operator_id = operator_id
        self.raw_dir = settings.RAW_DIR
        self.wiki_dir = settings.WIKI_DIR
        self.issues: List[LintIssue] = []

    def check_orphaned_pages(self) -> List[LintIssue]:
        issues = []

        all_links: Dict[str, List[str]] = {}
        all_titles = set()

        pages = self.db.query(WikiPage).all()
        for page in pages:
            all_titles.add(page.title)
            content = self._read_page_content(page)
            links = self._extract_wikilinks(content)
            all_links[page.title] = links

        referenced = set()
        for title, links in all_links.items():
            for link in links:
                referenced.add(link)

        for page in pages:
            if page.title not in referenced:
                issues.append(LintIssue(
                    issue_type="orphaned",
                    severity="warning",
                    page=page.title,
                    description=f"页面未被其他页面引用",
                    auto_fix=False
                ))

        return issues

    def check_missing_references(self) -> List[LintIssue]:
        issues = []

        pages = self.db.query(WikiPage).all()
        all_titles = {p.title for p in pages}

        for page in pages:
            content = self._read_page_content(page)
            links = self._extract_wikilinks(content)

            for link in links:
                if link not in all_titles:
                    issues.append(LintIssue(
                        issue_type="missing_ref",
                        severity="error",
                        page=page.title,
                        description=f"引用了不存在的页面: {link}",
                        auto_fix=True
                    ))

        return issues

    def check_raw_sync(self) -> List[LintIssue]:
        issues = []

        pages = self.db.query(WikiPage).all()

        for page in pages:
            if not Path(page.file_path).exists():
                issues.append(LintIssue(
                    issue_type="missing_file",
                    severity="error",
                    page=page.title,
                    description=f"页面文件不存在: {page.file_path}",
                    auto_fix=False
                ))

        return issues

    def check_contradictions(self) -> List[LintIssue]:
        issues = []

        pages = self.db.query(WikiPage).filter(WikiPage.category == "comparisons").all()

        for page in pages:
            content = self._read_page_content(page)
            if "矛盾" in content or "冲突" in content:
                issues.append(LintIssue(
                    issue_type="contradiction",
                    severity="warning",
                    page=page.title,
                    description="页面标记了潜在的矛盾信息",
                    auto_fix=False
                ))

        return issues

    def _read_page_content(self, page: WikiPage) -> str:
        file_path = Path(page.file_path)
        if not file_path.exists():
            return ""
        return file_path.read_text(encoding='utf-8')

    def _extract_wikilinks(self, content: str) -> List[str]:
        pattern = r'\[\[([^\]]+)\]\]'
        return re.findall(pattern, content)

    def auto_fix_issue(self, issue: LintIssue) -> bool:
        if issue.issue_type == "missing_ref":
            return self._auto_create_missing_page(issue)
        return False

    def _auto_create_missing_page(self, issue: LintIssue) -> bool:
        match = re.search(r':\s*(.+)$', issue.description)
        if not match:
            return False

        missing_title = match.group(1).strip()

        category = "entities"
        if any(kw in missing_title for kw in ["文化", "概念", "理论"]):
            category = "concepts"
        elif any(kw in missing_title for kw in ["对比", "比较"]):
            category = "comparisons"

        category_dir = self.wiki_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)

        safe_title = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', missing_title)
        file_path = category_dir / f"{safe_title}.md"

        if file_path.exists():
            return False

        frontmatter = f"""---
title: {missing_title}
category: {category}
created: {datetime.now().strftime('%Y-%m-%d')}
updated: {datetime.now().strftime('%Y-%m-%d')}
sources: []
description:
confidence: 0.3
status: active
---

## {missing_title}

<!-- 页面已自动创建以解决缺失引用问题 -->
<!-- 请补充内容 -->
"""
        file_path.write_text(frontmatter, encoding='utf-8')

        db_page = WikiPage(
            title=missing_title,
            category=category,
            file_path=str(file_path),
            confidence=0.3,
            status="active"
        )
        self.db.add(db_page)
        self.db.commit()

        return True

    def run(self, auto_fix: bool = True) -> Dict[str, Any]:
        self.issues = []

        self.issues.extend(self.check_orphaned_pages())
        self.issues.extend(self.check_missing_references())
        self.issues.extend(self.check_raw_sync())
        self.issues.extend(self.check_contradictions())

        fixed = []
        if auto_fix:
            for issue in self.issues:
                if issue.auto_fix:
                    if self.auto_fix_issue(issue):
                        fixed.append(issue.description)

        for issue in self.issues:
            if issue.severity == "error":
                page = self.db.query(WikiPage).filter(WikiPage.title == issue.page).first()
                if page:
                    page.status = PageStatus.STALE.value
                    page.updated_at = datetime.utcnow()
        self.db.commit()

        result = {
            "total_issues": len(self.issues),
            "errors": len([i for i in self.issues if i.severity == "error"]),
            "warnings": len([i for i in self.issues if i.severity == "warning"]),
            "info": len([i for i in self.issues if i.severity == "info"]),
            "fixed": fixed,
            "issues": [
                {
                    "type": i.issue_type,
                    "severity": i.severity,
                    "page": i.page,
                    "description": i.description,
                    "auto_fix": i.auto_fix
                }
                for i in self.issues
            ]
        }

        log = OperationLog(
            operation="lint",
            status="success",
            details=json.dumps(result, ensure_ascii=False),
            operator_id=self.operator_id
        )
        self.db.add(log)
        self.db.commit()

        return result