# 文物IP内容自动化生产链

基于 LLM Wiki 模式的知识库驱动的文物IP内容生成系统。

## 系统架构

```
用户输入 → 资料层 → 生成层 → 对接层 → AI视频Prompt
```

### 三层架构

| 层级 | 职责 | 核心模块 |
|------|------|---------|
| **资料层** | Wiki知识库 + 意图解析 | IntentParser, WikiKnowledgeBase, Retriever |
| **生成层** | 基于知识生成脚本 | ScriptGenerator |
| **对接层** | 脚本转Prompt | PromptGenerator |

## 项目结构

```
artifact_chain/
├── config/
│   └── settings.py              # 配置管理
├── wiki/                        # Wiki知识库（Markdown格式）
│   ├── index.md                 # 全局索引
│   ├── entities/                # 实体（文物）
│   │   ├── 青铜面具.md
│   │   └── 三星堆遗址.md
│   └── concepts/                # 概念（方法论）
│       ├── 悬疑叙事技巧.md
│       └── 短视频脚本结构.md
├── src/                         # 源代码
│   ├── intent_parser.py         # 意图解析
│   ├── wiki_kb.py               # Wiki操作
│   ├── retriever.py             # 检索
│   ├── script_gen.py            # 脚本生成（简化）
│   └── prompt_gen.py            # Prompt生成（简化）
├── tests/                       # 单元测试
├── main.py                      # 主入口
└── requirements.txt             # 依赖
```

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 运行演示
python main.py
```

## 使用 Obsidian 浏览 Wiki（可选）

本项目的 Wiki 知识库采用 Markdown 格式，可以直接用 [Obsidian](https://obsidian.md/) 打开浏览。

### 推荐的 Obsidian 配置

1. 打开本项目根目录作为 Vault
2. 安装 Dataview 插件（可选，用于动态查询）
3. 打开 Graph View 查看知识网络

### 效果

- Wiki 页面使用 `[[wikilinks]]` 互相链接
- Obsidian 会自动构建知识图谱
- 可以通过 Graph View 可视化知识结构

## 扩展方向

详见 [docs/项目理解.md](../docs/settings/项目理解.md)

## License

MIT
