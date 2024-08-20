import requests
from loguru import logger
import auth
import events
import stats
import os
from dotenv import load_dotenv


def main():
    # Load environment variables from .env file
    dotenv_loaded = load_dotenv(dotenv_path=".env")
    print(f'Current Working Directory: {os.getcwd()}')

    print(f'.env file loaded: {dotenv_loaded}')  # This should print True if the file was found and loaded

    logger.error("LOADING OS")
    print(os.getenv("USER_NAME"))

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
        
        # print(stats.player_attendance_stats(df))

        # stats.plot_attendance_line(df)

        return df

if __name__ == "__main__":
    main()
