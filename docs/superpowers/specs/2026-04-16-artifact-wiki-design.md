# 文物 IP 知识库系统设计

**日期：** 2026-04-16
**状态：** 待批准

---

## 1. 系统概述

**项目名称：** 文物 IP 知识库（Artifact Wiki）

**核心目标：** 构建一个支持史实约束与创意生成双模式的文物 IP 资料管理系统，同时满足管理员的内容管理需求和普通用户的知识问答需求。

**技术栈：**
- 后端：Python 3.11+ / FastAPI / SQLite
- 前端：Vue3 / Vite / Pinia / TailwindCSS
- LLM：MiniMax API

---

## 2. 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      前端 (Vue3)                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │  管理后台    │  │  用户前台   │  │  共享组件   │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                            │
                         REST API
                            │
┌─────────────────────────────────────────────────────────────┐
│                      后端 (FastAPI)                         │
│  ┌─────────────────────────────────────────────────┐        │
│  │                   API 路由层                      │        │
│  └─────────────────────────────────────────────────┘        │
│                            │                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  Ingest  │  │  Query   │  │  Lint    │  │ Publish  │     │
│  │  服务    │  │  服务    │  │  服务    │  │  服务    │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
│                            │                                │
│  ┌─────────────────────────────────────────────────┐        │
│  │              Wiki 引擎 (文件系统)                │        │
│  └─────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 目录结构

```
artifact_wiki/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI 入口
│   │   ├── config.py            # 配置管理
│   │   ├── api/                 # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── admin.py         # 管理接口
│   │   │   ├── query.py         # 问答接口
│   │   │   └── wiki.py          # Wiki 操作接口
│   │   ├── core/                # 核心业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── ingest.py        # Ingest 服务
│   │   │   ├── query.py         # Query 服务
│   │   │   ├── lint.py          # Lint 服务
│   │   │   └── publish.py       # Publish 服务
│   │   ├── models/              # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── wiki_page.py
│   │   │   └── log.py
│   │   ├── services/            # 业务服务
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   └── llm.py           # LLM 调用封装
│   │   └── db/
│   │       ├── __init__.py
│   │       ├── database.py
│   │       └── models.py
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── api/                 # API 调用
│   │   ├── assets/
│   │   ├── components/           # 通用组件
│   │   ├── views/
│   │   │   ├── admin/           # 管理后台
│   │   │   │   ├── Dashboard.vue
│   │   │   │   ├── Ingest.vue
│   │   │   │   ├── Lint.vue
│   │   │   │   └── UserManage.vue
│   │   │   └── user/            # 用户前台
│   │   │       ├── Home.vue
│   │   │       └── Chat.vue
│   │   ├── stores/              # Pinia 状态
│   │   ├── router/
│   │   ├── App.vue
│   │   └── main.js
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── wiki/                       # Wiki 内容存储
│   ├── raw/                    # 原始资料（只读）
│   │   ├── papers/
│   │   ├── articles/
│   │   ├── transcripts/
│   │   ├── docs/
│   │   └── assets/
│   └── wiki/                   # LLM 维护的知识库
│       ├── index.md
│       ├── log.md
│       ├── lifecycle.md
│       ├── entities/
│       ├── concepts/
│       ├── summaries/
│       ├── comparisons/
│       └── synthesis/
├── CLAUDE.md                   # Schema 规则
└── README.md
```

---

## 4. 数据模型

### 4.1 用户表 (users)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| username | VARCHAR(50) | 用户名，唯一 |
| password_hash | VARCHAR(255) | 密码哈希 |
| role | ENUM | 'admin' / 'user' |
| created_at | DATETIME | 创建时间 |

### 4.2 Wiki 页面表 (wiki_pages)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| title | VARCHAR(200) | 页面标题 |
| category | VARCHAR(50) | entities/concepts/summaries/comparisons/synthesis |
| file_path | VARCHAR(500) | 实际文件路径 |
| confidence | FLOAT | 置信度 0.0-1.0 |
| status | ENUM | active/stale/archived |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### 4.3 操作日志表 (operation_logs)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| operation | ENUM | ingest/query/lint/publish |
| status | ENUM | success/failed |
| details | TEXT | 操作详情 JSON |
| operator_id | INTEGER | 操作人 ID |
| created_at | DATETIME | 操作时间 |

---

## 5. API 设计

### 5.1 管理员接口 (/api/admin/*)

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/admin/ingest | 触发 Ingest 流程 |
| GET | /api/admin/ingest/status | 获取 Ingest 状态 |
| POST | /api/admin/lint | 触发 Lint 检查 |
| GET | /api/admin/lint/report | 获取 Lint 报告 |
| GET | /api/admin/wiki/pages | 获取 Wiki 页面列表 |
| PUT | /api/admin/wiki/pages/:id | 更新页面 |
| POST | /api/admin/publish | 触发 Publish |
| GET | /api/admin/users | 用户列表 |
| POST | /api/admin/users | 创建用户 |

### 5.2 用户接口 (/api/user/*)

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/user/query | 知识问答 |
| GET | /api/user/query/history | 查询历史 |

---

## 6. 核心流程

### 6.1 Ingest 流程

```
1. 管理员上传文件到 raw/
2. 调用 POST /api/admin/ingest
3. 后端：
   a. 读取 raw/ 下的源文件
   b. 调用 LLM 提取引用、概念、核心论点
   c. 与管理员确认重点（可选步骤）
   d. 创建/更新 Wiki 页面
   e. 维护交叉引用 [[wikilinks]]
   f. 更新 index.md
   g. 记录到 log.md
4. 返回处理结果
```

### 6.2 Query 流程

```
1. 用户发送问题
2. 调用 POST /api/user/query
3. 后端：
   a. 读取 wiki/index.md（理解 Wiki 结构）
   b. LLM 判断需要查询哪些页面
   c. LLM 读取选定页面
   d. 综合回答，标注来源
   e. 记录到 log.md
4. 返回答案
```

### 6.3 Lint 流程

```
1. 管理员触发 Lint
2. 后端执行检查：
   a. 检测矛盾页面
   b. 检测孤立页面（无引用）
   c. 检测缺失引用
   d. raw/ 同步检查（文件删除/移动/修改）
3. 生成报告
4. 可选：自动修复或标记问题
```

---

## 7. Wiki 页面格式

```markdown
---
title: 青铜面具
category: entities
created: 2026-04-16
updated: 2026-04-16
sources:
  - "[[raw/papers/三星堆考古报告_2023.pdf]]"
  - "[[raw/articles/青铜面具研究综述.md]]"
description: 三星堆遗址出土的青铜面具
confidence: 0.75
status: active
---

## 基本信息
- 出土地点：四川广汉三星堆遗址
- 年代：商代

## 外观特征
- 眼睛呈柱状向外突出（纵目）

## Related Pages
- [[三星堆遗址]]
- [[古蜀祭祀文化]]
```

---

## 8. 前端页面规划

### 8.1 管理后台

| 页面 | 功能 |
|------|------|
| Dashboard | 系统概览、Wiki 健康状态、最近操作 |
| Ingest | 上传文件、触发消化、查看进度 |
| Lint | 查看检查报告、处理问题页面 |
| UserManage | 用户 CRUD |

### 8.2 用户前台

| 页面 | 功能 |
|------|------|
| Home | Wiki 目录浏览、搜索入口 |
| Chat | 知识问答界面 |

---

## 9. 安全设计

1. **认证：** JWT Token
2. **权限：** 管理员 vs 普通用户
3. **Raw 保护：** 后端禁止直接修改 raw/ 文件
4. **输入验证：** 文件类型检查、大小限制

---

## 10. 第一期实现范围

**后端：**
- [ ] 项目脚手架（FastAPI + 目录结构）
- [ ] 数据库模型和迁移
- [ ] 认证模块（JWT）
- [ ] Ingest 服务（核心逻辑）
- [ ] Query 服务（LLM 集成）
- [ ] Lint 服务
- [ ] 基础 API 路由

**前端：**
- [ ] Vue3 项目脚手架
- [ ] 登录页面
- [ ] 管理后台 Dashboard
- [ ] Ingest 上传界面
- [ ] Lint 报告界面
- [ ] 用户前台 Home + Chat

---

- [x] Wiki 存储方式：文件系统（Markdown）
- [x] 用户注册登录：完整实现

---

**下一步：** 批准后进入 implementation-planning 阶段
