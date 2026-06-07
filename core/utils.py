import asyncio
from config import MAX_CONCURRENT
from curl_cffi import requests
from datetime import datetime, UTC
import json
from loguru import logger
from markdownify import markdownify as md
import random
import re
from urllib.parse import urlparse
from transformers import AutoTokenizer

SEMAPHORE = asyncio.Semaphore(MAX_CONCURRENT)

#============================================================

# utility function to clean alodokter.com content markdown result for discussion category
def clean_alodokter_discussion(text: str) -> str:
    '''
    Clean alodokter.com content markdown result for dicussion category.

    :param text: input alodokter.com markdown content string for discussion category.
    :return: clean alodokter.com markdown content string for discussion category.
    '''

    text = text.replace('\\n', '\n').replace('\"', '\n')
    
    lines = text.split('\n')
    cleaned_lines = [line.strip() for line in lines]

    text = '\n'.join(cleaned_lines)

    text = re.sub(r'\n{3,}', '\n\n', text)

    text = re.sub(r'(\d+)\.\s*\n\s*', r'\1. ', text)

    return text.strip()

#============================================================

# utility function to clean references from biofarma.co.id content markdown
def clean_biofarma_markdown(text: str) -> str:
    '''Clean references from biofarma.co.id content markdown.
    
    :param text: input biofarma.co.id markdown content string.
    :return: biofarma.co.id markdown content string without references.
    '''

    if not text:
        return ''

    # regex pattern explanation:
    # (?:#+|\*\*)*  -> ignore if started with ### or ** (optional)
    # referen[sc]*i -> handling typo! 'referen' followed by 's' or 'c' or 'sc' then ended by 'i' (referensi, referensci, referenci)
    # |reference    -> for english case
    # (?:#+|\*\*|:|\s)* -> ignore symbols like :, **, or space at the end
    # .*            -> take all remaining characters until the end of the document (using flags=re.DOTALL)

    pattern = r'(?:#+|\*\*)*referen[sc]*i(?:#+|\*\*|:|\s)*.*|(?:#+|\*\*)*reference(?:#+|\*\*|:|\s)*.*'

    text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

    return text.strip()

#============================================================

# utility function to clean table of contents and references from halodoc.com content markdown
def clean_halodoc_markdown(text: str) -> str:
    '''Clean table of contents and references from halodoc.com content markdown.
    
    :param text: input halodoc.com markdown content string.
    :return: halodoc.com markdown content string without table of contents and references.
    '''

    if not text:
        return ''
    
    # delete a block of table of contents along with points below
    toc_pattern = r'\*\*DAFTAR ISI\*\*.*?(?=\n##|\Z)'
    text = re.sub(toc_pattern, '', text, flags=re.DOTALL)
    
    # delete references 
    referensi_pattern = r'^######.*?(\n|\Z)'
    text = re.sub(referensi_pattern, '', text, flags=re.MULTILINE)
    
    # clean whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

#============================================================

# utility function to count tokens in a text
def count_token(text: str, tokenizer_path: str = 'temp/qwen3_tokenizer') -> int:
    '''Count the number of tokens in a given text using a specified tokenizer.
    
    :param text: input text to be tokenized.
    :param tokenizer_path: path or name of the tokenizer to use (default is 'temp/qwen3_tokenizer').
    :return: number of tokens in the input text.

    >>> count_token('Halo, apa kabar?')
    7
    '''
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, trust_remote_code=True)
    tokens = tokenizer.tokenize(text)
    return len(tokens)

# utility function to count total tokens in output file
def count_total_token(output_path: str) -> int:
    '''Count total tokens from scraping results in the output file.
    
    :param output_path: path or name of the output file.
    :return: total tokens from scraping results in the output file.
    '''

    total_tokens = 0
    with open(output_path, mode = 'r', encoding = 'utf-8') as f:
        for line in f:
            if line.strip():
                line_json = json.loads(line)

                total_tokens += line_json['metadata']['token_count']
    
    return total_tokens

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

# utility function to convert unix timestamp to stanardized date
def timestamp_to_date(timestamp: int | str) -> str:
    '''Convert Unix Timestamp to a date with format dd/mm/yyyy.
    
    :param timestamp: unix timestamp in milisecods.
    :return: Date string in dd/mm/yyyy format.

    >>> timestamp_to_date(1764324449000)
    '28/11/2025'

    >>> timestamp_to_date('1690948704000')
    '02/08/2023'
    '''

    timestamp = int(timestamp)

    return (datetime
            .fromtimestamp(timestamp / 1000, UTC)
            .strftime('%d/%m/%Y'))