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

## LLM Wiki Query 正确流程

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

## 扩展方向

1. **知识库扩展**：接入更多文物数据（敦煌、故宫等）
2. **生成层增强**：接入真实LLM API实现完整生成
3. **对接层扩展**：适配更多AI视频生成工具
4. **评估体系**：增加生成质量评估指标
