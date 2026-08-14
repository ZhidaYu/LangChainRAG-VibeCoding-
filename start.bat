@echo off
setlocal enabledelayedexpansion
set ROOT=%~dp0
title 电商RAG知识库问答系统 - 一键启动

echo.
echo   ============================================================
echo        电商 RAG 知识库问答系统 - 一键启动
echo   ============================================================
echo.
echo   [1/4] 检查运行环境...
echo.
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYVER=%%i
if "%PYVER%"=="" (
    echo   [X] 未找到 Python，请先安装 Python 3.11+
    pause
    exit /b 1
)
echo         Python: %PYVER%

for /f "tokens=*" %%i in ('node --version 2^>^&1') do set NODEVER=%%i
if "%NODEVER%"=="" (
    echo   [X] 未找到 Node.js，请先安装 Node.js 18+
    pause
    exit /b 1
)
echo         Node.js: %NODEVER%
echo.
echo   [2/4] 配置 Python 后端...
cd /d "%ROOT%backend"
if exist "venv\Lib\site-packages\fastapi" (
    echo         Python 依赖已就绪
) else (
    echo         正在安装 Python 依赖...
    venv\Scripts\python.exe -m pip install -r requirements.txt -q
    echo         Python 依赖安装完成
)
echo         启动后端服务 (FastAPI)...
start "RAG-Backend" cmd /k "venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo         后端已在新窗口中启动
echo.
echo   [3/4] 配置前端...
cd /d "%ROOT%frontend"
if exist "node_modules\antd" (
    echo         前端依赖已就绪
) else (
    echo         正在安装前端依赖...
    call npm install
    echo         前端依赖安装完成
)
echo         启动前端服务 (Vite)...
start "RAG-Frontend" cmd /k "npm run dev"
echo         前端已在新窗口中启动
echo.
echo   [4/4] 启动完成!
echo.
echo   ============================================================
echo.
echo     系统启动中，请等待两个新窗口就绪（约 5-10 秒）
echo.
echo     前端地址:   http://localhost:5173
echo     后端 API:   http://localhost:8000
echo     API 文档:   http://localhost:8000/docs
echo     管理员账号:  admin / 123456
echo.
echo     关闭此窗口不会影响已启动的服务
echo.
echo   ============================================================
echo.
set /p OPEN=是否打开前端页面? (Y/N): 
if /i "%OPEN%"=="Y" start http://localhost:5173
pause
