from loguru import logger
from spiders.alodokter import crawl_alodokter_page, scrape_alodokter_content
from spiders.biofarma import crawl_biofarma_page, scrape_biofarma_content
from spiders.bpom import crawl_bpom_page, scrape_bpom_content
from spiders.halodoc import crawl_halodoc_page, scrape_halodoc_content
from spiders.hellosehat import crawl_hellosehat_page, scrape_hellosehat_content


FUNCTION_REGISTRY = {
    'alodokter.com': {'crawler': crawl_alodokter_page,
                      'scraper': scrape_alodokter_content},
    'biofarma.co.id': {'crawler': crawl_biofarma_page,
                       'scraper': scrape_biofarma_content},
    'pom.go.id': {'crawler': crawl_bpom_page,
                   'scraper': scrape_bpom_content},
    'halodoc.com': {'crawler': crawl_halodoc_page,
                     'scraper': scrape_halodoc_content},
    'hellosehat.com': {'crawler': crawl_hellosehat_page,
                       'scraper': scrape_hellosehat_content}
}

#============================================================

# crawler router function
async def crawler_router(url: str, domain: str, category: str, session):
    '''Distribute crawling tasks to the appropriate crawler functions based on the website domain.
    
    :param url: URL to be crawled.
    :param domain: domain of the website to determine which crawler to use.
    :param category: category of the content to be crawled (e.g., article, discussion).
    :param session: an instance of requests.AsyncSession for making http requests.
    :return: a boolean indicating whether the crawling was successful or not.
    '''
    if domain in FUNCTION_REGISTRY:
        crawler_func = FUNCTION_REGISTRY[domain]['crawler']

        return await crawler_func(url, domain, category, session)
        
    else:
        logger.error(f"No crawler function registered for domain: {domain}")
        return False

#============================================================

# scraper router function
async def scraper_router(url: str, domain: str, category: str, session, file_lock, output_path: str):
    '''Distribute scraping tasks to the appropriate scraper functions based on the website domain.
    
    :param url: URL to be scraped.
    :param domain: domain of the website to determine which scraper to use.
    :param category: category of the content to be scraped (e.g., article, discussion).
    :param session: an instance of requests.AsyncSession for making http requests.
    :param file_lock: a lock for synchronizing file access.
    :param output_path: the path where the scraped data will be saved.
    :return: a boolean indicating whether the scraping was successful or not.
    '''
    if domain in FUNCTION_REGISTRY:
        scraper_func = FUNCTION_REGISTRY[domain]['scraper']

        return await scraper_func(url, domain, category, session, file_lock, output_path)
        
    else:
        logger.error(f"No scraper function registered for domain: {domain}")
        return False