from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import uvicorn
import requests
from typing import Optional

from api import auth, events
from middelware.authentication import LoginMiddleware
from middelware.logging import LoggingMiddleware

app = FastAPI()

session = requests.Session()
app.add_middleware(LoginMiddleware, session=session)
app.add_middleware(LoggingMiddleware, session=session)

@app.get("/")
def read_root():
    return {"message": "Welcome to the PlayerPlus API!"}

@app.get("/login")
def get_login():
    csrf_token = auth.get_csrf_token(session=session)
    return auth.login(session=session, csrf_token=csrf_token)

@app.get("/events")
@app.get("/events/{event_type}")
def get_events(event_type: Optional[str] = None):
    all_events = events.get_list_of_events(session, event_type)
    return StreamingResponse(all_events, media_type="application/json")

@app.get("/polls")
def get_polls():
    return {"polls": "polls"}

@app.get("/chat")
def get_chat():
    return {"chat": "chat"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)