from ..devstack import *

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
