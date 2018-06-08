import os
from ..aws import *

update_module_store_settings(MODULESTORE, doc_store_settings=DOC_STORE_CONFIG)

MEDIA_ROOT = "/openedx/data/uploads/"

# We need to activate dev_env for logging, otherwise rsyslog is required (but
# it is not available in docker).
LOGGING = get_logger_config(LOG_DIR,
                            logging_env=ENV_TOKENS['LOGGING_ENV'],
                            debug=False,
                            dev_env=True,
                            service_variant=SERVICE_VARIANT)

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

DEFAULT_FROM_EMAIL = 'registration@' + ENV_TOKENS['LMS_BASE']
DEFAULT_FEEDBACK_EMAIL = 'feedback@' + ENV_TOKENS['LMS_BASE']
SERVER_EMAIL = 'devops@' + ENV_TOKENS['LMS_BASE']
