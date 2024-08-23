# logging_middleware.py
from loguru import logger
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import sys
import uuid


logger.remove()
logger.add(sys.stdout, colorize=True)

class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, session):
        super().__init__(app)
        self.session = session

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        session_id = self.session.cookies.get('sessionid', 'No session ID')
        logger.info(f"Incoming request: {request_id} {session_id} {request.method} {request.url}")
        response = await call_next(request)
        logger.info(f"Outgoing response: {request_id} {response.status_code}")
        return response