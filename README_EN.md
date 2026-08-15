# E-Commerce RAG Knowledge Base Q&A System

> Graduation project — an enterprise-grade RAG knowledge base Q&A system built with LangChain + FastAPI + React
>
> For e-commerce product scenarios: users ask questions in the browser; the system retrieves relevant knowledge base content, streams answers, and displays cited source snippets.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Alibaba Cloud Bailian (DashScope) Qwen-Plus |
| Embedding | Alibaba Cloud Bailian text-embedding-v3 |
| RAG Framework | LangChain + LangChain-Community |
| Backend | FastAPI (Python 3.11) + Uvicorn |
| Frontend | React 18 + TypeScript + Vite |
| UI Library | Ant Design 5 |
| State Management | Zustand |
| Vector DB | ChromaDB |
| Relational DB | SQLite (SQLAlchemy 2.0) with WAL concurrency hardening |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Load Testing | Locust |

## Features

- ✅ Browser-based knowledge base management (upload/delete/stats, admin only)
- ✅ RAG Q&A with SSE streaming + citation cards for source snippets
- ✅ Multi-user, multi-session management (isolated conversations per user)
- ✅ Persistent chat history (recoverable across logins)
- ✅ User registration/login + password change
- ✅ Admin/user role isolation (RBAC)
- ✅ LRU semantic cache (instant answers for repeated questions)
- ✅ Chinese-optimized chunking strategy
- ✅ Multi-format document support (PDF/DOCX/TXT/MD/CSV/XLSX)
- ✅ Async retrieval (`asyncio.to_thread` + semaphore, non-blocking event loop)
- ✅ SQLite WAL mode (high-concurrency read/write hardening)
- ✅ 100-concurrent-user load test (Locust, 0% error rate)

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Alibaba Cloud Bailian API Key ([apply for free](https://bailian.console.aliyun.com/))

### 1. Configure

```bash
cd backend
copy .env.example .env
# Edit .env and fill in your DASHSCOPE_API_KEY
```

### 2. Install Dependencies

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 3. Start Services

**Option A: One-click launch (recommended)**

Double-click `start.bat` in the project root — it starts both the backend and frontend and opens the browser automatically.

**Option B: Manual launch**

```bash
# Terminal 1: backend (http://localhost:8000)
cd backend
venv\Scripts\python.exe start.py

# Terminal 2: frontend (http://localhost:5173)
cd frontend
npm run dev
```

### 4. Access the System

- Open http://localhost:5173 in your browser
- Admin: `admin` / `123456` (knowledge base & user management)
- Regular users: register via the sign-up page (Q&A only)

## System Architecture

```
Browser (React + Ant Design)
    ↓ HTTP/SSE
FastAPI Backend
├── Middleware: CORS · Logging · Global exception handling
├── Auth: JWT · Role guard (admin/user)
├── API: /auth · /conversations · /chat · /kb · /users
├── Services: AuthService · ConversationService · RagService
└── RAG Pipeline:
    ├── Ingestion: Load → Chinese chunking → Embed → ChromaDB
    ├── Retrieval: Query → Vectorize → Async search (thread pool + semaphore) → Top-K
    └── Generation: Prompt → Qwen-Plus → SSE streaming + citation tracking
        ↓
SQLite (WAL) · ChromaDB · Alibaba Bailian API
```

## Performance Optimizations

| Optimization | Approach |
|--------------|----------|
| Semantic cache | LRU cache (query → answer+sources), 1h TTL for repeated questions |
| Async retrieval | `asyncio.to_thread` offloading + `Semaphore(10)` concurrency limit |
| Streaming | SSE token-by-token push, low first-token latency |
| SQLite concurrency | WAL mode + 30s busy_timeout + larger connection pool |
| Frontend | Route lazy loading, debounced search |

## Load Testing

Locust-based 100-concurrent-user test (details in [stress-test/REPORT.md](stress-test/REPORT.md)):

- **Scenarios**: ~91 regular users (RAG Q&A / conversation management / registration) + ~9 admins (KB management)
- **Result**: 1,969 requests in 5 minutes at 100 users with **0 failures**; RAG Q&A P95 of 2s with warm cache
- **Web UI mode**: `cd stress-test && ..\backend\venv\Scripts\python.exe -m locust -f locustfile.py --host http://localhost:8000` → open http://localhost:8089

## Tests

```bash
# Backend unit tests (pytest, 42 cases)
cd backend
venv\Scripts\python.exe -m pytest tests/ -v

# Frontend unit tests (vitest, 28 cases)
cd frontend
npx vitest run
```

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for the Swagger UI.

Key endpoints:
- `POST /api/auth/register` — user registration
- `POST /api/auth/login` — user login
- `POST /api/auth/change-password` — change password
- `POST /api/chat/query` — SSE streaming Q&A
- `GET /api/conversations` — conversation list
- `POST /api/kb/documents/upload` — upload knowledge document (admin)
- `GET /api/kb/stats` — knowledge base statistics (admin)
- `GET /api/users` — user management (admin)

## Project Structure

```
LongChainRAG项目/
├── start.bat                # One-click launch script
├── backend/
│   ├── app/
│   │   ├── api/             # API routes (auth/conversations/chat/kb/users)
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── services/        # Business logic (Auth/Conversation/Rag)
│   │   ├── rag/             # LangChain RAG components
│   │   │   ├── embeddings.py    # Bailian embedding wrapper
│   │   │   ├── chunking.py      # Chinese chunking strategy
│   │   │   ├── retrievers.py    # Async retriever (to_thread + semaphore)
│   │   │   ├── prompts.py       # Prompt templates
│   │   │   ├── loaders.py       # Multi-format document loaders
│   │   │   ├── llm.py           # Bailian LLM wrapper
│   │   │   └── vector_store.py  # ChromaDB wrapper
│   │   ├── middleware/      # CORS/logging/error handling
│   │   └── utils/           # Cache/chunk IDs/text cleaning
│   ├── tests/               # pytest unit tests
│   ├── data/                # Runtime data (SQLite/ChromaDB/uploads)
│   ├── .env.example         # Environment template
│   └── start.py             # Backend startup script
├── frontend/
│   ├── src/
│   │   ├── pages/           # Pages (login/chat/KB/user management)
│   │   ├── components/      # Components (conversation list/bubbles/citations)
│   │   ├── stores/          # Zustand state management
│   │   ├── hooks/           # Custom hooks (useSSE/useAuth)
│   │   └── api/             # API client (auto token refresh)
│   └── tests/               # vitest unit tests
├── stress-test/             # Locust load testing
│   ├── locustfile.py        # Test scenarios
│   ├── questions.json       # Question pool
│   ├── seed_users.py        # Batch user creation
│   └── REPORT.md            # Load test report
└── .claude/                 # Claude Code config (agents/skills/hooks)
```
