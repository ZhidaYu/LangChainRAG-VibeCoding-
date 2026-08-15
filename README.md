# 电商RAG企业级知识库问答系统

> 毕业设计项目 — 基于 LangChain + FastAPI + React 的企业级 RAG 知识库问答系统
>
> 面向电商商品场景：用户通过浏览器提问，系统检索知识库内容并流式回答，答案附引用来源片段。

## 技术栈

| 层级 | 技术 |
|------|------|
| 大模型 | 阿里云百炼 Qwen-Plus（OpenAI 兼容 API） |
| 嵌入模型 | 阿里云百炼 text-embedding-v3 |
| RAG 框架 | LangChain + LangChain-Community |
| 后端框架 | FastAPI (Python 3.11) + Uvicorn |
| 前端框架 | React 18 + TypeScript + Vite |
| UI 组件库 | Ant Design 5 |
| 状态管理 | Zustand |
| 向量数据库 | ChromaDB |
| 关系数据库 | SQLite (SQLAlchemy 2.0) + WAL 并发加固 |
| 认证 | JWT (python-jose) + bcrypt (passlib) |
| 压力测试 | Locust |

## 功能特性

- ✅ 浏览器知识库管理（上传/删除/统计，仅管理员）
- ✅ 知识库问答 + SSE 流式输出 + 引用来源卡片展示
- ✅ 多用户多会话管理（每用户独立会话）
- ✅ 历史对话持久化（跨登录找回）
- ✅ 用户注册登录 + 修改密码
- ✅ 管理员/普通用户角色隔离（RBAC）
- ✅ LRU 语义缓存（重复问题秒回）
- ✅ 中文优化分块策略
- ✅ 多格式文档支持（PDF/DOCX/TXT/MD/CSV/XLSX）
- ✅ 异步检索（asyncio.to_thread + 信号量限流，不阻塞事件循环）
- ✅ SQLite WAL 模式（高并发读写加固）
- ✅ 100 人并发压力测试（Locust，0 错误率）

## 快速开始

### 前置要求

- Python 3.11+
- Node.js 18+
- 阿里云百炼 API Key（[免费申请](https://bailian.console.aliyun.com/)）

### 1. 配置环境

```bash
cd backend
copy .env.example .env
# 编辑 .env，填入你的 DASHSCOPE_API_KEY
```

### 2. 安装依赖

```bash
# 后端
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

### 3. 启动服务

**方式一：一键启动（推荐）**

双击项目根目录的 `start.bat`，自动启动后端 + 前端并打开浏览器。

**方式二：手动启动**

```bash
# 终端1: 启动后端 (http://localhost:8000)
cd backend
venv\Scripts\python.exe start.py

# 终端2: 启动前端 (http://localhost:5173)
cd frontend
npm run dev
```

### 4. 访问系统

- 浏览器打开 http://localhost:5173
- 管理员: `admin` / `123456`（知识库管理、用户管理）
- 普通用户: 注册页自行注册（知识库问答）

## 系统架构

```
浏览器 (React + Ant Design)
    ↓ HTTP/SSE
FastAPI 后端
├── 中间件: CORS · 日志 · 全局异常处理
├── 认证: JWT · 角色守卫 (admin/user)
├── API: /auth · /conversations · /chat · /kb · /users
├── 服务: AuthService · ConversationService · RagService
└── RAG 管道:
    ├── 摄入: 加载 → 中文分块 → 嵌入 → ChromaDB
    ├── 检索: Query → 向量化 → 异步检索(线程池+信号量) → Top-K
    └── 生成: Prompt → Qwen-Plus → SSE 流式 + 引用追踪
        ↓
SQLite(WAL) · ChromaDB · 阿里云百炼 API
```

## 性能优化

| 优化项 | 方案 |
|--------|------|
| 语义缓存 | LRU 缓存（query → answer+sources），重复问题 TTL 1 小时 |
| 异步检索 | `asyncio.to_thread` 抛线程池 + `Semaphore(10)` 限并发 |
| 流式响应 | SSE 逐 token 推送，首字延迟低 |
| SQLite 并发 | WAL 模式 + busy_timeout=30s + 连接池扩容 |
| 前端 | 路由懒加载、搜索防抖 |

## 压力测试

基于 Locust 的 100 人并发压测（详见 [stress-test/REPORT.md](stress-test/REPORT.md)）：

- **场景**：~91 普通用户（RAG 问答/对话管理/注册）+ ~9 管理员（知识库管理）
- **结果**：100 并发 5 分钟 1969 请求 **0 错误**，RAG 问答缓存热态 P95 2 秒
- **Web UI 模式**：`cd stress-test && ..\backend\venv\Scripts\python.exe -m locust -f locustfile.py --host http://localhost:8000` → 浏览器访问 http://localhost:8089

## 测试

```bash
# 后端单元测试 (pytest, 42 条)
cd backend
venv\Scripts\python.exe -m pytest tests/ -v

# 前端单元测试 (vitest, 28 条)
cd frontend
npx vitest run
```

## API 文档

启动后端后访问 http://localhost:8000/docs 查看 Swagger 文档。

主要端点:
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/change-password` - 修改密码
- `POST /api/chat/query` - SSE 流式问答
- `GET /api/conversations` - 对话列表
- `POST /api/kb/documents/upload` - 上传知识文档 (admin)
- `GET /api/kb/stats` - 知识库统计 (admin)
- `GET /api/users` - 用户管理 (admin)

## 项目结构

```
LongChainRAG项目/
├── start.bat                # 一键启动脚本
├── backend/
│   ├── app/
│   │   ├── api/             # API 路由层 (auth/conversations/chat/kb/users)
│   │   ├── models/          # SQLAlchemy ORM 模型
│   │   ├── schemas/         # Pydantic 请求/响应模型
│   │   ├── services/        # 业务逻辑 (Auth/Conversation/Rag)
│   │   ├── rag/             # LangChain RAG 组件
│   │   │   ├── embeddings.py    # 百炼嵌入封装
│   │   │   ├── chunking.py      # 中文分块策略
│   │   │   ├── retrievers.py    # 异步检索器 (to_thread+信号量)
│   │   │   ├── prompts.py       # Prompt 模板
│   │   │   ├── loaders.py       # 多格式文档加载
│   │   │   ├── llm.py           # 百炼 LLM 封装
│   │   │   └── vector_store.py  # ChromaDB 封装
│   │   ├── middleware/      # CORS/日志/异常处理
│   │   └── utils/           # 缓存/分块ID/文本清洗
│   ├── tests/               # pytest 单元测试
│   ├── data/                # 运行时数据 (SQLite/ChromaDB/上传文档)
│   ├── .env.example         # 环境变量模板
│   └── start.py             # 后端启动脚本
├── frontend/
│   ├── src/
│   │   ├── pages/           # 页面 (登录/对话/知识库/用户管理)
│   │   ├── components/      # 组件 (对话列表/消息气泡/引用卡片)
│   │   ├── stores/          # Zustand 状态管理
│   │   ├── hooks/           # 自定义 Hooks (useSSE/useAuth)
│   │   └── api/             # API 客户端 (自动刷新 token)
│   └── tests/               # vitest 单元测试
├── stress-test/             # Locust 压力测试
│   ├── locustfile.py        # 压测场景
│   ├── questions.json       # 问题池
│   ├── seed_users.py        # 批量创建测试用户
│   └── REPORT.md            # 压力测试报告
└── .claude/                 # Claude Code 配置 (agents/skills/hooks)
```
