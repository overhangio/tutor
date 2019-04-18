"""Settings shared between production and development
"""
import os
# This file is not supposed to be imported, but rather exec'd
# pylint: disable=undefined-variable


# Load module store settings from config files
update_module_store_settings(MODULESTORE, doc_store_settings=DOC_STORE_CONFIG)

# Set uploaded media file path
MEDIA_ROOT = "/openedx/data/uploads/"

# Video settings
VIDEO_IMAGE_SETTINGS['STORAGE_KWARGS']['location'] = MEDIA_ROOT
VIDEO_TRANSCRIPTS_SETTINGS['STORAGE_KWARGS']['location'] = MEDIA_ROOT

# Change syslog-based loggers which don't work inside docker containers
LOGGING_DEFAULT_LEVEL = os.environ.get('OPENEDX_LOGLEVEL', 'INFO')
LOGGING['loggers']['']['level'] = LOGGING_DEFAULT_LEVEL

LOGGING_FILENAME = os.path.join(LOG_DIR,
    '{}.log'.format(os.environ.get('SERVICE_VARIANT', 'other')))
LOGGING['handlers']['local'] = {
    'level': LOGGING_DEFAULT_LEVEL,
    'class': 'logging.handlers.WatchedFileHandler',
    'filename': LOGGING_FILENAME,
    'formatter': 'standard',
}

LOGGING['handlers']['tracking'] = {
    'level': 'DEBUG',
    'class': 'logging.handlers.WatchedFileHandler',
    'filename': os.path.join(LOG_DIR, 'tracking.log'),
    'formatter': 'standard',
}
