# -*- coding: utf-8 -*-
import os
from lms.envs.production import *

{% include "apps/openedx/settings/partials/common_lms.py" %}

ALLOWED_HOSTS = [
    ENV_TOKENS.get("LMS_BASE"),
    FEATURES["PREVIEW_LMS_BASE"],
    "lms",
]
CORS_ORIGIN_WHITELIST.append("{% if ENABLE_HTTPS %}https{% else %}http{% endif %}://{{ LMS_HOST }}")

{% if ENABLE_HTTPS %}
# Properly set the "secure" attribute on session/csrf cookies. This is required in
# Chrome to support samesite=none cookies.
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "None"
{% else %}
# When we cannot provide secure session/csrf cookies, we must disable samesite=none
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = "Lax"
{% endif %}

# CMS authentication
IDA_LOGOUT_URI_LIST.append("{% if ENABLE_HTTPS %}https{% else %}http{% endif %}://{{ CMS_HOST }}/logout/")

# Required to display all courses on start page
SEARCH_SKIP_ENROLLMENT_START_DATE_FILTERING = True

{{ patch("openedx-lms-production-settings") }}
