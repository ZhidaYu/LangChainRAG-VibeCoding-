---
name: unit-test
description: 创建单元测试、执行测试并生成测试报告（后端 pytest + 前端 vitest）
---

# 单元测试

为当前项目代码（前后端）创建单元测试，运行测试，并生成测试报告。

**测试框架**：
- 后端 (Python/FastAPI)：**pytest** + **pytest-asyncio** + **httpx**
- 前端 (React/TypeScript)：**vitest**

---

## 执行步骤

### 步骤 1：检查测试环境

**后端**：
检查 `backend/requirements.txt` 是否包含 pytest 依赖（pytest, pytest-asyncio, httpx）。如果未安装：
```bash
cd backend && venv\Scripts\python.exe -m pip install pytest pytest-asyncio httpx
```

**前端**：
检查 `frontend/package.json` 是否包含 vitest。如果未安装：
```bash
cd frontend && npm install -D vitest @types/node
```

### 步骤 2：分析要测试的代码

**后端优先测试**（纯函数，不依赖外部 API）：
- `backend/app/services/auth_service.py` — JWT 生成/验证、密码哈希
- `backend/app/utils/cache.py` — LRU 缓存逻辑
- `backend/app/utils/chunk_id.py` — 确定性 Chunk ID 生成
- `backend/app/utils/text_cleaner.py` — 中文文本清洗
- `backend/app/rag/chunking.py` — 中文分块策略
- `backend/app/rag/prompts.py` — Prompt 模板

**后端需要 Mock 的测试**：
- `backend/app/api/auth.py` — 需要 Mock 数据库
- `backend/app/api/chat.py` — 需要 Mock LLM 和 ChromaDB
- `backend/app/services/rag_service.py` — 需要 Mock LLM

**前端优先测试**：
- `frontend/src/utils/token.ts` — Token 存取
- `frontend/src/utils/format.ts` — 格式化函数
- `frontend/src/stores/authStore.ts` — 状态管理
- `frontend/src/stores/chatStore.ts` — 状态管理

### 步骤 3：创建测试文件

在后端 `backend/tests/` 和前端 `frontend/tests/` 分别创建测试文件。

**后端测试文件结构**：
```
backend/tests/
├── conftest.py              # pytest fixtures (async client, test db)
├── test_auth_service.py     # 认证服务测试
├── test_utils.py            # 工具函数测试
├── test_chunking.py         # 分块策略测试
└── test_api_auth.py         # 认证 API 测试
```

**前端测试文件结构**：
```
frontend/tests/
├── token.test.ts            # Token 工具测试
├── format.test.ts           # 格式化工具测试
└── authStore.test.ts        # 认证状态测试
```

### 步骤 4：执行测试

**后端测试**：
```bash
cd backend && venv\Scripts\python.exe -m pytest tests/ -v
```

**前端测试**：
```bash
cd frontend && npx vitest run --reporter=verbose
```

### 步骤 5：生成测试报告

根据测试输出，整理测试报告：

## 📊 测试报告

| 项目 | 后端 | 前端 | 合计 |
|------|------|------|------|
| 测试文件数 | X 个 | X 个 | X 个 |
| 测试用例数 | X 条 | X 条 | X 条 |
| 通过 | X 条 | X 条 | X 条 |
| 失败 | X 条 | X 条 | X 条 |
| 通过率 | XX% | XX% | XX% |

---

## 通行证输出

测试完毕后，写入项目根目录 `tester-result.txt`：
- 第一行：PASS 或 FAIL
- 第二行：简要统计

只有全部通过时第一行才写 PASS。
