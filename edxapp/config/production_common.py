import os
from .aws import *

update_module_store_settings(MODULESTORE, doc_store_settings=DOC_STORE_CONFIG)

MEDIA_ROOT = "/openedx/data/uploads/"
FEATURES['ENABLE_DISCUSSION_SERVICE'] = False

# Don't rely on AWS for sending email
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST = 'smtp'

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
