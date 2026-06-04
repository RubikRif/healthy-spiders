import aiosqlite
from loguru import logger

DB_PATH = "queue.db"

#============================================================

# database initialization
async def init_db():
    '''Initialize pagination queue table and URL queue table if they don't exist.'''
    
    async with aiosqlite.connect(DB_PATH) as db:
        # create pagination_queue table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS pagination_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pagination_url TEXT UNIQUE NOT NULL,
                domain TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'article',
                status TEXT NOT NULL DEFAULT 'pending'
            )
        ''')

        # create url_queue table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS url_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                domain TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'article',
                status TEXT NOT NULL DEFAULT 'pending'
            )
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

    >> get_pending_pagination(5)
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
    '''Update the status of pagination URLs in the pagination_queue table after batchcrawling.
    
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
    '''Save article URLs to be crawled along with their domain and category into the url_queue table.
    
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
    '''Get a batch of pending article URLs from the url_queue table randomly.
    
    :param batch_size: number of article URLs to retrieve in one batch.
    :return: list of tuples (id, url, domain, category).

    >> get_pending_url(5)
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
    '''Update the status of article URLs in the url_queue table after batch crawling.
    
    :param task_results: list of tuples (id, status) where id is the url id and status is a string indicating the crawling result.
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

# reset n-th first pagination status
async def reset_pagination_status(n: int):

    async with aiosqlite.connect(DB_PATH) as db:
        for i in range(1, n + 1):
            await db.execute('''
            UPDATE pagination_queue
            SET status = 'pending'
            WHERE domain = 'alodokter.com' 
                AND 
                pagination_url LIKE                              
            ''')
    pass