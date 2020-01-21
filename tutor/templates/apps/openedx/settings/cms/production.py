# -*- coding: utf-8 -*-
import os
from cms.envs.production import *

{% include "apps/openedx/settings/partials/common_cms.py" %}

ALLOWED_HOSTS = [
    ENV_TOKENS.get("CMS_BASE"),
    "cms",
]

MIDDLEWARE.insert(0, "whitenoise.middleware.WhiteNoiseMiddleware")

{{ patch("openedx-cms-production-settings") }}
