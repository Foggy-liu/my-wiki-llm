# Understand Anything 教学开发指南

> 本指南面向第一次接触代码分析工具的开发者，用最简单的话解释 Understand Anything 是什么、怎么用、以及它如何帮助你理解一个陌生的代码库。

---

## 目录

1. [Understand Anything 是什么？](#1-understand-anything-是什么)
2. [安装插件](#2-安装插件)
3. [快速开始：分析你的第一个项目](#3-快速开始分析你的第一个项目)
4. [所有命令详解](#4-所有命令详解)
5. [分析结果在哪里？](#5-分析结果在哪里)
6. [知识图谱是什么？](#6-知识图谱是什么)
7. [Dashboard 可视化界面](#7-dashboard-可视化界面)
8. [进阶用法](#8-进阶用法)
9. [常见问题](#9-常见问题)

---

## 1. Understand Anything 是什么？

### 一句话解释

**Understand Anything** 是一个让你用自然语言提问来理解任何代码库的工具。它会自动扫描你的代码，生成一张"知识地图"（叫做**知识图谱**），然后你可以通过文字聊天或者可视化界面来探索这张地图。

### 打个比方

想象你刚搬进一栋巨大的办公楼，里面有1000个房间，你不知道：
- 哪间是厨房？
- 哪间是会议室？
- 紧急出口在哪？

现在想象有一份**自动生成的地图**，上面标注了每个房间的用途、各房间之间的连接关系（哪些房间通向哪些），还可以在地图上搜索"会议室在哪里"。这就是 Understand Anything 给你代码库做的事情。

### 它能做什么？

| 功能 | 说明 |
|------|------|
| **自动分析代码结构** | 不用你手动看代码，AI 自动理解每个文件是干什么的 |
| **生成知识图谱** | 把代码里的关系（图）用 JSON 文件保存 |
| **可视化探索** | 用网页界面查看代码的"地图" |
| **自然语言问答** | 用中文/英文问"这个项目是怎么处理登录的？" |
| **理解代码变更** | 分析 PR 或 diff，告诉你改了什么、影响哪些地方 |
| **生成学习 tour** | 像看导览一样，一步一步带你走一遍项目 |

---

## 2. 安装插件

### 前置要求

- **Node.js** >= 22（建议 v24）
- **pnpm** >= 10
- **Claude Code** 已安装

### 安装步骤

1. 在 Claude Code 中运行插件安装命令：
   ```
   /plugin install understand-anything
   ```
   或者如果你有源代码仓库：
   ```bash
   cd Understand-Anything/understand-anything-plugin
   pnpm install
   ```

2. 构建插件：
   ```bash
   pnpm --filter @understand-anything/core build
   pnpm --filter @understand-anything/skill build
   ```

3. 重新加载插件：
   ```
   /reload-plugins
   ```

### 本地测试修改

插件安装在 Claude Code 的缓存目录中。要测试本地修改：
```bash
# 1. 构建
pnpm --filter @understand-anything/core build
pnpm --filter @understand-anything/skill build

# 2. 复制到缓存（替换 <VERSION> 为实际版本号）
cp -R ./understand-anything-plugin ~/.claude/plugins/cache/understand-anything/understand-anything/<VERSION>/

# 3. 开启新的 Claude Code 会话
```

---

## 3. 快速开始：分析你的第一个项目

### 最简单的用法

进入任意一个项目目录，运行：

```
/understand
```

然后等待分析完成。完成后会自动打开 Dashboard 网页界面。

### 第一次分析会发生什么？

```
┌─────────────────────────────────────────────────────┐
│  Step 1: 扫描文件                                    │
│  扫描项目中所有文件（代码、配置、文档等）               │
│                                                      │
│  Step 2: 分析文件                                    │
│  理解每个文件的作用、函数、类、关系                   │
│                                                      │
│  Step 3: 整理结构                                    │
│  把代码分成不同层次（API层、数据层、工具层等）         │
│                                                      │
│  Step 4: 生成导览                                    │
│  创建学习路线，带你一步步理解项目                     │
│                                                      │
│  Step 5: 验证结果                                    │
│  检查图谱有没有错误                                   │
│                                                      │
│  Step 6: 保存并打开 Dashboard                        │
│  自动打开网页版可视化界面                             │
└─────────────────────────────────────────────────────┘
```

### 完整重建（忽略已有结果）

如果已经有分析结果，想重新分析：

```
/understand --full
```

### 启用自动更新

每次 git 提交后自动更新知识图谱：

```
/understand --auto-update
```

---

## 4. 所有命令详解

### `/understand` —— 主分析命令

```
/understand [选项]
```

**选项：**

| 选项 | 作用 |
|------|------|
| `--full` | 强制完整重建，忽略已有结果 |
| `--auto-update` | 开启自动更新（git commit 后自动重新分析） |
| `--no-auto-update` | 关闭自动更新 |
| `--review` | 用 AI 深度审查已有图谱，不重新分析 |
| `--subdir/` | 只分析某个子目录 |

**示例：**
```
# 分析当前目录
/understand

# 强制完整重建
/understand --full

# 只分析 backend 子目录
/understand backend/

# 开启自动更新
/understand --auto-update
```

### `/understand-dashboard` —— 打开可视化界面

```
/understand-dashboard [项目路径]
```

不传参数则分析当前目录。Dashboard 是一个网页应用，展示代码的知识图谱。

### `/understand-chat` —— 终端问答

```
/understand-chat "这个项目的登录流程是怎么实现的？"
```

在终端里直接用自然语言提问，基于知识图谱回答。

### `/understand-explain` —— 深度解释某个文件

```
/understand-explain src/auth/login.ts
```

深入解释指定的文件或函数。

### `/understand-diff` —— 分析代码变更

```
/understand-diff
```

分析当前未提交的改动，告诉你改了什么文件、影响哪些模块、有什么风险。

### `/understand-domain` —— 提取业务领域知识

```
/understand-domain
```

从代码中提取**业务层面**的知识：
- 有哪些业务领域？（订单管理、用户管理、支付……）
- 每个领域的业务流程是什么？
- 流程中的步骤是怎样的？

加上 `--full` 可以强制重新扫描。

### `/understand-onboard` —— 生成新成员入门指南

```
/understand-onboard
```

为新加入项目的开发者生成一份结构化的上手指南。

---

## 5. 分析结果在哪里？

分析完成后，所有文件都保存在项目的 `.understand-anything/` 目录中：

```
my-project/
├── .understand-anything/
│   ├── knowledge-graph.json    # 最重要的文件！完整知识图谱
│   ├── domain-graph.json       # 业务领域图谱（可选）
│   ├── meta.json               # 分析元数据（时间、版本、git commit）
│   ├── config.json             # 配置（auto-update 等）
│   └── fingerprints.json       # 文件指纹（用于增量更新）
```

### `knowledge-graph.json` 结构简介

```json
{
  "version": "1.0.0",
  "project": {
    "name": "my-project",
    "languages": ["typescript", "javascript"],
    "frameworks": ["react", "vite"],
    "description": "一个用户管理系统"
  },
  "nodes": [
    {
      "id": "file:src/index.ts",
      "type": "file",
      "name": "index.ts",
      "summary": "项目入口文件，负责启动应用",
      "tags": ["entry-point"],
      "complexity": "simple"
    },
    {
      "id": "function:src/auth/login.ts:authenticate",
      "type": "function",
      "name": "authenticate",
      "summary": "验证用户名密码并返回会话token",
      "tags": ["auth", "security"],
      "complexity": "moderate"
    }
  ],
  "edges": [
    {
      "source": "file:src/index.ts",
      "target": "file:src/auth/login.ts",
      "type": "imports",
      "direction": "forward",
      "weight": 0.7
    }
  ],
  "layers": [
    {
      "id": "layer:api",
      "name": "API Layer",
      "description": "处理 HTTP 请求的路由和控制器",
      "nodeIds": ["file:src/routes/index.ts"]
    }
  ],
  "tour": [
    {
      "order": 1,
      "title": "项目概览",
      "description": "README 介绍项目基本功能",
      "nodeIds": ["document:README.md"]
    }
  ]
}
```

---

## 6. 知识图谱是什么？

### 核心概念：节点（Node）和边（Edge）

知识图谱由两部分组成：

**节点（Node）** = 代码中的实体

| 节点类型 | 含义 | 示例 |
|----------|------|------|
| `file` | 源代码文件 | `file:src/index.ts` |
| `function` | 函数或方法 | `function:src/auth/login.ts:authenticate` |
| `class` | 类或接口 | `class:src/models/User.ts:User` |
| `config` | 配置文件 | `config:tsconfig.json` |
| `document` | 文档文件 | `document:README.md` |
| `service` | 部署服务 | `service:Dockerfile` |
| `table` | 数据库表 | `table:db/migrations/001.sql:users` |
| `endpoint` | API 端点 | `endpoint:api/routes.yaml:/users` |
| `pipeline` | CI/CD 流水线 | `pipeline:.github/workflows/ci.yml` |
| `schema` | 数据schema | `schema:api/schema.graphql` |
| `resource` | 基础设施资源 | `resource:main.tf` |

**边（Edge）** = 节点之间的关系

| 边类型 | 含义 | 示例 |
|--------|------|------|
| `imports` | 文件导入了另一个文件 | `index.ts imports auth.ts` |
| `calls` | 函数调用了另一个函数 | `login calls authenticate` |
| `contains` | 文件包含某个函数/类 | `auth.ts contains authenticate` |
| `configures` | 配置影响代码 | `tsconfig.json configures index.ts` |
| `deploys` | 部署服务部署代码 | `Dockerfile deploys index.ts` |
| `documents` | 文档描述代码 | `README.md documents index.ts` |

### 图谱的层次（Layers）

Layers 把节点分组，帮你理解代码的架构层次：

```
┌─────────────────────────────────┐
│         UI Layer                │  ← React 组件、页面
├─────────────────────────────────┤
│        API Layer                │  ← 路由、控制器
├─────────────────────────────────┤
│       Service Layer             │  ← 业务逻辑
├─────────────────────────────────┤
│        Data Layer               │  ← 数据库、ORM
├─────────────────────────────────┤
│     Infrastructure              │  ← Docker、CI/CD
└─────────────────────────────────┘
```

### 导览（Tour）

Tour 是 AI 生成的代码学习路线，像景点导览一样，带你一步步理解项目：

```
第 1 步：项目概览
  → 阅读 README.md，了解项目是什么

第 2 步：入口文件
  → 看 index.ts，了解项目怎么启动

第 3 步：核心类型
  → 看 User 类型定义，建立领域概念

第 4 步：认证服务
  → 看 login.ts，了解登录流程

... 继续
```

---

## 7. Dashboard 可视化界面

### 启动 Dashboard

```
/understand-dashboard
```

然后打开显示的 URL（包含 token），例如：
```
http://127.0.0.1:5173?token=abc123
```

### Dashboard 界面介绍

```
┌──────────────────────────────────────────────────────────────┐
│  🔍 搜索框（自然语言搜索）                                      │
├────────────────────────┬─────────────────────────────────────┤
│                        │                                      │
│     图谱视图            │         代码查看器                    │
│   （节点和边的网络图）   │     （选中的文件内容）                 │
│                        │                                      │
│   点击节点可以看到详情   │     带语法高亮                        │
│                        │                                      │
├────────────────────────┼─────────────────────────────────────┤
│                        │                                      │
│     聊天面板            │         学习面板                      │
│   问关于项目的问题       │     Tour 导览 + 语言知识点             │
│                        │                                      │
└────────────────────────┴─────────────────────────────────────┘
```

### 图谱视图说明

- **节点颜色** = 不同类型
  - 蓝色 = 代码文件
  - 绿色 = 配置文件
  - 紫色 = 服务/容器
  - 橙色 = API 端点
  - 灰色 = 文档

- **节点大小** = 重要程度（被引用越多越大）

- **边的粗细** = 关系强度

### 侧边栏功能

| 面板 | 内容 |
|------|------|
| **Project Overview** | 项目概览，语言、框架、文件统计 |
| **Node Info** | 选中节点的详细信息（摘要、标签、复杂度） |
| **Learn** | 语言知识点讲解，学习模式 |

---

## 8. 进阶用法

### 增量更新

默认情况下，`/understand` 会检查 git 变更，只重新分析改动的文件。

要启用自动更新：
```
/understand --auto-update
```
之后每次 `git commit` 后 Claude Code 会自动检测并更新图谱。

### 忽略某些文件

创建 `.understand-anything/.understandignore` 文件（语法和 `.gitignore` 一样）：

```
# 忽略测试文件
*.test.*
*.spec.*

# 忽略某个目录
docs/
```

### 子目录分析

分析大型项目的某个部分：
```
/understand backend/
/understand frontend/
```

### 图谱审查

用 AI 深度审查已有图谱：
```
/understand --review
```

### 业务领域分析

不只是看代码结构，还理解业务逻辑：
```
/understand-domain
```

### 从头创建知识库

如果你的项目没有代码（如纯文档项目、SQL schema 集合），Understand Anything 仍然可以分析其中的所有文件类型。

---

## 9. 常见问题

### Q: 分析一个大型项目要多久？

- 小型项目（< 50 文件）：约 1-3 分钟
- 中型项目（50-200 文件）：约 5-15 分钟
- 大型项目（200+ 文件）：建议用子目录分析

### Q: 支持哪些编程语言？

支持 **26 种文件类型**，包括：

| 类别 | 语言/格式 |
|------|----------|
| 代码 | TypeScript, JavaScript, Python, Go, Rust, Java, C#, C++, Swift, Kotlin, Ruby, PHP |
| 配置 | JSON, YAML, TOML, XML, ENV |
| 文档 | Markdown, reStructuredText |
| 数据 | SQL, GraphQL, Protobuf, OpenAPI |
| 基础设施 | Dockerfile, Docker Compose, Terraform, Kubernetes, GitHub Actions, Makefile |
| 脚本 | Shell, PowerShell |
| 样式 | HTML, CSS, SCSS |

### Q: 分析结果保存在哪里？

每个项目的 `.understand-anything/` 目录中（不会污染项目根目录）。

### Q: 怎么更新已有的图谱？

运行 `/understand`，如果是增量分析会自动检测变更。如果想强制重建，运行 `/understand --full`。

### Q: Dashboard 打不开怎么办？

1. 确保端口 5173 没有被占用
2. 检查 URL 是否包含完整的 token 参数
3. 尝试用 `--full` 重新分析

### Q: 可以分析私有仓库吗？

可以，所有分析在本地进行，图谱文件保存在本地，不会上传到任何服务器。

---

## 附录：文件类型速查表

```
understand-anything/
├── packages/
│   ├── core/                    # 核心分析引擎（所有包的共享基础）
│   │   └── src/
│   │       ├── analyzer/         # LLM 分析器和图谱构建器
│   │       ├── languages/        # 各种编程语言的配置
│   │       ├── plugins/          # 插件系统（tree-sitter等）
│   │       └── persistence/      # JSON 文件读写
│   ├── skill/                   # Claude Code skill 实现
│   └── dashboard/                # React 网页界面
├── agents/                      # AI Agent 定义（做具体分析工作）
│   ├── project-scanner.md       # 扫描项目文件
│   ├── file-analyzer.md         # 分析单个文件
│   ├── architecture-analyzer.md # 分析架构层次
│   ├── tour-builder.md          # 生成学习导览
│   ├── domain-analyzer.md        # 分析业务领域
│   ├── graph-reviewer.md         # 审查图谱质量
│   └── ...
└── skills/                      # /understand 等命令的定义
```

---

*本指南基于 Understand Anything v2.3.1 编写*
