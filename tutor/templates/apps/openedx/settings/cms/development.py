import os
from cms.envs.devstack import *

{% include "apps/openedx/settings/partials/common/lms.py" %}

# Setup correct webpack configuration file for development
WEBPACK_CONFIG_PATH = "webpack.dev.config.js"
