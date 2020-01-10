# -*- coding: utf-8 -*-
import os
from lms.envs.devstack import *

{% include "apps/openedx/settings/partials/common_lms.py" %}

OAUTH_OIDC_ISSUER = "{{ JWT_COMMON_ISSUER }}"

# Setup correct webpack configuration file for development
WEBPACK_CONFIG_PATH = "webpack.dev.config.js"

{{ patch("openedx-lms-development-settings") }}
