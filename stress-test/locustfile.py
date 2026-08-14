"""电商RAG知识库问答系统 — 压力测试场景（Locust）。

模拟 100 人同时使用的真实行为：
- 普通用户（weight=100）：登录 → 建对话 → 循环 [提问(SSE流式等答案) / 浏览对话列表 / 查看历史消息 / 新建对话 / 注册新用户 / 个人中心]，思考间隔 8-20 秒
- 管理员（weight=10）：登录 → 循环 [知识库文档列表 / 知识库统计]，间隔 2-5 秒（保证 KB 接口有足够请求量）

运行方式（在 stress-test 目录下）：
    Web UI:  locust -f locustfile.py --host http://localhost:8000  →  浏览器 http://localhost:8089
    Headless: locust -f locustfile.py --host http://localhost:8000 --headless -u 100 -r 10 --run-time 5m --html report.html
"""
import json
import os
import random

from locust import HttpUser, task, between
from locust.exception import StopUser

# ── 问题池：40 条，全部基于已上传的产品文档 ──
_QUESTIONS_PATH = os.path.join(os.path.dirname(__file__), "questions.json")
with open(_QUESTIONS_PATH, encoding="utf-8") as f:
    QUESTIONS = json.load(f)["questions"]

USER_COUNT = 100           # 压测用户总数（需先用 seed_users.py 创建）
PASSWORD = "stress123456"  # 压测用户统一密码
BASE = "/api"              # 后端 API 前缀


def _pick_username() -> str:
    """随机挑一个压测账号（同一账号可被多个虚拟用户并发使用，模拟真实多端登录）。"""
    return f"stress_user_{random.randint(1, USER_COUNT):03d}"


class NormalUser(HttpUser):
    """普通用户：核心 RAG 问答 + 对话管理，占 100 份权重中的绝大多数。"""

    weight = 100
    wait_time = between(8, 20)  # 用户阅读答案/思考的时间

    def on_start(self):
        """登录 + 创建一个对话（每个用户只登录一次，符合真实行为）。"""
        username = _pick_username()
        with self.client.post(
            f"{BASE}/auth/login",
            json={"username": username, "password": PASSWORD},
            name="/api/auth/login",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"登录失败 HTTP {resp.status_code}: {resp.text[:200]}")
                raise StopUser()
            self.token = resp.json()["access_token"]

        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.conversation_id = None

        # 建一个对话，后续提问挂在这个对话上（真实用户行为）
        with self.client.post(
            f"{BASE}/conversations", json={},
            headers=self.headers, name="/api/conversations (创建)",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                self.conversation_id = resp.json()["id"]

    @task(5)
    def ask_question(self):
        """核心场景：RAG 问答。SSE 流式读取直到 done，完整响应时间 = 用户等待答案的时间。"""
        question = random.choice(QUESTIONS)
        payload = {"question": question}
        if self.conversation_id:
            payload["conversation_id"] = self.conversation_id

        with self.client.post(
            f"{BASE}/chat/query",
            json=payload,
            headers=self.headers,
            name="/api/chat/query (RAG问答)",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"HTTP {resp.status_code}: {resp.text[:200]}")
                return
            body = resp.text
            if '"type": "error"' in body:
                # 提取错误原因（如百炼 API 限流）
                resp.failure(f"流式错误: {body[:300]}")
                return
            if '"type": "done"' not in body:
                resp.failure("流未正常结束（缺少 done 事件）")
                return
            resp.success()

    @task(3)
    def list_conversations(self):
        """浏览对话列表。"""
        self.client.get(
            f"{BASE}/conversations",
            headers=self.headers,
            name="/api/conversations (列表)",
        )

    @task(2)
    def get_messages(self):
        """查看历史对话消息。"""
        if not self.conversation_id:
            return
        self.client.get(
            f"{BASE}/conversations/{self.conversation_id}",
            headers=self.headers,
            name="/api/conversations (历史消息)",
        )

    @task(1)
    def create_conversation(self):
        """新建对话。"""
        self.client.post(
            f"{BASE}/conversations", json={},
            headers=self.headers,
            name="/api/conversations (创建)",
        )

    @task(1)
    def register_user(self):
        """注册新用户（唯一用户名，模拟新用户流入）。"""
        username = f"stress_reg_{random.randint(100000, 999999)}"
        with self.client.post(
            f"{BASE}/auth/register",
            json={"username": username, "password": PASSWORD},
            name="/api/auth/register (注册)",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"注册失败 HTTP {resp.status_code}: {resp.text[:200]}")

    @task(1)
    def get_me(self):
        """个人中心。"""
        self.client.get(
            f"{BASE}/auth/me",
            headers=self.headers,
            name="/api/auth/me",
        )


class AdminUser(HttpUser):
    """管理员：知识库管理操作（全接口覆盖）。

    weight=10：100 用户场景中约 9 个管理员，
    wait_time 2-5 秒保证 KB 接口有足够的请求样本量（对齐教程场景 C）。
    """

    weight = 10
    wait_time = between(2, 5)

    def on_start(self):
        with self.client.post(
            f"{BASE}/auth/login",
            json={"username": "admin", "password": "123456"},
            name="/api/auth/login (admin)",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"管理员登录失败: {resp.text[:200]}")
                raise StopUser()
            self.headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

    @task(2)
    def list_documents(self):
        """知识库文档列表。"""
        self.client.get(
            f"{BASE}/kb/documents",
            headers=self.headers,
            name="/api/kb/documents (列表)",
        )

    @task(1)
    def kb_stats(self):
        """知识库统计。"""
        self.client.get(
            f"{BASE}/kb/stats",
            headers=self.headers,
            name="/api/kb/stats (统计)",
        )
