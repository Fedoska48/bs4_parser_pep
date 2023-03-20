from pathlib import Path

# URL
MAIN_DOC_URL = 'https://docs.python.org/3/'
WHATS_NEW = 'whatsnew/'
DOWNLOAD_URL = 'download.html'
PEP_URL = 'https://peps.python.org/'

# DIR
BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / 'logs'

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
