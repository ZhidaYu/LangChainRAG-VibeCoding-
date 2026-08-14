"""批量创建压力测试用户（直连数据库，秒级完成）。

用法：
    cd stress-test
    ../backend/venv/Scripts/python.exe seed_users.py

行为：
    - 删除旧的 stress_user_* 用户（幂等，可重复执行）
    - 创建 stress_user_001 ~ stress_user_100，统一密码 stress123456
    - bcrypt 哈希只计算一次后复用（避免 100 次慢哈希）
"""
import asyncio
import os
import sys

# 确保能 import 后端代码
BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, BACKEND_DIR)

# 切到 backend 目录：DATABASE_URL 是相对路径（./data/...），否则会开到错误的数据库
os.chdir(BACKEND_DIR)

from sqlalchemy import delete, select  # noqa: E402
from app.database import engine, AsyncSessionLocal  # noqa: E402
from app.models.user import User  # noqa: E402
from app.services.auth_service import hash_password  # noqa: E402

USER_COUNT = 100
PASSWORD = "stress123456"


async def main():
    # 预计算一次哈希（bcrypt 慢，100 次太浪费）
    password_hash = hash_password(PASSWORD)
    print(f"密码哈希计算完成（复用 {USER_COUNT} 次）")

    async with AsyncSessionLocal() as session:
        # 清理旧压测用户（幂等）
        result = await session.execute(
            delete(User).where(User.username.like("stress_user_%"))
        )
        deleted = result.rowcount
        if deleted:
            print(f"已删除旧压测用户 {deleted} 个")

        # 批量插入新用户
        for i in range(1, USER_COUNT + 1):
            session.add(User(
                username=f"stress_user_{i:03d}",
                password_hash=password_hash,
                role="user",
            ))
        await session.commit()
        print(f"已创建 {USER_COUNT} 个压测用户 (stress_user_001 ~ stress_user_{USER_COUNT:03d})")

        # 验证
        result = await session.execute(
            select(User).where(User.username.like("stress_user_%"))
        )
        count = len(result.scalars().all())
        print(f"验证：数据库中共 {count} 个压测用户")

    await engine.dispose()
    print("完成！")


if __name__ == "__main__":
    asyncio.run(main())
