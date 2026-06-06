import aiofiles
from bs4 import BeautifulSoup
from core.database import save_url
from core.utils import count_token, fetch_html, html_to_markdown
from datetime import datetime, timedelta, timezone
import hashlib
import json
from loguru import logger
from pathlib import Path
from urllib.parse import urljoin
import uuid

#============================================================

def get_hellosehat_pagination(config):
    '''Generate patterned pagination URLs to be crawled data for hellosehat.com based on the provided configuration.

    :param config: a dictionary containing the website domain and the number of pages to be crawled for each category (also unpatterned page content to be scraped if there exists).
    :return: a list of tuples containing pagination url, domain, and category.
    
    Example config:
    HELLOSEHAT_CONFIG = {
        'domain': 'hellosehat.com',
        'pages_2b_crawled': {
            '/page/': 1,
            '/discussion/': 2,
        },
        'contents_2b_scraped' : ...
    }

    >>> get_hellosehat_pagination(HELLOSEHAT_CONFIG)
    [('https://hellosehat.com/page/1', 'hellosehat.com', 'article'), 
     ('https://hellosehat.com/discussion/1', 'hellosehat.com', 'discussion'),
     ('https://hellosehat.com/discussion/2', 'hellosehat.com', 'discussion')]
    '''

    domain = config['domain']
    pages_2b_crawled = config['pages_2b_crawled']
    pages = list(pages_2b_crawled.keys())
    max_pages = list(pages_2b_crawled.values())

    pagination_data = []
    for page, max_page in zip(pages, max_pages):
        for i in range(1, max_page + 1):
            pagination_url = f'https://{domain}{page}{i}'

            category = 'article'

            pagination_data.append((pagination_url, domain, category))
    
    return pagination_data



async def update_obat_suplemen(config):
    '''Add new obat suplemen URL if there is an update and take max pages to be scraped from config.
    
    :param config: a dictionary containing the website domain and the number of pages to be crawled for each category (also unpatterned page content to be scraped if there exists).'''
    
    obat_suplemen_key = list(config['contents_2b_scraped'].keys())[0]

    # get all current obat suplemen urls 
    obat_suplemen_path = Path(obat_suplemen_key)
    obat_suplemen_path.touch(exist_ok=True)

    current_obat_suplemen = set()
    with open(obat_suplemen_path, mode = 'r', encoding = 'utf-8') as f:
        for line in f.readlines():
            current_obat_suplemen.add(line.strip())
    
    # add new url if there is an update
    html = await fetch_html('https://hellosehat.com/obat-suplemen/')
    if not html:
        return 
    
    soup = BeautifulSoup(html, 'html.parser')
    cards = soup.select('h5 a')
    all_href = [card.get('href') for card in cards if card.get('href', '')]

    new_obat_suplemen = set()
    for href in all_href:
        new_obat_suplemen.add(href)
    
    # add to the url table in the database
    max_page = config['contents_2b_scraped'][obat_suplemen_key]
    obat_suplemen_urls = [(f'https://{urljoin("hellosehat.com", obat_suplemen)}', 
                           'hellosehat.com', 
                           'article') 
                           for obat_suplemen in list(new_obat_suplemen)[:max_page]]

    await save_url(obat_suplemen_urls)

    # add to the obat_suplemen.txt
    new_urls = new_obat_suplemen - current_obat_suplemen
    if new_urls:
        with open(obat_suplemen_path, mode = 'a', encoding = 'utf-8') as f:
            for url in new_urls:
                f.write(new_urls + '\n')



async def crawl_hellosehat_page(url: str, domain: str, category: str, session):
    '''Extract the article URLs from a single pagination URL for hellosehat.com.
    
    :param url: the pagination URL to be crawled.
    :param domain: the domain of the website (hellosehat.com).
    :param category: the category of the content to be crawled.
    :param session: an instance of requests.AsyncSession for making http requests.
    :return: a boolean indicating whether the crawling was successful or not.
    '''

    html = await fetch_html(url, session)
    if not html:
        return False
    
    soup = BeautifulSoup(html, 'html.parser')

    cards = soup.select('div.banner a')

    found_urls = [(f'https://{urljoin(domain, card.get('href'))}',
                   domain,
                   category) 
                   for card in cards if card.get('href', '')]
    
    if found_urls:
        await save_url(found_urls)
        return True
    else:
        logger.warning(f'No URLs Found in {url}')
        return False



async def scrape_hellosehat_content(url: str, domain: str, category: str, session, file_lock, output_path: str):
    '''Extract the content and metadata of article URLs from a single URL for hellosehat.com.
    
    :param url: the pagination URL to be scraped.
    :param domain: the domain of the website (hellosehat.com).
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
    title_html = soup.select_one('div h1')
    title = title_html.get_text(strip = True) if title_html else ''

    # content
    content_html = soup.select_one('div.unique-content-wrapper')

    if not content_html:
        logger.warning(f'No content found in {url}')
        return False
    
    content_md = html_to_markdown(str(content_html))

    # date
    last_updated_html = soup.select_one('p.author')
    last_updated = last_updated_html.get_text(strip = True) if last_updated_html else ''
    last_updated_splitted = last_updated.split(' · ')
    date = last_updated_splitted[0]

    # author
    writer = last_updated_splitted[-1]
    
    reviewer_html = soup.select_one('div.information a')
    reviewer = reviewer_html.get_text(strip = True) if reviewer_html else ''

    author = (' & ').join([writer, reviewer])

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