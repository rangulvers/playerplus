import httpx
import requests
from loguru import logger

async def fetch_events():
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", "http://127.0.0.1:8000/events") as response:
            async for chunk in response.aiter_text():
                if chunk:
                    logger.success("Recieved chunk from server")
                    logger.success(chunk.strip())
                    

if __name__ == "__main__":
    import asyncio
    r = requests.get("http://localhost:8000/login")
    if r.status_code == 200:

        asyncio.run(fetch_events())