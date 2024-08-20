import requests
from loguru import logger
import auth
import events
import stats
import os
from dotenv import load_dotenv


def main():
    load_dotenv(dotenv_path=".env")
    
    payload = {
        "LoginForm[email]": os.getenv("USER_NAME"),
        "LoginForm[password]": os.getenv("PASSWORD"),
        "_csrf": "",
    }
    with requests.Session() as session:
        csrf_token = auth.get_csrf_token(session)
        payload["_csrf"] = csrf_token
        if auth.login(session=session, payload=payload):
            all_events = events.get_list_of_events(session)
        df = stats.create_data_frame(all_events)
        return df

if __name__ == "__main__":
    logger.success("Starting the app")
    main()
