import requests
from bs4 import BeautifulSoup
from loguru import logger
from pydantic import BaseModel, Field
from typing import List, Optional

class Player(BaseModel):
    name: str
    state: str

class Event(BaseModel):
    id: str
    type: str
    date: str
    link: str
    players: List[Player]

def get_list_of_events(session: requests.Session):
    logger.info("Getting list of events")
    page_number = 1

    while True:
        url = f"https://player.plus/en-gb/events/list?page={page_number}"
        html = fetch_page(session, url)

        table = html.find("table", class_="table-hover")
        if table is None:
            logger.error("No events have been found on this page.")
            break

        rows = table.find_all("tr")

        for row in rows:
            event = parse_event_row(session, row)
            if event:
                yield event.json()

        if not has_next_page(html):
            logger.info("No more pages found.")
            break

        page_number += 1


def fetch_page(session: requests.Session, url: str) -> BeautifulSoup:
    logger.info(f"Fetching page: {url}")
    req = session.get(url).text
    return BeautifulSoup(req, "html.parser")


def parse_event_row(session: requests.Session, row: BeautifulSoup) -> Optional[Event]:
    if "data-key" not in row.attrs:
        logger.error("Warning: 'data-key' attribute missing in row")
        return None

    data_key = row["data-key"]
    event_type = row.select_one("td:nth-of-type(1) a")
    event_date = row.select_one("td:nth-of-type(2)")
    show_link = row.select_one("td:nth-of-type(3) a")

    event_type = event_type.text.strip() if event_type else "N/A"
    event_date = event_date.text.strip() if event_date else "N/A"
    show_link = show_link["href"] if show_link else "N/A"

    event_id = data_key.split("_")[1]
    player_info = get_event_attendance(session, show_link, event_id, event_type)

    return Event(
        id=data_key,
        type=event_type,
        date=event_date,
        link=show_link,
        players=player_info,
    )


def has_next_page(html: BeautifulSoup) -> bool:
    pagination = html.find("ul", class_="pagination")
    next_button = pagination.find("li", class_="next") if pagination else None
    return bool(next_button and next_button.find("a"))


def lazy_load_event_details(session: requests.Session, event_id, event_type):
    url = "https://player.plus/en-gb/events/ajaxgetparticipation"
    payload = {"eventid": event_id, "eventtype": event_type.lower()}
    req = session.post(url, data=payload)
    
    if req.status_code == 200:
        return req.json()


def get_event_attendance(session: requests.Session, event_link, event_id, event_type):
    url = "https://player.plus" + event_link
    html = fetch_page(session, url)

    modal_body = html.find("div", class_="modal-body")
    if not modal_body:
        logger.error("HTML code does not include a div with class 'modal-body'")
        return []

    modal_content = lazy_load_event_details(session, event_id, event_type)
    if not modal_content:
        logger.error("No modal body found in HTML code")
        return []

    return parse_player_info(modal_content)


def parse_player_info(modal_content: dict) -> List[Player]:
    html_content = modal_content.get("html", "")
    modal_content = BeautifulSoup(html_content, "html.parser")
    lists = modal_content.find_all("div", class_="participation-list")

    players = []

    for participation_list in lists:
        header = extract_participation_header(participation_list)
        list_of_players = participation_list.find_all("div", class_="participation-list-user-name")
        
        for player in list_of_players:
            try:
                name = player.text.strip()
                player = Player(name=name, state=header)
                players.append(player)
            except Exception as e:
                logger.error(f"Error: {e}")

    return players


def extract_participation_header(participation_list: BeautifulSoup) -> str:
    header = participation_list.find("div", class_="participation-list-header").text
    return "".join(filter(lambda x: not x.isdigit(), header)).strip()


if __name__ == "__main__":
    pass
