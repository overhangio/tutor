import os
from cms.envs.devstack import *


execfile(os.path.join(os.path.dirname(__file__), 'common.py'), globals())

LOCALE_PATHS.append('/openedx/locale')

# Setup correct webpack configuration file for development
WEBPACK_CONFIG_PATH = 'webpack.dev.config.js'

# Create folders if necessary
for folder in [LOG_DIR, MEDIA_ROOT, STATIC_ROOT_BASE]:
    if not os.path.exists(folder):
        os.makedirs(folder)
