import asyncio
from config import (BATCH_SIZE,
                    OUTPUT_PATH, 
                    RESET_FIRST_PATTERNED_PAGINATION,
                    ALODOKTER_CONFIG, 
                    BIOFARMA_CONFIG, 
                    BPOM_CONFIG, 
                    HALODOC_CONFIG, 
                    HELLOSEHAT_CONFIG)
from core.database import (init_db, 
                           save_pagination, 
                           get_pending_pagination, 
                           update_pagination_status, 
                           get_pending_url,
                           update_url_status,
                           count_success_url,
                           count_failed_url,
                           reset_first_patterned_pagination_status)
from loguru import logger
from core.router import crawler_router, scraper_router
from spiders.alodokter import get_alodokter_pagination
from spiders.biofarma import get_biofarma_pagination
from spiders.bpom import get_bpom_pagination
from spiders.halodoc import get_halodoc_pagination
from spiders.hellosehat import get_hellosehat_pagination, update_obat_suplemen

#============================================================

# main crawler function
async def run_crawler(session):
    '''Run the crawler for all configured websites and categories. 
    This function will iterate through each website and its respective categories, generate the pagination URLs, and dispatch crawling tasks to the appropriate crawler functions via the router.
    
    :param session: an instance of requests.AsyncSession for making http requests.
    '''

    logger.info("Starting crawler general...")

    # initialize the database (create tables if they don't exist)
    await init_db()

    # generate pagination urls for each website and category, then save them to the database
    pagination_data = []
    pagination_data.extend(get_alodokter_pagination(ALODOKTER_CONFIG))
    pagination_data.extend(get_biofarma_pagination(BIOFARMA_CONFIG))
    pagination_data.extend(get_bpom_pagination(BPOM_CONFIG))
    pagination_data.extend(get_halodoc_pagination(HALODOC_CONFIG))
    pagination_data.extend(get_hellosehat_pagination(HELLOSEHAT_CONFIG))

    await save_pagination(pagination_data)

    while True:
        # get a batch of pending pagination urls from the database
        batch_pending_paginations = await get_pending_pagination(BATCH_SIZE)

        if not batch_pending_paginations:
            logger.info('All pagination URLs have been crawled.')
            return
        
        logger.info(f"Crawling {len(batch_pending_paginations)} pending pagination URLs...")

        # dispatch crawling tasks to the appropriate crawler functions via the router
        tasks = []
        for pagination in batch_pending_paginations:
            tasks.append(crawler_router(pagination['pagination_url'], 
                                        pagination['domain'], 
                                        pagination['category'], 
                                        session))
        
        results = await asyncio.gather(*tasks)

        # crawled urls from the crawling tasks will be saved to the url_queue table in each crawler function, 
        # so here we just need to update the status of the crawled pagination urls in the database

        # update the status of the crawled pagination urls in the database
        status_updates = []
        for i, is_success in enumerate(results):
            row_id = batch_pending_paginations[i]['id']
            new_status = 'success' if is_success else 'failed'
            status_updates.append((row_id, new_status))
    
        await update_pagination_status(status_updates)

        logger.info('Crawling has been completed.')

#============================================================

# main scraper function
async def run_scraper(session):
    '''Run the scraper for all configured websites and categories. 
    This function will retrieve the pending URLs from the database and dispatch scraping tasks to the appropriate scraper functions via the router.
    
    :param session: an instance of requests.AsyncSession for making http requests.
    '''

    logger.info("Starting scraper general...")

    # special treatment for obat-suplemen from hellosehat.com
    # update the obat-suplemen
    await update_obat_suplemen()

    while True:
        # get a batch of pending urls from the database
        batch_pending_urls = await get_pending_url(BATCH_SIZE)

        if not batch_pending_urls:
            logger.info('All URLs have been scraped.')
            return
        
        logger.info(f"Scraping {len(batch_pending_urls)} pending URLs...")

        # dispatch scraping tasks to the appropriate scraper functions via the router
        tasks = []
        file_lock = asyncio.Lock
        for url in batch_pending_urls:
            tasks.append(scraper_router(url['url'], 
                                        url['domain'], 
                                        url['category'], 
                                        session,
                                        file_lock,
                                        OUTPUT_PATH))
        
        results = await asyncio.gather(*tasks)

        # update the status of the scraped urls in the database
        status_updates = []
        for i, is_success in enumerate(results):
            row_id = batch_pending_urls[i]['id']
            new_status = 'success' if is_success else 'failed'
            status_updates.append((row_id, new_status))

        await update_url_status(status_updates)

        success = await count_success_url
        failed = await count_failed_url
        logger.info('Scraping has been completed.')
        logger.info(f'Scraping results: {success} success, {failed} failed')

        if RESET_FIRST_PATTERNED_PAGINATION:
            await reset_first_patterned_pagination_status()