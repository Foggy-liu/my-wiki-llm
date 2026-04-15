# 文物 IP 内容自动化生产链 - 重构计划 v3.0

> **结合 v2.0 实现计划 + LLM Wiki 完整链路重构**

**Goal:** 按照 LLM Wiki 规范重构 artifact_chain，建立完整的 Ingest/Query/Lint/Publish 四大操作链路

---

## 核心问题

### 当前问题（测试发现）

| 问题 | 说明 |
|------|------|
| **召回率低** | 37.5% (9/24 测试用例) |
| **IntentParser 硬编码** | 无法识别"长城"、"清明上河图"等新文物 |
| **Query 只是关键字匹配** | `retrieve()` 未调用 LLM，未读取 index.md 理解结构 |
| **没有 raw 层** | wiki 页面引用 `[[raw/...]]` 但源材料不存在 |
| **Log 没有更新** | 操作没有记录到 `wiki/log.md` |
| **Summaries 误用** | 存放了综合分析，应该是原材料摘要 |

### 正确的 LLM Wiki 链路

```
raw/*.md  →  [Ingest]  →  wiki/summaries/
                                       ↓晋升
                                  wiki/entities/
                                       ↓晋升
                             wiki/concepts/
                                       ↓晋升
                    wiki/comparisons/ + synthesis/
                                       ↓晋升
                              output/*
```

---

## 一、目录结构调整

```
artifact_chain/
├── raw/                              # 新增：源材料层
│   ├── papers/
│   │   └── 三星堆考古报告_2023.pdf
│   ├── articles/
│   │   ├── 青铜面具研究综述.md
│   │   └── 短视频创作指南.md
│   └── docs/
│       ├── 古风短视频创作指南.md
│       └── 科幻短视频创作指南.md
│
├── src/
│   ├── pipelines/                    # 新增：四大操作
│   │   ├── ingest.py               # Ingest 流程
│   │   ├── query.py                # Query 流程（LLM辅助）
│   │   ├── lint.py                 # Lint 流程
│   │   └── publish.py              # Publish 流程
│   │
│   ├── wiki_kb.py                  # 扩展：生命周期 + 日志
│   ├── retriever.py                # 重写：LLM辅助选择页面
│   ├── intent_parser.py            # 扩展：支持更多关键词
│   └── ...
│
├── wiki/
│   ├── index.md                    # 已修正
│   ├── log.md                     # 操作日志（每次操作记录）
│   ├── lifecycle.md                # 生命周期数据
│   ├── log-archive/              # 日志归档
│   │
│   ├── entities/                  # 实体（13个）
│   ├── concepts/                  # 概念（9个）
│   ├── summaries/                 # 工作记忆：原材料摘要（应该是raw消化产物）
│   ├── comparisons/               # 语义记忆：对比分析
│   └── synthesis/                  # 语义记忆：综合洞察
│
├── output/                         # 程序化记忆
│   ├── posts/
│   ├── reports/
│   ├── slides/
│   ├── tutorials/
│   └── newsletters/
│
└── tests/
    ├── test_retrieval.py
    ├── test_recall_rate.py
    ├── test_ingest.py             # 新增
    ├── test_query.py               # 新增
    ├── test_lint.py                # 新增
    ├── test_publish.py             # 新增
    └── test_integration.py         # 新增
```

---

## 二、四大操作实现

### 2.1 Ingest 流程

```
raw/*.md → 提取引用/概念 → 创建/更新wiki页面 →
维护交叉引用 → 更新lifecycle → 更新index → 记录log
```

**核心接口：**
```python
class IngestPipeline:
    def ingest_file(self, raw_path: Path) -> IngestResult
    def run_interactive(self)  # 交互式消化
```

### 2.2 Query 流程（核心修复）

```python
# 错误的实现（当前）
def retrieve(self, intent):
    return wiki_kb.search(intent.artifact)  # 关键字匹配

# 正确的实现
def query(self, question: str) -> QueryResult:
    # 1. LLM 读取 index.md（理解 Wiki 结构）
    index = wiki_kb.read_index()

    # 2. LLM 选择页面（不是关键字匹配！）
    selected = llm_select_pages(question, index)

    # 3. 读取选定页面
    pages = [wiki_kb.get_page(t) for t in selected]

    # 4. LLM 综合回答
    answer = llm_synthesize(question, pages)

    # 5. 更新 lifecycle + 记录 log
    ...
```

### 2.3 Lint 流程

```
矛盾检测 → 孤立页面 → 缺失页面 →
交叉引用完整性 → 生命周期检查 → 归档 → 记录log
```

### 2.4 Publish 流程

```
明确需求 → 定位源材料 → 生成草稿 →
格式适配 → 用户审核 → 记录log
```

---

## 三、Log 机制（核心修复）

每次操作必须记录到 `wiki/log.md`：

```markdown
## [2026-04-15] ingest | raw/articles/青铜面具研究综述.md
- Created: [[raw-articles-青铜面具综合研究]]
- Updated: [[青铜面具]] (confidence +0.10)
- Note: 从原材料消化

## [2026-04-15] query | 三星堆的特点是什么
- Consulted: [[三星堆遗址]], [[青铜面具]], [[悬疑叙事技巧]]
- Answer length: 500 chars

## [2026-04-15] lint | Health Check
- Fixed: 3 items | Pending: 1 item

## [2026-04-15] publish | post | 三星堆悬疑脚本
- Output: output/posts/三星堆悬疑脚本.md
- wiki_deps: [[三星堆遗址]], [[悬疑叙事技巧]]
```

---

## 四、生命周期管理

### 4.1 状态流转

```
active ──→ stale ──→ archived
  ↑         │
  └─────────┘
  （被访问或被新来源确认可恢复）
```

### 4.2 时间衰减规则

| 未访问时间 | 基础衰减 |
|-----------|---------|
| 30-59 天 | -0.02 |
| 60-89 天 | -0.05 |
| 90-179 天 | -0.10 |
| >= 180 天 | -0.15 |

### 4.3 晋升规则

| 方向 | 条件 |
|------|------|
| summaries → entities | 实体被 2+ 材料提到 |
| entities → concepts | 3+ 实体形成可比主题 |
| concepts → synthesis | 综合置信度 >= 0.85 |

---

## 五、实施任务

### Phase 1: 基础设施

- [ ] **T1.1** 创建 `raw/` 目录，放入示例原材料
- [ ] **T1.2** 创建 `src/pipelines/` 目录
- [ ] **T1.3** 扩展 `WikiEntry` 添加 lifecycle 字段

### Phase 2: Log 机制

- [ ] **T2.1** 实现 `wiki_kb.append_log()` 方法
- [ ] **T2.2** 修改所有操作方法，调用 `append_log()`
- [ ] **T2.3** 创建 `tests/test_log.py` 验证日志记录

### Phase 3: Ingest 流程

- [ ] **T3.1** 实现 `IngestPipeline`
- [ ] **T3.2** 实现 raw 文件解析和知识提取
- [ ] **T3.3** 创建 `tests/test_ingest.py`

### Phase 4: Query 流程（核心修复）

- [ ] **T4.1** 重写 `QueryPipeline.query()`
- [ ] **T4.2** 实现 LLM 选择页面逻辑
- [ ] **T4.3** 实现 LLM 综合回答
- [ ] **T4.4** 更新 `tests/test_query.py`

### Phase 5: Lint 流程

- [ ] **T5.1** 实现 `LintPipeline`
- [ ] **T5.2** 实现矛盾检测和孤立页面检查
- [ ] **T5.3** 实现生命周期衰减
- [ ] **T5.4** 创建 `tests/test_lint.py`

### Phase 6: Publish 流程

- [ ] **T6.1** 实现 `PublishPipeline`
- [ ] **T6.2** 实现多格式生成（script/prompt/slides/report）
- [ ] **T6.3** 创建 `tests/test_publish.py`

### Phase 7: 集成测试

- [ ] **T7.1** 创建 `tests/test_integration.py`
- [ ] **T7.2** 运行 `test_recall_rate.py` 验证召回率提升
- [ ] **T7.3** 验证 log 是否完整记录

---

## 六、关键文件

| 文件 | 作用 |
|------|------|
| `src/wiki_kb.py` | 核心：LLM 辅助查询依赖，日志/lifecycle 管理 |
| `src/pipelines/query.py` | 核心：LLM 读取 index.md 选择页面 |
| `src/pipelines/ingest.py` | 从 raw 消化到 wiki |
| `src/pipelines/lint.py` | 健康检查和生命周期 |
| `src/pipelines/publish.py` | 从 wiki 生成交付物 |
| `wiki/index.md` | LLM 理解 Wiki 结构的入口 |
| `wiki/lifecycle.md` | 衰减规则和状态流转 |

---

## 七、验证方案

```bash
# 1. 运行召回率测试（目标：>70%）
python test_recall_rate.py

# 2. 验证日志记录
cat wiki/log.md
# 期望：包含 ingest/query/lint/publish 操作记录

# 3. 运行集成测试
pytest tests/test_integration.py -v

# 4. 验证目录结构
find . -type d | grep -E "(raw|output|log-archive)"
# 期望：raw/, output/, wiki/log-archive/ 存在
```

---

## 八、与 v2.0 的差异

| v2.0 | v3.0 (本计划) |
|------|---------------|
| 修正 wiki 页面格式 | 添加 raw/ 原材料层 |
| 修正 index.md 格式 | 实现完整 Ingest 流程 |
| 添加 log.md 框架 | 实现 Log 机制（每次操作记录） |
| 添加 lifecycle.md 框架 | 实现 Lifecycle 衰减和晋升 |
| 修正 retriever.py（保留关键字匹配） | 重写 Query 为 LLM 辅助 |
| - | 添加 Lint 流程 |
| - | 添加 Publish 流程 |

---

## 九、Summaries 修正

**当前问题**：summaries 目录存放了综合分析（如 `raw-articles-石窟艺术综合.md`）

**正确用法**：
- `summaries/` = 原材料摘要（一个文件 = 一篇原材料的消化产物）
- `comparisons/` = 对比分析（A vs B）
- `synthesis/` = 综合洞察（多材料融合）

**需要修正**：
- `summaries/raw-articles-石窟艺术综合.md` → 应是单个原材料的摘要
- `summaries/raw-articles-汉代丧葬文化.md` → 应是单个原材料的摘要
