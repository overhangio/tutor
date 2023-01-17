# -*- coding: utf-8 -*-
import os
from cms.envs.production import *

{% include "apps/openedx/settings/partials/common_cms.py" %}

ALLOWED_HOSTS = [
    ENV_TOKENS.get("CMS_BASE"),
    "cms",
]
CORS_ORIGIN_WHITELIST.append("{% if ENABLE_HTTPS %}https{% else %}http{% endif %}://{{ CMS_HOST }}")

# Authentication
SOCIAL_AUTH_EDX_OAUTH2_KEY = "{{ CMS_OAUTH2_KEY_SSO }}"
SOCIAL_AUTH_EDX_OAUTH2_PUBLIC_URL_ROOT = "{% if ENABLE_HTTPS %}https{% else %}http{% endif %}://{{ LMS_HOST }}"

{{ patch("openedx-cms-production-settings") }}
