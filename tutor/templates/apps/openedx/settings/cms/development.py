# -*- coding: utf-8 -*-
import os
from cms.envs.devstack import *

{% include "apps/openedx/settings/partials/common_cms.py" %}

# Setup correct webpack configuration file for development
WEBPACK_CONFIG_PATH = "webpack.dev.config.js"

{{ patch("openedx-development-settings") }}
{{ patch("openedx-cms-development-settings") }}