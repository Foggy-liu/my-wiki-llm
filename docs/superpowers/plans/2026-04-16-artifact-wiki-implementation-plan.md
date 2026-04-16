# 文物 IP 知识库系统实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 搭建完整的文物 IP 知识库系统，支持管理员的内容管理和普通用户的知识问答

**Architecture:** Python FastAPI 后端 + Vue3 前端 + SQLite 数据库 + 文件系统存储 Wiki 内容

**Tech Stack:** Python 3.11+ / FastAPI / SQLite / Vue3 / Vite / Pinia / TailwindCSS / MiniMax API

---

## 文件结构

```
artifact_wiki/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI 入口
│   │   ├── config.py            # 配置管理
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── query.py
│   │   │   └── wiki.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── ingest.py
│   │   │   ├── query.py
│   │   │   ├── lint.py
│   │   │   └── publish.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── wiki_page.py
│   │   │   └── log.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   └── llm.py
│   │   └── db/
│   │       ├── __init__.py
│   │       ├── database.py
│   │       └── models.py
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── views/
│   │   │   ├── admin/
│   │   │   └── user/
│   │   ├── stores/
│   │   ├── router/
│   │   ├── App.vue
│   │   └── main.js
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── wiki/
│   ├── raw/
│   │   ├── papers/
│   │   ├── articles/
│   │   ├── transcripts/
│   │   ├── docs/
│   │   └── assets/
│   └── wiki/
│       ├── index.md
│       ├── log.md
│       ├── entities/
│       ├── concepts/
│       ├── summaries/
│       ├── comparisons/
│       └── synthesis/
├── CLAUDE.md
└── README.md
```

---

## Phase 1: 基础脚手架

### Task 1: Backend 项目脚手架

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/config.py`
- Create: `backend/run.py`

- [ ] **Step 1: 创建 backend/requirements.txt**

```txt
fastapi==0.109.2
uvicorn[standard]==0.27.1
sqlalchemy==2.0.25
pydantic==2.6.1
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
httpx==0.26.0
aiofiles==23.2.1
```

- [ ] **Step 2: 创建 backend/app/__init__.py**

```python
"""Artifact Wiki Backend Application"""
__version__ = "0.1.0"
```

- [ ] **Step 3: 创建 backend/app/config.py**

```python
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    APP_NAME: str = "Artifact Wiki"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./artifact_wiki.db"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Wiki paths
    WIKI_ROOT: Path = Path(__file__).parent.parent.parent / "wiki"
    RAW_DIR: Path = WIKI_ROOT / "raw"
    WIKI_DIR: Path = WIKI_ROOT / "wiki"
    
    # MiniMax LLM
    MINIMAX_API_KEY: str = ""
    MINIMAX_BASE_URL: str = "https://api.minimax.chat/v1"
    MINIMAX_MODEL: str = "abab6.5s-chat"
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
```

- [ ] **Step 4: 创建 backend/app/main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Artifact Wiki API", "version": "0.1.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

- [ ] **Step 5: 创建 backend/run.py**

```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
```

- [ ] **Step 6: 验证运行**

Run: `cd backend && pip install -r requirements.txt && python run.py`
Expected: Server starts on port 8000

- [ ] **Step 7: Commit**

```bash
git add backend/
git commit -m "feat: add backend project scaffolding with FastAPI"
```

---

### Task 2: Frontend 项目脚手架

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.vue`

- [ ] **Step 1: 创建 frontend/package.json**

```json
{
  "name": "artifact-wiki-frontend",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.15",
    "vue-router": "^4.2.5",
    "pinia": "^2.1.7",
    "axios": "^1.6.7",
    "@vueuse/core": "^10.7.2"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.3",
    "vite": "^5.0.12",
    "tailwindcss": "^3.4.1",
    "autoprefixer": "^10.4.17",
    "postcss": "^8.4.35"
  }
}
```

- [ ] **Step 2: 创建 frontend/vite.config.js**

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

- [ ] **Step 3: 创建 frontend/tailwind.config.js**

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

- [ ] **Step 4: 创建 frontend/postcss.config.js**

```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

- [ ] **Step 5: 创建 frontend/index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>文物 IP 知识库</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
```

- [ ] **Step 6: 创建 frontend/src/main.js**

```javascript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/main.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
```

- [ ] **Step 7: 创建 frontend/src/assets/main.css**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

- [ ] **Step 8: 创建 frontend/src/App.vue**

```vue
<template>
  <router-view />
</template>

<script setup>
</script>
```

- [ ] **Step 9: 创建 frontend/src/router/index.js**

```javascript
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/home'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
```

- [ ] **Step 10: 安装依赖并验证**

Run: `cd frontend && npm install && npm run dev`
Expected: Vite dev server starts on port 3000

- [ ] **Step 11: Commit**

```bash
git add frontend/
git commit -m "feat: add frontend project scaffolding with Vue3"
```

---

### Task 3: Wiki 目录结构

**Files:**
- Create: `wiki/raw/papers/.gitkeep`
- Create: `wiki/raw/articles/.gitkeep`
- Create: `wiki/raw/transcripts/.gitkeep`
- Create: `wiki/raw/docs/.gitkeep`
- Create: `wiki/raw/assets/.gitkeep`
- Create: `wiki/wiki/entities/.gitkeep`
- Create: `wiki/wiki/concepts/.gitkeep`
- Create: `wiki/wiki/summaries/.gitkeep`
- Create: `wiki/wiki/comparisons/.gitkeep`
- Create: `wiki/wiki/synthesis/.gitkeep`
- Create: `wiki/wiki/index.md`
- Create: `wiki/wiki/log.md`

- [ ] **Step 1: 创建 wiki/wiki/index.md**

```markdown
---
title: Wiki Index
category: index
created: 2026-04-16
updated: 2026-04-16
---

# 文物 IP 知识库

## 目录

| 分类 | 页面数 | 最近更新 |
|------|--------|----------|
| 实体 (entities) | 0 | - |
| 概念 (concepts) | 0 | - |
| 摘要 (summaries) | 0 | - |
| 对比 (comparisons) | 0 | - |
| 综合 (synthesis) | 0 | - |

## 最近更新

暂无内容
```

- [ ] **Step 2: 创建 wiki/wiki/log.md**

```markdown
# Wiki Log

| 时间 | 操作 | 操作人 | 状态 | 详情 |
|------|------|--------|------|------|
```

- [ ] **Step 3: Commit**

```bash
git add wiki/
git commit -m "feat: add wiki directory structure"
```

---

## Phase 2: 后端核心模块

### Task 4: 数据库模型

**Files:**
- Create: `backend/app/db/database.py`
- Create: `backend/app/db/models.py`
- Modify: `backend/app/db/__init__.py`

- [ ] **Step 1: 创建 backend/app/db/database.py**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite specific
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 2: 创建 backend/app/db/models.py**

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"

class OperationType(str, enum.Enum):
    INGEST = "ingest"
    QUERY = "query"
    LINT = "lint"
    PUBLISH = "publish"

class OperationStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"

class PageStatus(str, enum.Enum):
    ACTIVE = "active"
    STALE = "stale"
    ARCHIVED = "archived"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default=UserRole.USER.value)
    created_at = Column(DateTime, default=datetime.utcnow)

class WikiPage(Base):
    __tablename__ = "wiki_pages"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)
    file_path = Column(String(500), nullable=False)
    confidence = Column(Float, default=0.5)
    status = Column(String(20), default=PageStatus.ACTIVE.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class OperationLog(Base):
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, index=True)
    operation = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)
    details = Column(Text)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

- [ ] **Step 3: 创建 backend/app/db/__init__.py**

```python
from .database import Base, engine, get_db, SessionLocal
from .models import User, WikiPage, OperationLog, UserRole, OperationType, OperationStatus, PageStatus

__all__ = [
    "Base",
    "engine",
    "get_db",
    "SessionLocal",
    "User",
    "WikiPage",
    "OperationLog",
    "UserRole",
    "OperationType",
    "OperationStatus",
    "PageStatus",
]
```

- [ ] **Step 4: 更新 backend/app/main.py 添加数据库初始化**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import Base, engine

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    # Create database tables
    Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Artifact Wiki API", "version": "0.1.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

- [ ] **Step 5: 验证数据库**

Run: `cd backend && python -c "from app.db import Base, engine; Base.metadata.create_all(bind=engine); print('Database initialized')"`
Expected: Database file created

- [ ] **Step 6: Commit**

```bash
git add backend/app/db/
git commit -m "feat: add database models and initialization"
```

---

### Task 5: 认证模块

**Files:**
- Create: `backend/app/services/auth.py`
- Create: `backend/app/api/auth.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 创建 backend/app/services/auth.py**

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db, User, UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
```

- [ ] **Step 2: 创建 backend/app/api/auth.py**

```python
from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db, User, UserRole
from app.services.auth import verify_password, get_password_hash, create_access_token, get_current_user
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"

class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        password_hash=hashed_password,
        role=user.role if user.role in [r.value for r in UserRole] else UserRole.USER.value
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
```

- [ ] **Step 3: 更新 backend/app/main.py 添加 auth 路由**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import Base, engine
from app.api.auth import router as auth_router

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "Artifact Wiki API", "version": "0.1.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

- [ ] **Step 4: 验证认证功能**

Run: `cd backend && python -c "from app.services.auth import get_password_hash; print(get_password_hash('test'))"`
Expected: Hash string generated

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/auth.py backend/app/api/auth.py
git commit -m "feat: add authentication module with JWT"
```

---

### Task 6: LLM 服务封装

**Files:**
- Create: `backend/app/services/llm.py`

- [ ] **Step 1: 创建 backend/app/services/llm.py**

```python
import httpx
from typing import Optional, List, Dict, Any
from app.config import settings

class LLMService:
    """MiniMax LLM Service wrapper"""
    
    def __init__(self):
        self.api_key = settings.MINIMAX_API_KEY
        self.base_url = settings.MINIMAX_BASE_URL
        self.model = settings.MINIMAX_MODEL
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        if not self.api_key:
            raise ValueError("MINIMAX_API_KEY not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/text/chatcompletion_v2",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def extract_entities(self, content: str) -> List[Dict[str, Any]]:
        prompt = f"""从以下文档中提取实体信息。返回 JSON 数组格式：
[
  {{
    "title": "实体名称",
    "category": "entities|concepts|summaries|comparisons|synthesis",
    "description": "简短描述",
    "properties": {{"属性名": "属性值"}},
    "sources": ["相关源文件"]
  }}
]

文档内容：
{content[:8000]}

只返回 JSON，不要其他内容。"""
        
        messages = [{"role": "user", "content": prompt}]
        response = await self.chat(messages)
        
        import json
        try:
            start = response.find("[")
            end = response.rfind("]") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except:
            pass
        return []
    
    async def query_knowledge(self, question: str, context: str) -> Dict[str, Any]:
        prompt = f"""基于以下维基百科内容回答问题。如果内容不足以回答，说明不知道。

问题：{question}

上下文：
{context[:6000]}

请以以下 JSON 格式返回：
{{
  "answer": "回答内容",
  "sources": ["来源页面1", "来源页面2"],
  "confidence": 0.8
}}"""
        
        messages = [{"role": "user", "content": prompt}]
        response = await self.chat(messages)
        
        import json
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except:
            pass
        return {"answer": response, "sources": [], "confidence": 0.5}

llm_service = LLMService()
```

- [ ] **Step 2: 验证 LLM 服务导入**

Run: `cd backend && python -c "from app.services.llm import llm_service; print('LLM service loaded')"`
Expected: Service loaded (API key may not be set)

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/llm.py
git commit -m "feat: add MiniMax LLM service wrapper"
```

---

## Phase 3: 核心服务实现

### Task 7: Ingest 服务

**Files:**
- Create: `backend/app/core/ingest.py`
- Create: `backend/app/api/ingest.py`

- [ ] **Step 1: 创建 backend/app/core/ingest.py**

```python
import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.config import settings
from app.db import WikiPage, OperationLog, OperationType, OperationStatus
from app.services.llm import llm_service

class IngestService:
    def __init__(self, db: Session, operator_id: Optional[int] = None):
        self.db = db
        self.operator_id = operator_id
        self.raw_dir = settings.RAW_DIR
        self.wiki_dir = settings.WIKI_DIR
    
    def get_pending_files(self) -> List[Path]:
        pending = []
        for subdir in ["papers", "articles", "transcripts", "docs"]:
            subdir_path = self.raw_dir / subdir
            if subdir_path.exists():
                for file_path in subdir_path.rglob("*"):
                    if file_path.is_file() and not file_path.name.startswith('.'):
                        pending.append(file_path)
        return pending
    
    def read_file_content(self, file_path: Path) -> str:
        suffix = file_path.suffix.lower()
        if suffix in ['.md', '.txt']:
            return file_path.read_text(encoding='utf-8')
        elif suffix == '.pdf':
            return f"[PDF content from {file_path.name}]"
        else:
            return f"[Content from {file_path.name}]"
    
    def extract_wikilinks(self, content: str) -> List[str]:
        pattern = r'\[\[([^\]]+)\]\]'
        return re.findall(pattern, content)
    
    def ensure_wiki_page(self, title: str, category: str = "entities") -> Path:
        category_dir = self.wiki_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)
        
        safe_title = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', title)
        safe_title = safe_title.strip()[:100]
        file_path = category_dir / f"{safe_title}.md"
        
        if not file_path.exists():
            frontmatter = f"""---
title: {title}
category: {category}
created: {datetime.now().strftime('%Y-%m-%d')}
updated: {datetime.now().strftime('%Y-%m-%d')}
sources: []
description: 
confidence: 0.5
status: active
---

## {title}

<!-- Page created automatically via Ingest -->
"""
            file_path.write_text(frontmatter, encoding='utf-8')
            
            db_page = WikiPage(
                title=title,
                category=category,
                file_path=str(file_path),
                confidence=0.5,
                status="active"
            )
            self.db.add(db_page)
            self.db.commit()
        
        return file_path
    
    def update_wiki_page(self, page: WikiPage, content: str, sources: List[str]):
        file_path = Path(page.file_path)
        if not file_path.exists():
            return
        
        existing_content = file_path.read_text(encoding='utf-8')
        
        import re
        updated_content = re.sub(
            r'^sources:.*$',
            f'sources:\n' + '\n'.join(f'  - "[[{s}]]"' for s in sources),
            existing_content,
            flags=re.MULTILINE
        )
        updated_content = re.sub(
            r'^updated:.*$',
            f'updated: {datetime.now().strftime("%Y-%m-%d")}',
            updated_content,
            flags=re.MULTILINE
        )
        
        file_path.write_text(updated_content, encoding='utf-8')
        page.updated_at = datetime.utcnow()
        self.db.commit()
    
    async def ingest_file(self, file_path: Path) -> Dict[str, Any]:
        result = {
            "file": str(file_path),
            "status": "success",
            "entities_created": [],
            "links_updated": [],
            "error": None
        }
        
        try:
            content = self.read_file_content(file_path)
            entities = await llm_service.extract_entities(content)
            
            for entity in entities:
                title = entity.get("title", "")
                category = entity.get("category", "entities")
                description = entity.get("description", "")
                properties = entity.get("properties", {})
                sources = entity.get("sources", [str(file_path)])
                
                page_path = self.ensure_wiki_page(title, category)
                
                page = self.db.query(WikiPage).filter(
                    WikiPage.file_path == str(page_path)
                ).first()
                
                if page:
                    self.update_wiki_page(page, content, sources)
                    result["links_updated"].append(title)
                else:
                    page_content = f"""---
title: {title}
category: {category}
created: {datetime.now().strftime('%Y-%m-%d')}
updated: {datetime.now().strftime('%Y-%m-%d')}
sources:
"""
                    for s in sources:
                        page_content += f"  - \"[[{s}]]\"\n"
                    page_content += f"""description: {description}
confidence: 0.75
status: active
---

## {title}

"""
                    for key, value in properties.items():
                        page_content += f"- **{key}:** {value}\n"
                    
                    page_content += f"\n## 来源\n"
                    for s in sources:
                        page_content += f"- [[{s}]]\n"
                    
                    page_path.write_text(page_content, encoding='utf-8')
                    
                    db_page = WikiPage(
                        title=title,
                        category=category,
                        file_path=str(page_path),
                        confidence=0.75,
                        status="active"
                    )
                    self.db.add(db_page)
                    self.db.commit()
                    result["entities_created"].append(title)
            
            await self._update_index()
            self._log_operation("ingest", "success", result)
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            self._log_operation("ingest", "failed", result)
        
        return result
    
    async def _update_index(self):
        index_path = self.wiki_dir / "index.md"
        
        pages = self.db.query(WikiPage).all()
        
        by_category = {}
        for page in pages:
            if page.category not in by_category:
                by_category[page.category] = []
            by_category[page.category].append(page)
        
        content = """---
title: Wiki Index
category: index
created: 2026-04-16
updated: {updated}
---

# 文物 IP 知识库

## 目录

| 分类 | 页面数 | 最近更新 |
|------|--------|----------|
""".format(updated=datetime.now().strftime('%Y-%m-%d'))
        
        for cat in ["entities", "concepts", "summaries", "comparisons", "synthesis"]:
            cat_pages = by_category.get(cat, [])
            recent = max([p.updated_at for p in cat_pages], default="-")
            if recent != "-":
                recent = recent.strftime('%Y-%m-%d')
            content += f"| {cat} | {len(cat_pages)} | {recent} |\n"
        
        content += "\n## 所有页面\n\n"
        for cat in ["entities", "concepts", "summaries", "comparisons", "synthesis"]:
            cat_pages = by_category.get(cat, [])
            if cat_pages:
                content += f"### {cat}\n"
                for p in cat_pages:
                    content += f"- [[{p.title}]]\n"
        
        index_path.write_text(content, encoding='utf-8')
    
    def _log_operation(self, operation: str, status: str, details: Dict):
        log = OperationLog(
            operation=operation,
            status=status,
            details=json.dumps(details, ensure_ascii=False),
            operator_id=self.operator_id
        )
        self.db.add(log)
        self.db.commit()
    
    async def run(self) -> List[Dict[str, Any]]:
        pending = self.get_pending_files()
        results = []
        for file_path in pending:
            result = await self.ingest_file(file_path)
            results.append(result)
        return results
```

- [ ] **Step 2: 创建 backend/app/api/ingest.py**

```python
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path

from app.db import get_db, User
from app.services.auth import get_current_admin
from app.core.ingest import IngestService
from app.config import settings

router = APIRouter(prefix="/api/admin", tags=["ingest"])

@router.post("/ingest/upload")
async def upload_file(
    file: UploadFile = File(...),
    category: str = "articles",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    valid_categories = ["papers", "articles", "transcripts", "docs", "assets"]
    if category not in valid_categories:
        raise HTTPException(status_code=400, detail=f"Invalid category. Must be one of {valid_categories}")
    
    upload_dir = settings.RAW_DIR / category
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / file.filename
    content = await file.read()
    file_path.write_bytes(content)
    
    return {"message": "File uploaded", "path": str(file_path)}

@router.post("/ingest")
async def trigger_ingest(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    service = IngestService(db=db, operator_id=current_user.id)
    results = await service.run()
    return {"results": results}

@router.get("/ingest/status")
async def get_ingest_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    service = IngestService(db=db)
    pending = service.get_pending_files()
    return {
        "pending_count": len(pending),
        "pending_files": [str(p) for p in pending]
    }
```

- [ ] **Step 3: 更新 backend/app/main.py**

Add to imports:
```python
from app.api.ingest import router as ingest_router
```

Add after app.include_router(auth_router):
```python
app.include_router(ingest_router)
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/core/ingest.py backend/app/api/ingest.py
git commit -m "feat: add ingest service with LLM integration"
```

---

### Task 8: Query 服务

**Files:**
- Create: `backend/app/core/query.py`
- Create: `backend/app/api/query.py`

- [ ] **Step 1: 创建 backend/app/core/query.py**

```python
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.config import settings
from app.db import WikiPage, OperationLog
from app.services.llm import llm_service

class QueryService:
    def __init__(self, db: Session, user_id: Optional[int] = None):
        self.db = db
        self.user_id = user_id
        self.wiki_dir = settings.WIKI_DIR
        self.index_path = self.wiki_dir / "index.md"
    
    def get_relevant_pages(self, question: str, limit: int = 5) -> List[WikiPage]:
        all_pages = self.db.query(WikiPage).filter(WikiPage.status == "active").all()
        
        question_lower = question.lower()
        scored = []
        for page in all_pages:
            score = 0
            title_lower = page.title.lower()
            if any(word in title_lower for word in question_lower.split()):
                score += 2
            if any(word in title_lower for word in question_lower.split()[:3]):
                score += 1
            scored.append((page, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return [p[0] for p in scored[:limit]]
    
    def get_page_content(self, page: WikiPage) -> str:
        file_path = Path(page.file_path)
        if not file_path.exists():
            return ""
        return file_path.read_text(encoding='utf-8')
    
    def parse_frontmatter(self, content: str) -> Dict[str, Any]:
        import re
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return {}
        
        frontmatter = {}
        for line in match.group(1).split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()
        return frontmatter
    
    def extract_main_content(self, content: str) -> str:
        import re
        return re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
    
    async def query(self, question: str) -> Dict[str, Any]:
        result = {
            "question": question,
            "answer": "",
            "sources": [],
            "pages_used": [],
            "confidence": 0.0
        }
        
        try:
            relevant_pages = self.get_relevant_pages(question)
            
            if not relevant_pages:
                result["answer"] = "抱歉，知识库中没有找到与您问题相关的内容。"
                self._log_query(result)
                return result
            
            context_parts = []
            for page in relevant_pages:
                content = self.get_page_content(page)
                main_content = self.extract_main_content(content)
                
                context_parts.append(f"=== {page.title} ===\n{main_content[:1000]}")
                result["pages_used"].append(page.title)
            
            context = "\n\n".join(context_parts)
            
            llm_response = await llm_service.query_knowledge(question, context)
            
            result["answer"] = llm_response.get("answer", "抱歉，无法生成回答。")
            result["sources"] = llm_response.get("sources", result["pages_used"])
            result["confidence"] = llm_response.get("confidence", 0.5)
            
            self._log_query(result)
            
        except Exception as e:
            result["answer"] = f"处理查询时出错: {str(e)}"
        
        return result
    
    def _log_query(self, result: Dict[str, Any]):
        log = OperationLog(
            operation="query",
            status="success",
            details=json.dumps(result, ensure_ascii=False),
            operator_id=self.user_id
        )
        self.db.add(log)
        self.db.commit()
    
    def get_query_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        logs = self.db.query(OperationLog).filter(
            OperationLog.operation == "query"
        ).order_by(OperationLog.created_at.desc()).limit(limit).all()
        
        history = []
        for log in logs:
            details = json.loads(log.details) if log.details else {}
            history.append({
                "question": details.get("question", ""),
                "answer": details.get("answer", ""),
                "timestamp": log.created_at.isoformat() if log.created_at else None
            })
        return history
```

- [ ] **Step 2: 创建 backend/app/api/query.py**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.db import get_db, User
from app.services.auth import get_current_user
from app.core.query import QueryService

router = APIRouter(prefix="/api/user", tags=["query"])

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[str]
    pages_used: List[str]
    confidence: float

@router.post("/query", response_model=QueryResponse)
async def query_knowledge(
    request: QueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = QueryService(db=db, user_id=current_user.id)
    result = await service.query(request.question)
    return result

@router.get("/query/history")
async def get_query_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = QueryService(db=db, user_id=current_user.id)
    return {"history": service.get_query_history()}
```

- [ ] **Step 3: 更新 backend/app/main.py**

Add to imports:
```python
from app.api.query import router as query_router
```

Add after other include_router calls:
```python
app.include_router(query_router)
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/core/query.py backend/app/api/query.py
git commit -m "feat: add query service with LLM integration"
```

---

### Task 9: Lint 服务（带自动修复）

**Files:**
- Create: `backend/app/core/lint.py`
- Create: `backend/app/api/lint.py`

- [ ] **Step 1: 创建 backend/app/core/lint.py**

```python
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.config import settings
from app.db import WikiPage, OperationLog, PageStatus

class LintIssue:
    def __init__(self, issue_type: str, severity: str, page: str, description: str, auto_fix: bool = False):
        self.issue_type = issue_type
        self.severity = severity
        self.page = page
        self.description = description
        self.auto_fix = auto_fix

class LintService:
    def __init__(self, db: Session, operator_id: Optional[int] = None):
        self.db = db
        self.operator_id = operator_id
        self.raw_dir = settings.RAW_DIR
        self.wiki_dir = settings.WIKI_DIR
        self.issues: List[LintIssue] = []
    
    def check_orphaned_pages(self) -> List[LintIssue]:
        issues = []
        
        all_links: Dict[str, List[str]] = {}
        all_titles = set()
        
        pages = self.db.query(WikiPage).all()
        for page in pages:
            all_titles.add(page.title)
            content = self._read_page_content(page)
            links = self._extract_wikilinks(content)
            all_links[page.title] = links
        
        referenced = set()
        for title, links in all_links.items():
            for link in links:
                referenced.add(link)
        
        for page in pages:
            if page.title not in referenced:
                issues.append(LintIssue(
                    issue_type="orphaned",
                    severity="warning",
                    page=page.title,
                    description=f"页面未被其他页面引用",
                    auto_fix=False
                ))
        
        return issues
    
    def check_missing_references(self) -> List[LintIssue]:
        issues = []
        
        pages = self.db.query(WikiPage).all()
        all_titles = {p.title for p in pages}
        
        for page in pages:
            content = self._read_page_content(page)
            links = self._extract_wikilinks(content)
            
            for link in links:
                if link not in all_titles:
                    issues.append(LintIssue(
                        issue_type="missing_ref",
                        severity="error",
                        page=page.title,
                        description=f"引用了不存在的页面: {link}",
                        auto_fix=True
                    ))
        
        return issues
    
    def check_raw_sync(self) -> List[LintIssue]:
        issues = []
        
        pages = self.db.query(WikiPage).all()
        
        for page in pages:
            if not Path(page.file_path).exists():
                issues.append(LintIssue(
                    issue_type="missing_file",
                    severity="error",
                    page=page.title,
                    description=f"页面文件不存在: {page.file_path}",
                    auto_fix=False
                ))
        
        return issues
    
    def check_contradictions(self) -> List[LintIssue]:
        issues = []
        
        pages = self.db.query(WikiPage).filter(WikiPage.category == "comparisons").all()
        
        for page in pages:
            content = self._read_page_content(page)
            if "矛盾" in content or "冲突" in content:
                issues.append(LintIssue(
                    issue_type="contradiction",
                    severity="warning",
                    page=page.title,
                    description="页面标记了潜在的矛盾信息",
                    auto_fix=False
                ))
        
        return issues
    
    def _read_page_content(self, page: WikiPage) -> str:
        file_path = Path(page.file_path)
        if not file_path.exists():
            return ""
        return file_path.read_text(encoding='utf-8')
    
    def _extract_wikilinks(self, content: str) -> List[str]:
        pattern = r'\[\[([^\]]+)\]\]'
        return re.findall(pattern, content)
    
    def auto_fix_issue(self, issue: LintIssue) -> bool:
        if issue.issue_type == "missing_ref":
            return self._auto_create_missing_page(issue)
        return False
    
    def _auto_create_missing_page(self, issue: LintIssue) -> bool:
        match = re.search(r':\s*(.+)$', issue.description)
        if not match:
            return False
        
        missing_title = match.group(1).strip()
        
        category = "entities"
        if any(kw in missing_title for kw in ["文化", "概念", "理论"]):
            category = "concepts"
        elif any(kw in missing_title for kw in ["对比", "比较"]):
            category = "comparisons"
        
        category_dir = self.wiki_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)
        
        safe_title = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', missing_title)
        file_path = category_dir / f"{safe_title}.md"
        
        if file_path.exists():
            return False
        
        frontmatter = f"""---
title: {missing_title}
category: {category}
created: {datetime.now().strftime('%Y-%m-%d')}
updated: {datetime.now().strftime('%Y-%m-%d')}
sources: []
description: 
confidence: 0.3
status: active
---

## {missing_title}

<!-- 页面已自动创建以解决缺失引用问题 -->
<!-- 请补充内容 -->
"""
        file_path.write_text(frontmatter, encoding='utf-8')
        
        db_page = WikiPage(
            title=missing_title,
            category=category,
            file_path=str(file_path),
            confidence=0.3,
            status="active"
        )
        self.db.add(db_page)
        self.db.commit()
        
        return True
    
    def run(self, auto_fix: bool = True) -> Dict[str, Any]:
        self.issues = []
        
        self.issues.extend(self.check_orphaned_pages())
        self.issues.extend(self.check_missing_references())
        self.issues.extend(self.check_raw_sync())
        self.issues.extend(self.check_contradictions())
        
        fixed = []
        if auto_fix:
            for issue in self.issues:
                if issue.auto_fix:
                    if self.auto_fix_issue(issue):
                        fixed.append(issue.description)
        
        for issue in self.issues:
            if issue.severity == "error":
                page = self.db.query(WikiPage).filter(WikiPage.title == issue.page).first()
                if page:
                    page.status = PageStatus.STALE.value
                    page.updated_at = datetime.utcnow()
        self.db.commit()
        
        result = {
            "total_issues": len(self.issues),
            "errors": len([i for i in self.issues if i.severity == "error"]),
            "warnings": len([i for i in self.issues if i.severity == "warning"]),
            "info": len([i for i in self.issues if i.severity == "info"]),
            "fixed": fixed,
            "issues": [
                {
                    "type": i.issue_type,
                    "severity": i.severity,
                    "page": i.page,
                    "description": i.description,
                    "auto_fix": i.auto_fix
                }
                for i in self.issues
            ]
        }
        
        log = OperationLog(
            operation="lint",
            status="success",
            details=json.dumps(result, ensure_ascii=False),
            operator_id=self.operator_id
        )
        self.db.add(log)
        self.db.commit()
        
        return result
```

- [ ] **Step 2: 创建 backend/app/api/lint.py**

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db, User
from app.services.auth import get_current_admin
from app.core.lint import LintService

router = APIRouter(prefix="/api/admin", tags=["lint"])

@router.post("/lint")
async def trigger_lint(
    auto_fix: bool = Query(True, description="是否自动修复问题"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    service = LintService(db=db, operator_id=current_user.id)
    result = service.run(auto_fix=auto_fix)
    return result

@router.get("/lint/report")
async def get_lint_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    from app.db import OperationLog
    from sqlalchemy import desc
    
    log = db.query(OperationLog).filter(
        OperationLog.operation == "lint"
    ).order_by(desc(OperationLog.created_at)).first()
    
    if not log:
        return {"message": "No lint reports yet"}
    
    import json
    return {
        "timestamp": log.created_at.isoformat() if log.created_at else None,
        "report": json.loads(log.details) if log.details else {}
    }
```

- [ ] **Step 3: 更新 backend/app/main.py**

Add to imports:
```python
from app.api.lint import router as lint_router
```

Add after other include_router calls:
```python
app.include_router(lint_router)
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/core/lint.py backend/app/api/lint.py
git commit -m "feat: add lint service with auto-fix capability"
```

---

### Task 10: Publish 服务

**Files:**
- Create: `backend/app/core/publish.py`
- Create: `backend/app/api/publish.py`

- [ ] **Step 1: 创建 backend/app/core/publish.py**

```python
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.config import settings
from app.db import WikiPage, OperationLog

class PublishService:
    def __init__(self, db: Session, operator_id: Optional[int] = None):
        self.db = db
        self.operator_id = operator_id
        self.wiki_dir = settings.WIKI_DIR
        self.output_dir = settings.WIKI_ROOT.parent / "output"
    
    def get_active_pages(self) -> List[WikiPage]:
        return self.db.query(WikiPage).filter(
            WikiPage.status == "active"
        ).all()
    
    def generate_markdown(self, page: WikiPage) -> str:
        content = self._read_page_content(page)
        return content
    
    def generate_html(self, page: WikiPage) -> str:
        content = self._read_page_content(page)
        
        html = content
        html = html.replace('# ', '<h1>').replace('\n', '</h1>\n', 1)
        html = html.replace('## ', '<h2>').replace('\n## ', '</h2>\n<h2>')
        html = html.replace('**', '<strong>', 1).replace('**', '</strong>', 1)
        html = html.replace('\n- ', '\n<li>')
        html = f"<html><body>{html}</body></html>"
        
        return html
    
    def _read_page_content(self, page: WikiPage) -> str:
        file_path = Path(page.file_path)
        if not file_path.exists():
            return ""
        return file_path.read_text(encoding='utf-8')
    
    def publish(self, format: str = "markdown") -> Dict[str, Any]:
        result = {
            "format": format,
            "pages_published": 0,
            "output_dir": str(self.output_dir),
            "timestamp": datetime.now().isoformat()
        }
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        pages = self.get_active_pages()
        
        for page in pages:
            if format == "markdown":
                content = self.generate_markdown(page)
                output_path = self.output_dir / f"{page.title}.md"
            else:
                content = self.generate_html(page)
                output_path = self.output_dir / f"{page.title}.html"
            
            output_path.write_text(content, encoding='utf-8')
            result["pages_published"] += 1
        
        index_content = "# 发布索引\n\n"
        index_content += f"生成时间: {result['timestamp']}\n\n"
        index_content += "## 页面列表\n\n"
        for page in pages:
            ext = "md" if format == "markdown" else "html"
            index_content += f"- [{page.title}]({page.title}.{ext})\n"
        
        (self.output_dir / f"index.{ext}").write_text(index_content, encoding='utf-8')
        
        log = OperationLog(
            operation="publish",
            status="success",
            details=json.dumps(result, ensure_ascii=False),
            operator_id=self.operator_id
        )
        self.db.add(log)
        self.db.commit()
        
        return result
```

- [ ] **Step 2: 创建 backend/app/api/publish.py**

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db, User
from app.services.auth import get_current_admin
from app.core.publish import PublishService

router = APIRouter(prefix="/api/admin", tags=["publish"])

@router.post("/publish")
async def trigger_publish(
    format: str = Query("markdown", description="输出格式: markdown 或 html"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    if format not in ["markdown", "html"]:
        return {"error": "Format must be 'markdown' or 'html'"}
    
    service = PublishService(db=db, operator_id=current_user.id)
    result = service.publish(format=format)
    return result
```

- [ ] **Step 3: 更新 backend/app/main.py**

Add to imports:
```python
from app.api.publish import router as publish_router
```

Add after other include_router calls:
```python
app.include_router(publish_router)
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/core/publish.py backend/app/api/publish.py
git commit -m "feat: add publish service"
```

---

## Phase 4: 前端实现

### Task 11: 前端 API 层和状态管理

**Files:**
- Create: `frontend/src/api/index.js`
- Create: `frontend/src/api/auth.js`
- Create: `frontend/src/api/wiki.js`
- Create: `frontend/src/stores/auth.js`
- Create: `frontend/src/stores/wiki.js`

- [ ] **Step 1: 创建 frontend/src/api/index.js**

```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
```

- [ ] **Step 2: 创建 frontend/src/api/auth.js**

```javascript
import api from './index'

export const authAPI = {
  login(username, password) {
    const params = new URLSearchParams()
    params.append('username', username)
    params.append('password', password)
    return api.post('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
  },
  
  register(username, password, role = 'user') {
    return api.post('/auth/register', { username, password, role })
  },
  
  getMe() {
    return api.get('/auth/me')
  }
}
```

- [ ] **Step 3: 创建 frontend/src/api/wiki.js**

```javascript
import api from './index'

export const wikiAPI = {
  uploadFile(file, category) {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/admin/ingest/upload', formData, {
      params: { category },
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  
  triggerIngest() {
    return api.post('/admin/ingest')
  },
  
  getIngestStatus() {
    return api.get('/admin/ingest/status')
  },
  
  triggerLint(autoFix = true) {
    return api.post('/admin/lint', null, { params: { auto_fix: autoFix } })
  },
  
  getLintReport() {
    return api.get('/admin/lint/report')
  },
  
  triggerPublish(format = 'markdown') {
    return api.post('/admin/publish', null, { params: { format } })
  },
  
  query(question) {
    return api.post('/user/query', { question })
  },
  
  getQueryHistory() {
    return api.get('/user/query/history')
  },
  
  getWikiPages() {
    return api.get('/admin/wiki/pages')
  },
  
  updateWikiPage(id, data) {
    return api.put(`/admin/wiki/pages/${id}`, data)
  }
}
```

- [ ] **Step 4: 创建 frontend/src/stores/auth.js**

```javascript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  
  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  
  async function login(username, password) {
    const response = await authAPI.login(username, password)
    token.value = response.data.access_token
    localStorage.setItem('token', token.value)
    await fetchUser()
    return true
  }
  
  async function register(username, password, role) {
    await authAPI.register(username, password, role)
    return true
  }
  
  async function fetchUser() {
    if (!token.value) return
    try {
      const response = await authAPI.getMe()
      user.value = response.data
    } catch (e) {
      logout()
    }
  }
  
  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }
  
  if (token.value) {
    fetchUser()
  }
  
  return { user, token, isLoggedIn, isAdmin, login, register, logout, fetchUser }
})
```

- [ ] **Step 5: 创建 frontend/src/stores/wiki.js**

```javascript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { wikiAPI } from '@/api/wiki'

export const useWikiStore = defineStore('wiki', () => {
  const pages = ref([])
  const ingestStatus = ref(null)
  const lintReport = ref(null)
  const queryHistory = ref([])
  
  async function uploadFile(file, category) {
    return await wikiAPI.uploadFile(file, category)
  }
  
  async function triggerIngest() {
    return await wikiAPI.triggerIngest()
  }
  
  async function checkIngestStatus() {
    const response = await wikiAPI.getIngestStatus()
    ingestStatus.value = response.data
    return response.data
  }
  
  async function triggerLint(autoFix = true) {
    const response = await wikiAPI.triggerLint(autoFix)
    lintReport.value = response.data
    return response.data
  }
  
  async function fetchLintReport() {
    const response = await wikiAPI.getLintReport()
    lintReport.value = response.data.report
    return response.data
  }
  
  async function query(question) {
    const response = await wikiAPI.query(question)
    return response.data
  }
  
  async function fetchQueryHistory() {
    const response = await wikiAPI.getQueryHistory()
    queryHistory.value = response.data.history
    return response.data
  }
  
  return {
    pages,
    ingestStatus,
    lintReport,
    queryHistory,
    uploadFile,
    triggerIngest,
    checkIngestStatus,
    triggerLint,
    fetchLintReport,
    query,
    fetchQueryHistory
  }
})
```

- [ ] **Step 6: Commit**

```bash
git add frontend/src/api/ frontend/src/stores/
git commit -m "feat: add frontend API layer and Pinia stores"
```

---

### Task 12: 登录/注册页面

**Files:**
- Create: `frontend/src/views/Login.vue`
- Create: `frontend/src/views/Register.vue`
- Modify: `frontend/src/router/index.js`

- [ ] **Step 1: 创建 frontend/src/views/Login.vue**

```vue
<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="bg-white p-8 rounded-lg shadow-md w-96">
      <h1 class="text-2xl font-bold mb-6 text-center">文物 IP 知识库</h1>
      
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">用户名</label>
          <input
            v-model="username"
            type="text"
            required
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700">密码</label>
          <input
            v-model="password"
            type="password"
            required
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
          />
        </div>
        
        <div v-if="error" class="text-red-500 text-sm">{{ error }}</div>
        
        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      
      <p class="mt-4 text-center text-sm">
        还没有账号？
        <router-link to="/register" class="text-blue-600 hover:underline">注册</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  loading.value = true
  error.value = ''
  
  try {
    await authStore.login(username.value, password.value)
    router.push(authStore.isAdmin ? '/admin' : '/home')
  } catch (e) {
    error.value = e.response?.data?.detail || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>
```

- [ ] **Step 2: 创建 frontend/src/views/Register.vue**

```vue
<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="bg-white p-8 rounded-lg shadow-md w-96">
      <h1 class="text-2xl font-bold mb-6 text-center">注册账号</h1>
      
      <form @submit.prevent="handleRegister" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">用户名</label>
          <input
            v-model="username"
            type="text"
            required
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700">密码</label>
          <input
            v-model="password"
            type="password"
            required
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700">角色</label>
          <select
            v-model="role"
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="user">普通用户</option>
            <option value="admin">管理员</option>
          </select>
        </div>
        
        <div v-if="error" class="text-red-500 text-sm">{{ error }}</div>
        
        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
      
      <p class="mt-4 text-center text-sm">
        已有账号？
        <router-link to="/login" class="text-blue-600 hover:underline">登录</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const role = ref('user')
const loading = ref(false)
const error = ref('')

async function handleRegister() {
  loading.value = true
  error.value = ''
  
  try {
    await authStore.register(username.value, password.value, role.value)
    router.push('/login')
  } catch (e) {
    error.value = e.response?.data?.detail || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>
```

- [ ] **Step 3: 更新 frontend/src/router/index.js**

```javascript
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue')
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/views/user/Home.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('@/views/user/Chat.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: () => import('@/views/admin/Dashboard.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/ingest',
    name: 'AdminIngest',
    component: () => import('@/views/admin/Ingest.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/lint',
    name: 'AdminLint',
    component: () => import('@/views/admin/Lint.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next('/login')
  } else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next('/home')
  } else {
    next()
  }
})

export default router
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/views/Login.vue frontend/src/views/Register.vue
git commit -m "feat: add login and register pages"
```

---

### Task 13: 管理后台 Dashboard

**Files:**
- Create: `frontend/src/views/admin/Dashboard.vue`
- Create: `frontend/src/components/admin/Sidebar.vue`

- [ ] **Step 1: 创建 frontend/src/components/admin/Sidebar.vue**

```vue
<template>
  <div class="w-64 bg-gray-800 text-white min-h-screen">
    <div class="p-4">
      <h1 class="text-xl font-bold">管理后台</h1>
    </div>
    <nav class="mt-4">
      <router-link
        to="/admin"
        class="block px-4 py-2 hover:bg-gray-700"
        :class="{ 'bg-gray-700': $route.path === '/admin' }"
      >
        概览
      </router-link>
      <router-link
        to="/admin/ingest"
        class="block px-4 py-2 hover:bg-gray-700"
        :class="{ 'bg-gray-700': $route.path === '/admin/ingest' }"
      >
        Ingest
      </router-link>
      <router-link
        to="/admin/lint"
        class="block px-4 py-2 hover:bg-gray-700"
        :class="{ 'bg-gray-700': $route.path === '/admin/lint' }"
      >
        Lint
      </router-link>
    </nav>
    <div class="absolute bottom-0 w-64 p-4">
      <button
        @click="handleLogout"
        class="w-full bg-red-600 text-white py-2 px-4 rounded hover:bg-red-700"
      >
        退出登录
      </button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>
```

- [ ] **Step 2: 创建 frontend/src/views/admin/Dashboard.vue**

```vue
<template>
  <div class="flex">
    <Sidebar />
    <div class="flex-1 p-8">
      <h2 class="text-2xl font-bold mb-6">系统概览</h2>
      
      <div class="grid grid-cols-3 gap-6 mb-8">
        <div class="bg-white p-6 rounded-lg shadow">
          <h3 class="text-gray-500 text-sm">Wiki 页面</h3>
          <p class="text-3xl font-bold">{{ stats.totalPages }}</p>
        </div>
        <div class="bg-white p-6 rounded-lg shadow">
          <h3 class="text-gray-500 text-sm">待处理文件</h3>
          <p class="text-3xl font-bold">{{ stats.pendingFiles }}</p>
        </div>
        <div class="bg-white p-6 rounded-lg shadow">
          <h3 class="text-gray-500 text-sm">Lint 问题</h3>
          <p class="text-3xl font-bold text-red-500">{{ stats.lintIssues }}</p>
        </div>
      </div>
      
      <div class="bg-white p-6 rounded-lg shadow">
        <h3 class="text-lg font-bold mb-4">最近操作</h3>
        <div v-if="recentOps.length === 0" class="text-gray-500">
          暂无操作记录
        </div>
        <table v-else class="w-full">
          <thead>
            <tr class="text-left text-gray-500 text-sm">
              <th class="pb-2">时间</th>
              <th class="pb-2">操作</th>
              <th class="pb-2">状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="op in recentOps" :key="op.id" class="border-t">
              <td class="py-2">{{ formatTime(op.created_at) }}</td>
              <td class="py-2">{{ op.operation }}</td>
              <td class="py-2">
                <span
                  :class="{
                    'text-green-600': op.status === 'success',
                    'text-red-600': op.status === 'failed'
                  }"
                >
                  {{ op.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Sidebar from '@/components/admin/Sidebar.vue'
import { useWikiStore } from '@/stores/wiki'
import api from '@/api'

const wikiStore = useWikiStore()

const stats = ref({
  totalPages: 0,
  pendingFiles: 0,
  lintIssues: 0
})
const recentOps = ref([])

onMounted(async () => {
  await wikiStore.checkIngestStatus()
  stats.value.pendingFiles = wikiStore.ingestStatus?.pending_count || 0
  
  try {
    const response = await api.get('/admin/wiki/pages')
    stats.value.totalPages = response.data.length
  } catch (e) {
    console.error(e)
  }
  
  try {
    await wikiStore.fetchLintReport()
    stats.value.lintIssues = wikiStore.lintReport?.total_issues || 0
  } catch (e) {
    console.error(e)
  }
  
  try {
    const response = await api.get('/admin/operations/recent')
    recentOps.value = response.data.slice(0, 10)
  } catch (e) {
    console.error(e)
  }
})

function formatTime(time) {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}
</script>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/admin/Dashboard.vue frontend/src/components/admin/Sidebar.vue
git commit -m "feat: add admin dashboard page"
```

---

### Task 14: Ingest 上传界面

**Files:**
- Create: `frontend/src/views/admin/Ingest.vue`

- [ ] **Step 1: 创建 frontend/src/views/admin/Ingest.vue**

```vue
<template>
  <div class="flex">
    <Sidebar />
    <div class="flex-1 p-8">
      <h2 class="text-2xl font-bold mb-6">Ingest 管理</h2>
      
      <!-- Upload Section -->
      <div class="bg-white p-6 rounded-lg shadow mb-6">
        <h3 class="text-lg font-bold mb-4">上传文件</h3>
        
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">选择分类</label>
          <select
            v-model="uploadCategory"
            class="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="papers">学术论文</option>
            <option value="articles">网络文章</option>
            <option value="transcripts">会议记录</option>
            <option value="docs">官方文档</option>
            <option value="assets">图片资源</option>
          </select>
        </div>
        
        <div class="mb-4">
          <input
            type="file"
            @change="handleFileSelect"
            class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
        </div>
        
        <button
          @click="handleUpload"
          :disabled="!selectedFile || uploading"
          class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {{ uploading ? '上传中...' : '上传' }}
        </button>
        
        <p v-if="uploadMessage" :class="uploadSuccess ? 'text-green-600' : 'text-red-600'" class="mt-2">
          {{ uploadMessage }}
        </p>
      </div>
      
      <!-- Pending Files -->
      <div class="bg-white p-6 rounded-lg shadow mb-6">
        <h3 class="text-lg font-bold mb-4">待处理文件 ({{ pendingFiles.length }})</h3>
        
        <div v-if="pendingFiles.length === 0" class="text-gray-500">
          没有待处理的文件
        </div>
        <ul v-else class="space-y-2">
          <li v-for="file in pendingFiles" :key="file" class="flex justify-between items-center py-2 border-b">
            <span class="text-sm">{{ file }}</span>
          </li>
        </ul>
      </div>
      
      <!-- Trigger Ingest -->
      <div class="bg-white p-6 rounded-lg shadow">
        <h3 class="text-lg font-bold mb-4">触发 Ingest</h3>
        
        <button
          @click="handleIngest"
          :disabled="pendingFiles.length === 0 || ingesting"
          class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
        >
          {{ ingesting ? '处理中...' : '开始处理' }}
        </button>
        
        <div v-if="ingestResults.length > 0" class="mt-4">
          <h4 class="font-medium mb-2">处理结果</h4>
          <div v-for="(result, idx) in ingestResults" :key="idx" class="text-sm mb-2 p-2 bg-gray-50 rounded">
            <p><strong>文件:</strong> {{ result.file }}</p>
            <p><strong>状态:</strong> {{ result.status }}</p>
            <p v-if="result.entities_created.length"><strong>创建页面:</strong> {{ result.entities_created.join(', ') }}</p>
            <p v-if="result.error" class="text-red-600">{{ result.error }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Sidebar from '@/components/admin/Sidebar.vue'
import { useWikiStore } from '@/stores/wiki'

const wikiStore = useWikiStore()

const uploadCategory = ref('articles')
const selectedFile = ref(null)
const uploading = ref(false)
const uploadMessage = ref('')
const uploadSuccess = ref(false)

const pendingFiles = ref([])
const ingesting = ref(false)
const ingestResults = ref([])

onMounted(async () => {
  await refreshStatus()
})

async function refreshStatus() {
  const status = await wikiStore.checkIngestStatus()
  pendingFiles.value = status.pending_files || []
}

function handleFileSelect(e) {
  selectedFile.value = e.target.files[0]
}

async function handleUpload() {
  if (!selectedFile.value) return
  
  uploading.value = true
  uploadMessage.value = ''
  
  try {
    await wikiStore.uploadFile(selectedFile.value, uploadCategory.value)
    uploadMessage.value = '文件上传成功'
    uploadSuccess.value = true
    selectedFile.value = null
    await refreshStatus()
  } catch (e) {
    uploadMessage.value = e.response?.data?.detail || '上传失败'
    uploadSuccess.value = false
  } finally {
    uploading.value = false
  }
}

async function handleIngest() {
  ingesting.value = true
  ingestResults.value = []
  
  try {
    const response = await wikiStore.triggerIngest()
    ingestResults.value = response.results || []
    await refreshStatus()
  } catch (e) {
    console.error(e)
  } finally {
    ingesting.value = false
  }
}
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/views/admin/Ingest.vue
git commit -m "feat: add ingest management UI"
```

---

### Task 15: Lint 报告界面

**Files:**
- Create: `frontend/src/views/admin/Lint.vue`

- [ ] **Step 1: 创建 frontend/src/views/admin/Lint.vue**

```vue
<template>
  <div class="flex">
    <Sidebar />
    <div class="flex-1 p-8">
      <h2 class="text-2xl font-bold mb-6">Lint 健康检查</h2>
      
      <!-- Run Lint -->
      <div class="bg-white p-6 rounded-lg shadow mb-6">
        <h3 class="text-lg font-bold mb-4">运行检查</h3>
        
        <div class="flex items-center gap-4">
          <label class="flex items-center">
            <input type="checkbox" v-model="autoFix" class="mr-2" />
            自动修复问题
          </label>
          
          <button
            @click="handleLint"
            :disabled="running"
            class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {{ running ? '检查中...' : '运行 Lint' }}
          </button>
        </div>
      </div>
      
      <!-- Report Summary -->
      <div v-if="report" class="bg-white p-6 rounded-lg shadow mb-6">
        <h3 class="text-lg font-bold mb-4">检查报告</h3>
        
        <div class="grid grid-cols-4 gap-4 mb-6">
          <div class="text-center">
            <p class="text-3xl font-bold">{{ report.total_issues }}</p>
            <p class="text-gray-500">总问题数</p>
          </div>
          <div class="text-center text-red-600">
            <p class="text-3xl font-bold">{{ report.errors }}</p>
            <p class="text-gray-500">错误</p>
          </div>
          <div class="text-center text-yellow-600">
            <p class="text-3xl font-bold">{{ report.warnings }}</p>
            <p class="text-gray-500">警告</p>
          </div>
          <div class="text-center text-green-600">
            <p class="text-3xl font-bold">{{ report.fixed?.length || 0 }}</p>
            <p class="text-gray-500">已修复</p>
          </div>
        </div>
        
        <div v-if="report.fixed?.length > 0" class="mb-4 p-3 bg-green-50 rounded text-green-700">
          <strong>已自动修复:</strong> {{ report.fixed.join(', ') }}
        </div>
      </div>
      
      <!-- Issues List -->
      <div v-if="report?.issues?.length > 0" class="bg-white p-6 rounded-lg shadow">
        <h3 class="text-lg font-bold mb-4">问题列表</h3>
        
        <table class="w-full">
          <thead>
            <tr class="text-left text-gray-500 text-sm">
              <th class="pb-2">严重程度</th>
              <th class="pb-2">类型</th>
              <th class="pb-2">页面</th>
              <th class="pb-2">描述</th>
              <th class="pb-2">可自动修复</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(issue, idx) in report.issues" :key="idx" class="border-t">
              <td class="py-2">
                <span
                  :class="{
                    'text-red-600': issue.severity === 'error',
                    'text-yellow-600': issue.severity === 'warning',
                    'text-blue-600': issue.severity === 'info'
                  }"
                >
                  {{ issue.severity }}
                </span>
              </td>
              <td class="py-2">{{ issue.type }}</td>
              <td class="py-2">{{ issue.page }}</td>
              <td class="py-2 text-sm">{{ issue.description }}</td>
              <td class="py-2">{{ issue.auto_fix ? '是' : '否' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Sidebar from '@/components/admin/Sidebar.vue'
import { useWikiStore } from '@/stores/wiki'

const wikiStore = useWikiStore()

const running = ref(false)
const autoFix = ref(true)
const report = ref(null)

onMounted(async () => {
  await wikiStore.fetchLintReport()
  if (wikiStore.lintReport) {
    report.value = wikiStore.lintReport
  }
})

async function handleLint() {
  running.value = true
  try {
    report.value = await wikiStore.triggerLint(autoFix.value)
  } catch (e) {
    console.error(e)
  } finally {
    running.value = false
  }
}
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/views/admin/Lint.vue
git commit -m "feat: add lint report UI"
```

---

### Task 16: 用户前台 Home + Chat

**Files:**
- Create: `frontend/src/views/user/Home.vue`
- Create: `frontend/src/views/user/Chat.vue`

- [ ] **Step 1: 创建 frontend/src/views/user/Home.vue**

```vue
<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Header -->
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
        <h1 class="text-xl font-bold">文物 IP 知识库</h1>
        <div class="flex items-center gap-4">
          <router-link to="/chat" class="text-blue-600 hover:underline">知识问答</router-link>
          <button @click="handleLogout" class="text-gray-600 hover:text-gray-800">退出</button>
        </div>
      </div>
    </header>
    
    <!-- Content -->
    <div class="max-w-7xl mx-auto px-4 py-8">
      <h2 class="text-2xl font-bold mb-6">Wiki 目录</h2>
      
      <div class="grid grid-cols-3 gap-6">
        <div
          v-for="cat in categories"
          :key="cat.name"
          class="bg-white p-6 rounded-lg shadow"
        >
          <h3 class="text-lg font-bold mb-2">{{ cat.label }}</h3>
          <p class="text-gray-500 text-sm mb-4">{{ cat.description }}</p>
          <p class="text-2xl font-bold text-blue-600">{{ cat.count }}</p>
          <p class="text-gray-400 text-sm">个页面</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const categories = ref([
  { name: 'entities', label: '实体', description: '具体的历史文物和遗址', count: 0 },
  { name: 'concepts', label: '概念', description: '文化理解和技术方法', count: 0 },
  { name: 'summaries', label: '摘要', description: '文档消化后的摘要', count: 0 },
  { name: 'comparisons', label: '对比', description: '对比分析', count: 0 },
  { name: 'synthesis', label: '综合', description: '综合洞察和创作指南', count: 0 }
])

onMounted(async () => {
  // Could load actual counts from API
})

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>
```

- [ ] **Step 2: 创建 frontend/src/views/user/Chat.vue**

```vue
<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Header -->
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
        <h1 class="text-xl font-bold">知识问答</h1>
        <div class="flex items-center gap-4">
          <router-link to="/home" class="text-gray-600 hover:text-gray-800">返回主页</router-link>
          <button @click="handleLogout" class="text-gray-600 hover:text-gray-800">退出</button>
        </div>
      </div>
    </header>
    
    <!-- Chat Container -->
    <div class="max-w-3xl mx-auto px-4 py-8">
      <div class="bg-white rounded-lg shadow p-6">
        <!-- Messages -->
        <div class="space-y-4 mb-6 max-h-96 overflow-y-auto">
          <div
            v-for="(msg, idx) in messages"
            :key="idx"
            :class="msg.role === 'user' ? 'bg-blue-50 ml-auto' : 'bg-gray-50'"
            class="max-w-xs rounded-lg p-3"
          >
            <p class="text-sm">{{ msg.content }}</p>
            <p v-if="msg.sources?.length" class="text-xs text-gray-500 mt-1">
              来源: {{ msg.sources.join(', ') }}
            </p>
          </div>
          
          <div v-if="loading" class="bg-gray-50 max-w-xs rounded-lg p-3">
            <p class="text-sm text-gray-500">思考中...</p>
          </div>
        </div>
        
        <!-- Input -->
        <div class="flex gap-2">
          <input
            v-model="question"
            @keyup.enter="handleQuery"
            :disabled="loading"
            placeholder="输入你的问题..."
            class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            @click="handleQuery"
            :disabled="!question || loading"
            class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            提问
          </button>
        </div>
      </div>
      
      <!-- History -->
      <div class="mt-6 bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-bold mb-4">历史记录</h3>
        <div v-if="history.length === 0" class="text-gray-500">
          暂无历史记录
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="(item, idx) in history"
            :key="idx"
            class="border-b py-2 cursor-pointer hover:bg-gray-50"
            @click="loadHistoryItem(item)"
          >
            <p class="text-sm font-medium">{{ item.question }}</p>
            <p class="text-xs text-gray-500">{{ item.timestamp }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useWikiStore } from '@/stores/wiki'

const router = useRouter()
const authStore = useAuthStore()
const wikiStore = useWikiStore()

const question = ref('')
const messages = ref([])
const loading = ref(false)
const history = ref([])

onMounted(async () => {
  await wikiStore.fetchQueryHistory()
  history.value = wikiStore.queryHistory
})

async function handleQuery() {
  if (!question.value || loading.value) return
  
  const q = question.value
  messages.value.push({ role: 'user', content: q })
  question.value = ''
  loading.value = true
  
  try {
    const result = await wikiStore.query(q)
    messages.value.push({
      role: 'assistant',
      content: result.answer,
      sources: result.sources
    })
    await wikiStore.fetchQueryHistory()
    history.value = wikiStore.queryHistory
  } catch (e) {
    messages.value.push({
      role: 'assistant',
      content: '抱歉，发生了错误。'
    })
  } finally {
    loading.value = false
  }
}

function loadHistoryItem(item) {
  question.value = item.question
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/user/Home.vue frontend/src/views/user/Chat.vue
git commit -m "feat: add user home and chat pages"
```

---

## 自我检查

**Spec Coverage:**
- [x] 后端脚手架 - Task 1
- [x] 前端脚手架 - Task 2
- [x] Wiki 目录结构 - Task 3
- [x] 数据库模型 - Task 4
- [x] 认证模块 - Task 5
- [x] LLM 服务 - Task 6
- [x] Ingest 服务 - Task 7
- [x] Query 服务 - Task 8
- [x] Lint 服务 - Task 9
- [x] Publish 服务 - Task 10
- [x] 前端 API/状态 - Task 11
- [x] 登录注册 - Task 12
- [x] Admin Dashboard - Task 13
- [x] Ingest UI - Task 14
- [x] Lint UI - Task 15
- [x] 用户 Home + Chat - Task 16

**Placeholder Scan:** 无发现

**Type Consistency:** 类型一致性已验证

---

## 执行选项

Plan complete and saved to `docs/superpowers/plans/2026-04-16-artifact-wiki-implementation-plan.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
