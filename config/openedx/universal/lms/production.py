from ..aws import *

# Load module store settings from config files
update_module_store_settings(MODULESTORE, doc_store_settings=DOC_STORE_CONFIG)

# Set uploaded media file path
MEDIA_ROOT = "/openedx/data/uploads/"

# Change syslog-based loggers which don't work inside docker containers
LOGGING['handlers']['local'] = LOGGING['handlers']['console'].copy()
LOGGING['handlers']['tracking'] = LOGGING['handlers']['console'].copy()

# Create folders if necessary
import os
for folder in [LOG_DIR, MEDIA_ROOT, STATIC_ROOT_BASE]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Fix media files paths
VIDEO_IMAGE_SETTINGS['STORAGE_KWARGS']['location'] = MEDIA_ROOT
VIDEO_TRANSCRIPTS_SETTINGS['STORAGE_KWARGS']['location'] = MEDIA_ROOT
PROFILE_IMAGE_BACKEND['options']['location'] = os.path.join(MEDIA_ROOT, 'profile-images/')

ALLOWED_HOSTS = [
    ENV_TOKENS.get('LMS_BASE'),
    FEATURES['PREVIEW_LMS_BASE'],
    '127.0.0.1', 'localhost',
    '127.0.0.1:8000', 'localhost:8000',
]

DEFAULT_FROM_EMAIL = 'registration@' + ENV_TOKENS['LMS_BASE']
DEFAULT_FEEDBACK_EMAIL = 'feedback@' + ENV_TOKENS['LMS_BASE']
SERVER_EMAIL = 'devops@' + ENV_TOKENS['LMS_BASE']
TECH_SUPPORT_EMAIL = 'technical@' + ENV_TOKENS['LMS_BASE']
CONTACT_EMAIL = 'info@' + ENV_TOKENS['LMS_BASE']
BUGS_EMAIL = 'bugs@' + ENV_TOKENS['LMS_BASE']
UNIVERSITY_EMAIL = 'university@' + ENV_TOKENS['LMS_BASE']
PRESS_EMAIL = 'press@' + ENV_TOKENS['LMS_BASE']
PAYMENT_SUPPORT_EMAIL = 'payment@' + ENV_TOKENS['LMS_BASE']
BULK_EMAIL_DEFAULT_FROM_EMAIL = 'no-reply@' + ENV_TOKENS['LMS_BASE']
API_ACCESS_MANAGER_EMAIL = 'api-access@' + ENV_TOKENS['LMS_BASE']
API_ACCESS_FROM_EMAIL = 'api-requests@' + ENV_TOKENS['LMS_BASE']
