from pathlib import Path
from urllib.parse import urljoin

# URL
MAIN_DOC_URL = 'https://docs.python.org/3/'
WHATS_NEW_URL = urljoin(MAIN_DOC_URL, 'whatsnew/')
DOWNLOAD_URL = urljoin(MAIN_DOC_URL, 'download.html')
PEP_URL = 'https://peps.python.org/'

# DIR
BASE_DIR = Path(__file__).parent
# DOWNLOADS_DIR = BASE_DIR / 'downloads'
LOG_DIR = BASE_DIR / 'logs'
# RESULTS_DIR = BASE_DIR / 'results'

# FORMAT
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'

# NAME
CONST_FILE = 'file'
CONST_PRETTY = 'pretty'

# DATA
EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
