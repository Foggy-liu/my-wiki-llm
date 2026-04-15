"""Ingest Pipeline - 从原材料消化到 Wiki"""

import os
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Dict
from datetime import datetime


@dataclass
class IngestResult:
    """Ingest 操作结果"""
    created_pages: List[str]
    updated_pages: List[str]
    contradictions: List[dict]
    cross_ref_fixes: List[str]
    log_entry: str


class IngestPipeline:
    """
    Ingest 流程

    raw/*.md → 提取引用/概念 → 创建/更新wiki页面 →
    维护交叉引用 → 更新lifecycle → 更新index → 记录log
    """

    def __init__(self, wiki_kb, raw_dir: str = "raw"):
        self.wiki_kb = wiki_kb
        self.raw_dir = Path(raw_dir)

    def ingest_file(self, raw_path: Path) -> IngestResult:
        """
        消化单个源文件

        Args:
            raw_path: raw/ 下的文件路径

        Returns:
            IngestResult
        """
        # 1. 读取 raw 文件
        with open(raw_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 2. 解析文件名获取标题
        title = raw_path.stem
        category = self._guess_category(raw_path)

        # 3. 构建 summary 页面标题
        summary_title = f"raw-{raw_path.parent.name}-{title}"

        # 4. 提取引用/概念（查找 [[wikilinks]]）
        mentioned_pages = self._extract_wikilinks(content)

        # 5. 创建或更新 wiki 页面
        created_pages = []
        updated_pages = []

        page_content = self._build_summary_content(raw_path, content, mentioned_pages)
        new_entry = self._save_summary_page(summary_title, category, page_content)
        created_pages.append(summary_title)

        # 6. 更新 index.md
        self._update_index(new_entry)

        # 7. 检测矛盾（简化版：检查是否有冲突的实体）
        contradictions = self._check_contradictions(mentioned_pages)

        # 8. 维护交叉引用
        cross_ref_fixes = self._fix_cross_references(summary_title, mentioned_pages)

        # 9. 更新 lifecycle
        self.wiki_kb.update_access(summary_title)

        # 10. 记录 log
        log_entry = self._create_log_entry(raw_path, created_pages, updated_pages)
        self.wiki_kb.append_log(log_entry)

        return IngestResult(
            created_pages=created_pages,
            updated_pages=updated_pages,
            contradictions=contradictions,
            cross_ref_fixes=cross_ref_fixes,
            log_entry=log_entry
        )

    def _guess_category(self, raw_path: Path) -> str:
        """根据路径猜测分类"""
        path_str = str(raw_path).lower()
        if "articles" in path_str:
            return "summaries"
        elif "docs" in path_str:
            return "concepts"
        elif "papers" in path_str:
            return "summaries"
        return "summaries"

    def _extract_wikilinks(self, content: str) -> List[str]:
        """从内容中提取引用页面"""
        # 匹配 [[页面标题]] 格式
        wikilink_pattern = r'\[\[([^\]]+)\]\]'
        matches = re.findall(wikilink_pattern, content)
        return list(set(matches))  # 去重

    def _build_summary_content(self, raw_path: Path, content: str, mentioned: List[str]) -> str:
        """构建 summary 页面内容"""
        lines = [
            f"# {raw_path.stem}",
            "",
            f"**源文件**: {raw_path}",
            f"**消化时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 引用页面",
        ]

        if mentioned:
            for m in mentioned:
                lines.append(f"- [[{m}]]")
        else:
            lines.append("(无引用)")

        lines.extend([
            "",
            "## 内容摘要",
            "",
            content[:1000] + "..." if len(content) > 1000 else content,
        ])

        return "\n".join(lines)

    def _save_summary_page(self, title: str, category: str, content: str):
        """保存 summary 页面到 wiki"""
        from artifact_chain.src.wiki_kb import WikiEntry

        now = datetime.now().isoformat()
        entry = WikiEntry(
            title=title,
            category=category,
            content=content,
            tags=["raw", "ingested"],
            sources=[],
            description=f"从原材料消化: {title}",
            confidence=0.5,
            status="active",
            aliases=[],
            created=now,
            updated=now,
            last_accessed=now,
            access_count=0
        )

        # 保存到文件
        category_dir = self.wiki_kb.wiki_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)

        file_path = category_dir / f"{title}.md"
        frontmatter_lines = [
            "---",
            f'title: "{title}"',
            f'category: {category}',
            f'tags: [{", ".join(entry.tags)}]',
            f'sources: []',
            f'description: "{entry.description}"',
            f'confidence: {entry.confidence}',
            f'status: {entry.status}',
            f'aliases: []',
            f'created: "{entry.created}"',
            f'updated: "{entry.updated}"',
            f'last_accessed: "{entry.last_accessed}"',
            f'access_count: {entry.access_count}',
            "---",
            "",
        ]

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(frontmatter_lines))
            f.write(content)

        # 更新内存索引
        self.wiki_kb.entries.append(entry)
        self.wiki_kb._index[title] = entry

        return entry

    def _update_index(self, new_entry) -> None:
        """更新 index.md 文件"""
        index_path = self.wiki_kb.wiki_dir / "index.md"

        # 读取现有 index 内容
        if index_path.exists():
            with open(index_path, 'r', encoding='utf-8') as f:
                index_content = f.read()
        else:
            index_content = "# Wiki Index\n\n> Last updated: \n\n## Entities\n\n| Page | Summary | confidence | status |\n|------|---------|------------|--------|\n\n## Concepts\n\n| Page | Summary | confidence | status |\n|------|---------|------------|--------|\n\n## Summaries\n\n| Page | Summary | confidence | status |\n|------|---------|------------|--------|\n\n## Comparisons\n\n| Page | Summary | confidence | status |\n|------|---------|------------|--------|\n\n## Synthesis\n\n| Page | Summary | confidence | status |\n|------|---------|------------|--------|\n"

        # 找到对应的 category 表格并添加新行
        category_map = {
            "entities": "Entities",
            "concepts": "Concepts",
            "summaries": "Summaries",
            "comparisons": "Comparisons",
            "synthesis": "Synthesis",
        }

        category_name = category_map.get(new_entry.category, "")
        if not category_name:
            return

        # 构建新行
        new_row = f"| [[{new_entry.title}]] | {new_entry.description} | {new_entry.confidence} | {new_entry.status} |\n"

        # 在对应 category 下添加（简单处理：追加到表格末尾）
        # 更完善的实现需要解析 markdown 表格
        lines = index_content.split('\n')

        # 找到 category 标题所在的行
        category_line_idx = -1
        for i, line in enumerate(lines):
            if line.strip() == f"## {category_name}":
                category_line_idx = i
                break

        if category_line_idx >= 0:
            # 找到下一个 ## 标题或文件末尾
            insert_idx = len(lines)
            for i in range(category_line_idx + 1, len(lines)):
                if lines[i].startswith("## "):
                    insert_idx = i
                    break

            # 在表格末尾添加新行（在 |---- 之后）
            # 找到最近的 |---- 行
            table_end_idx = category_line_idx + 1
            while table_end_idx < insert_idx and not lines[table_end_idx].strip().startswith("|---"):
                table_end_idx += 1

            if table_end_idx < insert_idx:
                # 在 |---- 行之后插入新行
                lines.insert(table_end_idx + 1, new_row.rstrip())

            # 更新 total count
            total_match = [l for l in lines if "Total pages:" in l]
            if total_match:
                idx = lines.index(total_match[0])
                import re
                match = re.search(r'Total pages: (\d+)', lines[idx])
                if match:
                    count = int(match.group(1)) + 1
                    lines[idx] = re.sub(r'Total pages: \d+', f'Total pages: {count}', lines[idx])

            # 更新时间戳
            for i, line in enumerate(lines):
                if line.startswith("> Last updated:"):
                    lines[i] = f"> Last updated: {datetime.now().strftime('%Y-%m-%d')}"
                    break

            with open(index_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

    def _check_contradictions(self, mentioned: List[str]) -> List[dict]:
        """检测矛盾（简化版）"""
        contradictions = []

        # 检查是否有同名实体但不同描述的情况（简化检测）
        for page_title in mentioned:
            existing = self.wiki_kb.get_page(page_title)
            if existing and existing.status == "active":
                # 可能存在矛盾（简化处理）
                pass

        return contradictions

    def _fix_cross_references(self, summary_title: str, mentioned: List[str]) -> List[str]:
        """维护交叉引用"""
        fixes = []

        for mentioned_title in mentioned:
            mentioned_page = self.wiki_kb.get_page(mentioned_title)
            if mentioned_page:
                # 确保 summary 页面被提及页面引用
                if f"[[{summary_title}]]" not in mentioned_page.content:
                    # 更新提及页面，添加对 summary 的引用
                    mentioned_page.content += f"\n\n- [[{summary_title}]]"
                    fixes.append(f"Added [[{summary_title}]] to [[{mentioned_title}]]")

        return fixes

    def run_interactive(self) -> List[IngestResult]:
        """交互式消化所有 raw 文件"""
        results = []

        for raw_file in self.raw_dir.rglob("*.md"):
            print(f"Processing: {raw_file}")
            result = self.ingest_file(raw_file)
            results.append(result)
            print(f"  Created: {result.created_pages}")

        return results

    def _create_log_entry(self, raw_path: Path, created: List[str], updated: List[str]) -> str:
        """创建日志条目"""
        now = datetime.now().strftime("%Y-%m-%d")
        created_str = ", ".join([f"[[{c}]]" for c in created]) if created else "None"
        updated_str = ", ".join([f"[[{u}]]" for u in updated]) if updated else "None"

        return f"## [{now}] ingest | {raw_path}\n- Created: {created_str}\n- Updated: {updated_str}\n"
