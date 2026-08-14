"""一键启动脚本 - 启动后端服务"""
import os
import sys
import subprocess

def main():
    print("=" * 60)
    print("  电商RAG知识库问答系统 - 后端启动")
    print("=" * 60)

    # Get the project root
    root = os.path.dirname(os.path.abspath(__file__))

    # Ensure data directories exist
    os.makedirs(os.path.join(root, "data", "raw"), exist_ok=True)
    os.makedirs(os.path.join(root, "data", "chroma"), exist_ok=True)

    # Start uvicorn
    print("\n启动 FastAPI 服务 (http://localhost:8000)...")
    print("API 文档: http://localhost:8000/docs")
    print("健康检查: http://localhost:8000/api/health")
    print("\n按 Ctrl+C 停止服务\n")

    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload",
    ], cwd=root)

if __name__ == "__main__":
    main()
