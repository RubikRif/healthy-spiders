# general config
BATCH_SIZE = 100

MAX_CONCURRENT = 5

OUTPUT_PATH = 'output/output.jsonl'

RESET_FIRST_PATTERNED_PAGINATION = True

# website-specific configs
# every website's config must contain:
# - domain: the domain of the website
# - pages_2b_crawled: dictionary with keys are representing patterned paginations,
# 					  and values are representing max pages to be crawled
# - contents_2b_scraped: dictionary with keys are representing path of the file consisting endpoints of url,
# 					 	 and values are representing max pages to be scraped or None
ALODOKTER_CONFIG = {
	'domain': 'alodokter.com',
	'pages_2b_crawled': {
		'/page/': 200, # article, max 1162
		'/komunitas/diskusi/penyakit/page/': 200 # patient-doctor discussion, max 7423
	},
    'contents_2b_scraped': None
} 

BIOFARMA_CONFIG = {
	'domain': 'biofarma.co.id',
	'pages_2b_crawled': {
		'/id/artikel-kesehatan/page/': 19 # article, max 19
	},
    'contents_2b_scraped': None
} 

BPOM_CONFIG = {
	'domain': 'pom.go.id',
	'pages_2b_crawled': {
		'/penjelasan-publik?page=': 10, # public explanation, max 10,
		'/siaran-pers?page=': 25, # press release, max 25,
		'/berita?page=': 239 # news, max 239
	},
    'contents_2b_scraped': None
} 

# special
HALODOC_CONFIG = {
	'domain': 'halodoc.com',
	'pages_2b_crawled': {
		'https://customers.api.halodoc.com/magneto-api/cms/categories?per_page=100&search_text=': 26 
        # article, max 26 (a-z)
	},
    'contents_2b_scraped': None
}

HELLOSEHAT_CONFIG = {
	'domain': 'hellosehat.com',
	'pages_2b_crawled': {
        '/parenting/?page=': 10, # max 243
		'/kehamilan/kesuburan/?page=': 10, # max 28
		'/kehamilan/kandungan/?page=': 10, # max 112
		'/kehamilan/melahirkan/?page=': 10, # max 20
		'/kehamilan/perawatan-ibu/?page=': 10, # max 11
		'/nutrisi/?page=': 10, # max 249
		'/penyakit-kulit/?page=': 10, # max 149
		'/mental/?page=': 10, # max 140
		'/kebugaran/?page=': 10, # max 65
		'/pernapasan/?page=': 10, # max 40
		'/hidup-sehat/?page=': 10, # max 49
		'/gigi-mulut/?page=': 10, # max 58
		'/wanita/?page=': 10, # max 70
		'/pria/?page=': 10, # max 31
		'/alergi/?page=': 10, # max 11
		'/jantung/?page=': 10, # max 45
		'/kanker/?page=': 10, # max 39
		'/urologi/?page=': 10, # max 21
		'/diabetes/?page=': 10, # max 22
		'/muskuloskeletal/?page=': 10, # max 39
		'/kelainan-darah/?page=': 10, # max 16
		'/mata/?page=': 10, # max 35
		'/tht/?page=': 10, # max 31
		'/saraf/?page=': 10, # max 50
		'/infeksi/?page=': 10, # max 52
		'/pencernaan/?page=': 10, # max 80
		'/seks/?page=': 10, # max 59
		'/lansia/?page=': 10, # max 15
		'/herbal-alternatif/?page=': 10, # max 36
		'/pola-tidur/?page=': 10, # max 23
		'/sehat/?page=': 10 # max 180
	},
    'contents_2b_scraped': {
        'temp/obat_suplemen.txt': 10 # max 1391
	}
} 