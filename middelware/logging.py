# logging_middleware.py
from loguru import logger
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import sys
import uuid

logger.remove()
logger.add(sys.stdout, colorize=True)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())        
        logger.info(f"Incoming request: id={request_id} {request.method} {request.url}")
        response = await call_next(request)
        logger.info(f"Outgoing response: id={request_id} {response.status_code}")
        return response