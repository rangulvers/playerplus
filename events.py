import requests
from bs4 import BeautifulSoup
from loguru import logger
from tqdm import tqdm

def get_list_of_events(session: requests.Session):
    logger.info("Getting list of events")
    events = []
    page_number = 1

    while True:
        logger.info(f"Fetching page {page_number}")
        url = f"https://player.plus/en-gb/events/list?page={page_number}"
        req = session.get(url).text
        html = BeautifulSoup(req, "html.parser")

        table = html.find("table", class_="table-hover")
        if table is None:
            logger.error("No events have been found on this page.")
            break

        rows = table.find_all("tr")

        for row in tqdm(rows):
            if "data-key" in row.attrs:
                data_key = row["data-key"]
                event_type = row.select_one("td:nth-of-type(1) a")
                event_date = row.select_one("td:nth-of-type(2)")
                show_link = row.select_one("td:nth-of-type(3) a")

                event_type = event_type.text if event_type else "N/A"
                event_date = event_date.text if event_date else "N/A"
                show_link = show_link["href"] if show_link else "N/A"

                event_id = data_key.split("_")[1]
                player_info = get_event_attendance(session, show_link, event_id, event_type)

                event = {
                    "id": data_key,
                    "type": event_type,
                    "date": event_date,
                    "link": show_link,
                    "players": player_info,
                }
                events.append(event)
            else:
                logger.error("Warning: 'data-key' attribute missing in row")
                continue

        pagination = html.find("ul", class_="pagination")
        next_button = pagination.find("li", class_="next") if pagination else None
        if next_button and next_button.find("a"):
            page_number += 1
        else:
            logger.info("No more pages found.")
            break

    return events


def lazy_load_event_details(session: requests.Session, event_id, event_type):
    url = "https://player.plus/en-gb/events/ajaxgetparticipation"
    payload = {"eventid": event_id, "eventtype": event_type.lower()}
    req = session.post(url, data=payload)
    
    if req.status_code == 200:
        return req.json()


def get_event_attendance(session: requests.Session, event_link, event_id, event_type):
    url = "https://player.plus" + event_link
    req = session.get(url).text
    html = BeautifulSoup(req, "html.parser")

    modal_body = html.find("div", class_="modal-body")
    if modal_body:
        modal_content = lazy_load_event_details(session, event_id, event_type)
        if modal_content:
            html_content = modal_content.get("html", "")
            modal_content = BeautifulSoup(html_content, "html.parser")
            lists = modal_content.find_all("div", class_="participation-list")

            players = []

            for participation_list in lists:
                header = participation_list.find("div", class_="participation-list-header").text
                header = "".join(filter(lambda x: not x.isdigit(), header)).strip()
                list_of_players = participation_list.find_all("div", class_="participation-list-user-name")
                
                for player in list_of_players:
                    try:
                        name = player.text
                        player = {"name": name, "state": header}
                        players.append(player)
                    except Exception as e:
                        logger.error(f"Error: {e}")
                        pass

            return players
        else:
            logger.error("No modal body found in HTML code")
    else:
        logger.error("HTML code does not include a div with class 'modal-body'")


if __name__ == "__main__":
    pass
