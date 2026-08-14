"""全局异常处理器。

注意：错误详情只记录到服务端日志，不返回给前端——
内部错误信息可能包含文件路径、数据库结构等敏感信息，
泄露给用户会带来安全风险（详情见 security-audit 技能）。
"""
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("rag_ecommerce")


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        # 详细错误只写入服务端日志，方便排查问题
        logger.error(
            "未处理异常 | 路径: %s | 方法: %s | 错误: %s",
            request.url.path,
            request.method,
            exc,
            exc_info=True,
        )
        # 前端只收到通用提示，不暴露内部细节
        return JSONResponse(
            status_code=500,
            content={"detail": "服务器内部错误，请稍后重试"},
        )
