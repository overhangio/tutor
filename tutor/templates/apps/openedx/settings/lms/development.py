# -*- coding: utf-8 -*-
import os
from lms.envs.devstack import *

{% include "apps/openedx/settings/partials/common_lms.py" %}

# Setup correct webpack configuration file for development
WEBPACK_CONFIG_PATH = "webpack.dev.config.js"

SESSION_COOKIE_DOMAIN = ".{{ LMS_HOST|common_domain(CMS_HOST) }}"

LMS_BASE = "{{ LMS_HOST}}:8000"
LMS_ROOT_URL = "http://{}".format(LMS_BASE)
LMS_INTERNAL_ROOT_URL = LMS_ROOT_URL
SITE_NAME = LMS_BASE
CMS_BASE = "{{ CMS_HOST}}:8001"
CMS_ROOT_URL = "http://{}".format(CMS_BASE)
LOGIN_REDIRECT_WHITELIST.append(CMS_BASE)

# CMS authentication
IDA_LOGOUT_URI_LIST.append("http://{{ CMS_HOST }}:8001/complete/logout")

FEATURES['ENABLE_COURSEWARE_MICROFRONTEND'] = False

LOGGING["loggers"]["oauth2_provider"] = {
    "handlers": ["console"],
    "level": "DEBUG"
}

{{ patch("openedx-development-settings") }}
{{ patch("openedx-lms-development-settings") }}
