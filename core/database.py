import aiosqlite
from config import (DB_PATH,
                    ALODOKTER_CONFIG,
                    BIOFARMA_CONFIG,
                    BPOM_CONFIG,
                    HALODOC_CONFIG,
                    HELLOSEHAT_CONFIG)
from loguru import logger

#============================================================

# database initialization
async def init_db():
    '''Initialize pagination queue table and URL queue table if they don't exist.'''
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript('''
            -- create pagination_queue table
            CREATE TABLE IF NOT EXISTS pagination_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pagination_url TEXT UNIQUE NOT NULL,
                domain TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'article',
                status TEXT NOT NULL DEFAULT 'pending'
            );

            -- create url_queue table
            CREATE TABLE IF NOT EXISTS url_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                domain TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'article',
                status TEXT NOT NULL DEFAULT 'pending'
            );
        ''')
        
        await db.commit()
    
    logger.info("Database initialized.")

#============================================================

# crawler: pagination queue functions
async def save_pagination(urls_data: list):
    '''Save pagination URLs to be crawled along with their domain and category into the pagination_queue table.
    
    :param urls_data: list of tuples (pagination_url, domain, category).
    '''

    async with aiosqlite.connect(DB_PATH) as db:
        for found_url, dom, cat in urls_data:
            await db.execute('''
                INSERT OR IGNORE INTO pagination_queue (pagination_url, domain, category)
                VALUES (?, ?, ?)
            ''', (found_url, dom, cat))

        await db.commit()

async def get_pending_pagination(batch_size: int) -> list:
    '''Get a batch of pending pagination URLs from the pagination_queue table randomly.
    
    :param batch_size: number of pagination urls to retrieve in one batch.
    :return: list of tuples (id, pagination_url, domain, category).

    >>> get_pending_pagination(5)
    [(5, 'https://example1.com/page/3', 'example1.com', 'article'),
     (2, 'https://example3.com/page/5', 'example3.com', 'discussion'),
     (4, 'https://example2.com/page/1', 'example2.com', 'article'),
     (1, 'https://example2.com/page/4', 'example2.com', 'article'),
     (3, 'https://example1.com/page/2', 'example1.com', 'discussion')]
    '''
    
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT id, pagination_url, domain, category
            FROM pagination_queue
            WHERE status = 'pending'
            ORDER BY RANDOM()
            LIMIT ?
        ''', (batch_size,))
        
        rows = await cursor.fetchall()
    
    return rows

async def update_pagination_status(task_results: list):
    '''Update the status of pagination URLs in the pagination_queue table after batch crawling.
    
    :param task_results: list of tuples (id, status) where id is the pagination url id and status is a string indicating the crawling result.
    '''
    
    async with aiosqlite.connect(DB_PATH) as db:
        for pagination_id, status in task_results:
            new_status = status
            await db.execute('''
                UPDATE pagination_queue
                SET status = ?
                WHERE id = ?
            ''', (new_status, pagination_id))
        
        await db.commit()

#============================================================

# scraper: url queue functions
async def save_url(urls_data: list):
    '''Save URLs to be scraped along with their domain and category into the url_queue table.
    
    :param urls_data: list of tuples (url, domain, category).
    '''

    async with aiosqlite.connect(DB_PATH) as db:
        for found_url, dom, cat in urls_data:
            await db.execute('''
                INSERT OR IGNORE INTO url_queue (url, domain, category)
                VALUES (?, ?, ?)
            ''', (found_url, dom, cat))

        await db.commit()

async def get_pending_url(batch_size: int) -> list:
    '''Get a batch of pending URLs from the url_queue table randomly.
    
    :param batch_size: number of to be scraped URLs to retrieve in one batch.
    :return: list of tuples (id, url, domain, category).

    >>> get_pending_url(5)
    [(10, 'https://example1.com/article/123', 'example1.com', 'article'),
     (7, 'https://example3.com/discussion/456', 'example3.com', 'discussion'),
     (9, 'https://example2.com/article/789', 'example2.com', 'article'),
     (6, 'https://example2.com/article/101', 'example2.com', 'article'),
     (8, 'https://example1.com/discussion/112', 'example1.com', 'discussion')]
    '''
    
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT id, url, domain, category
            FROM url_queue
            WHERE status = 'pending'
            ORDER BY RANDOM()
            LIMIT ?
        ''', (batch_size,))
        
        rows = await cursor.fetchall()
    
    return rows

async def update_url_status(task_results: list):
    '''Update the status of URLs in the url_queue table after batch scraping.
    
    :param task_results: list of tuples (id, status) where id is the url id and status is a string indicating the scraping result.
    '''
    
    async with aiosqlite.connect(DB_PATH) as db:
        for url_id, status in task_results:
            new_status = status
            await db.execute('''
                UPDATE url_queue
                SET status = ?
                WHERE id = ?
            ''', (new_status, url_id))
        
        await db.commit()

#============================================================

# utility database functions

# count success scraped urls
async def count_success_url() -> int:
    '''Count URLs that successfully have been scraped.
    
    :return: integer indicating numbers of urls that successfully have been scraped.
    '''

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
                    SELECT COUNT(*)
                    FROM url_queue
                    WHERE status = 'success'
                ''')
    
        row = await cursor.fetchone()
        success = row[0] if row else 0

    return success

# count failed scraped urls
async def count_failed_url():
    '''Count URLs that failed to scrape.
    
    :return: integer indicating numbers of urls that failed to scrape.
    '''
    
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
                    SELECT COUNT(*)
                    FROM url_queue
                    WHERE status = 'failed'
                ''')
    
        row = await cursor.fetchone()
        failed = row[0] if row else 0
    
    return failed

#============================================================

# functions for reset status

# reset first patterned pagination status
async def reset_first_patterned_pagination_status():
    '''Reset the first patterned pagination status to get new URL if there is an update in the website.'''

    # we don't include halodoc config, since its crawling-scraping mechanism is different
    configs = [ALODOKTER_CONFIG, BIOFARMA_CONFIG, BPOM_CONFIG, HELLOSEHAT_CONFIG] 

    first_patterned_paginations = []
    for config in configs:
        domain = config['domain']
        pages_2b_crawled = list(config['pages_2b_crawled'].keys())

        for page_2b_crawled in pages_2b_crawled:
            if domain == 'hellosehat.com':
                first_patterned_paginations.append(f'https://{domain}{page_2b_crawled}1')
                    
            else:
                first_patterned_paginations.append(f'https://www.{domain}{page_2b_crawled}1')
                    
    async with aiosqlite.connect(DB_PATH) as db:
        for first_patterned_pagination in first_patterned_paginations:
            await db.execute('''
                UPDATE pagination_queue
                SET status = 'pending'
                WHERE pagination_url = ?
            ''', (first_patterned_pagination,))
        
        await db.commit()

# reset all halodoc pagination
async def reset_all_halodoc_pagination():
    '''Reset all of the halodoc.com pagination status to get new URL if there is an update in the website.'''

    config = HALODOC_CONFIG
    pages_2b_crawled = config['pages_2b_crawled']
    pages = list(pages_2b_crawled.keys())
    max_pages = list(pages_2b_crawled.values())

    all_halodoc_paginations =  []
    for page, max_page in zip(pages, max_pages):
        for i in range(1, max_page + 1):
            pagination_url = f"{page}{chr(96 + i)}" # convert 1 to 'a', 2 to 'b', etc.

            all_halodoc_paginations.append(pagination_url)
    
    async with aiosqlite.connect(DB_PATH) as db:
        for halodoc_pagination in all_halodoc_paginations:
            await db.execute('''
                UPDATE pagination_queue
                SET status = 'pending'
                WHERE pagination_url = ?
            ''', (halodoc_pagination,))
        
        await db.commit()

# reset all failed pagination
async def reset_all_failed_pagination():
    '''Reset all paginations with failed status to pending so that they can be re-crawled when the next main script run.'''

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
                    UPDATE pagination_queue
                    SET status = 'pending'
                    WHERE status = 'failed'
                ''')
        
        rows_affected = cursor.rowcount

        await db.commit()
    
    if rows_affected > 0:
        logger.info(f"Successfully reset {rows_affected} failed paginations status to 'pending'.")
    else:
        logger.info('There is no failed pagination to reset.')
    
    return rows_affected

# reset all failed url
async def reset_all_failed_url():
    '''Reset all URLs with failed status to pending so that they can be re-scraped when the next main script run.'''
    
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
                    UPDATE url_queue
                    SET status = 'pending'
                    WHERE status = 'failed'
                ''')
        
        rows_affected = cursor.rowcount

        await db.commit()
    
    if rows_affected > 0:
        logger.info(f"Successfully reset {rows_affected} failed URLs status to 'pending'.")
    else:
        logger.info('There is no failed URL to reset.')

    return rows_affected