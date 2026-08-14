# 压力测试 — 模拟 100 人同时使用

基于 Locust 的压力测试，模拟 100 个用户同时使用电商RAG知识库问答系统。

## 前置条件

1. 后端已启动（生产模式，不带 --reload）：
   ```bash
   cd backend
   venv/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
2. 知识库已有文档（问答检索需要）
3. 百炼 API Key 有效且余额充足

## 使用方法

### 1. 创建压测用户（100 个）

```bash
cd stress-test
../backend/venv/Scripts/python.exe seed_users.py
```

### 2. 执行压测（三阶段）

```bash
# 阶段 1：热身（10 用户 × 2 分钟）— 验证脚本 + 预热缓存
../backend/venv/Scripts/python.exe -m locust -f locustfile.py --host http://localhost:8000 \
  --headless -u 10 -r 2 --run-time 2m --html report-phase1.html

# 阶段 2：50 用户 × 5 分钟
../backend/venv/Scripts/python.exe -m locust -f locustfile.py --host http://localhost:8000 \
  --headless -u 50 -r 5 --run-time 5m --html report-phase2.html --csv phase2

# 阶段 3：100 用户 × 5 分钟（目标场景）
../backend/venv/Scripts/python.exe -m locust -f locustfile.py --host http://localhost:8000 \
  --headless -u 100 -r 10 --run-time 5m --html report-phase3.html --csv phase3
```

### 3. 查看结果

- `report-phaseX.html`：Locust 完整报告（浏览器打开）
- `phaseX_stats.csv`：分接口统计数据（论文图表数据源）
- 终端实时输出：RPS、响应时间、错误率

## 场景说明

| 用户类型 | 数量 | 行为 |
|---------|------|------|
| NormalUser | ~99 | 登录→建对话→提问(RAG问答，权重5)/浏览对话(3)/看历史(2)/新建(1)/个人中心(1)，思考间隔 8-20 秒 |
| AdminUser | ~1 | 知识库文档列表(2)/统计(1)，间隔 15-30 秒 |

问题池 40 条，基于示例产品文档（华为/小米/iPhone），覆盖参数/价格/对比/特性查询。

## 成本预估

- 百炼 API：qwen-plus 按 token 计费，13 分钟压测约 1000-2000 次问答，预计 < 5 元

## 注意事项

- 压测期间不要操作后端数据库（避免干扰测试数据）
- 若错误率中大量出现"流式错误: ... Rate limit"，说明触及百炼 API 限流，需降低并发或加大思考间隔
- 压测产生的对话数据在压测后可通过删除 stress_user_* 用户清理
