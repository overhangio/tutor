import os
from lms.envs.production import *

{% include "apps/openedx/settings/partials/common_lms.py" %}

ALLOWED_HOSTS = [
    ENV_TOKENS.get("LMS_BASE"),
    FEATURES["PREVIEW_LMS_BASE"],
    "lms",
    "127.0.0.1",
    "localhost",
    "preview.localhost",
]

# Required to display all courses on start page
SEARCH_SKIP_ENROLLMENT_START_DATE_FILTERING = True

# Allow insecure oauth2 for local interaction with local containers
OAUTH_ENFORCE_SECURE = False

{{ patch("openedx-lms-production-settings") }}
