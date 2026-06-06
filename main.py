import asyncio
from curl_cffi import requests
from core.engine import run_crawler, run_scraper
from loguru import logger

logger.add("healthy_spiders_{time:YYYY-MM-DD}.log",
         rotation="00:00",        # new file daily
         retention="1 week",      # keep 1 week of logs
         format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")

async def main():
    logger.info('Starting healthy spiders 💪🕷️...')

    async with requests.AsyncSession() as session:
        await run_crawler(session)

        await asyncio.sleep(5)

        await run_scraper(session)

    logger.info('Healthy spiders are going to sleep 💪🕷️💤...')

if __name__ == "__main__":
    asyncio.run(main())