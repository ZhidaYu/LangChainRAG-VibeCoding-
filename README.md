# 电商RAG企业级知识库问答系统

> 毕业设计项目 — 基于 LangChain + FastAPI + React 的企业级 RAG 知识库问答系统

## 技术栈

| 层级 | 技术 |
|------|------|
| 大模型 | 阿里云百炼 Qwen-Plus |
| 嵌入模型 | 阿里云百炼 text-embedding-v3 |
| RAG 框架 | LangChain + LangChain-Community |
| 后端框架 | FastAPI (Python 3.11) |
| 前端框架 | React 18 + TypeScript + Vite |
| UI 组件库 | Ant Design 5 |
| 状态管理 | Zustand |
| 向量数据库 | ChromaDB |
| 关系数据库 | SQLite (SQLAlchemy 2.0) |
| 认证 | JWT (python-jose) + bcrypt (passlib) |

## 功能特性

- ✅ 浏览器知识库管理（上传/删除/统计/分块预览）
- ✅ 知识库问答 + 流式输出 + 引用来源展示
- ✅ 多用户多会话管理（每用户独立会话）
- ✅ 历史对话持久化（跨登录找回）
- ✅ 用户注册登录 + 修改密码
- ✅ 管理员/普通用户角色隔离
- ✅ LRU 内存缓存加速
- ✅ 中文优化分块策略
- ✅ 多格式文档支持（PDF/DOCX/TXT/MD/CSV/XLSX）

## 快速开始

### 前置要求

- Python 3.11+
- Node.js 18+
- 阿里云百炼 API Key（[免费申请](https://bailian.console.aliyun.com/)）

### 1. 配置环境

```bash
cd backend
cp .env.example .env
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

```bash
# 终端1: 启动后端 (http://localhost:8000)
cd backend
python start.py

# 终端2: 启动前端 (http://localhost:5173)
cd frontend
npm run dev
```

### 4. 访问系统

- 浏览器打开 http://localhost:5173
- 管理员: `admin` / `123456`
- 普通用户: 自行注册

## 系统架构

```
浏览器 (React + Ant Design)
    ↓ HTTP/SSE
FastAPI 后端
├── 中间件: CORS · 限流 · 日志
├── 认证: JWT · 角色守卫
├── API: /auth · /conversations · /chat · /kb
├── 服务: AuthService · ConversationService · RagService
└── RAG 管道:
    ├── 摄入: 加载 → 分块 → 嵌入 → ChromaDB
    ├── 检索: Query → 向量化 → 搜索 → 重排序
    └── 生成: Prompt → Qwen-Plus → 流式 + 引用
        ↓
SQLite · ChromaDB · 阿里云百炼 API
```

## API 文档

启动后端后访问 http://localhost:8000/docs 查看 Swagger 文档。

主要端点:
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/chat/query` - SSE 流式问答
- `POST /api/kb/documents/upload` - 上传知识文档 (admin)
- `GET /api/kb/stats` - 知识库统计 (admin)

## 项目结构

```
LongChainRAG项目/
├── backend/
│   ├── app/
│   │   ├── api/          # API 路由
│   │   ├── models/       # SQLAlchemy ORM
│   │   ├── schemas/      # Pydantic 模型
│   │   ├── services/     # 业务逻辑
│   │   ├── rag/          # LangChain RAG 组件
│   │   │   ├── embeddings.py  # 嵌入模型
│   │   │   ├── chunking.py    # 中文分块
│   │   │   ├── retrievers.py  # 检索器
│   │   │   ├── prompts.py     # Prompt 模板
│   │   │   ├── loaders.py     # 文档加载
│   │   │   └── vector_store.py # 向量存储
│   │   ├── middleware/    # 中间件
│   │   └── utils/         # 工具函数
│   ├── data/              # 持久化数据
│   └── start.py           # 启动脚本
├── frontend/
│   └── src/
│       ├── pages/         # 页面组件
│       ├── components/    # 通用组件
│       ├── stores/        # Zustand 状态
│       ├── hooks/         # 自定义 Hooks
│       └── api/           # API 客户端
└── README.md
```
