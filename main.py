import asyncio
from curl_cffi import requests
from core.engine import run_crawler, run_scraper
import random

async def main():
    async with requests.AsyncSession() as session:
        await run_crawler(session)

        await asyncio.sleep(random.uniform(3, 5))

        await run_scraper(session)

if __name__ == "__main__":
    asyncio.run(main())