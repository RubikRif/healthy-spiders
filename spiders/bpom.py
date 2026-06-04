

def get_bpom_pagination(config):
    '''Generate pagination URLs data for pom.go.id based on the provided configuration.
    
    :param config: a dictionary containing the domain and pages to be crawled for each category.
    :return: a list of tuples containing pagination url, domain, and category.
    
    Example of config:
    BPOM_CONFIG = {
        'domain': 'pom.go.id',
        'pages_2b_crawled': {
            '/page/': 1,
            '/discussion/': 2
        }
    }

    >> get_bpom_pagination(BPOM_CONFIG)
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
            pagination_url = f"https://www.{domain}{page}{i}"

            if page == '/penjelasan-publik?page=':
                category = 'public explanation'
            elif page == '/siaran-pers?page=':
                category = 'press release'
            elif page == '/berita?page=':
                category = 'news'

            pagination_data.append((pagination_url, domain, category))
    
    return pagination_data

async def crawl_bpom_page():
    pass

async def scrape_bpom_content():
    pass