"""Wiki知识库操作模块 - 修正版"""
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass


@dataclass
class WikiEntry:
    """Wiki词条"""
    title: str
    category: str
    content: str
    tags: List[str]
    sources: List[str]
    description: str
    confidence: float = 0.5
    status: str = "active"
    aliases: List[str] = None
    created: str = ""
    updated: str = ""

    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []


@dataclass
class RetrievedEntry:
    """检索结果"""
    entry: WikiEntry
    score: float
    highlight: str


class WikiKnowledgeBase:
    """Wiki知识库"""

    def __init__(self, wiki_dir: str = "wiki"):
        self.wiki_dir = Path(wiki_dir)
        self.entries: List[WikiEntry] = []
        self._index: Dict[str, WikiEntry] = {}
        self._load_entries()

    def _load_entries(self):
        """加载所有Wiki页面"""
        if not self.wiki_dir.exists():
            return

        for subdir in ["entities", "concepts"]:
            subpath = self.wiki_dir / subdir
            if subpath.exists():
                for md_file in subpath.glob("*.md"):
                    if md_file.name in ["index.md", "log.md", "lifecycle.md"]:
                        continue
                    entry = self._parse_markdown(md_file, subdir)
                    if entry:
                        self.entries.append(entry)
                        self._index[entry.title] = entry
                        for alias in entry.aliases:
                            self._index[alias] = entry

    def _parse_markdown(self, file_path: Path, category: str) -> Optional[WikiEntry]:
        """解析Markdown文件，提取 frontmatter 和正文"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        frontmatter = {}
        body_lines = []
        in_frontmatter = False
        current_list_key = None
        current_list_values = []

        for line in content.split("\n"):
            if line.strip() == "---":
                if in_frontmatter and current_list_key:
                    frontmatter[current_list_key] = current_list_values
                in_frontmatter = not in_frontmatter
                current_list_key = None
                current_list_values = []
                continue
            if in_frontmatter:
                stripped = line.strip()
                # 检查是否是列表项 (以 - 开头)
                if stripped.startswith("- "):
                    value = stripped[2:].strip().strip('"').strip("'")
                    if current_list_key:
                        current_list_values.append(value)
                    else:
                        current_list_key = None
                elif ":" in line:
                    # 保存之前的列表
                    if current_list_key and current_list_values:
                        frontmatter[current_list_key] = current_list_values
                        current_list_key = None
                        current_list_values = []

                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")

                    if value.startswith("["):
                        items = value.strip("[]").split(",")
                        frontmatter[key] = [i.strip().strip('"').strip("'") for i in items]
                    elif value == "":
                        # 空值可能是列表的开始
                        current_list_key = key
                        current_list_values = []
                    else:
                        frontmatter[key] = value
            else:
                body_lines.append(line)

        # 保存最后的列表
        if current_list_key and current_list_values:
            frontmatter[current_list_key] = current_list_values

        body = "\n".join(body_lines)

        tags = frontmatter.get("tags", [category])
        if isinstance(tags, str):
            tags = [tags]

        sources = frontmatter.get("sources", [])
        if isinstance(sources, str):
            sources = [sources]

        confidence_str = frontmatter.get("confidence", "0.5")
        confidence = float(confidence_str) if confidence_str else 0.5

        status = frontmatter.get("status", "active")

        aliases = frontmatter.get("aliases", [])
        if isinstance(aliases, str):
            aliases = [aliases]

        created = frontmatter.get("created", "")
        updated = frontmatter.get("updated", "")
        description = frontmatter.get("description", "")

        return WikiEntry(
            title=frontmatter.get("title", file_path.stem),
            category=category,
            content=body,
            tags=tags,
            sources=sources,
            description=description,
            confidence=confidence,
            status=status,
            aliases=aliases,
            created=created,
            updated=updated
        )

    def get_page(self, title: str) -> Optional[WikiEntry]:
        """
        根据标题或别名获取 Wiki 页面

        这是 LLM 辅助查询的核心方法
        """
        return self._index.get(title)

    def list_pages(self, category: Optional[str] = None,
                   status: Optional[str] = None) -> List[WikiEntry]:
        """
        列出 Wiki 页面（支持过滤）

        LLM 读取 index.md 后，可以用此方法筛选页面
        """
        results = self.entries
        if category:
            results = [e for e in results if e.category == category]
        if status:
            results = [e for e in results if e.status == status]
        return results

    def get_high_confidence_pages(self, threshold: float = 0.7) -> List[WikiEntry]:
        """获取高置信度页面（供 LLM 优先查询）"""
        return [e for e in self.entries if e.confidence >= threshold]

    def get_related_pages(self, title: str) -> List[WikiEntry]:
        """
        获取相关页面（通过 [[wikilinks]] 关联）
        """
        target = self.get_page(title)
        if not target:
            return []

        related = []
        for entry in self.entries:
            if entry.title == title:
                continue
            if f"[[{title}]]" in entry.content:
                related.append(entry)

        return related

    def search(self, keyword: str) -> List[RetrievedEntry]:
        """
        关键字搜索（简单查询后备）

        注意：这是简单的关键字匹配，不是 LLM 辅助查询
        LLM 辅助查询应该使用 get_page() + list_pages() 组合
        """
        results = []
        keyword_lower = keyword.lower()

        for entry in self.entries:
            score = 0.0
            if keyword_lower in entry.title.lower():
                score = 1.0
            elif any(keyword_lower in alias.lower() for alias in entry.aliases):
                score = 0.9
            elif keyword_lower in entry.content.lower():
                score = 0.5

            if score > 0:
                highlight = self._extract_highlight(entry.content, keyword)
                results.append(RetrievedEntry(
                    entry=entry,
                    score=score,
                    highlight=highlight
                ))

        results.sort(key=lambda x: x.score, reverse=True)
        return results

    def _extract_highlight(self, content: str, keyword: str, context_len: int = 100) -> str:
        """提取关键词周围的上下文"""
        keyword_lower = keyword.lower()
        content_lower = content.lower()
        pos = content_lower.find(keyword_lower)

        if pos == -1:
            return content[:context_len] + "..."

        start = max(0, pos - context_len // 2)
        end = min(len(content), pos + len(keyword) + context_len // 2)

        return content[start:end] + "..."

    def read_index(self) -> str:
        """读取 index.md 内容（供 LLM 理解 Wiki 结构）"""
        index_path = self.wiki_dir / "index.md"
        if index_path.exists():
            with open(index_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def read_log(self) -> str:
        """读取 log.md 内容（最近操作历史）"""
        log_path = self.wiki_dir / "log.md"
        if log_path.exists():
            with open(log_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""
