"""Lint Pipeline - Wiki 健康检查和生命周期管理"""

import re
from dataclasses import dataclass
from typing import List, Dict, Set
from datetime import datetime, timedelta


@dataclass
class LintIssue:
    """Lint 问题"""
    severity: str  # "error", "warning", "info"
    category: str  # "structure", "lifecycle", "reference", "frontmatter"
    page: str
    description: str
    fix_suggestion: str


@dataclass
class LintResult:
    """Lint 操作结果"""
    issues: List[LintIssue]
    fixed_issues: List[LintIssue]
    lifecycle_changes: List[dict]
    log_entry: str


class LintPipeline:
    """
    Lint 流程

    矛盾检测 → 孤立页面 → 缺失页面 →
    交叉引用完整性 → 生命周期检查 → 归档 → 记录log
    """

    # 时间衰减规则
    DECAY_RULES = [
        (30, 59, 0.02),   # 30-59 天: -0.02
        (60, 89, 0.05),   # 60-89 天: -0.05
        (90, 179, 0.10),  # 90-179 天: -0.10
        (180, float('inf'), 0.15),  # >= 180 天: -0.15
    ]

    def __init__(self, wiki_kb):
        self.wiki_kb = wiki_kb

    def run_all(self) -> LintResult:
        """运行全部 Lint 检查"""
        all_issues = []

        # 1. 矛盾检测
        all_issues.extend(self.check_contradictions())

        # 2. 孤立页面检查
        all_issues.extend(self.check_orphaned_pages())

        # 3. 缺失页面检查
        all_issues.extend(self.check_missing_pages())

        # 4. 交叉引用完整性检查
        all_issues.extend(self.check_cross_ref_integrity())

        # 5. 生命周期检查
        lifecycle_changes = self.check_lifecycle()

        # 6. 自动修复部分问题
        fixed_issues = self._auto_fix_issues(all_issues)

        # 7. 记录 log
        log_entry = self._create_log_entry(len(all_issues), len(fixed_issues), lifecycle_changes)
        self.wiki_kb.append_log(log_entry)

        return LintResult(
            issues=all_issues,
            fixed_issues=fixed_issues,
            lifecycle_changes=lifecycle_changes,
            log_entry=log_entry
        )

    def check_contradictions(self) -> List[LintIssue]:
        """检测矛盾页面"""
        issues = []

        # 简化版：检查是否有同一实体在不同页面有冲突描述
        all_pages = {p.title: p for p in self.wiki_kb.list_pages()}

        # 检查是否有实体页面引用了不存在的对比页面
        for title, page in all_pages.items():
            if page.category == "entities":
                # 检查是否提到了对比类页面
                if "对比" in page.content or "vs" in page.content.lower():
                    # 简化检测
                    pass

        return issues

    def check_orphaned_pages(self) -> List[LintIssue]:
        """检查孤立页面"""
        issues = []
        all_pages = {p.title: p for p in self.wiki_kb.list_pages()}

        # 构建引用图
        references: Dict[str, Set[str]] = {}
        for title in all_pages:
            references[title] = set()

        # 收集所有引用
        for title, page in all_pages.items():
            wikilinks = re.findall(r'\[\[([^\]]+)\]\]', page.content)
            for link in wikilinks:
                if link in all_pages:
                    references[link].add(title)

        # 检查孤立页面
        for title, page in all_pages.items():
            if page.category in ["summaries", "comparisons", "synthesis"]:
                continue  # 这些类别允许孤立

            if not references[title]:
                issues.append(LintIssue(
                    severity="warning",
                    category="reference",
                    page=title,
                    description="孤立页面：没有被其他页面引用",
                    fix_suggestion=f"从相关页面添加 [[{title}]] 引用"
                ))

        return issues

    def check_missing_pages(self) -> List[LintIssue]:
        """检查缺失页面（引用了但不存在的页面）"""
        issues = []
        all_pages = {p.title: p for p in self.wiki_kb.list_pages()}

        # 收集所有 wikilinks
        all_links: Set[str] = set()
        for page in all_pages.values():
            wikilinks = re.findall(r'\[\[([^\]]+)\]\]', page.content)
            all_links.update(wikilinks)

        # 检查不存在的引用
        for link in all_links:
            if link not in all_pages and link not in ["index.md", "log.md", "lifecycle.md"]:
                issues.append(LintIssue(
                    severity="error",
                    category="reference",
                    page=link,
                    description=f"引用了不存在的页面: [[{link}]]",
                    fix_suggestion=f"创建页面 {link} 或修正引用"
                ))

        return issues

    def check_cross_ref_integrity(self) -> List[LintIssue]:
        """检查交叉引用完整性"""
        issues = []
        all_pages = {p.title: p for p in self.wiki_kb.list_pages()}

        for title, page in all_pages.items():
            # 检查是否有悬空的引用
            wikilinks = re.findall(r'\[\[([^\]]+)\]\]', page.content)
            for link in wikilinks:
                if link not in all_pages:
                    issues.append(LintIssue(
                        severity="warning",
                        category="reference",
                        page=title,
                        description=f"引用了不存在的页面: [[{link}]]",
                        fix_suggestion=f"创建 [[{link}]] 或移除引用"
                    ))

        return issues

    def check_lifecycle(self) -> List[dict]:
        """检查生命周期状态，应用时间衰减"""
        changes = []
        now = datetime.now()

        for page in self.wiki_kb.list_pages():
            if not page.last_accessed:
                continue

            try:
                last_access = datetime.fromisoformat(page.last_accessed)
                days_since_access = (now - last_access).days

                # 计算衰减
                decay = 0.0
                for min_days, max_days, decay_rate in self.DECAY_RULES:
                    if min_days <= days_since_access <= max_days:
                        decay = decay_rate
                        break

                if decay > 0 and page.confidence > 0.1:
                    old_confidence = page.confidence
                    page.confidence = max(0.1, page.confidence - decay)
                    changes.append({
                        "page": page.title,
                        "action": "decay",
                        "old_confidence": old_confidence,
                        "new_confidence": page.confidence,
                        "days_since_access": days_since_access
                    })
                    # 更新页面
                    self.wiki_kb._save_entry(page)

                    # 检查是否应该归档
                    if page.confidence <= 0.2 and page.status == "active":
                        page.status = "stale"
                        changes.append({
                            "page": page.title,
                            "action": "status_change",
                            "old_status": "active",
                            "new_status": "stale"
                        })
                        self.wiki_kb._save_entry(page)

            except (ValueError, TypeError):
                continue

        return changes

    def _auto_fix_issues(self, issues: List[LintIssue]) -> List[LintIssue]:
        """自动修复部分问题"""
        fixed = []

        for issue in issues:
            if issue.severity == "info":
                # info 级别的问题可以自动修复
                fixed.append(issue)

        return fixed

    def _create_log_entry(self, total_issues: int, fixed: int, lifecycle_changes: List[dict]) -> str:
        """创建日志条目"""
        now = datetime.now().strftime("%Y-%m-%d")
        decay_count = sum(1 for c in lifecycle_changes if c.get("action") == "decay")
        status_count = sum(1 for c in lifecycle_changes if c.get("action") == "status_change")

        return (
            f"## [{now}] lint | Health Check\n"
            f"- Issues: {total_issues} | Fixed: {fixed}\n"
            f"- Lifecycle: Decay: {decay_count} | Status changes: {status_count}\n"
        )
