# -*- coding: utf-8 -*-
import os
from lms.envs.devstack import *

{% include "apps/openedx/settings/partials/common_lms.py" %}

# Setup correct webpack configuration file for development
WEBPACK_CONFIG_PATH = "webpack.dev.config.js"

{{ patch("openedx-development-settings") }}
{{ patch("openedx-lms-development-settings") }}
