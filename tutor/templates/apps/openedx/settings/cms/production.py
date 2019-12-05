# -*- coding: utf-8 -*-
import os
from cms.envs.production import *

{% include "apps/openedx/settings/partials/common_cms.py" %}

ALLOWED_HOSTS = [
    ENV_TOKENS.get("CMS_BASE"),
    "cms",
    "127.0.0.1",
    "localhost",
    "studio.localhost",
]

{{ patch("openedx-cms-production-settings") }}
