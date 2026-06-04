

def get_halodoc_pagination(config):
    '''Generate pagination URLs for Halodoc articles based on the provided configuration.
    
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

async def crawl_halodoc_page():
    pass

async def scrape_halodoc_content():
    pass