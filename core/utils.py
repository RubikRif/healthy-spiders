import asyncio
from config import MAX_CONCURRENT
from curl_cffi import requests
from datetime import datetime
from loguru import logger
from markdownify import markdownify as md
import random
from urllib.parse import urlparse
from transformers import AutoTokenizer

SEMAPHORE = asyncio.Semaphore(MAX_CONCURRENT)

#============================================================

# utility function to count tokens in a text
def count_token(text: str, tokenizer_path: str = 'temp/qwen3_tokenizer') -> int:
    '''Count the number of tokens in a given text using a specified tokenizer.
    
    :param text: input text to be tokenized.
    :param tokenizer_path: path or name of the tokenizer to use (default is 'temp/qwen3_tokenizer').
    :return: number of tokens in the input text.

    >> count_token('Halo, apa kabar?')
    7
    '''
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, trust_remote_code=True)
    tokens = tokenizer.tokenize(text)
    return len(tokens)

#============================================================

# utility function to fetch html
async def fetch_html(url: str, session: requests.AsyncSession) -> str:
    '''Fetch HTML content of a URL using curl_cffi and random delays asynchronously.
    
    :param url: url to fetch.
    :param session: an instance of requests.AsyncSession for making http requests.
    :return: HTML content as a string.
    '''

    async with SEMAPHORE:
        # Add a random delay to mimic human behavior
        await asyncio.sleep(random.uniform(1, 3))

        browsers = ['chrome99', 'chrome110', 'chrome101', 'chrome104', 'chrome107',
                    'chrome110', 'chrome116', 'chrome119', 'chrome120', 'chrome123',
                    'chrome124', 'chrome131', 'edge99', 'edge101']
        browser = random.choice(browsers)

        try:
            logger.info(f"Fetching URL: {url}")

            # handle ssl verification for pom.go.id
            parsed_url = urlparse(url)
            raw_domain = parsed_url.netloc
            if 'pom.go.id' in raw_domain:
                response = await session.get(url, impersonate=browser, verify = False)  # Disable SSL verification for pom.go.id
            else:
                response = await session.get(url, impersonate=browser)
            
            if response.status_code == 200:
                return response.text
            else:
                logger.warning(f'[{response.status_code}] Failed to fetch: {url}')
                return ''
            
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return ''

#============================================================

# utility function to convert html string to markdown
def html_to_markdown(html: str) -> str:
    '''Convert HTML content to Markdown format using markdownify.
    
    :param html: input html string.
    :return: converted markdown string.
    '''
    return md(html, heading_style = 'ATX', strip = ['a', 'img'])

#============================================================

# utility function to standardize date formats
def standardize_date(date: str) -> str:
    '''Standardize common date string format in Indonesia to a consistent format dd/mm/yyyy.
    
    :param date: input date string in various formats.
    :return: standardized date string in the format dd/mm/yyyy.

    >> standardize_date('12 Mei 2023')
    '12/05/2023'
    '''
    
    # frequently used formats in indonesia
    frequently_used_formats = ['%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y', '%d %B %Y']
    for format in frequently_used_formats:
        try:
            parsed_date = datetime.strptime(date, format)
            return parsed_date.strftime('%d/%m/%Y')
        except ValueError:
            continue
    
    return date