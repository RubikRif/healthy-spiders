import aiofiles
from bs4 import BeautifulSoup
from core.database import save_url
from core.utils import count_token, fetch_html, html_to_markdown, standardize_date
from curl_cffi import requests
from datetime import datetime, timedelta, timezone
import hashlib
import json
from loguru import logger
from urllib.parse import urljoin
import uuid

#============================================================

def get_hellosehat_pagination(config):
    '''Generate pagination URLs for hellosehat.com based on the provided configuration.

    :param config: a dictionary containing the website domain and the number of pages to be crawled for each category.
    :return: a list of tuples containing pagination url, domain, and category.
    
    Example config:
    HELLOSEHAT_CONFIG = {
        'domain': 'hellosehat.com',
        'pages_2b_crawled': {
            '/page/': 1,
            '/discussion/': 2,
        }
    }

    >> get_hellosehat_pagination(HELLOSEHAT_CONFIG)
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
            pagination_url = f"https://{domain}{page}{i}"

            category = 'article'

            pagination_data.append((pagination_url, domain, category))
    
    return pagination_data

async def update_obat_suplemen():
    '''Add new obat suplemen URL if there is an update.'''

    # get all current obat suplemen urls 
    current_obat_suplemen = set()
    with open('temp/obat_suplemen.txt', mode = 'r', encoding = 'utf-8') as f:
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
    obat_suplemen_urls = [(f'https://{urljoin("hellosehat.com", obat_suplemen)}', 
                           'hellosehat.com', 
                           'article') 
                           for obat_suplemen in new_obat_suplemen]

    await save_url(obat_suplemen_urls)

    # add to the obat_suplemen.txt
    new_urls = new_obat_suplemen - current_obat_suplemen
    if new_urls:
        with open('temp/obat_suplemen.txt', mode = 'a', encoding = 'utf-8') as f:
            for url in new_urls:
                f.write(new_urls + '\n')



async def crawl_hellosehat_page(url: str, domain: str, category: str, session):
    '''Extract the article or discussion URLs from a single pagination URL for hellosehat.com.
    
    :param url: the pagination URL to be crawled.
    :param domain: the domain of the website (alodokter.com).
    :param category: the category of the content to be crawled.
    :param session: an instance of requests.AsyncSession for making http requests.
    :return: a boolean indicating whether the crawling was successful or not.
    '''
    pass



async def scrape_hellosehat_content(url: str, domain: str, category: str, session, file_lock, output_path: str):
    '''Extract the content and metadata of article or discussion URLs from a single URL for hellosehat.com.
    
    :param url: the pagination URL to be scraped.
    :param domain: the domain of the website (alodokter.com).
    :param category: the category of the content to be scraped.
    :param session: an instance of requests.AsyncSession for making http requests.
    :param file_lock: a lock for synchronizing file access.
    :param output_path: the path where the scraped data will be saved.
    :return: a boolean indicating whether the scraping was successful or not.
    '''

    pass