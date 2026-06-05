import aiofiles
from bs4 import BeautifulSoup
from core.database import save_url
from core.utils import count_token, fetch_html, html_to_markdown, standardize_date
from datetime import datetime, timedelta, timezone
import hashlib
import json
from loguru import logger
from urllib.parse import urljoin
import uuid

#============================================================

def get_alodokter_pagination(config):
    '''Generate pagination URLs data for alodokter.com based on the provided configuration.
    
    :param config: a dictionary containing the domain and pages to be crawled for each category.
    :return: a list of tuples containing pagination url, domain, and category.
    
    Example of config:
    ALODOKTER_CONFIG = {
        'domain': 'alodokter.com',
        'pages_2b_crawled': {
            '/page/': 1,
            '/discussion/': 2
        }
    }

    >> get_alodokter_pagination(ALODOKTER_CONFIG)
    [('https://www.alodokter.com/page/1', 'alodokter.com', 'article'), 
     ('https://www.alodokter.com/discussion/1', 'alodokter.com', 'discussion'),
     ('https://www.alodokter.com/discussion/2', 'alodokter.com', 'discussion')]
    '''

    domain = config['domain']
    pages_2b_crawled = config['pages_2b_crawled']
    pages = list(pages_2b_crawled.keys())
    max_pages = list(pages_2b_crawled.values())

    pagination_data = []
    for page, max_page in zip(pages, max_pages):
        for i in range(1, max_page + 1):
            pagination_url = f'https://www.{domain}{page}{i}'

            if page == '/page/':
                category = 'article'
            else:
                category = 'discussion'

            pagination_data.append((pagination_url, domain, category))

    return pagination_data



async def crawl_alodokter_page(url: str, domain: str, category: str, session):
    '''Extract the article or discussion URLs from a single pagination URL for alodokter.com.
    
    :param url: the pagination URL to be crawled.
    :param domain: the domain of the website (alodokter.com).
    :param category: the category of the content to be crawled.
    :param session: an instance of requests.AsyncSession for making http requests.
    :return: a boolean indicating whether the crawling was successful or not.
    '''

    html = await fetch_html(url, session)
    if not html:
        return False

    soup = BeautifulSoup(html, 'html.parser')

    if category == 'article':
        cards = soup.select('card-post-index')
        found_urls = [(f'https://www.{urljoin(domain, card.get('url-path'))}',
                        domain,
                        category) 
                        for card in cards if card.get('url-path', '')]
    elif category == 'dicussion':
        cards = soup.select('#topic-list card-topic')
        found_urls = [(f'https://www.{urljoin(domain, card.get('href'))}',
                       domain,
                       category) 
                       for card in cards if card.get('href', '')]

    if found_urls:
        await save_url(found_urls)
        return True
    else:
        logger.warning(f'No URLs Found in {url}')
        return False



async def scrape_alodokter_content(url: str, domain: str, category: str, session, file_lock, output_path: str):
    '''Extract the content and metadata of article or discussion URLs from a single URL for alodokter.com.
    
    :param url: the pagination URL to be scraped.
    :param domain: the domain of the website (alodokter.com).
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

    if category == 'article':
        # title
        post_title = soup.select_one('#post_title')
        title = post_title.get_text(strip = True) if post_title else ''

        # content
        content_html = soup.select_one('#postContent')

        if not content_html:
            logger.warning(f'No content found in {url}')
            return False
        
        content_md = html_to_markdown(str(content_html))

        # date
        last_updated_html = soup.select_one('div.date-article')
        last_updated = last_updated_html.get_text(strip = True) if last_updated_html else ''
        date = last_updated.split(': ')[1] if last_updated else ''
        date = standardize_date(date)

        # author
        source_post = soup.select_one('sources-post')
        author = source_post.get('doctor-name', '') if source_post else ''

    elif category == 'discussion':
        # title
        detail_topic = soup.select_one('#detailTopic')
        title = detail_topic.get('member-topic-title', '') if detail_topic else ''

        # content
        patient_content = detail_topic.get('member-topic-content', '') if detail_topic else ''
        patient_content = patient_content.replace('\u003c', '<').replace('\u003e', '>')
        
        doctor_topic = soup.select_one('doctor-topic')
        doctor_content = doctor_topic.get('doctor-topic-content', '') if doctor_topic else ''
        doctor_content = doctor_content.replace('\u003c', '<').replace('\u003e', '>')
        
        if not patient_content and not doctor_content:
            logger.warning(f'No content found in {url}')
            return False
        
        patient_content_md = html_to_markdown(patient_content)
        doctor_content_md = html_to_markdown(doctor_content)
        content_md = f'## Pasien:\n{patient_content_md}\n## Dokter:\n{doctor_content_md}'

        # date
        post_date = doctor_topic.get('post-date', '') if doctor_topic else ''
        date = post_date.split(', ')[0]
        date = standardize_date(date)

        # author
        author = doctor_topic.get('doctor-name-title', '') if doctor_topic else ''

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