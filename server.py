from fastapi import FastAPI
import uvicorn
import requests

from api import auth, events

app = FastAPI()

session = requests.Session()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/login")
def get_login():
    csrf_token = auth.get_csrf_token(session=session)
    return auth.login(session=session, csrf_token=csrf_token)
    

@app.get("/events")
def get_events():
    all_events = events.get_list_of_events(session)
    return all_events

@app.get("/polls")
def get_polls():
    return {"polls": "polls"}

@app.get("/chat")
def get_chat():
    return {"chat": "chat"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)