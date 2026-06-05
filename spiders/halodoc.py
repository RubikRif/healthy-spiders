import aiofiles
from bs4 import BeautifulSoup
from core.database import save_url
from core.utils import count_token, fetch_html, html_to_markdown, standardize_date
from datetime import datetime, timedelta, timezone
import hashlib
import json
from loguru import logger
from pathlib import Path
from urllib.parse import urljoin
import uuid

def get_halodoc_pagination(config):
    '''Generate pagination URLs for halodoc.com articles based on the provided configuration.
    
    :param config: a dictionary containing the domain and pagination configuration for halodoc.
    :return: a list of tuples containing pagination url, domain, and category.

    Example of config:
    HALODOC_CONFIG = {
        'domain': 'halodoc.com',
        'pages_2b_crawled': {
            '/page/': 1,
            '/discussion/': 2
        }
    }

    >> get_halodoc_pagination(HALODOC_CONFIG)
    [('https://halodoc.com/page/1', 'halodoc.com', 'article'), 
     ('https://halodoc.com/discussion/1', 'halodoc.com', 'discussion'),
     ('https://halodoc.com/discussion/2', 'halodoc.com', 'discussion')]
    '''

    domain = config['domain']
    pages_2b_crawled = config['pages_2b_crawled']
    pages = list(pages_2b_crawled.keys())
    max_pages = list(pages_2b_crawled.values())

    pagination_data = []
    for page, max_page in zip(pages, max_pages):
        for i in range(1, max_page + 1):
            pagination_url = f"{page}{chr(96 + i)}" # convert 1 to 'a', 2 to 'b', etc.

            category = 'article'

            pagination_data.append((pagination_url, domain, category))
    
    return pagination_data

# keknya ntar text dalam json hasil crawling api halodoc disimpen ke output/halodoc_temp.txt
# selalu reset semua pagination halodoc aja kali ya?
async def crawl_halodoc_page(url: str, domain: str, category: str, session):
    '''Extract the article or discussion URLs from a single pagination URL for halodoc.com.
    
    :param url: the pagination URL to be crawled.
    :param domain: the domain of the website (halodoc.com).
    :param category: the category of the content to be crawled.
    :param session: an instance of requests.AsyncSession for making http requests.
    :return: a boolean indicating whether the crawling was successful or not.
    '''

    html = await fetch_html(url, session)
    if not html:
        return False
    
    response_json = json.loads(html)

    results = response_json['result']

    # save the urls to url_queue table in the database
    # and save the main component data to temp/halodoc_temp.jsonl if the data doesn't already exist in the file
    found_urls = []
    temp_data_path = Path('temp/halodoc_temp.jsonl')
    temp_data_path.touch(exist_ok=True)

    current_urls = set()

    with open(temp_data_path, mode = 'r', encoding = 'utf-8') as f:
        for line in f:
            if line.strip():  # skip baris kosong
                line_json = json.loads(line)
                current_urls.add(line_json["source"])

    with open(temp_data_path, mode = 'a+', encoding = 'utf-8') as f:
        for result in results:
            found_url = f'https://www.{domain}/kesehatan/{result['slug']}'
            found_urls.append((found_url, domain, category))
            
            temp_data = {
                'created_at': result['created_at'],
                'author_name': result['author']['name'],
                'name': result['name'],
                'content': result['content'],
                'source': found_url
                }
            
            if temp_data['source'] not in current_urls:
                f.write(json.dumps(temp_data, ensure_ascii = False) + '\n')
    
    await save_url(found_urls)

    return True

async def scrape_halodoc_content(url: str, domain: str, category: str, session, file_lock, output_path: str):
    '''Extract the content and metadata of article or discussion URLs from a single URL for halodoc.com.
    
    :param url: the pagination URL to be scraped.
    :param domain: the domain of the website (halodoc.com).
    :param category: the category of the content to be scraped.
    :param session: an instance of requests.AsyncSession for making http requests.
    :param file_lock: a lock for synchronizing file access.
    :param output_path: the path where the scraped data will be saved.
    :return: a boolean indicating whether the scraping was successful or not.
    '''



    return True

    