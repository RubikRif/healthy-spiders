# Healthy Spiders 💪🕷️

A naive crawler-scraper for health domain websites built with Python. This project autonomously extracts health-related content from multiple Indonesian health websites using asynchronous crawling and scraping techniques.

## Overview

### Crawling-Scraping Mechanism

The **Healthy Spiders** project implements a two-phase pipeline:

#### Phase 1: Crawling
The crawler discovers content URLs by processing paginated endpoint lists. It:
- Fetches pagination pages from predefined URL patterns
- Extracts individual content URLs from HTML/JSON responses
- Stores discovered URLs in an SQLite queue database
- Supports multiple categories per website (articles, discussions, news, etc.)

#### Phase 2: Scraping
The scraper extracts detailed content from discovered URLs. It:
- Retrieves pending URLs from the database in configurable batches
- Fetches and parses HTML content with BeautifulSoup
- Converts HTML to clean Markdown format
- Extracts metadata (title, date, author, tokens count, etc.)
- Saves structured data as JSONL (JSON Lines) format

### Supported Websites

The project currently supports crawling and scraping from:
- **alodokter.com** - Articles and patient-doctor discussions
- **biofarma.co.id** - Health articles
- **pom.go.id** - Public health information and news
- **halodoc.com** - Medical articles
- **hellosehat.com** - Comprehensive health content

### Key Features

- **Asynchronous Processing**: Built on Python `asyncio` for concurrent requests
- **Rate Limiting**: Configurable concurrency limits to avoid overwhelming servers
- **Error Handling**: Automatic retry mechanisms and failure tracking
- **Logging**: Detailed logging with daily rotation using `loguru`
- **Token Counting**: Quantifies content using Qwen3 tokenizer
- **Database Tracking**: SQLite persistence for pagination and URL status

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/RubikRif/healthy-spiders.git
cd healthy-spiders
```

### 2. Create and Activate Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```
### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Pipeline

Edit `config.py` to customize the crawling and scraping behavior:

#### General Configuration
```python
BATCH_SIZE = 100                    # Number of items to process per batch
DB_PATH = "queue.db"                # SQLite database file
MAX_CONCURRENT = 5                  # Maximum concurrent async requests
OUTPUT_PATH = 'output/output.jsonl' # Output file path for scraped data
```

#### Website-Specific Configuration

Each website config requires:
- **domain**: The website domain
- **pages_2b_crawled**: Dictionary with pagination patterns and max pages to crawl
- **contents_2b_scraped**: Dictionary with unpatterned URL sources and max pages to scrape

Example configuration:
```python
ALODOKTER_CONFIG = {
    'domain': 'alodokter.com',
    'pages_2b_crawled': {
        '/page/': 100,                              # Article pages, max 1162 available
        '/komunitas/diskusi/penyakit/page/': 100   # Discussion pages, max 7423 available
    },
    'contents_2b_scraped': None
}
```

#### Reset Flags

Control behavior between pipeline runs:
```python
RESET_FIRST_PATTERNED_PAGINATION = True  # Reset first pagination batch
RESET_ALL_HALODOC_PAGINATION = True      # Reset Halodoc-specific pagination
RESET_ALL_FAILED_PAGINATION = True       # Retry failed pagination URLs
RESET_ALL_FAILED_URL = True              # Retry failed content URLs
```

### 5. Run the Pipeline

```bash
python main.py
```

The pipeline will:
1. Initialize the SQLite database
2. Generate pagination URLs for all configured websites
3. **Crawl** all pagination pages to discover content URLs
4. Wait 5 seconds between crawler and scraper phases
5. **Scrape** all discovered URLs to extract content
6. Save results to `output/output.jsonl`
7. Generate daily log files: `healthy_spiders_YYYY-MM-DD.log`

### Output Format

Scraped content is saved in JSONL format with the following structure:
```json
{
  "url": "https://example.com/article",
  "domain": "example.com",
  "category": "article",
  "title": "Article Title",
  "content": "# Article Title\n\nMarkdown formatted content...",
  "author": "Author Name",
  "date": "2024-01-15",
  "token_count": 1250,
  "hash": "abc123def456...",
  "id": "uuid-string"
}
```

---

## Project Structure

```
healthy-spiders/
├── main.py              # Entry point
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── core/
│   ├── engine.py        # Main crawler and scraper orchestration
│   ├── router.py        # Route tasks to appropriate website handlers
│   ├── database.py      # SQLite database operations
│   └── utils.py         # Utility functions (token counting, HTML parsing, etc.)
├── spiders/             # Website-specific crawlers and scrapers
│   ├── alodokter.py
│   ├── biofarma.py
│   ├── bpom.py
│   ├── halodoc.py
│   └── hellosehat.py
├── temp/                # Temporary data and tokenizer files
└── output/              # Scraped data output directory
```

---

## Requirements

- Python 3.8+
- See `requirements.txt` for full dependencies

Key dependencies:
- `curl_cffi` - HTTP requests with CFFI support
- `beautifulsoup4` - HTML parsing
- `aiofiles` & `aiosqlite` - Async file and database operations
- `loguru` - Advanced logging
- `markdownify` - HTML to Markdown conversion
- `transformers` - Token counting support

---

## Logging

Application logs are automatically created and rotated daily:
- **Location**: `healthy_spiders_YYYY-MM-DD.log`
- **Rotation**: Daily at 00:00
- **Retention**: 1 week of logs

Example log output:
```
2024-01-15 10:30:45 | INFO | Starting healthy spiders 💪🕷️...
2024-01-15 10:30:45 | INFO | Starting crawler...
2024-01-15 10:30:47 | INFO | Crawling 100 pending pagination URLs...
```

---

## License

MIT License - See LICENSE file for details

---

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.