import re
from pathlib import Path

MAIN_DOC_URL = 'https://docs.python.org/3/'
MAIN_PEP_URL = 'https://peps.python.org/'

BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'parser.log'

DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'

# PYTHON_VERSION_STATUS определяет шаблон поиска типа "Python 3.11 (stable)",
# выделяя при этом номер версии в группу version, а статус в группу status."
PYTHON_VERSION_STATUS = re.compile(
    r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
)

# PDF_FILES_IN_ZIP определяет шаблон поиска типа "любое_имя_файла.pdf-a4.zip"
PDF_FILES_IN_ZIP = re.compile(r'.+pdf-a4\.zip$')

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

# class ArgumentOutput(StrEnum):
#     RESULT_IN_TABLE = 'pretty'
#     RESULT_IN_FILE = 'file'
