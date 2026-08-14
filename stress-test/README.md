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

### 0. 创建压测用户（100 个）

```bash
cd stress-test
../backend/venv/Scripts/python.exe seed_users.py
```

### 方式一：Web UI 交互模式（推荐调试 / 答辩演示）

适合手动设置并发、实时观察测试过程。

#### 1. 启动 Locust Web 界面

```bash
cd stress-test
../backend/venv/Scripts/python.exe -m locust -f locustfile.py --host http://localhost:8000
```

终端出现 `Starting web interface at http://0.0.0.0:8089` 后，浏览器打开：

**http://localhost:8089**

#### 2. 在 Web UI 中设置并启动

| 设置项 | 说明 | 示例 |
|--------|------|------|
| Number of users | 并发用户总数 | 100 |
| Spawn rate | 每秒爬升的用户数 | 10（10 秒爬满 100） |
| Host | 后端地址（启动命令已指定） | http://localhost:8000 |
| Class picker | 选择用户场景 | NormalUser（问答+对话）/ AdminUser（知识库管理） |

点 **Start** 开始，点 **Stop** 停止，可随时修改并发数重启。

#### 3. 实时看板

- **Statistics**：每个接口的 Requests / Failures / 平均响应时间 / RPS
- **Charts**：总 RPS、响应时间、活跃用户数实时曲线图
- **Failures**：失败请求详情

### 方式二：Headless 命令行模式（无人值守三阶段批量测试）

适合一次性跑完阶梯并发并自动生成报告文件（论文数据收集）。

```bash
cd stress-test

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

### 查看结果（headless 模式）

- `report-phaseX.html`：Locust 完整报告（浏览器打开）
- `phaseX_stats.csv`：分接口统计数据（论文图表数据源）
- 终端实时输出：RPS、响应时间、错误率

## 场景说明

| 用户类型 | 数量 | 行为 |
|---------|------|------|
| NormalUser | ~91 | 登录→建对话→提问(RAG问答，权重5)/浏览对话(3)/看历史(2)/新建(1)/注册新用户(1)/个人中心(1)，思考间隔 8-20 秒 |
| AdminUser | ~9 | 知识库文档列表(2)/统计(1)，间隔 2-5 秒（保证 KB 接口有足够请求样本量） |

问题池 40 条，基于示例产品文档（华为/小米/iPhone），覆盖参数/价格/对比/特性查询。

## 成本预估

- 百炼 API：qwen-plus 按 token 计费，13 分钟压测约 1000-2000 次问答，预计 < 5 元

## 注意事项

- 压测期间不要操作后端数据库（避免干扰测试数据）
- 若错误率中大量出现"流式错误: ... Rate limit"，说明触及百炼 API 限流，需降低并发或加大思考间隔
- 压测产生的对话数据在压测后可通过删除 stress_user_* 用户清理
