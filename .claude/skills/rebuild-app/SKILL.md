---
name: rebuild-app
description: 重新构建前端生产版本并验证后端，用于答辩部署
---

# 重新构建电商RAG知识库问答系统

将项目构建为生产版本（前端编译 + 后端验证），用于答辩演示或部署。

## 构建步骤

### 1. 前端构建

```bash
cd frontend
npx vite build
```

构建产物输出到 `frontend/dist/` 目录。

### 2. 验证构建产物

```bash
ls frontend/dist/index.html
```

确认构建成功（有 `dist/index.html` 和 `dist/assets/`）。

### 3. 后端验证

```bash
cd backend
venv/Scripts/python.exe -c "from app.main import app; print('Import OK')"
```

确认后端可以正常导入。

### 4. 端到端验证

启动后端（`venv/Scripts/python.exe start.py`），然后测试：

```bash
curl http://localhost:8000/api/health
```

确认返回 `{"status": "ok", ...}`。

---

## 部署方式

### 方式一：本地演示（推荐）

双击 `start.bat` 一键启动，或手动分别启动前后端。

### 方式二：前端静态托管

把 `frontend/dist/` 部署到 Nginx，后端用 uvicorn 常驻：

```bash
# 后端生产模式（不用 --reload）
venv/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

注意：生产模式需要把 `.env` 中的 `CORS_ORIGINS` 改为实际前端地址。

---

## 重要说明

### 构建过程

```
清理旧构建产物（可选）→ vite build 编译 → 验证产物 → 后端导入验证 → 端到端测试
```

- 前端构建只需几秒（Vite 极快）
- 无需 Docker
- 无需打包 exe（本项目是 Web 应用，不是桌面应用）

### 约束条件

- 后端依赖阿里云百炼 API（需要联网 + 有效 API Key）
- SQLite 和 ChromaDB 数据在 `backend/data/` 目录，备份时整体复制该目录即可

---

## 常见问题

### Q1: vite build 失败

```bash
cd frontend
rm -rf node_modules
npm install
npx vite build
```

### Q2: 构建后前端页面空白

**原因**：前端 API 地址硬编码为 `http://localhost:8000`（`frontend/src/api/client.ts`）。

**解决**：部署到其他机器时，把 `client.ts` 中的 `baseURL` 改为实际后端地址。

### Q3: 答辩演示时 API 不稳定

**预防**：
1. 答辩前 1 天充值并确认百炼余额
2. 提前预热：用常见问题先问答一遍（会写入 LRU 缓存）
3. 准备断网预案说明
