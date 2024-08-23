# middleware.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from api.auth import login, get_csrf_token
import requests


class LoginMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, session: requests.Session):
        super().__init__(app)
        self.session = session
        self.logged_in = False

    async def dispatch(self, request: Request, call_next):
        if not self.logged_in:
            csrf_token = get_csrf_token(self.session)
            self.logged_in = login(self.session, csrf_token)
            if not self.logged_in:
                raise HTTPException(status_code=401, detail="Unauthorized")
        response = await call_next(request)
        return response
