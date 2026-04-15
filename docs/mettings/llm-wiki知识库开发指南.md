# LLM Wiki 知识库开发指南

> 本文档整合了 LLM Wiki 的核心理论（llm-wiki.md）与实际示例项目（llm-wiki/）的最佳实践
> **版本：v3.0** — 修正架构层数、index格式、补充tags/output规范

---

## 一、什么是 LLM Wiki？

### 1.1 一句话定义

**LLM Wiki = LLM 持续维护的、可编译的、可积累的知识库**

不是简单的"把文档存起来"，而是让 LLM **预先消化知识、整理成结构化的笔记**，知识被固化下来而不是每次查询时临时拼凑。

### 1.2 生活中的类比

| 普通图书馆 | LLM Wiki |
|-----------|---------|
| 每次问问题，管理员去书架翻书临时拼凑答案 | 图书管理员先读完所有书，整理成笔记，问问题直接查笔记 |
| 同一本书被不同人问，重复翻找 | 知识被整理过一次，所有人都直接查整理好的笔记 |

### 1.3 与传统 RAG 的核心区别

| | 传统 RAG | LLM Wiki |
|---|---|---|
| **知识存储** | 原始文档 + 向量索引 | 结构化的、相互链接的 Markdown 页面 |
| **查询方式** | 每次从原始文档临时检索拼凑 | **LLM 先读 index.md 理解结构，再选择性读取页面，综合回答** |
| **知识积累** | 无 —— 每次都重新检索 | 有 —— 每次操作都让 Wiki 更丰富 |
| **交叉引用** | 无 | 自动维护 `[[wikilinks]]` 链接网络 |
| **矛盾处理** | 不知道、不处理 | 主动标注，附上来源 |

### 1.4 Query 操作的核心误解（必须纠正）

**我之前的错误理解：**
```
用户输入 → 关键字匹配 Wiki 页面 → 返回结果
```

**正确的 LLM Wiki Query 流程：**
```
用户提问
    ↓
LLM 读取 index.md（理解 Wiki 结构：有哪些页面、主题是什么）
    ↓
LLM 理解用户问题，决定需要查询哪些相关页面
    ↓
LLM 读取选定的 Wiki 页面（不是全部页面）
    ↓
LLM 综合已有知识回答问题
    ↓
如果答案有价值，询问用户是否保存为新页面
```

**为什么这样设计？**
- 小规模 Wiki（<100页面）：index.md 足够定位相关页面
- 大规模 Wiki（>100页面）：可用 qmd 等工具增强检索
- 关键：**LLM 理解 Wiki 结构来决定读什么，而不是简单关键字匹配**

---

## 二、核心原则（必须遵守）

### 2.1 六大原则

```
1. Raw is Immutable      — raw/ 下的文件永远不要修改
2. Wiki is Compiled      — Wiki 内容可以从 raw 重新生成
3. Compound Interest     — 每次操作都让 Wiki 更有价值
4. Cross-references First — [[wikilinks]] 是 Wiki 最大的价值
5. Contradictions Transparent — 矛盾要显式标注来源
6. Complete Logging     — 所有操作都要记录到 log.md
```

### 2.2 为什么这些原则重要？

- **Raw 不可修改**：保证知识有唯一的真实来源，Wiki 出错时可以重建
- **Wiki 是编译产物**：知识被提炼过，比原始文档更结构化、更易用
- **交叉引用是网络**：知识节点互相连接，形成知识图谱，而非孤立散落
- **矛盾透明**：不掩盖矛盾，让使用者自己判断置信度

---

## 三、架构详解

### 3.1 五层架构

```
┌─────────────────────────────────────────────────────────────┐
│  Schema 层（CLAUDE.md / AGENTS.md）                          │
│  规则手册 —— 告诉 LLM 如何维护 Wiki                          │
│  人类和 LLM 共同演进                                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Skills 层（skills/llm-wiki/）                              │
│  技能定义 —— ingest/query/lint/publish 的详细流程           │
│  按需加载，不占用日常上下文                                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Raw 层（raw/）                                             │
│  原始资料 —— 人类整理，LLM 只读                              │
│  这是知识的真实来源，永不修改                                 │
│                                                             │
│  raw/articles/    — 网页文章、博客                           │
│  raw/papers/      — 学术论文                                 │
│  raw/docs/        — 官方文档                                 │
│  raw/transcripts/ — 会议记录、播客笔记                        │
│  raw/assets/      — 图片、图表、数据文件                       │
└─────────────────────────────────────────────────────────────┘
                            │
                         LLM 编译
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Wiki 层（wiki/）                                            │
│  LLM 编译的产物 —— LLM 可读写，人类只读                       │
│                                                             │
│  wiki/index.md      — 全局索引（包含置信度和状态）            │
│  wiki/log.md        — 操作日志                               │
│  wiki/lifecycle.md  — [可插拔] 知识生命周期数据               │
│  wiki/entities/     — 实体页面（工具、框架、人、文物）        │
│  wiki/concepts/     — 概念页面（设计模式、方法论）            │
│  wiki/summaries/    — 材料摘要页面                           │
│  wiki/comparisons/  — 对比分析页面                          │
│  wiki/synthesis/    — 综合洞察页面                          │
└─────────────────────────────────────────────────────────────┘
                            │
                         LLM 发布
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Output 层（output/）                                       │
│  精炼的交付物 —— LLM 生成，人类审核定稿                       │
│                                                             │
│  output/posts/      — 博客文章                               │
│  output/reports/    — 研究报告                               │
│  output/slides/     — 演示文稿（Marp 格式）                  │
│  output/tutorials/  — 教程                                 │
│  output/newsletters/— 知识简报                               │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Wiki 页面的标准格式

每个 Wiki 页面必须包含：

**Frontmatter（必须）：**
```yaml
---
title: 页面标题
aliases: [别名1, 别名2]        # 可选，但推荐添加
tags: [标签1, 标签2]
category: entities | concepts | summaries | comparisons | synthesis
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources:
  - "[[raw/path/source-filename]]"
description: 一句话描述，不超过 100 字符
confidence: 0.75                 # 可选（lifecycle.md 存在时必须有）
status: active | stale | archived # 可选（lifecycle.md 存在时必须有）
---
```

**正文结构要求：**
- 清晰的 h2/h3 标题层级
- 关键词使用 `[[wikilinks]]` 引用其他 Wiki 页面
- 原始材料引用使用 `[[raw/path/filename]]` 格式
- **每个页面末尾必须有 `## Related Pages` 章节**
- 代码块要指定语言类型

### 3.3 index.md 的正确格式

```markdown
# Wiki Index

> Last updated: YYYY-MM-DD | Total pages: N | Total materials: M

## Entities

| Page | Summary | confidence | status |
|------|---------|------------|--------|
| [[Obsidian]] | Local markdown-based knowledge management tool | 0.70 | active |

## Concepts
(same table format)

## Summaries
(same table format)

## Comparisons
(same table format)

## Synthesis
(same table format)
```

**关键点：**
- 使用**表格格式**（不是列表）
- 必须包含 `Summary`、`confidence` 和 `status` 列
- `Summary` 列填写页面的一句话描述
- LLM 读取 index.md 来定位相关页面，而不是直接遍历所有文件

### 3.4 log.md 的正确格式

```markdown
# Wiki Log

## [2026-04-15] ingest | 三星堆考古报告.pdf
- Source: `raw/papers/三星堆考古报告.pdf`
- Created: [[青铜面具]], [[三星堆遗址]]
- Updated: [[悬疑叙事技巧]] (confidence +0.10)
- Note: 发现与现有页面矛盾之处，已标注

## [2026-04-15] query | 如何写一个60秒悬疑脚本？
- Consulted: [[青铜面具]], [[悬疑叙事技巧]], [[短视频脚本结构]]
- Answer: 综合三篇页面内容生成回答

## [2026-04-15] lint | Health Check
- Fixed: 2 items | Pending: 0 items
```

**关键点：**
- 每条记录以 `## [YYYY-MM-DD] <operation> | <target>` 格式开头
- 用 `grep "^## \[" log.md | tail -5` 可以查看最近 5 条
- 仅保留最近 30 天，更早的由 lint 归档

### 3.5 tags.md 的正确格式（标签规范）

每个页面标签由三个维度组合而成：

**域名标签（技术/业务领域）：**
```
AI, software-engineering, testing, CI-CD, infrastructure, observability,
frontend, backend, DevOps, architecture, programming-languages,
knowledge-management, databases, middleware, distributed-systems,
cloud-native, security, information-science
```

**类型标签（页面描述的事物的类型）：**
```
framework, tool, pattern, practice, standard, concept, person,
project, methodology, comparative-analysis, synthesis
```

**成熟度标签（可选，仅在可明确判断时添加）：**
```
mature, emerging, experimental, deprecated
```

**规则：**
- 每个页面至少需要 1 个域名标签 + 1 个类型标签
- 成熟度标签可选
- 标签使用小写英文，用连字符分隔
- 优先复用现有标签，新增标签前先检查是否有可复用的同义词

**示例：**
```yaml
tags: [AI, knowledge-management, tool]
```

### 3.6 命名规范

| 类型 | 命名规则 | 示例 |
|---|---|---|
| Entity 页面 | 实体名称，中横线分隔 | `Obsidian.md` |
| Concept 页面 | 概念名称 | `RAG.md` |
| Summary 页面 | `raw-` + 源路径缩写 | `raw-articles-llm-wiki.md` |
| Comparison 页面 | `A-vs-B-主题` | `LLM-Wiki-vs-RAG.md` |
| Synthesis 页面 | 描述性分析主题 | `index-and-log-scalability-analysis.md` |

---

## 四、知识生命周期管理

> 这是一个**可插拔**的功能，删除 `lifecycle.md` 不影响核心功能

### 4.1 置信度（Confidence）

每个页面都有一个 0.0–1.0 的置信度分数：

| 来源数量 | 初始置信度 |
|---------|----------|
| 单源（thin） | 0.55 |
| 多源（substantial） | 0.65 |
| 多方交叉印证 | 0.75 |
| 综合分析（synthesis） | 0.80 |

**触发置信度提升：**
- 被查询 → +0.05
- 被新来源确认 → +0.10
- Lint 无矛盾 → +0.02
- 发布为 deliverable → +0.15

### 4.2 状态流转

```
active ──→ stale ──→ archived
  ↑         │
  └─────────┘
  （被访问或被新来源确认可恢复）
```

**流转规则：**
- `active → stale`：90 天未访问且置信度 < 0.5
- `stale → archived`：180 天无新来源

### 4.3 遗忘曲线

灵感来自艾宾浩斯遗忘曲线：长期未访问的知识会自然衰减置信度

```
衰减 = 天数 × 类型系数
```

不同类型衰减速度不同：concept 衰减慢，comparison 衰减快。

### 4.4 替代与降级

- **superseded_by / supersedes**：新信息推翻旧结论时，建立双向链接，旧版本标记为 outdated
- **降级**：synthesis 的核心结论被推翻 → 降级为 stale，等待重新验证

---

## 五、核心操作详解

### 5.1 四种操作概览

| 操作 | 命令 | 描述 |
|------|------|------|
| **Ingest** | `/llm-wiki ingest <file>` | 消化新材料，更新 Wiki |
| **Query** | `/llm-wiki query <question>` | 基于 Wiki 知识回答问题 |
| **Lint** | `/llm-wiki lint` | 健康检查，修复问题 |
| **Publish** | `/llm-wiki publish <type> [topic]` | 从 Wiki 生成交付物 |

### 5.2 Query（查询）详细流程 — **核心澄清**

这是最容易误解的操作，必须仔细理解：

```
1. 用户提问
   ↓
2. 【关键】读取 index.md
   - LLM 理解 Wiki 的整体结构
   - 有哪些页面？主题是什么？
   ↓
3. 【关键】LLM 判断需要查询哪些页面
   - 不是关键字匹配！
   - LLM 理解用户意图，选择相关页面
   ↓
4. 读取选定的 Wiki 页面
   ↓
5. 综合回答（基于 Wiki 内容，不要从 raw 重新推导）
   - 如果引用 stale 页面，注明"此信息可能已过时"
   ↓
6. 更新生命周期（如果 lifecycle.md 存在）
   - 被查询的页面 access +1
   - index.md confidence +0.05
   ↓
7. 提供引用
   - 标注具体的 Wiki 页面
   - 标注原始材料来源
   ↓
8. 询问是否归档
   - 如果答案有复用价值，问用户是否保存到 comparisons/ 或 synthesis/
   ↓
9. 记录日志到 log.md
```

**为什么这样设计？**

假设用户问："青铜面具在古蜀祭祀中扮演什么角色？"

**关键字匹配的方式：**
- 搜索"青铜面具"和"祭祀"
- 可能返回不相关的内容

**LLM 辅助查询的方式：**
1. 读 index.md → 了解有 [[青铜面具]]、[[三星堆遗址]] 等页面
2. LLM 理解这个问题需要：
   - 青铜面具的基本信息（[[青铜面具]]）
   - 古蜀祭祀文化背景（可能需要查 [[古蜀祭祀文化]]）
3. LLM 选择性读取这些页面
4. LLM 综合回答

### 5.3 Ingest（消化）详细流程

```
1. 读取 raw/ 下的源文件
2. 提取引用、概念、核心论点、数据、结论
3. 与用户讨论关键发现，确认重点
4. 创建/更新 Wiki 页面：
   - Summary → wiki/summaries/
   - Entity → wiki/entities/
   - Concept → wiki/concepts/
5. 处理矛盾：新材料与现有内容矛盾 → 显式标注，引用双方来源
6. 维护交叉引用：[[wikilinks]] 连接相关页面
7. 生命周期评估：
   - 新页面：设置初始置信度
   - 现有页面被新来源确认：置信度 +0.10
   - 检查晋升：实体/概念被 2+ 材料提到 → 创建对应页面
   - 检查替代：核心结论被推翻 → 建立 superseded_by 链接
8. 更新 index.md
9. 更新 lifecycle.md（如果存在）
10. 记录到 log.md
```

### 5.4 Lint（体检）详细流程

```
1. 结构性检查：
   - 矛盾检测：页面间的矛盾声明
   - 孤立页面：无入站链接的页面（index.md 链接不算）
   - 缺失页面：被多个 [[wikilinks]] 引用但尚未创建的页面
   - 交叉引用：相关页面之间的双向链接
   - Frontmatter：必填字段完整性

2. 生命周期检查（如果 lifecycle.md 存在）：
   - 时间衰减：计算置信度衰减，更新 index.md 和 lifecycle.md
   - 状态流转：active → stale → archived
   - 降级检查：synthesis 核心结论被推翻 → 降级
   - 晋升建议：满足晋升条件但尚未晋升的页面
   - 过期交付物：依赖的页面已 stale/archived → 标记为过期

3. 日志归档：30 天前的记录 → wiki/log-archive/YYYY-MM.md

4. 生成修复列表：输出问题清单，用户确认后执行修复

5. 记录日志
```

### 5.5 Publish（发布）详细流程

```
1. 明确需求：确认类型（post/report/slides/tutorial/newsletter）、受众、长度
2. 定位源材料：读取 index.md，优先高置信度 active 页面
3. 深读源材料
4. 生成草稿：基于 Wiki 内容写交付物，保存到对应 output/ 目录
5. 格式适配：
   - [[wikilinks]] → 标准链接或纯文本
   - 引用用脚注格式
   - 按类型调整格式
6. 更新生命周期：被引用页面 → lifecycle.md access +1
7. 用户审核：展示草稿，根据反馈修订
8. 记录日志
```

### 5.6 Output 交付物格式规范

**目录结构：**
```
output/
├── posts/           # 博客文章
├── reports/         # 研究报告、技术调查报告
├── slides/          # 演示文稿（Marp 格式）
├── tutorials/       # 教程、可独立跟随的步骤指南
└── newsletters/     # 周报、月报、知识简报
```

**Frontmatter 要求：**
```yaml
---
title: 交付物标题
type: post | report | slides | tutorial | newsletter
audience: 目标受众描述
created: YYYY-MM-DD
status: draft | reviewed | published
wiki_sources:
  - "wiki/page-path"
---
```

**格式要求：**
| 类型 | 格式要求 |
|------|---------|
| post | 标准 Markdown，包含标题、摘要、正文、参考文献 |
| report | 标准 Markdown，包含摘要、正文、结论、参考文献 |
| slides | Marp 格式，`---` 分页，frontmatter 包含 `marp: true` |
| tutorial | 清晰的步骤、完整的代码、可独立跟随 |
| newsletter | 简洁的条目式结构，总结近期关键洞察 |

**通用规则：**
- 交付物必须**独立可读** — 不依赖 wiki 内部的 `[[wikilinks]]`
- `[[wikilinks]]` → 标准 Markdown 链接或纯文本
- 引用使用脚注或参考文献格式

---

## 六、在文物 IP 项目中的正确应用

### 6.1 错误理解（常见误区）

```
用户输入 → 意图解析 → 关键字匹配 Wiki → 返回结果
```

**问题：** 把 Wiki 当成普通数据库，用关键字查询，丢失了 LLM 辅助的核心价值

### 6.2 正确理解

```
用户输入 → IntentParser（意图解析，提取 artifact/style/intent_type）
                          ↓
                    LLM 辅助查询 Wiki
                    （读取 index.md → 理解结构 → 选择页面 → 综合）
                          ↓
                    返回结构化知识给生成层
```

**关键区别：**
- IntentParser 负责分解用户输入（素材是什么？风格是什么？需要什么类型的内容？）
- Wiki 负责提供**史实约束**（这件文物的历史背景、特征、祭祀含义等）
- **Wiki 查询是 LLM 辅助的**，LLM 理解 Wiki 结构后选择读哪些页面

### 6.3 针对文物 IP 的 Wiki 结构

```
artifact_wiki/
├── raw/                           # 原始资料层（不可修改）
│   ├── papers/
│   │   └── 三星堆考古报告_2023.pdf
│   ├── articles/
│   │   └── 青铜面具研究综述.md
│   └── transcripts/
│       └── 博物馆讲解记录.md
│
├── wiki/                          # Wiki 层（LLM 维护）
│   ├── index.md                  # 全局索引（包含 confidence 和 status）
│   ├── log.md                    # 操作日志
│   ├── lifecycle.md              # [可插拔] 生命周期
│   │
│   ├── entities/                 # 实体（史实资料）
│   │   ├── 青铜面具.md
│   │   ├── 三星堆遗址.md
│   │   ├── 纵目面具.md
│   │   └── 金杖.md
│   │
│   ├── concepts/                 # 概念（方法论 + 文化理解）
│   │   ├── 悬疑叙事技巧.md
│   │   ├── 短视频脚本结构.md
│   │   ├── 古蜀祭祀文化.md
│   │   ├── 青铜冶炼工艺.md
│   │   └── 镜头语言.md
│   │
│   ├── summaries/                 # 材料摘要
│   │   └── 三星堆考古报告摘要.md
│   │
│   ├── comparisons/              # 对比分析
│   │   └── 青铜面具vs纵目面具.md
│   │
│   └── synthesis/                # 综合洞察
│       └── 青铜面具悬疑创作指南.md
│
└── output/                        # 输出层
    ├── posts/                    # 博客文章
    ├── reports/                  # 研究报告
    ├── slides/                   # 演示文稿
    ├── tutorials/                # 教程
    └── newsletters/              # 知识简报
```

### 6.4 Wiki 页面示例（正确的格式）

**wiki/entities/青铜面具.md：**

```markdown
---
title: 青铜面具
aliases: [Bronze Mask, 三星堆面具]
tags: [knowledge-management, concept, mature]
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

## 文化含义

- 象征古蜀国的宗教权力
- 可能用于与天神沟通的祭祀仪式
- 纵目造型暗示超越人类的感知能力

## Related Pages

- [[三星堆遗址]] - 出土地点
- [[古蜀祭祀文化]] - 相关文化背景
- [[悬疑叙事技巧]] - 可用于悬疑风格创作
- [[短视频脚本结构]] - 脚本格式参考
```

---

## 七、Embedding 在 LLM Wiki 中的位置

### 7.1 Embedding 没有被抛弃

Embedding 仍然是重要的检索技术，只是应用方式不同：

| 场景 | 传统 RAG | LLM Wiki |
|------|---------|---------|
| **检索对象** | 原始文档碎片 | LLM 整理好的结构化 Wiki 页面 |
| **检索目的** | 直接回答问题 | 找到相关 Wiki 页面，再综合回答 |
| **知识质量** | 碎片化，可能不完整 | 结构化，被 LLM 整理过，质量更高 |

### 7.2 何时需要 Embedding

- **小规模（<100 页面）**：直接用 index.md 遍历就够用
- **大规模（>100 页面）**：用 Embedding 增强检索，llm-wiki 示例推荐 [qmd](https://github.com/tobi/qmd) 工具

### 7.3 Embedding 的正确流程

```
原始资料 → Ingest → Wiki 页面（结构化） → Embedding → 向量索引
                                     ↑
                           用户查询时匹配 Wiki 页面（而非原始文档）
```

---

## 八、Schema（规则手册）简介

### 8.1 什么是 Schema

Schema 是告诉 LLM "如何维护 Wiki"的规则文件，不同工具有不同版本：

| 工具 | Schema 文件 |
|------|-----------|
| OpenAI Codex / 通用 | AGENTS.md |
| Claude Code | CLAUDE.md |
| Gemini CLI | GEMINI.md |

### 8.2 Schema 包含什么

- **架构概述**：各层的职责和权限
- **技能定义**：ingest/query/lint/publish 的流程
- **核心原则**：6 大原则
- **工具使用约定**：如何读写文件

### 8.3 Skills（技能）与 References（参考文档）

```
skills/llm-wiki/
├── SKILL.md                    # 技能主文件，定义 4 种操作
└── references/
    ├── wiki-page-spec.md       # Wiki 页面格式规范
    ├── output-page-spec.md     # 输出交付物格式规范
    ├── tags-spec.md            # 标签规范
    ├── naming-spec.md          # 命名规范
    ├── index-spec.md           # index.md 格式规范
    ├── log-spec.md             # log.md 格式规范
    └── lifecycle-spec.md       # 生命周期详细规则
```

**按需加载**：不需要预加载所有参考文档，只在触发对应条件时才加载。

---

## 九、常见问题

### Q: LLM Wiki 和普通文件夹有什么区别？

A: 普通文件夹只是存储文件，LLM Wiki 是 LLM 主动整理、归纳、更新知识。想象一个图书馆 vs 一个会自己整理书架的图书管理员。

### Q: Wiki 内容会不会过时？

A: 需要定期 Lint 检查，LLM 发现新资料和老内容冲突时会标记或更新。置信度系统（lifecycle）会追踪哪些知识可能过时，并自动衰减置信度。

### Q: 需要多少资料才能开始？

A: 3-5 个核心词条 + 一些原始资料就足够展示设计思路了。Wiki 是渐进式的，资料越多越丰富。

### Q: lifecycle.md 是必须的吗？

A: 不是，它是可插拔的增强功能。删除它不影响 Wiki 核心功能，只是失去置信度追踪和状态管理。

### Q: 如何处理矛盾的信息？

A: 在页面中显式标注矛盾，引用两个来源，让使用者自己判断置信度。新材料与现有内容矛盾时，该页面置信度 −0.15。

### Q: Query 操作和普通搜索有什么区别？

A: 关键区别在于 LLM 辅助。Query 时 LLM 先读 index.md 理解 Wiki 结构，然后决定读哪些页面，而不是简单的关键字匹配。这让 Wiki 查询更智能，能理解语义，并综合多页面的知识回答。

### Q: Embedding 向量检索在 LLM Wiki 中还有用吗？

A: 有用，但应用方式不同。传统 RAG 在原始文档碎片上做向量检索；LLM Wiki 在整理好的结构化页面上做向量检索。小规模 Wiki（<100 页面）直接用 index.md 遍历就够用；大规模 Wiki（>100 页面）可用 qmd 等工具增强检索。

---

## 十、下一步行动

1. ✅ 理解 LLM Wiki 核心理论（Query 是 LLM 辅助的，不是关键字匹配）
2. ⬜ 构建项目的 Raw 层（放入原始资料）
3. ⬜ 使用 Ingest 消化第一批材料
4. ⬜ 体验 Query 操作
5. ⬜ 定期 Lint 检查 Wiki 健康状态
6. ⬜ 使用 Publish 生成第一个交付物

---

## 附录：参考资源

- [Karpathy's LLM Wiki concept](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [qmd - 本地 Markdown 搜索工具](https://github.com/tobi/qmd)
- [Obsidian - 推荐的知识库浏览器](https://obsidian.md/)
