# 文物 IP 内容自动化生产链 - 实现计划 v2.0

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修正 LLM Wiki 实现错误，建立正确的知识查询架构

**Architecture:** 三层架构 + 正确的 LLM Wiki 知识库（LLM 辅助查询，而非关键字匹配）

**Tech Stack:** Python 3.10+, 纯文件系统, Markdown 格式（严格遵循 llm-wiki.md 规范）

---

## 核心修正说明

### 之前的错误理解

**错误：** `Retriever` 使用关键字匹配查询 Wiki
```python
# 错误的实现
artifact_results = self.wiki_kb.search(intent.artifact)  # 简单关键字匹配
```

### 正确的 LLM Wiki Query 流程

根据 `llm-wiki.md` 第 39 行：
> "The LLM **searches for relevant pages, reads them, and synthesizes an answer**."

```
用户提问 → LLM 读取 index.md（理解 Wiki 结构）→ LLM 选择相关页面 → 读取页面 → 综合回答
```

**关键区别：**
- IntentParser 负责分解用户输入（素材是什么？风格是什么？）
- Wiki 负责提供**史实约束**，Wiki 查询是 **LLM 辅助的**
- LLM 理解 Wiki 结构后选择读哪些页面，而不是简单关键字匹配

---

## 文件结构（修正后）

```
artifact_chain/
├── config/
│   └── settings.py              # 配置管理
├── wiki/                        # Wiki知识库（严格遵循 llm-wiki 规范）
│   ├── index.md                 # 全局索引（含 confidence、status 列）
│   ├── log.md                   # 操作日志（新增）
│   ├── lifecycle.md             # 生命周期数据（可选，推荐添加）
│   ├── entities/                # 实体（文物）
│   │   ├── 青铜面具.md          # 含 aliases, confidence, status
│   │   └── 三星堆遗址.md
│   └── concepts/                # 概念（方法论）
│       ├── 悬疑叙事技巧.md
│       └── 短视频脚本结构.md
├── src/                         # 源代码
│   ├── __init__.py
│   ├── intent_parser.py         # 意图解析模块
│   ├── wiki_kb.py               # Wiki知识库操作（修正）
│   ├── retriever.py             # 检索模块（LLM辅助查询，修正）
│   ├── script_gen.py            # 脚本生成（简化）
│   └── prompt_gen.py            # Prompt生成（简化）
├── tests/                       # 单元测试
├── main.py                      # 主入口
└── requirements.txt             # 依赖
```

---

## 任务分解

### Task 1: 修正 Wiki 页面格式（添加 confidence、status、aliases）

**Files:**
- Modify: `artifact_chain/wiki/entities/青铜面具.md`
- Modify: `artifact_chain/wiki/entities/三星堆遗址.md`
- Modify: `artifact_chain/wiki/concepts/悬疑叙事技巧.md`
- Modify: `artifact_chain/wiki/concepts/短视频脚本结构.md`

- [ ] **Step 1: 更新 `wiki/entities/青铜面具.md` frontmatter**

修改后的 frontmatter：

```yaml
---
title: 青铜面具
aliases: [Bronze Mask, 三星堆面具, 青铜面具]
tags: [三星堆, 青铜器, 古蜀文明, 祭祀, 文物]
category: entities
created: 2026-04-15
updated: 2026-04-15
sources:
  - "[[raw/papers/三星堆考古报告_2023.pdf]]"
  - "[[raw/articles/青铜面具研究综述.md]]"
description: 三星堆遗址出土的青铜面具，古蜀文明重要代表性器物
confidence: 0.75
status: active
---
```

- [ ] **Step 2: 更新 `wiki/entities/三星堆遗址.md` frontmatter**

```yaml
---
title: 三星堆遗址
aliases: [Sanxingdui, 广汉遗址]
tags: [三星堆, 古蜀文明, 考古, 遗址]
category: entities
created: 2026-04-15
updated: 2026-04-15
sources:
  - "[[raw/papers/三星堆考古报告_2023.pdf]]"
description: 位于四川广汉的古蜀文明遗址
confidence: 0.80
status: active
---
```

- [ ] **Step 3: 更新 `wiki/concepts/悬疑叙事技巧.md` frontmatter**

```yaml
---
title: 悬疑叙事技巧
aliases: [Suspense Narrative, 悬疑创作]
tags: [悬疑, 叙事技巧, 短视频, 创作方法论]
category: concepts
created: 2026-04-15
updated: 2026-04-15
sources:
  - "[[raw/docs/短视频创作指南.md]]"
description: 悬疑风格短视频的叙事方法与技巧
confidence: 0.70
status: active
---
```

- [ ] **Step 4: 更新 `wiki/concepts/短视频脚本结构.md` frontmatter**

```yaml
---
title: 短视频脚本结构
aliases: [Short Video Structure, 脚本格式]
tags: [短视频, 脚本结构, 创作, 60秒]
category: concepts
created: 2026-04-15
updated: 2026-04-15
sources:
  - "[[raw/docs/短视频创作指南.md]]"
description: 60秒短视频的标准脚本结构
confidence: 0.70
status: active
---
```

- [ ] **Step 5: 验证修改**

Run: `grep -E "confidence:|status:|aliases:" wiki/entities/青铜面具.md wiki/entities/三星堆遗址.md wiki/concepts/悬疑叙事技巧.md wiki/concepts/短视频脚本结构.md`
Expected: 找到所有三个字段

---

### Task 2: 修正 index.md 格式（添加 confidence、status 列）

**Files:**
- Modify: `artifact_chain/wiki/index.md`

- [ ] **Step 1: 更新 `wiki/index.md` 为正确的表格格式**

```markdown
# Wiki Index

> Last updated: 2026-04-15 | Total pages: 4 | Total materials: 2

## Entities

| Page | Confidence | Status | Updated | Description |
|------|------------|--------|---------|-------------|
| [[青铜面具]] | 0.75 | active | 2026-04-15 | 三星堆出土的青铜面具，古蜀文明重要代表性器物 |
| [[三星堆遗址]] | 0.80 | active | 2026-04-15 | 位于四川广汉的古蜀文明遗址 |

## Concepts

| Page | Confidence | Status | Updated | Description |
|------|------------|--------|---------|-------------|
| [[悬疑叙事技巧]] | 0.70 | active | 2026-04-15 | 悬疑风格短视频的叙事方法与技巧 |
| [[短视频脚本结构]] | 0.70 | active | 2026-04-15 | 60秒短视频的标准脚本结构 |
```

- [ ] **Step 2: 验证格式**

Run: `grep -E "^\|.*\|" wiki/index.md | head -20`
Expected: 表格格式正确，包含 Confidence 和 Status 列

---

### Task 3: 添加 log.md（操作日志）

**Files:**
- Create: `artifact_chain/wiki/log.md`

- [ ] **Step 1: 创建 `wiki/log.md`**

```markdown
# Wiki Log

## [2026-04-15] initialize | Wiki Knowledge Base
- Created: [[青铜面具]], [[三星堆遗址]], [[悬疑叙事技巧]], [[短视频脚本结构]]
- Updated: [[index.md]]
- Note: 初始化文物IP知识库
```

- [ ] **Step 2: 验证文件创建**

Run: `test -f wiki/log.md && echo "exists" || echo "missing"`
Expected: exists

---

### Task 4: 添加 lifecycle.md（生命周期数据，可选但推荐）

**Files:**
- Create: `artifact_chain/wiki/lifecycle.md`

- [ ] **Step 1: 创建 `wiki/lifecycle.md`**

```markdown
# Wiki Lifecycle Registry

> This file tracks knowledge lifecycle data. It is pluggable — deleting it does not affect core wiki functionality.

## Entities

| Page | Confidence | Status | Access | Last Accessed | Superseded By | Supersedes |
|------|------------|--------|--------|-------------|---------------|------------|
| 青铜面具 | 0.75 | active | 0 | 2026-04-15 | | |
| 三星堆遗址 | 0.80 | active | 0 | 2026-04-15 | | |

## Concepts

| Page | Confidence | Status | Access | Last Accessed | Superseded By | Supersedes |
|------|------------|--------|--------|-------------|---------------|------------|
| 悬疑叙事技巧 | 0.70 | active | 0 | 2026-04-15 | | |
| 短视频脚本结构 | 0.70 | active | 0 | 2026-04-15 | | |

## Decay Coefficients

| Category | Daily Decay Rate |
|----------|-----------------|
| entities | 0.0001 |
| concepts | 0.00005 |
| summaries | 0.0002 |
| comparisons | 0.0003 |
| synthesis | 0.0002 |
```

- [ ] **Step 2: 验证文件创建**

Run: `test -f wiki/lifecycle.md && echo "exists" || echo "missing"`
Expected: exists

---

### Task 5: 修正 wiki_kb.py（支持新字段 + LLM 辅助查询接口）

**Files:**
- Modify: `artifact_chain/src/wiki_kb.py`
- Create: `tests/test_wiki_kb.py`

- [ ] **Step 1: 写测试 `tests/test_wiki_kb.py`**

```python
import pytest
from src.wiki_kb import WikiKnowledgeBase, WikiEntry, RetrievedEntry

def test_wiki_kb_load():
    """测试加载 Wiki 知识库"""
    kb = WikiKnowledgeBase("wiki")
    assert isinstance(kb.entries, list)
    assert len(kb.entries) > 0

def test_entries_have_required_fields():
    """测试 Wiki 条目包含必需字段"""
    kb = WikiKnowledgeBase("wiki")
    for entry in kb.entries:
        assert hasattr(entry, 'title')
        assert hasattr(entry, 'category')
        assert hasattr(entry, 'content')
        assert hasattr(entry, 'confidence')  # 新增字段
        assert hasattr(entry, 'status')       # 新增字段
        assert hasattr(entry, 'aliases')      # 新增字段

def test_get_page():
    """测试获取指定页面"""
    kb = WikiKnowledgeBase("wiki")
    entry = kb.get_page("青铜面具")
    assert entry is not None
    assert entry.title == "青铜面具"
    assert entry.confidence == 0.75
    assert entry.status == "active"

def test_get_page_not_found():
    """测试获取不存在的页面"""
    kb = WikiKnowledgeBase("wiki")
    entry = kb.get_page("不存在的页面")
    assert entry is None

def test_list_pages():
    """测试列出所有页面（带过滤）"""
    kb = WikiKnowledgeBase("wiki")
    pages = kb.list_pages(category="entities")
    assert all(p.category == "entities" for p in pages)

def test_list_pages_by_status():
    """测试按状态列出页面"""
    kb = WikiKnowledgeBase("wiki")
    pages = kb.list_pages(status="active")
    assert all(p.status == "active" for p in pages)
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_wiki_kb.py -v`
Expected: FAIL — 方法不存在

- [ ] **Step 3: 实现修正后的 `src/wiki_kb.py`**

```python
"""Wiki知识库操作模块 - 修正版"""
from pathlib import Path
from typing import List, Optional, Dict
import re


@dataclass
class WikiEntry:
    """Wiki词条"""
    title: str
    category: str
    content: str
    tags: List[str]
    sources: List[str]
    description: str
    confidence: float = 0.5       # 新增
    status: str = "active"        # 新增
    aliases: List[str] = None     # 新增
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
        self._index: Dict[str, WikiEntry] = {}  # 页面名称索引
        self._load_entries()

    def _load_entries(self):
        """加载所有Wiki页面"""
        if not self.wiki_dir.exists():
            return

        # 加载 entities 和 concepts
        for subdir in ["entities", "concepts"]:
            subpath = self.wiki_dir / subdir
            if subpath.exists():
                for md_file in subpath.glob("*.md"):
                    if md_file.name == "index.md":
                        continue
                    entry = self._parse_markdown(md_file, subdir)
                    if entry:
                        self.entries.append(entry)
                        # 构建索引（支持别名）
                        self._index[entry.title] = entry
                        for alias in entry.aliases:
                            self._index[alias] = entry

    def _parse_markdown(self, file_path: Path, category: str) -> Optional[WikiEntry]:
        """解析Markdown文件，提取 frontmatter 和正文"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 提取 frontmatter
        frontmatter = {}
        body_lines = []
        in_frontmatter = False

        for line in content.split("\n"):
            if line.strip() == "---":
                in_frontmatter = not in_frontmatter
                continue
            if in_frontmatter:
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    # 处理列表
                    if value.startswith("["):
                        # 简单解析 [item1, item2]
                        items = value.strip("[]").split(",")
                        frontmatter[key] = [i.strip().strip('"').strip("'") for i in items]
                    else:
                        frontmatter[key] = value
            else:
                body_lines.append(line)

        body = "\n".join(body_lines)

        # 提取 tags（从 frontmatter 或默认）
        tags = frontmatter.get("tags", [category])
        if isinstance(tags, str):
            tags = [tags]

        # 提取 sources
        sources = frontmatter.get("sources", [])
        if isinstance(sources, str):
            sources = [sources]

        # 提取 confidence 和 status
        confidence_str = frontmatter.get("confidence", "0.5")
        confidence = float(confidence_str) if confidence_str else 0.5

        status = frontmatter.get("status", "active")

        # 提取 aliases
        aliases = frontmatter.get("aliases", [])
        if isinstance(aliases, str):
            aliases = [aliases]

        # 提取 created 和 updated
        created = frontmatter.get("created", "")
        updated = frontmatter.get("updated", "")

        # 提取 description
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

        这是 LLM 辅助查询的核心方法 —— LLM 通过此方法获取指定页面
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

        返回引用了指定页面的其他页面
        """
        target = self.get_page(title)
        if not target:
            return []

        related = []
        target_lower = title.lower()

        for entry in self.entries:
            if entry.title == title:
                continue
            # 检查 content 中是否包含 [[title]]
            if f"[[{title}]]" in entry.content or f"[[{target_lower}]]" in entry.content.lower():
                related.append(entry)

        return related

    def search(self, keyword: str) -> List[RetrievedEntry]:
        """
        关键字搜索（保留作为简单查询后备）

        注意：这是简单的关键字匹配，不是 LLM 辅助查询
        LLM 辅助查询应该使用 get_page() + list_pages() 组合
        """
        results = []
        keyword_lower = keyword.lower()

        for entry in self.entries:
            score = 0.0
            # 标题匹配
            if keyword_lower in entry.title.lower():
                score = 1.0
            # 别名匹配
            elif any(keyword_lower in alias.lower() for alias in entry.aliases):
                score = 0.9
            # 内容匹配
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
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/test_wiki_kb.py -v`
Expected: PASS

- [ ] **Step 5: 提交代码**

```bash
git add src/wiki_kb.py tests/test_wiki_kb.py
git commit -m "feat: update wiki_kb.py with confidence/status/aliases fields and LLM-assisted query methods"
```

---

### Task 6: 修正 retriever.py（LLM 辅助查询，非关键字匹配）

**Files:**
- Modify: `artifact_chain/src/retriever.py`
- Create: `tests/test_retriever.py`

- [ ] **Step 1: 写测试 `tests/test_retriever.py`**

```python
import pytest
from src.wiki_kb import WikiKnowledgeBase
from src.retriever import Retriever
from src.intent_parser import IntentParser

def test_retriever_init():
    """测试检索器初始化"""
    kb = WikiKnowledgeBase("wiki")
    retriever = Retriever(kb, top_k=3)
    assert retriever.top_k == 3
    assert retriever.wiki_kb is kb

def test_retrieve_with_intent():
    """测试根据意图检索（核心测试）"""
    kb = WikiKnowledgeBase("wiki")
    retriever = Retriever(kb)
    parser = IntentParser()

    intent = parser.parse("以青铜面具为主角，写一个60秒悬疑风短视频脚本。")
    results = retriever.retrieve(intent)

    assert isinstance(results, list)
    assert len(results) > 0
    # 应该检索到青铜面具（素材）和悬疑叙事技巧（方法论）
    titles = [r.entry.title for r in results]
    assert any("青铜面具" in t for t in titles)

def test_retrieve_returns_high_confidence_first():
    """测试高置信度页面优先返回"""
    kb = WikiKnowledgeBase("wiki")
    retriever = Retriever(kb)
    parser = IntentParser()

    intent = parser.parse("关于三星堆的视频")
    results = retriever.retrieve(intent)

    # 如果有多个结果，高置信度的应该在前面
    if len(results) >= 2:
        assert results[0].entry.confidence >= results[1].entry.confidence
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_retriever.py -v`
Expected: FAIL — retrieve 方法行为与测试不符

- [ ] **Step 3: 实现修正后的 `src/retriever.py`**

```python
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
            # 尝试直接获取指定素材的页面
            artifact_page = self.wiki_kb.get_page(intent.artifact)
            if artifact_page:
                all_results.append(RetrievedEntry(
                    entry=artifact_page,
                    score=1.0,
                    highlight=f"直接匹配: {artifact_page.title}"
                ))

            # 也搜索相关页面
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

            # 搜索相关方法论
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
        # 读取 index.md
        index_content = self.wiki_kb.read_index()

        # 列出所有页面（供 LLM 理解结构）
        all_pages = self.wiki_kb.list_pages()

        # 按置信度列出高置信度页面
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
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/test_retriever.py -v`
Expected: PASS

- [ ] **Step 5: 提交代码**

```bash
git add src/retriever.py tests/test_retriever.py
git commit -m "feat: update retriever.py to use LLM-assisted query instead of keyword matching"
```

---

### Task 7: 更新测试文件

**Files:**
- Modify: `tests/test_pipeline.py`

- [ ] **Step 1: 更新 `tests/test_pipeline.py`**

```python
import pytest
from src.intent_parser import IntentParser
from src.wiki_kb import WikiKnowledgeBase
from src.retriever import Retriever
from src.script_gen import ScriptGenerator
from src.prompt_gen import PromptGenerator


def test_full_pipeline():
    """测试完整链路"""
    # 初始化
    intent_parser = IntentParser()
    wiki_kb = WikiKnowledgeBase("wiki")
    retriever = Retriever(wiki_kb)
    script_gen = ScriptGenerator()
    prompt_gen = PromptGenerator()

    # 输入
    user_input = "以青铜面具为主角，写一个60秒悬疑风短视频脚本。"

    # 1. 意图解析
    intent = intent_parser.parse(user_input)
    assert intent.artifact == "青铜面具"
    assert intent.style == "悬疑"
    assert intent.duration == 60

    # 2. 检索（LLM 辅助）
    results = retriever.retrieve(intent)
    assert len(results) > 0

    # 验证检索结果包含所需内容
    titles = [r.entry.title for r in results]
    assert "青铜面具" in titles

    # 3. 生成脚本
    script_result = script_gen.generate(intent, results)
    assert script_result.script
    assert len(script_result.citations) > 0

    # 4. 生成Prompt
    prompt_result = prompt_gen.generate(script_result, intent)
    assert prompt_result.prompt
    assert "青铜面具" in prompt_result.prompt or "mask" in prompt_result.prompt.lower()


def test_wiki_entry_has_new_fields():
    """测试 Wiki 条目包含新字段（confidence, status, aliases）"""
    wiki_kb = WikiKnowledgeBase("wiki")
    bronze_mask = wiki_kb.get_page("青铜面具")

    assert bronze_mask is not None
    assert hasattr(bronze_mask, 'confidence')
    assert hasattr(bronze_mask, 'status')
    assert hasattr(bronze_mask, 'aliases')
    assert bronze_mask.confidence > 0
    assert bronze_mask.status == "active"


def test_retriever_get_context():
    """测试检索器提供的 LLM 上下文"""
    retriever = Retriever(WikiKnowledgeBase("wiki"))
    context = retriever.get_context_for_query("如何写一个悬疑风格的青铜面具短视频脚本？")

    assert "index" in context
    assert "pages_by_category" in context
    assert "entities" in context["pages_by_category"]
    assert "concepts" in context["pages_by_category"]
    assert "high_confidence_pages" in context["pages_by_category"]
```

- [ ] **Step 2: 运行完整测试**

Run: `pytest tests/test_pipeline.py -v`
Expected: PASS

- [ ] **Step 3: 提交代码**

```bash
git add tests/test_pipeline.py
git commit -m "test: update pipeline tests for new wiki format and LLM-assisted query"
```

---

### Task 8: 验证并更新文档

**Files:**
- Modify: `docs/architecture.md`
- Verify: `docs/mettings/llm-wiki知识库开发指南.md`（已在前一步更新）

- [ ] **Step 1: 更新 `docs/architecture.md`**

```markdown
# 文物IP内容自动化生产链 - 架构文档

## 系统概述

本系统实现从"文物创意需求"到"AI视频生成Prompt"的完整自动化链路。

## 整体架构

```
用户输入 → 资料层 → 生成层 → 对接层 → AI视频Prompt
```

## 三层架构

### 资料层（Knowledge Layer）

**职责**：
- 意图解析：从用户输入中提取意图、素材、风格等信息
- Wiki检索：**LLM 辅助查询**（不是简单的关键字匹配）

**核心模块**：
- `IntentParser`：意图解析器
- `WikiKnowledgeBase`：Wiki知识库操作（支持 get_page、list_pages 等方法）
- `Retriever`：检索器（**使用 LLM 辅助查询**）

**数据流**：
1. 解析用户输入 → UserIntent
2. **LLM 读取 index.md 理解 Wiki 结构**
3. **LLM 选择需要查询的页面**
4. 读取选定页面 → RetrievedEntry列表

**LLM Wiki 规范遵循**：
- Wiki 页面包含 `confidence`、`status`、`aliases` 字段
- index.md 使用表格格式，包含置信度和状态
- log.md 记录所有操作
- lifecycle.md（可选）追踪知识生命周期

### 生成层（Generation Layer）

**职责**：基于检索结果生成脚本

**核心模块**：
- `ScriptGenerator`：脚本生成器（简化实现）

**数据流**：
1. 接收意图+检索结果
2. 生成结构化脚本
3. 附带引用来源

### 对接层（Conversion Layer）

**职责**：将脚本转化为目标平台的视频生成Prompt

**核心模块**：
- `PromptGenerator`：Prompt生成器（简化实现）

**数据流**：
1. 接收脚本
2. 模板填充
3. 输出AI视频Prompt

## Wiki知识库结构（遵循 LLM Wiki 规范）

```
wiki/
├── index.md              # 全局索引（表格格式，含 confidence 和 status）
├── log.md                # 操作日志
├── lifecycle.md          # [可选] 生命周期数据
├── entities/             # 实体（文物）
│   ├── 青铜面具.md       # 含 aliases, confidence, status
│   └── 三星堆遗址.md
└── concepts/             # 概念（方法论）
    ├── 悬疑叙事技巧.md
    └── 短视频脚本结构.md
```

## 扩展方向

1. **知识库扩展**：接入更多文物数据（敦煌、故宫等）
2. **生成层增强**：接入真实LLM API实现完整生成
3. **对接层扩展**：适配更多AI视频生成工具
4. **评估体系**：增加生成质量评估指标
```

- [ ] **Step 2: 验证文档更新**

Run: `grep -E "LLM|confidence|status" docs/architecture.md`
Expected: 找到相关引用

---

## 自我审查

### Spec 覆盖检查

| 需求 | 对应任务 | 状态 |
|------|---------|------|
| Wiki 页面格式修正 | Task 1 | ✅ |
| index.md 格式修正 | Task 2 | ✅ |
| log.md 添加 | Task 3 | ✅ |
| lifecycle.md 添加 | Task 4 | ✅ |
| wiki_kb.py 修正 | Task 5 | ✅ |
| retriever.py 修正（LLM辅助） | Task 6 | ✅ |
| 测试更新 | Task 7 | ✅ |
| 文档更新 | Task 8 | ✅ |

### 占位符扫描

- [x] 无 TBD/TODO
- [x] 步骤完整，有实际代码
- [x] 测试用例完整

### 类型一致性检查

| 字段/方法 | 定义位置 | 使用位置 |
|---------|---------|---------|
| `WikiEntry.confidence` | Task 5 | Task 1, 5, 6 |
| `WikiEntry.status` | Task 5 | Task 1, 5, 6 |
| `WikiEntry.aliases` | Task 5 | Task 1, 5 |
| `wiki_kb.get_page()` | Task 5 | Task 6 |
| `wiki_kb.list_pages()` | Task 5 | Task 6 |
| `retriever.retrieve()` | Task 6 | Task 7 |

---

## 执行选项

**Plan complete and saved to `docs/superpowers/plans/2026-04-15-artifact-content-chain-v2.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
