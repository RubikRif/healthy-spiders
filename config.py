# general config
BATCH_SIZE = 100

DB_PATH = "queue.db"

# special for halodoc.com only
HALODOC_TEMP_DATA_PATH = 'temp/halodoc_temp.jsonl'

MAX_CONCURRENT = 5

OUTPUT_PATH = 'output/output.jsonl'

RESET_FIRST_PATTERNED_PAGINATION = True

# special for halodoc.com only
RESET_ALL_HALODOC_PAGINATION = True

RESET_ALL_FAILED_PAGINATION = True

RESET_ALL_FAILED_URL = True

# website-specific configs
# every website's config must contain:
# - domain: the domain of the website
# - pages_2b_crawled: dictionary with keys are representing patterned paginations,
# 					  and values are representing max pages to be crawled
# - contents_2b_scraped: dictionary with keys are representing path of the file consisting unpatterned endpoints of url,
# 					 	 and values are representing max pages to be scraped or None
ALODOKTER_CONFIG = {
	'domain': 'alodokter.com',
	'pages_2b_crawled': {
		'/page/': 2, # article, max 1162
		'/komunitas/diskusi/penyakit/page/': 2 # patient-doctor discussion, max 7423
	},
    'contents_2b_scraped': None
} 

BIOFARMA_CONFIG = {
	'domain': 'biofarma.co.id',
	'pages_2b_crawled': {
		'/id/artikel-kesehatan/page/': 2 # article, max 19
	},
    'contents_2b_scraped': None
} 

BPOM_CONFIG = {
	'domain': 'pom.go.id',
	'pages_2b_crawled': {
		'/penjelasan-publik?page=': 1, # public explanation, max 10,
		'/siaran-pers?page=': 1, # press release, max 25,
		'/berita?page=': 0 # news, max 239
	},
    'contents_2b_scraped': None
} 

# special for halodoc.com only
HALODOC_CONFIG = {
	'domain': 'halodoc.com',
	'pages_2b_crawled': {
		'https://customers.api.halodoc.com/magneto-api/cms/categories?per_page=100&search_text=': 2 
        # article, max 26 (a-z)
	},
    'contents_2b_scraped': None
}

HELLOSEHAT_CONFIG = {
	'domain': 'hellosehat.com',
	'pages_2b_crawled': {
        '/parenting/?page=': 1, # max 243
		'/kehamilan/kesuburan/?page=': 1, # max 28
		'/kehamilan/kandungan/?page=': 0, # max 112
		'/kehamilan/melahirkan/?page=': 1, # max 20
		'/kehamilan/perawatan-ibu/?page=': 0, # max 11
		'/nutrisi/?page=': 0, # max 249
		'/penyakit-kulit/?page=': 0, # max 149
		'/mental/?page=': 0, # max 140
		'/kebugaran/?page=': 0, # max 65
		'/pernapasan/?page=': 0, # max 40
		'/hidup-sehat/?page=': 0, # max 49
		'/gigi-mulut/?page=': 0, # max 58
		'/wanita/?page=': 0, # max 70
		'/pria/?page=': 0, # max 31
		'/alergi/?page=': 0, # max 11
		'/jantung/?page=': 0, # max 45
		'/kanker/?page=': 0, # max 39
		'/urologi/?page=': 0, # max 21
		'/diabetes/?page=': 0, # max 22
		'/muskuloskeletal/?page=': 0, # max 39
		'/kelainan-darah/?page=': 0, # max 16
		'/mata/?page=': 0, # max 35
		'/tht/?page=': 0, # max 31
		'/saraf/?page=': 0, # max 50
		'/infeksi/?page=': 0, # max 52
		'/pencernaan/?page=': 0, # max 80
		'/seks/?page=': 0, # max 59
		'/lansia/?page=': 0, # max 15
		'/herbal-alternatif/?page=': 1, # max 36
		'/pola-tidur/?page=': 0, # max 23
		'/sehat/?page=': 0 # max 180
	},
    'contents_2b_scraped': {
        'temp/obat_suplemen.txt': 2 # max 1391
	}
} 