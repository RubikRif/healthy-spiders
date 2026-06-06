import aiofiles
from bs4 import BeautifulSoup
from core.database import save_url
from core.utils import count_token, fetch_html, html_to_markdown, standardize_date
from datetime import datetime, timedelta, timezone
import hashlib
import json
from loguru import logger
import uuid

#============================================================

def get_bpom_pagination(config):
    '''Generate patterned pagination URLs to be crawled data for pom.go.id based on the provided configuration.
    
    :param config: a dictionary containing the domain and pages to be crawled for each category (also unpatterned page content to be scraped if there exists).
    :return: a list of tuples containing pagination url, domain, and category.
    
    Example of config:
    BPOM_CONFIG = {
        'domain': 'pom.go.id',
        'pages_2b_crawled': {
            '/page/': 1,
            '/discussion/': 2
        },
        'contents_2b_scraped' : ...
    }

    >>> get_bpom_pagination(BPOM_CONFIG)
    [('https://www.pom.go.id/page/1', 'pom.go.id', 'article'), 
     ('https://www.pom.go.id/discussion/1', 'pom.go.id', 'discussion'),
     ('https://www.pom.go.id/discussion/2', 'pom.go.id', 'discussion')]
    '''

    domain = config['domain']
    pages_2b_crawled = config['pages_2b_crawled']
    pages = list(pages_2b_crawled.keys())
    max_pages = list(pages_2b_crawled.values())

    pagination_data = []
    for page, max_page in zip(pages, max_pages):
        for i in range(1, max_page + 1):
            pagination_url = f'https://www.{domain}{page}{i}'

            if page == '/penjelasan-publik?page=':
                category = 'public explanation'
            elif page == '/siaran-pers?page=':
                category = 'press release'
            elif page == '/berita?page=':
                category = 'news'

            pagination_data.append((pagination_url, domain, category))
    
    return pagination_data



async def crawl_bpom_page(url: str, domain: str, category: str, session) -> bool:
    '''Extract the public explanation, press release, or news URLs from a single pagination URL for pom.go.id.
    
    :param url: the pagination URL to be crawled.
    :param domain: the domain of the website (pom.go.id).
    :param category: the category of the content to be crawled.
    :param session: an instance of requests.AsyncSession for making http requests.
    :return: a boolean indicating whether the crawling was successful or not.
    '''
    
    html = await fetch_html(url, session)
    if not html:
        return False
    
    soup = BeautifulSoup(html, 'html.parser')

    cards = soup.select('a.py-3')
    found_urls = [(f'https://www.{domain}{card.get('href')}',
                   domain,
                   category) 
                   for card in cards if card.get('href', '')]

    if found_urls:
        await save_url(found_urls)
        return True
    else:
        logger.warning(f'No URLs Found in {url}')
        return False



async def scrape_bpom_content(url: str, domain: str, category: str, session, file_lock, output_path: str) -> bool:
    '''Extract the content and metadata of public explanation, press release, or news URLs from a single URL for pom.go.id.
    
    :param url: the pagination URL to be scraped.
    :param domain: the domain of the website (pom.go.id).
    :param category: the category of the content to be scraped.
    :param session: an instance of requests.AsyncSession for making http requests.
    :param file_lock: a lock for synchronizing file access.
    :param output_path: the path where the scraped data will be saved.
    :return: a boolean indicating whether the scraping was successful or not.
    '''
    
    html = await fetch_html(url, session)
    if not html:
        return False
    
    soup = BeautifulSoup(html, 'html.parser')

    # title
    title_html = soup.select_one('div.d-block h1')
    title = title_html.get_text(strip = True) if title_html else ''

    # content
    content_html = soup.select_one('div.col-12')

    if not content_html:
        logger.warning(f'No content found in {url}')
        return False
    
    content_md = html_to_markdown(str(content_html))

    # date
    last_updated_html = soup.select_one('div.d-block p')
    last_updated = last_updated_html.get_text(strip = False) if last_updated_html else ''
    last_updated_splitted = last_updated.split('  ')
    date = last_updated_splitted[0].strip()
    date = standardize_date(date)

    # author
    author = last_updated_splitted[-1].strip()

    doc_id = str(uuid.uuid4())
    doc_hash = hashlib.sha256(content_md.encode('utf-8')).hexdigest()

    payload = {
        'id': doc_id,
        'text': content_md,
        'content_hash': doc_hash,
        'metadata': {
            'title': title,
            'url': url,
            'domain': domain,
            'category': category,
            'last_updated': date,
            'author': author,
            'source_modality': 'html',
            'extraction_method': 'beautifulsoup',
            'language': 'id',
            'domain_labels': ['health'],
            'token_count': count_token(content_md),
            'extraction_timestamp': datetime.now(timezone(timedelta(hours = 7))).isoformat()
        }
    }

    # write payload to output file
    async with file_lock:
        async with aiofiles.open(output_path, mode = 'a', encoding = 'utf-8') as f:
            await f.write(json.dumps(payload, ensure_ascii = False) + '\n')

    return True


