# -*- coding: utf-8 -*-
import os
from lms.envs.production import *

{% include "apps/openedx/settings/partials/common_lms.py" %}

ALLOWED_HOSTS = [
    ENV_TOKENS.get("LMS_BASE"),
    FEATURES["PREVIEW_LMS_BASE"],
    "lms",
]

# CMS authentication
IDA_LOGOUT_URI_LIST.append("{% if ENABLE_HTTPS %}https{% else %}http{% endif %}://{{ CMS_HOST }}/complete/logout")

# Required to display all courses on start page
SEARCH_SKIP_ENROLLMENT_START_DATE_FILTERING = True

{{ patch("openedx-lms-production-settings") }}
