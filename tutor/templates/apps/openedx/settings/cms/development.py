import os
from cms.envs.devstack import *
from .common import *


# Load module store settings from config files
update_module_store_settings(MODULESTORE, doc_store_settings=DOC_STORE_CONFIG)

LOCALE_PATHS.append('/openedx/locale')

# Setup correct webpack configuration file for development
WEBPACK_CONFIG_PATH = 'webpack.dev.config.js'

# Create folders if necessary
for folder in [LOG_DIR, MEDIA_ROOT, STATIC_ROOT_BASE]:
    if not os.path.exists(folder):
        os.makedirs(folder)
