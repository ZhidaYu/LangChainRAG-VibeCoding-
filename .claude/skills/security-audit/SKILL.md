---
name: security-audit
description: 代码安全审计，检查密钥泄露、注入漏洞、Web API 安全等风险
---

# 代码安全审计

当用户调用此技能时，对项目代码进行全面的安全检查。

---

## 执行步骤

### 步骤 1：确定审查范围

默认检查以下内容：
- `backend/app/` 下所有 `.py` 源代码文件
- `frontend/src/` 下所有 `.ts`、`.tsx` 文件
- `backend/requirements.txt`（依赖安全）
- `frontend/package.json`（依赖安全）
- `.env`、`.env.example`（配置安全）
- `.claude/settings*.json`（权限配置）

### 步骤 2：逐项检查

按以下 6 个类别依次检查，每项给出"安全 / ⚠️ 警告 / 🔴 危险"评级。

---

## 检查类别一：敏感信息泄露（硬编码密码/密钥）

### 检查什么

扫描所有代码和配置文件，查找硬编码的：
- 密码（`password`, `passwd`, `pwd`）
- API 密钥（`api_key`, `apikey`, `secret`, `token`, `dashscope`）
- JWT 密钥
- 数据库密码

### 搜索方法

```bash
grep -rn -i "password\|passwd\|secret\|api_key\|apikey\|token\|dashscope" backend/app/ --include="*.py" | grep -v "password_hash\|hashed_password\|hash_password\|verify_password\|get_password\|password_hash"
grep -rn -i "sk-\|api[_-]?key\|secret" frontend/src/ --include="*.ts" --include="*.tsx"
```

### 判定标准

| 发现 | 评级 | 说明 |
|------|------|------|
| 无任何敏感信息 | 🟢 安全 | — |
| 存在测试用的假数据（如 `password: 'test123'`） | 🟡 警告 | 测试代码也需要避免 |
| 存在真实的密码/密钥（如 `sk-xxx` 开头的 API Key） | 🔴 危险 | 必须立即删除，改用环境变量 |

### 本项目关键检查点

- `backend/.env` 中的 `DASHSCOPE_API_KEY` 是真实的密钥，检查：
  1. `.env` 是否在 `.gitignore` 中（如果项目是 git 仓库）
  2. `.env.example` 中是否只有占位符 `sk-xxx` 而非真实密钥
  3. 代码中是否有 `api_key="sk-..."` 硬编码

---

## 检查类别二：SQL 注入漏洞

### 检查什么

检查所有数据库操作代码，看 SQL 语句是否拼接了用户输入。

### 搜索方法

```bash
grep -rn "execute\|text(\|raw(" backend/app/ --include="*.py"
grep -rn "f\".*SELECT\|f\".*INSERT\|f\".*UPDATE\|f\".*DELETE\|f'.*SELECT" backend/app/ --include="*.py"
```

### 判定标准

| 写法 | 评级 | 说明 |
|------|------|------|
| 全部使用 SQLAlchemy ORM（`select()`, `insert()`） | 🟢 安全 | 自动参数化，无注入风险 |
| 使用 `text()` 但带参数绑定（`text("... WHERE x=:val").bindparams(val=...)`） | 🟢 安全 | 参数化查询 |
| f-string 拼接 SQL + 用户输入 | 🔴 危险 | 攻击者可能通过输入控制 SQL 逻辑 |

### 本项目关键检查点

- `backend/app/services/` 中所有查询是否使用 SQLAlchemy `select()` 构造器
- 特别注意 `conversation_service.py` 中的过滤查询
- 用户输入（`username`、`question`）绝不能进入 SQL 字符串拼接

---

## 检查类别三：配置文件敏感信息

### 检查什么

检查所有配置文件中是否有明文敏感信息：

#### backend/.env
- `DASHSCOPE_API_KEY` 是否为真实密钥
- `.env` 是否被 `.gitignore` 排除

#### .env.example
- 是否只有占位符

#### .claude/settings*.json
- 权限白名单是否过于宽松
- 是否有危险的 Bash 权限

### 判定标准

| 发现 | 评级 | 说明 |
|------|------|------|
| 无敏感配置 | 🟢 安全 | — |
| 权限配置过于宽松 | 🟡 警告 | 如 `Bash(*)` 表示任何命令都能跑 |
| 配置文件中包含真实密钥 | 🔴 危险 | 必须移到环境变量并加入 .gitignore |

---

## 检查类别四：Web API 安全（本项目专用）

本项目是 Web 应用（FastAPI 后端 + React 前端），安全重点：

### ① JWT 认证安全

检查 `backend/app/dependencies.py` 和 `backend/app/services/auth_service.py`：

| 检查项 | 安全值 | 说明 |
|--------|--------|------|
| JWT 算法 | HS256（显式指定） | 不要用 `none` 算法 |
| Token 过期时间 | 15 分钟（access） | 合理范围 |
| 密钥强度 | ≥ 32 字符随机串 | 弱密钥可被暴力破解 |
| 密码哈希 | bcrypt（12 轮） | 不要用 MD5/SHA1 |

```bash
grep -rn "jwt.decode\|jwt.encode" backend/app/ --include="*.py"
grep -rn "hash(" backend/app/services/auth_service.py
```

### ② 权限控制（RBAC）

检查所有管理接口是否使用 `require_admin`：

```bash
grep -rn "router\.\(get\|post\|put\|delete\)" backend/app/api/kb.py backend/app/api/users.py -A 3
```

**规则**：
- `/api/kb/*` 全部端点必须 `Depends(require_admin)` 🔴
- `/api/users/*` 全部端点必须 `Depends(require_admin)` 🔴
- `/api/chat/*` 和 `/api/conversations/*` 必须 `Depends(get_current_user)` 🔴
- `/api/auth/*` 中只有 register/login/refresh 是公开的

### ③ 对话越权访问

检查 `conversations.py`：用户能否访问其他用户的对话？

```bash
grep -rn "user_id" backend/app/api/conversations.py
```

**规则**：所有 `get/put/delete` 对话操作必须校验 `conv.user_id == current_user.id`，否则 🔴 危险（用户可以读取他人对话）。

### ④ CORS 配置

检查 `backend/app/main.py` 的 CORS 设置：

- ✅ 安全：只允许 `http://localhost:5173` 等白名单来源
- 🔴 危险：`allow_origins=["*"]` + `allow_credentials=True`

### ⑤ 文件上传安全

检查 `backend/app/api/kb.py` 的上传端点：

| 检查项 | 安全做法 |
|--------|---------|
| 文件类型 | 必须有扩展名白名单（`ALLOWED_EXTENSIONS`）✅ |
| 文件大小 | 是否限制最大上传大小？未限制是 🟡 |
| 文件名 | 是否使用 `uuid4()` 重命名（防路径遍历）✅ |
| 文件内容 | 是否校验真实 MIME 类型？只查扩展名可被伪造 🟡 |

---

## 检查类别五：路径遍历与文件操作

### 检查什么

检查所有文件读写操作，看文件路径是否来自用户输入。

```bash
grep -rn "open(\|write_bytes\|read_bytes\|Path(" backend/app/ --include="*.py"
```

### 本项目关键检查点

#### 上传文件保存（`kb.py`）

```python
unique_name = f"{uuid.uuid4().hex}_{file.filename}"  # ✅ 加了随机前缀
file_path = UPLOAD_DIR / unique_name
```

- 文件名被 `uuid4().hex` 前缀化，且 `file.filename` 来自 UploadFile ✅
- 但如果 `file.filename` 包含 `../` 仍然危险 — 检查是否有 `Path(file.filename).name` 处理

#### 文档加载（`rag/loaders.py`）

```python
def load_document(file_path: str)
```

- `file_path` 只来自后端生成的路径（uuid 前缀），非用户直接输入 ✅

### 判定标准

| 情况 | 评级 | 说明 |
|------|------|------|
| 文件路径由后端生成 | 🟢 安全 | 用户无法控制路径 |
| 文件路径直接使用用户输入 | 🔴 危险 | 攻击者可能输入 `../../etc/passwd` |
| 文件路径有校验/白名单 | 🟢 安全 | 即使来自用户输入也做了防御 |

---

## 检查类别六：其他安全隐患

### ① 错误信息泄露

检查全局异常处理器：

```python
# backend/app/middleware/error_handler.py
return JSONResponse(status_code=500, content={"detail": f"服务器内部错误: {str(exc)}"})
```

**风险**：`str(exc)` 可能包含文件系统路径、数据库结构、API 密钥等敏感信息。

**建议**：详细错误记日志，只返回通用信息（如"服务器内部错误，请稍后重试"）。

```bash
grep -rn "str(exc)\|str(e)" backend/app/ --include="*.py"
```

### ② 危险操作缺少确认

检查文档删除端点是否合理：
- 前端是否有确认对话框？（`Popconfirm`）✅ 有
- 后端删除向量失败时是否静默吞掉？（`except Exception: pass`）

### ③ 依赖安全

```bash
cd backend && venv/Scripts/python.exe -m pip list --outdated 2>/dev/null | head -20
cd frontend && npm audit 2>/dev/null | tail -20
```

检查是否有已知漏洞的依赖包。

### ④ print 遗留

```bash
grep -rn "^[[:space:]]*print(" backend/app/ --include="*.py"
```

### ⑤ 数据安全

- SQLite 数据库文件中的数据是否明文存储？
- ChromaDB 向量数据是否明文存储？
- 对于本地演示项目这是可接受的，但要明确告知用户。

---

## 步骤 3：生成安全审计报告

### 报告格式

```
🔒 安全审计报告
项目：电商RAG知识库问答系统
审计时间：YYYY-MM-DD
审查范围：X 个文件

═══════════════════════════════════
📊 总览

| 类别 | 结果 | 风险数 |
|------|------|--------|
| 敏感信息泄露     | 🟢/🟡/🔴 | N 项 |
| SQL 注入         | 🟢/🟡/🔴 | N 项 |
| 配置安全         | 🟢/🟡/🔴 | N 项 |
| Web API 安全     | 🟢/🟡/🔴 | N 项 |
| 路径遍历         | 🟢/🟡/🔴 | N 项 |
| 其他隐患         | 🟢/🟡/🔴 | N 项 |

总风险数：🔴 N 项  🟡 N 项  🟢 N 项

═══════════════════════════════════
🔴 高危（必须立即修复）

1. [文件:行号] 问题描述
   风险：...
   修复：...

═══════════════════════════════════
🟡 中危（建议修复）

1. [文件:行号] 问题描述
   建议：...

═══════════════════════════════════
🟢 检查通过

- 所有 SQL 查询使用 SQLAlchemy ORM，无注入风险
- ...

═══════════════════════════════════
📈 安全评分：XX / 100
```

---

## 重要补充

### 什么是安全问题？

用生活类比解释：

| 类比 | 安全问题 |
|------|---------|
| 你家钥匙放在门垫下面 | **硬编码密码**：API Key 写在代码里，谁都能看到 |
| 任何人都能打开你的保险柜 | **权限缺失**：管理接口没有 admin 校验 |
| 别人拆了你的快递看到你的信 | **错误信息泄露**：内部细节暴露给用户 |
| 陌生人拿着你的钥匙配了一把 | **弱密钥**：JWT 密钥太简单可被破解 |

### 本项目的安全边界

本项目是**本地演示的 Web 应用**（毕设项目），安全威胁模型：
- 运行在 localhost，暴露面小
- 但有百炼 API Key（真实付费资源）需要保护
- 多用户系统 → 数据隔离（用户间对话不可互看）是核心安全要求
- 最重要的资产：API Key + 用户数据隔离 + 管理权限控制
