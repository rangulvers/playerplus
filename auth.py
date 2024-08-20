import requests
from bs4 import BeautifulSoup
from loguru import logger

URL = "https://player.plus/en-gb/site/login"


def get_csrf_token(session: requests.Session):
    logger.info("Getting CSRF Token")
    req = session.get(URL).text
    html = BeautifulSoup(req, "html.parser")
    csrf_token = html.find("meta", {"name": "csrf-token"})["content"]
    if csrf_token:
        return csrf_token


def login(session: requests.Session, payload: dict):
    logger.info(f"Attempting to login with CSRF Token {payload['_csrf']}")
    p = session.post(URL, data=payload)

    if "loggedin" in p.text:
        logger.info("Successfully logged in")
        return True
    else:
        logger.error("Failed to login")
        return False
