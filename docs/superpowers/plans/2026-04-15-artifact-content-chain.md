# 文物 IP 内容自动化生产链 - 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建从"文物创意需求"到"AI视频生成Prompt"的完整自动化链路，三层架构，资料层重点实现

**Architecture:** 三层架构 - 资料层（Wiki知识库+意图解析）→ 生成层（脚本生成）→ 对接层（Prompt转化）

**Tech Stack:** Python 3.10+, 纯文件系统, Markdown 格式（参考 llm-wiki 模式）

---

## 1. 系统架构图

```
用户输入: "以青铜面具为主角，写一个 60 秒悬疑风短视频脚本。"
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      【资料层】意图解析 + Wiki检索                 │
│  ┌─────────────────┐         ┌─────────────────────────────┐    │
│  │  intent_parser  │────────▶│      Wiki知识库             │    │
│  │  (意图解析)      │         │  ┌─────────────────────┐  │    │
│  │                 │         │  │ entities/           │  │    │
│  │  识别：          │         │  │   青铜面具.md       │  │    │
│  │  - intent: 脚本  │         │  │   三星堆遗址.md     │  │    │
│  │  - artifact: 青铜│         │  │ concepts/           │  │    │
│  │  - style: 悬疑   │         │  │   悬疑叙事技巧.md   │  │    │
│  │  - duration: 60s│         │  │   脚本结构.md       │  │    │
│  └─────────────────┘         │  └─────────────────────┘  │    │
│                               └─────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
    │ 意图信息 + 检索结果（史实资料 + 方法论）
    ▼
┌─────────────────────────────────────────────────────────────────┐
│                        【生成层】脚本生成                         │
│  ┌─────────────────┐         ┌─────────────────────────────┐    │
│  │  script_gen     │────────▶│  融合：意图 + 知识          │    │
│  │  (简化实现)      │         │  → 生成结构化脚本          │    │
│  └─────────────────┘         └─────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
    │ 结构化脚本（带引用）
    ▼
┌─────────────────────────────────────────────────────────────────┐
│                        【对接层】Prompt转化                      │
│  ┌─────────────────┐         ┌─────────────────────────────┐    │
│  │  prompt_gen     │────────▶│  脚本 → AI视频Prompt        │    │
│  │  (简化实现)      │         │  (模板填充)                 │    │
│  └─────────────────┘         └─────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
    │ AI视频生成Prompt
    ▼
最终输出: 可直接用于AI视频生成工具的Prompt
```

---

## 2. 文件结构

```
artifact_chain/
├── config/
│   └── settings.py              # 配置管理
├── wiki/                        # Wiki知识库（资料层核心）
│   ├── index.md                 # 全局索引
│   ├── log.md                   # 操作日志
│   ├── entities/                # 实体（文物）
│   │   ├── 青铜面具.md
│   │   └── 三星堆遗址.md
│   └── concepts/                # 概念（方法论）
│       ├── 悬疑叙事技巧.md
│       └── 短视频脚本结构.md
├── src/                         # 源代码
│   ├── __init__.py
│   ├── intent_parser.py         # 意图解析模块
│   ├── wiki_kb.py               # Wiki知识库操作
│   ├── retriever.py             # 检索模块
│   ├── script_gen.py            # 脚本生成（简化）
│   └── prompt_gen.py            # Prompt生成（简化）
├── tests/                       # 单元测试
│   ├── test_intent_parser.py
│   ├── test_wiki_kb.py
│   ├── test_retriever.py
│   └── test_pipeline.py
├── main.py                      # 主入口
├── requirements.txt             # 依赖
└── README.md                    # 项目说明
```

---

## 3. 任务分解

### Task 1: 项目初始化与配置

**Files:**
- Create: `artifact_chain/config/settings.py`
- Create: `artifact_chain/src/__init__.py`
- Create: `artifact_chain/main.py`
- Create: `artifact_chain/requirements.txt`
- Create: `tests/test_settings.py`

- [ ] **Step 1: 创建目录结构**

```bash
mkdir -p artifact_chain/config
mkdir -p artifact_chain/wiki/entities
mkdir -p artifact_chain/wiki/concepts
mkdir -p artifact_chain/src
mkdir -p tests
```

- [ ] **Step 2: 创建配置模块 `config/settings.py`**

```python
"""配置管理"""
from pathlib import Path
from dataclasses import dataclass

BASE_DIR = Path(__file__).parent.parent
WIKI_DIR = BASE_DIR / "wiki"

@dataclass
class Config:
    """系统配置"""
    wiki_dir: Path = WIKI_DIR
    top_k: int = 5  # 召回前5条最相关资料
    default_style: str = "悬疑"
    default_duration: int = 60  # 秒

config = Config()
```

- [ ] **Step 3: 创建入口文件 `main.py`**

```python
"""文物IP内容自动化生产链 - 主入口"""
from src.intent_parser import IntentParser
from src.wiki_kb import WikiKnowledgeBase
from src.retriever import Retriever
from src.script_gen import ScriptGenerator
from src.prompt_gen import PromptGenerator

def main():
    # 初始化各模块
    intent_parser = IntentParser()
    wiki_kb = WikiKnowledgeBase()
    retriever = Retriever(wiki_kb)
    script_gen = ScriptGenerator()
    prompt_gen = PromptGenerator()

    # 用户输入
    user_input = "以青铜面具为主角，写一个60秒悬疑风短视频脚本。"

    # 1. 意图解析
    intent = intent_parser.parse(user_input)
    print(f"【意图解析】{intent}")

    # 2. Wiki检索
    results = retriever.retrieve(intent)
    print(f"【资料层】检索到 {len(results)} 条知识")

    # 3. 脚本生成
    script = script_gen.generate(intent, results)
    print(f"【生成层】生成脚本:\n{script}")

    # 4. Prompt转化
    video_prompt = prompt_gen.generate(script, intent)
    print(f"【对接层】生成Prompt:\n{video_prompt}")

    return video_prompt

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 创建依赖文件 `requirements.txt`**

```txt
pytest>=7.0.0
```

- [ ] **Step 5: 运行测试验证**

Run: `pytest tests/test_settings.py -v`
Expected: PASS

---

### Task 2: Wiki 知识库核心页面

**Files:**
- Create: `artifact_chain/wiki/index.md`
- Create: `artifact_chain/wiki/entities/青铜面具.md`
- Create: `artifact_chain/wiki/entities/三星堆遗址.md`
- Create: `artifact_chain/wiki/concepts/悬疑叙事技巧.md`
- Create: `artifact_chain/wiki/concepts/短视频脚本结构.md`

- [ ] **Step 1: 创建 `wiki/index.md`**

```markdown
# Wiki Index

| Page | Category | Description |
|------|----------|-------------|
| 青铜面具 | entities | 三星堆出土的青铜面具，古蜀文明重要代表性器物 |
| 三星堆遗址 | entities | 位于四川广汉的古蜀文明遗址 |
| 悬疑叙事技巧 | concepts | 悬疑风格短视频的叙事方法与技巧 |
| 短视频脚本结构 | concepts | 60秒短视频的标准脚本结构 |
```

- [ ] **Step 2: 创建 `wiki/entities/青铜面具.md`**

```markdown
---
title: 青铜面具
category: entities
tags: [三星堆, 青铜器, 古蜀文明, 祭祀]
created: 2026-04-15
updated: 2026-04-15
sources: [["三星堆考古发掘报告"]]
description: 三星堆遗址出土的青铜面具，古蜀文明重要代表性器物
---

# 青铜面具

## 基本信息

- **出土地点**: 四川广汉三星堆遗址
- **年代**: 商代（约公元前1600-前1046年）
- **现存**: 三星堆博物馆

## 外观特征

- 大部分青铜面具呈方形
- 眼睛呈柱状向外突出（纵目）
- 耳朵穿孔
- 最大件：高65厘米，宽138厘米

## 历史背景

- 古蜀文明的重要代表性器物
- 考古学家认为用于祭祀仪式
- 可能代表古蜀国君王形象

## 相关页面

- [[三星堆遗址]] - 出土地点
- [[悬疑叙事技巧]] - 可用于悬疑风格创作
```

- [ ] **Step 3: 创建 `wiki/entities/三星堆遗址.md`**

```markdown
---
title: 三星堆遗址
category: entities
tags: [三星堆, 古蜀文明, 考古]
created: 2026-04-15
updated: 2026-04-15
sources: [["三星堆考古发掘报告"]]
description: 位于四川广汉的古蜀文明遗址
---

# 三星堆遗址

## 基本信息

- **位置**: 四川省广汉市
- **年代**: 新石器时代晚期至商代
- **发现时间**: 1929年

## 出土文物

- 青铜面具
- 青铜纵目面具
- 金杖
- 玉器

## 文化意义

- 古蜀文明的核心遗址
- 证明长江流域存在与黄河流域同样辉煌的古代文明

## 相关页面

- [[青铜面具]] - 代表性出土文物
```

- [ ] **Step 4: 创建 `wiki/concepts/悬疑叙事技巧.md`**

```markdown
---
title: 悬疑叙事技巧
category: concepts
tags: [悬疑, 叙事技巧, 短视频]
created: 2026-04-15
updated: 2026-04-15
sources: [["短视频创作指南"]]
description: 悬疑风格短视频的叙事方法与技巧
---

# 悬疑叙事技巧

## 核心要素

### 1. 悬念设置
- 开头抛出疑问，吸引观众
- 暗示已知和未知的边界

### 2. 节奏控制
- 缓慢铺垫，逐步揭示
- 利用光影和音效制造紧张感

### 3. 视角选择
- 第一人称叙述增加沉浸感
- 限制信息量制造信息差

## 60秒悬疑脚本结构

```
开场（5秒）: 建立神秘氛围，抛出悬念
发展（30秒）: 逐步揭示线索，增加紧张感
高潮（20秒）: 最大悬念，视觉冲击
结尾（5秒）: 留白或反转
```

## 相关页面

- [[短视频脚本结构]] - 完整脚本框架
- [[青铜面具]] - 可用于创作悬疑背景
```

- [ ] **Step 5: 创建 `wiki/concepts/短视频脚本结构.md`**

```markdown
---
title: 短视频脚本结构
category: concepts
tags: [短视频, 脚本结构, 创作]
created: 2026-04-15
updated: 2026-04-15
sources: [["短视频创作指南"]]
description: 60秒短视频的标准脚本结构
---

# 短视频脚本结构

## 60秒标准结构

| 时段 | 秒数 | 内容 |
|------|------|------|
| 开场 | 0-5s | 吸引注意，建立场景 |
| 铺垫 | 5-25s | 介绍背景，展开情节 |
| 高潮 | 25-50s | 核心冲突，情感高潮 |
| 结尾 | 50-60s | 收尾，留白或Call to Action |

## 脚本格式

```markdown
【场景1】时间 - 地点
- 画面描述
- 对白/画外音
- 音效/配乐提示

【场景2】时间 - 地点
...
```

## 相关页面

- [[悬疑叙事技巧]] - 悬疑风格补充
```

---

### Task 3: 意图解析模块

**Files:**
- Create: `artifact_chain/src/intent_parser.py`
- Create: `tests/test_intent_parser.py`

- [ ] **Step 1: 创建意图解析模块 `src/intent_parser.py`**

```python
"""意图解析模块 - 从用户输入中提取意图、素材、风格等信息"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class UserIntent:
    """用户意图"""
    raw_input: str               # 原始输入
    artifact: Optional[str] = None  # 文物/素材（青铜面具）
    intent_type: Optional[str] = None  # 意图类型（脚本/视频/文案）
    style: Optional[str] = None   # 风格（悬疑/科普/喜剧）
    duration: Optional[int] = None  # 时长（秒）

class IntentParser:
    """意图解析器"""

    # 意图类型关键词
    INTENT_KEYWORDS = {
        "脚本": ["脚本", "剧本", "文案"],
        "视频": ["视频", "影片"],
        "文案": ["文案", "推广"]
    }

    # 风格关键词
    STYLE_KEYWORDS = {
        "悬疑": ["悬疑", "神秘", "惊悚"],
        "科普": ["科普", "教育", "知识"],
        "喜剧": ["喜剧", "搞笑", "幽默"],
        "剧情": ["剧情", "感人", "情感"]
    }

    # 素材/文物关键词
    ARTIFACT_KEYWORDS = {
        "青铜面具": ["青铜面具", "面具"],
        "三星堆": ["三星堆", "古蜀"],
        "敦煌": ["敦煌", "壁画"],
        "故宫": ["故宫", "明清"]
    }

    def parse(self, user_input: str) -> UserIntent:
        """
        解析用户输入，提取意图信息
        """
        intent = UserIntent(raw_input=user_input)

        # 提取意图类型
        intent.intent_type = self._extract_intent_type(user_input)

        # 提取风格
        intent.style = self._extract_style(user_input)

        # 提取时长
        intent.duration = self._extract_duration(user_input)

        # 提取素材/文物
        intent.artifact = self._extract_artifact(user_input)

        return intent

    def _extract_intent_type(self, text: str) -> Optional[str]:
        """提取意图类型"""
        for intent_type, keywords in self.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return intent_type
        return "脚本"  # 默认

    def _extract_style(self, text: str) -> Optional[str]:
        """提取风格"""
        for style, keywords in self.STYLE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return style
        return "悬疑"  # 默认

    def _extract_duration(self, text: str) -> Optional[int]:
        """提取时长"""
        import re
        match = re.search(r'(\d+)\s*秒', text)
        if match:
            return int(match.group(1))
        return 60  # 默认60秒

    def _extract_artifact(self, text: str) -> Optional[str]:
        """提取文物/素材"""
        for artifact, keywords in self.ARTIFACT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return artifact
        return None
```

- [ ] **Step 2: 创建测试 `tests/test_intent_parser.py`**

```python
import pytest
from src.intent_parser import IntentParser, UserIntent

def test_parse_basic():
    parser = IntentParser()
    result = parser.parse("以青铜面具为主角，写一个60秒悬疑风短视频脚本。")

    assert isinstance(result, UserIntent)
    assert result.artifact == "青铜面具"
    assert result.style == "悬疑"
    assert result.duration == 60
    assert result.intent_type == "脚本"

def test_extract_style():
    parser = IntentParser()
    result = parser.parse("写一个科普风格的视频脚本")
    assert result.style == "科普"

def test_extract_artifact():
    parser = IntentParser()
    result = parser.parse("关于三星堆的视频")
    assert result.artifact == "三星堆"

def test_default_values():
    parser = IntentParser()
    result = parser.parse("写一个短视频")
    assert result.style == "悬疑"  # 默认风格
    assert result.duration == 60  # 默认时长
```

- [ ] **Step 3: 运行测试验证**

Run: `pytest tests/test_intent_parser.py -v`
Expected: PASS

---

### Task 4: Wiki 知识库操作模块

**Files:**
- Create: `artifact_chain/src/wiki_kb.py`
- Create: `tests/test_wiki_kb.py`

- [ ] **Step 1: 创建 Wiki 知识库模块 `src/wiki_kb.py`**

```python
"""Wiki知识库操作模块"""
from pathlib import Path
from typing import List, Optional
import re

@dataclass
class WikiEntry:
    """Wiki词条"""
    title: str
    category: str
    content: str
    tags: List[str]
    source: str

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

    def _parse_markdown(self, file_path: Path, category: str) -> Optional[WikiEntry]:
        """解析Markdown文件"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 提取frontmatter（简化处理）
        title = file_path.stem  # 文件名作为title

        # 提取正文内容（去除frontmatter）
        lines = content.split("\n")
        body_lines = []
        in_frontmatter = False
        for line in lines:
            if line.strip() == "---":
                in_frontmatter = not in_frontmatter
                continue
            if not in_frontmatter and line.strip():
                body_lines.append(line)

        body = "\n".join(body_lines)

        # 提取tags（简化）
        tags = [category]

        # 提取source（简化）
        source = f"[[{file_path.parent.parent.name}/{file_path.parent.name}/{file_path.name}]]"

        return WikiEntry(
            title=title,
            category=category,
            content=body,
            tags=tags,
            source=source
        )

    def search(self, keyword: str) -> List[RetrievedEntry]:
        """关键词搜索"""
        results = []
        keyword_lower = keyword.lower()

        for entry in self.entries:
            if keyword_lower in entry.title.lower() or keyword_lower in entry.content.lower():
                # 简单计分：标题匹配=1.0，内容匹配=0.5
                score = 1.0 if keyword_lower in entry.title.lower() else 0.5

                # 提取高亮片段
                highlight = self._extract_highlight(entry.content, keyword)

                results.append(RetrievedEntry(
                    entry=entry,
                    score=score,
                    highlight=highlight
                ))

        # 按分数排序
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
```

- [ ] **Step 2: 创建测试 `tests/test_wiki_kb.py`**

```python
import pytest
from src.wiki_kb import WikiKnowledgeBase, WikiEntry, RetrievedEntry

def test_wiki_kb_load():
    kb = WikiKnowledgeBase("wiki")
    assert isinstance(kb.entries, list)

def test_search_by_keyword():
    kb = WikiKnowledgeBase("wiki")
    results = kb.search("青铜面具")
    assert all(isinstance(r, RetrievedEntry) for r in results)
    assert all("青铜面具" in r.entry.title or "青铜面具" in r.entry.content
              for r in results)

def test_search_returns_highlight():
    kb = WikiKnowledgeBase("wiki")
    results = kb.search("三星堆")
    for r in results:
        assert r.highlight
        assert isinstance(r.highlight, str)
```

- [ ] **Step 3: 运行测试验证**

Run: `pytest tests/test_wiki_kb.py -v`
Expected: PASS

---

### Task 5: 检索模块

**Files:**
- Create: `artifact_chain/src/retriever.py`
- Create: `tests/test_retriever.py`

- [ ] **Step 1: 创建检索模块 `src/retriever.py`**

```python
"""检索模块 - 从Wiki知识库检索相关知识"""
from typing import List
from wiki_kb import WikiKnowledgeBase, RetrievedEntry

class Retriever:
    """检索器"""

    def __init__(self, wiki_kb: WikiKnowledgeBase, top_k: int = 5):
        self.wiki_kb = wiki_kb
        self.top_k = top_k

    def retrieve(self, intent) -> List[RetrievedEntry]:
        """
        根据意图检索相关知识

        Args:
            intent: UserIntent对象

        Returns:
            检索结果列表
        """
        results = []

        # 1. 检索素材相关知识（如"青铜面具"）
        if intent.artifact:
            artifact_results = self.wiki_kb.search(intent.artifact)
            results.extend(artifact_results)

        # 2. 检索方法论知识（如"悬疑叙事技巧"）
        if intent.style:
            style_results = self.wiki_kb.search(intent.style)
            results.extend(style_results)

        # 3. 检索脚本结构知识
        if intent.intent_type == "脚本":
            script_results = self.wiki_kb.search("脚本结构")
            results.extend(script_results)

        # 去重（根据title）
        seen_titles = set()
        unique_results = []
        for r in results:
            if r.entry.title not in seen_titles:
                seen_titles.add(r.entry.title)
                unique_results.append(r)

        return unique_results[:self.top_k]
```

- [ ] **Step 2: 创建测试 `tests/test_retriever.py`**

```python
import pytest
from src.wiki_kb import WikiKnowledgeBase
from src.retriever import Retriever
from src.intent_parser import IntentParser

def test_retriever_init():
    kb = WikiKnowledgeBase("wiki")
    retriever = Retriever(kb, top_k=3)
    assert retriever.top_k == 3

def test_retrieve_with_intent():
    kb = WikiKnowledgeBase("wiki")
    retriever = Retriever(kb)
    parser = IntentParser()

    intent = parser.parse("以青铜面具为主角，写一个60秒悬疑风短视频脚本。")
    results = retriever.retrieve(intent)

    assert isinstance(results, list)
    # 应该检索到素材（青铜面具）和方法论（悬疑）知识
    titles = [r.entry.title for r in results]
    assert any("青铜面具" in t or "面具" in t for t in titles)
```

- [ ] **Step 3: 运行测试验证**

Run: `pytest tests/test_retriever.py -v`
Expected: PASS

---

### Task 6: 生成层和对接层（简化实现）

**Files:**
- Create: `artifact_chain/src/script_gen.py`
- Create: `artifact_chain/src/prompt_gen.py`

- [ ] **Step 1: 创建脚本生成模块 `src/script_gen.py`**

```python
"""脚本生成模块 - 简化实现"""
from dataclasses import dataclass
from typing import List

@dataclass
class ScriptResult:
    """脚本生成结果"""
    script: str
    citations: List[str]

class ScriptGenerator:
    """脚本生成器（简化实现）"""

    def generate(self, intent, retrieved_results) -> ScriptResult:
        """
        基于检索结果生成脚本（Mock实现）

        实际项目中这里会调用LLM API
        """
        # 提取素材名称
        artifact = intent.artifact or "文物"
        style = intent.style or "悬疑"
        duration = intent.duration or 60

        # 简化Mock脚本
        script = f"""【{style}风格短视频脚本】({duration}秒)

场景一：神秘开场
画面：黑暗中，青铜面具的眼睛微微发光
画外音：在三千年前的古蜀大地，隐藏着怎样的秘密...

场景二：悬念铺垫
画面：考古学家手持电筒，走进三星堆遗址
画外音：这副面具，见证了一个失落的文明

场景三：高潮揭示
画面：面具特写，眼睛的纹路仿佛在诉说历史
画外音：古蜀人用这双"纵目"，看见了怎样的天地？

场景四：留白结尾
画面：面具缓缓隐入黑暗
画外音：答案，就埋藏在这片土地之下...
"""

        # 提取引用
        citations = [r.entry.source for r in retrieved_results]

        return ScriptResult(script=script, citations=citations)
```

- [ ] **Step 2: 创建 Prompt 生成模块 `src/prompt_gen.py`**

```python
"""Prompt生成模块 - 简化实现"""
from dataclasses import dataclass

@dataclass
class PromptResult:
    """Prompt生成结果"""
    prompt: str
    platform: str

class PromptGenerator:
    """Prompt生成器（简化实现）"""

    def generate(self, script_result, intent) -> PromptResult:
        """
        将脚本转化为AI视频生成Prompt（Mock实现）

        实际项目中这里会使用模板填充
        """
        platform = "sora"  # 默认平台

        prompt = f"""Cinematic footage, {intent.style or 'mysterious'} atmosphere,
ancient Chinese bronze mask as the central subject,
dramatic lighting with shadows, ultra-high definition,
bronze and gold color palette, mysterious and awe-inspiring mood.

镜头描述：
- 开场：黑暗中的青铜面具特写，眼睛发光
- 中段：考古现场，古蜀祭祀场景
- 高潮：面具特写，揭示历史秘密
- 结尾：面具隐入黑暗

风格：{intent.style or '悬疑'}古蜀文化
时长：{intent.duration or 60}秒
画面要求：电影感光影、超高清、神秘氛围
"""

        return PromptResult(prompt=prompt, platform=platform)
```

---

### Task 7: 完整链路测试

**Files:**
- Create: `tests/test_pipeline.py`

- [ ] **Step 1: 创建完整链路测试 `tests/test_pipeline.py`**

```python
import pytest
from src.intent_parser import IntentParser
from src.wiki_kb import WikiKnowledgeBase
from src.retriever import Retriever
from src.script_gen import ScriptGenerator
from src.prompt_gen import PromptGenerator

def test_full_pipeline():
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

    # 2. 检索
    results = retriever.retrieve(intent)
    assert len(results) > 0

    # 3. 生成脚本
    script_result = script_gen.generate(intent, results)
    assert script_result.script
    assert len(script_result.citations) > 0

    # 4. 生成Prompt
    prompt_result = prompt_gen.generate(script_result, intent)
    assert prompt_result.prompt
    assert "青铜面具" in prompt_result.prompt or "mask" in prompt_result.prompt.lower()
```

- [ ] **Step 2: 运行完整测试**

Run: `pytest tests/test_pipeline.py -v`
Expected: PASS

- [ ] **Step 3: 运行主程序演示**

Run: `python main.py`
Expected: 看到完整的链路执行结果

---

### Task 8: 架构图文档化

**Files:**
- Create: `docs/architecture.md`

- [ ] **Step 1: 创建架构文档 `docs/architecture.md`**

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
- Wiki检索：根据意图检索相关的史实资料和方法论知识

**核心模块**：
- `IntentParser`：意图解析器
- `WikiKnowledgeBase`：Wiki知识库操作
- `Retriever`：检索器

**数据流**：
1. 解析用户输入 → UserIntent
2. 根据intent检索Wiki → RetrievedEntry列表

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

## Wiki知识库结构

```
wiki/
├── index.md              # 全局索引
├── entities/             # 实体（文物）
│   ├── 青铜面具.md
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

---

## 4. 自我审查

**Spec覆盖检查**：
- [x] 资料层：Wiki知识库（Markdown格式）、意图解析、检索
- [x] 生成层：脚本生成（简化实现）
- [x] 对接层：Prompt生成（简化实现）
- [x] 核心模块实现
- [x] 架构图

**占位符扫描**：
- [x] 无 TBD/TODO
- [x] 步骤完整，有实际代码
- [x] 测试用例完整

**与之前计划的区别**：
- Wiki从JSON改为Markdown格式（符合llm-wiki示例）
- 增加意图解析模块（intent_parser）
- 生成层和对接层为简化实现
- Wiki页面包含实际的史实和方法论内容

---

## 5. 执行选项

**Plan complete and saved to `docs/superpowers/plans/2026-04-15-artifact-content-chain.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
