import os
from lms.envs.production import *

# Load module store settings from config files
update_module_store_settings(MODULESTORE, doc_store_settings=DOC_STORE_CONFIG)

# Set uploaded media file path
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

# Fix media files paths
VIDEO_IMAGE_SETTINGS['STORAGE_KWARGS']['location'] = MEDIA_ROOT
VIDEO_TRANSCRIPTS_SETTINGS['STORAGE_KWARGS']['location'] = MEDIA_ROOT
PROFILE_IMAGE_BACKEND['options']['location'] = os.path.join(MEDIA_ROOT, 'profile-images/')

ALLOWED_HOSTS = [
    ENV_TOKENS.get('LMS_BASE'),
    FEATURES['PREVIEW_LMS_BASE'],
    '127.0.0.1', 'localhost', 'preview.localhost',
    '127.0.0.1:8000', 'localhost:8000', 'preview.localhost:8000',
]

# Required to display all courses on start page
SEARCH_SKIP_ENROLLMENT_START_DATE_FILTERING = True

# Allow insecure oauth2 for local interaction with local containers
OAUTH_ENFORCE_SECURE = False

DEFAULT_FROM_EMAIL = ENV_TOKENS['CONTACT_EMAIL']
DEFAULT_FEEDBACK_EMAIL = ENV_TOKENS['CONTACT_EMAIL']
SERVER_EMAIL = ENV_TOKENS['CONTACT_EMAIL']
TECH_SUPPORT_EMAIL = ENV_TOKENS['CONTACT_EMAIL']
CONTACT_EMAIL = ENV_TOKENS['CONTACT_EMAIL']
BUGS_EMAIL = ENV_TOKENS['CONTACT_EMAIL']
UNIVERSITY_EMAIL = ENV_TOKENS['CONTACT_EMAIL']
PRESS_EMAIL = ENV_TOKENS['CONTACT_EMAIL']
PAYMENT_SUPPORT_EMAIL = ENV_TOKENS['CONTACT_EMAIL']
BULK_EMAIL_DEFAULT_FROM_EMAIL = 'no-reply@' + ENV_TOKENS['LMS_BASE']
API_ACCESS_MANAGER_EMAIL = ENV_TOKENS['CONTACT_EMAIL']
API_ACCESS_FROM_EMAIL = ENV_TOKENS['CONTACT_EMAIL']

ORA2_FILEUPLOAD_BACKEND = 'filesystem'
ORA2_FILEUPLOAD_ROOT = '/openedx/data/ora2'
ORA2_FILEUPLOAD_CACHE_NAME = 'ora2-storage'

GRADES_DOWNLOAD = {
    'STORAGE_TYPE': '',
    'STORAGE_KWARGS': {
        'base_url': "/media/grades/",
        'location': os.path.join(MEDIA_ROOT, 'grades'),
    }
}

LOCALE_PATHS.append('/openedx/locale')

# Create folders if necessary
for folder in [LOG_DIR, MEDIA_ROOT, STATIC_ROOT_BASE, ORA2_FILEUPLOAD_ROOT]:
    if not os.path.exists(folder):
        os.makedirs(folder)
