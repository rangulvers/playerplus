import requests
from bs4 import BeautifulSoup
from loguru import logger
import os
from dotenv import load_dotenv

URL = "https://player.plus/en-gb/site/login"

load_dotenv(dotenv_path=".env")


def get_csrf_token(session: requests.Session):
    logger.info("Getting CSRF Token")
    req = session.get(URL).text
    html = BeautifulSoup(req, "html.parser")
    csrf_token = html.find("meta", {"name": "csrf-token"})["content"]
    if csrf_token:
        return csrf_token


def login(session: requests.Session, csrf_token: str):
    payload = {
        "LoginForm[email]": os.getenv("USER_NAME"),
        "LoginForm[password]": os.getenv("PASSWORD"),
        "_csrf": "",
    }
    payload["_csrf"] = csrf_token
    logger.info(f"Attempting to login with CSRF Token {payload['_csrf']}")
    p = session.post(URL, data=payload)

    if "loggedin" in p.text:
        logger.success("Successfully logged in")
        return True
    else:
        logger.error("Failed to login")
        return False


if __name__ == "__main__":
    pass