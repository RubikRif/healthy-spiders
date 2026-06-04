

def get_hellosehat_pagination(config):
    '''Generate pagination URLs for HelloSehat based on the provided configuration.

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

    with open('obat_suplemen.txt', 'r') as f:
        all_obat_suplemen = [line.strip() for line in f.readlines()]

    pagination_data = []
    for page, max_page in zip(pages, max_pages):
        if page == 'obat-suplemen/?page=':
            for i in range(max_page):
                pagination_url = f"https://{domain}{all_obat_suplemen[i]}"

                category = 'article'

                pagination_data.append((pagination_url, domain, category))
        
        else:
            for i in range(1, max_page + 1):
                pagination_url = f"https://{domain}{page}{i}"

                category = 'article'

                pagination_data.append((pagination_url, domain, category))
    
    return pagination_data

async def crawl_hellosehat_page():
    pass

async def scrape_hellosehat_content():
    pass