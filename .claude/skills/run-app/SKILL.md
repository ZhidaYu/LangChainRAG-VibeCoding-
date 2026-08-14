---
name: run-app
description: 启动电商RAG知识库问答系统（后端 FastAPI + 前端 Vite）
---

# 启动电商RAG知识库问答系统

当用户调用此技能时，按以下步骤启动应用：

## 启动步骤

### 1. 检查后端环境

```bash
cd backend
ls venv/Scripts/python.exe
```

如果虚拟环境不存在，创建并安装依赖：

```bash
cd backend
python -m venv venv
venv/Scripts/python.exe -m pip install -r requirements.txt
```

### 2. 检查配置

确认 `backend/.env` 存在且 `DASHSCOPE_API_KEY` 已填写（真实密钥，以 `sk-` 开头）。

### 3. 启动后端

```bash
cd backend
venv/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

确认输出 `Uvicorn running on http://0.0.0.0:8000`。

### 4. 检查前端依赖

```bash
cd frontend
ls node_modules/antd
```

如果不存在，运行 `npm install`。

### 5. 启动前端

```bash
cd frontend
npm run dev
```

确认输出 `Local: http://localhost:5173`。

### 6. 确认启动成功

访问 http://localhost:5173，看到登录页即表示启动成功。

---

## 一键启动

也可以直接双击项目根目录的 `start.bat`，自动完成以上所有步骤。

---

## 重要补充

### 运行环境

- **后端必须用项目 venv 的 Python**（`backend/venv/Scripts/python.exe`），不能用系统 Python
- 前端用系统 Node.js 即可（v18+）

### 数据存储位置

- 用户/对话/消息数据：`backend/data/rag_ecommerce.db`（SQLite 单文件）
- 向量数据：`backend/data/chroma/`（ChromaDB 持久化目录）
- 上传的原始文档：`backend/data/raw/`

### API 依赖

- LLM 和 Embedding 调用阿里云百炼 API，需要联网
- 断网时问答功能不可用（但用户登录、对话历史查询不受影响）

### 默认账号

- 管理员：`admin / 123456`（首次启动自动创建）
- 普通用户：注册页自行注册

---

## 常见问题

### Q1: 后端启动报 `No module named uvicorn`

**原因**：用了系统 Python 而不是项目 venv。

**解决**：
```bash
cd backend
venv/Scripts/python.exe -m uvicorn app.main:app --port 8000
```

### Q2: 端口被占用 `[WinError 10013]`

**原因**：8000 端口已有进程。

**解决**：
```bash
netstat -ano | findstr :8000
taskkill /F /PID <PID号>
```

### Q3: 登录失败

**原因**：前端端口不是 5173，CORS 拦截了请求。

**解决**：
1. 检查前端地址是否是 http://localhost:5173
2. 如果 Vite 自动换了端口（5174 等），编辑 `backend/.env` 的 `CORS_ORIGINS` 加上新端口，然后重启后端

### Q4: 问答报错 `Error code: 400 InvalidParameter`

**原因**：百炼 API Key 无效或过期。

**解决**：检查 `backend/.env` 中 `DASHSCOPE_API_KEY` 是否正确。

### Q5: 管理员密码忘了

**解决**：删除 `backend/data/rag_ecommerce.db` 后重启后端，会重新创建 `admin/123456`。（注意：会丢失所有用户和对话数据）
