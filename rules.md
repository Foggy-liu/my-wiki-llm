# LLM Wiki 实践规则

## 核心原则

1. **Query 是 LLM 辅助的，不是关键字匹配**
   - 正确流程：读取 index.md → LLM 理解 Wiki 结构 → 选择页面 → 综合回答
   - 错误做法：关键字匹配搜索 Wiki 页面

2. **Wiki 页面必须有 confidence 和 status 字段**
   - 每个页面 frontmatter 必须包含 confidence (0.0-1.0) 和 status (active/stale/archived)

3. **index.md 使用表格格式，不是列表**
   - 必须包含列：Page、Confidence、Status、Updated、Description

4. **所有操作必须记录到 log.md**
   - 格式：`## [YYYY-MM-DD] operation | target`

## 常见错误

| 错误 | 后果 | 正确做法 |
|------|------|----------|
| Query 用关键字匹配 | 无法理解语义，查准率低 | LLM 读取 index.md 理解结构后选择页面 |
| Wiki 页面缺 confidence/status | 无法追踪知识质量 | frontmatter 必须包含这两个字段 |
| index.md 用列表格式 | LLM 无法高效定位页面 | 必须用表格格式 |
| 不记录 log.md | 操作历史丢失，无法追溯 | 每次操作都要追加记录 |

## Wiki 页面 Frontmatter 必须字段

```yaml
---
title: 页面标题
aliases: [别名1, 别名2]
tags: [标签1, 标签2]
category: entities | concepts | summaries | comparisons | synthesis
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources:
  - "[[raw/path/source-filename]]"
description: 一句话描述，不超过100字符
confidence: 0.75
status: active
---
```

## Query 操作正确流程

```
用户提问
    ↓
LLM 读取 index.md（理解 Wiki 有哪些页面、主题是什么）
    ↓
LLM 判断需要查询哪些页面（基于语义理解，不是关键字）
    ↓
LLM 读取选定的 Wiki 页面
    ↓
LLM 综合已有知识回答问题
    ↓
如果答案有价值，询问用户是否保存为新页面
    ↓
更新 lifecycle（如有）：被查询页面 access +1
    ↓
记录到 log.md
```

## 文件位置规范

```
raw/
├── articles/      # 网络文章、博客
├── papers/        # 学术论文
├── docs/          # 官方文档摘录
├── transcripts/    # 会议记录、演讲稿
└── assets/        # 图片、图表、数据文件

wiki/
├── index.md              # 全局索引（表格格式）
├── log.md                # 操作日志
├── lifecycle.md          # [可选] 生命周期数据
├── entities/             # 实体
├── concepts/             # 概念/方法论
├── summaries/            # 材料摘要
├── comparisons/           # 对比分析
└── synthesis/            # 综合洞察
```

## Ingest 链路规则

1. **自动创建缺失引用**
   - Ingest 提取到 [[wikilink]] 时，如果页面不存在，自动创建占位实体页面
   - 占位页面 confidence=0.1，标签包含 auto-created
   - 不要留给人修补，不要依赖 Lint 事后发现

2. **自动更新 index.md**
   - Ingest 创建新页面后，必须同步更新 index.md 对应分类表格
   - index.md 的 Last updated 时间戳同步更新

3. **自动记录 log.md**
   - Ingest/Query/Lint/Publish 四个操作都必须调用 append_log()
   - 格式：`## [YYYY-MM-DD] ingest | file\n- Created: [[page]]\n- Updated: [[page]]`

## 晋升规则

| 方向 | 条件 |
|------|------|
| summaries → entities/concepts | 实体/概念被 2+ 素材提及 |
| entities/concepts → comparisons/synthesis | 3+ 个形成可比主题或模式 |
| synthesis confidence >= 0.85 | 建议 publish 为成品 |

## Pipeline 操作通用模式

每个 pipeline 操作必须遵循同一套流程：

```
操作执行
    ↓
更新 lifecycle（update_access）
    ↓
记录 log（append_log）
    ↓
返回结果
```

## WikiEntry 必须字段（扩展）

```yaml
last_accessed: ""      # ISO datetime，生命周期衰减用
access_count: 0        # 访问次数，用于晋升规则
```

## Lint 职责边界

- Lint 负责检测：孤立页面、矛盾、交叉引用完整性、生命周期衰减
- Lint 不负责修复：修复是 Ingest 的职责
- Error 级别问题应该在 Ingest 阶段就被消除
