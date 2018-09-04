import os
from ..aws import *

update_module_store_settings(MODULESTORE, doc_store_settings=DOC_STORE_CONFIG)

MEDIA_ROOT = "/openedx/data/uploads/"

# Change syslog-based loggers which don't work inside docker containers
LOGGING['handlers']['local'] = LOGGING['handlers']['console'].copy()
LOGGING['handlers']['tracking'] = LOGGING['handlers']['console'].copy()

# Create folders if necessary
for folder in [LOG_DIR, MEDIA_ROOT, STATIC_ROOT_BASE]:
    if not os.path.exists(folder):
        os.makedirs(folder)

ALLOWED_HOSTS = [
    ENV_TOKENS.get('CMS_BASE'),
    '127.0.0.1', 'localhost', 'studio.localhost',
    '127.0.0.1:8000', 'localhost:8000',
    '127.0.0.1:8001', 'localhost:8001',
]

DEFAULT_FROM_EMAIL = ENV_TOKENS.get('DEFAULT_FROM_EMAIL', 'registration@' + ENV_TOKENS['LMS_BASE'])
DEFAULT_FEEDBACK_EMAIL = ENV_TOKENS.get('DEFAULT_FEEDBACK_EMAIL', 'feedback@' + ENV_TOKENS['LMS_BASE'])
SERVER_EMAIL = ENV_TOKENS.get('SERVER_EMAIL', 'devops@' + ENV_TOKENS['LMS_BASE'])
