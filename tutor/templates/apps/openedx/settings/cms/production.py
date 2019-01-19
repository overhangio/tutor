import os
from cms.envs.production import *

update_module_store_settings(MODULESTORE, doc_store_settings=DOC_STORE_CONFIG)

MEDIA_ROOT = "/openedx/data/uploads/"

# Video settings
VIDEO_IMAGE_SETTINGS['STORAGE_KWARGS']['location'] = MEDIA_ROOT
VIDEO_TRANSCRIPTS_SETTINGS['STORAGE_KWARGS']['location'] = MEDIA_ROOT

# Change syslog-based loggers which don't work inside docker containers
LOGGING['handlers']['local'] = {'class': 'logging.NullHandler'}
LOGGING['handlers']['tracking'] = {
    'level': 'DEBUG',
    'class': 'logging.StreamHandler',
    'formatter': 'standard',
}

ALLOWED_HOSTS = [
    ENV_TOKENS.get('CMS_BASE'),
    '127.0.0.1', 'localhost', 'studio.localhost',
    '127.0.0.1:8000', 'localhost:8000',
    '127.0.0.1:8001', 'localhost:8001',
]

DEFAULT_FROM_EMAIL = ENV_TOKENS['CONTACT_EMAIL']
DEFAULT_FEEDBACK_EMAIL = ENV_TOKENS['CONTACT_EMAIL']
SERVER_EMAIL = ENV_TOKENS['CONTACT_EMAIL']

LOCALE_PATHS.append('/openedx/locale')

# Create folders if necessary
for folder in [LOG_DIR, MEDIA_ROOT, STATIC_ROOT_BASE]:
    if not os.path.exists(folder):
        os.makedirs(folder)
