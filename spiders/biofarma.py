

def get_biofarma_pagination(config):
    '''Generate pagination URLs data for biofarma.co.id based on the provided configuration.
    
    :param config: a dictionary containing the domain and pages to be crawled for each category.
    :return: a list of tuples containing pagination url, domain, and category.
    
    Example of config:
    BIOFARMA_CONFIG = {
        'domain': 'biofarma.co.id',
        'pages_2b_crawled': {
            '/page/': 1,
            '/discussion/': 2
        }
    }

    >> get_biofarma_pagination(BIOFARMA_CONFIG)
    [('https://www.biofarma.co.id/page/1', 'biofarma.co.id', 'article'), 
     ('https://www.biofarma.co.id/discussion/1', 'biofarma.co.id', 'discussion'),
     ('https://www.biofarma.co.id/discussion/2', 'biofarma.co.id', 'discussion')]
    '''

    domain = config['domain']
    pages_2b_crawled = config['pages_2b_crawled']
    pages = list(pages_2b_crawled.keys())
    max_pages = list(pages_2b_crawled.values())

    pagination_data = []
    for page, max_page in zip(pages, max_pages):
        for i in range(1, max_page + 1):
            pagination_url = f"https://www.{domain}{page}{i}"

            category = 'article'

            pagination_data.append((pagination_url, domain, category))
    
    return pagination_data

async def crawl_biofarma_page():
    pass

async def scrape_biofarma_content():
    pass