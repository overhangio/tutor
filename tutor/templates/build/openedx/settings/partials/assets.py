"""
Bare minimum settings for collecting production assets.
"""
from ..common import *
from openedx.core.lib.derived import derive_settings

ENABLE_COMPREHENSIVE_THEMING = True

SECRET_KEY = 'secret'
XQUEUE_INTERFACE = {
    'django_auth': None,
    'url': None,
}
DATABASES = {
    "default": {},
}
# Dummy value required for the static asset build steps to run,
# but it has no impact on the output produced by those steps.
LMS_ROOT_URL = "https://lms.local"

{{ patch("openedx-common-assets-settings") }}
