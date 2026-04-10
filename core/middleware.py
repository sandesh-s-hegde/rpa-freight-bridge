import time
import uuid
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from core.context import correlation_id_ctx

logger = logging.getLogger("rpa-bridge")


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        correlation_id_ctx.set(req_id)

        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        logger.info(f"Path: {request.url.path} | Duration: {process_time:.4f}s")
        response.headers["X-Correlation-ID"] = req_id
        return response
