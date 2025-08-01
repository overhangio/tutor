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
LMS_BASE = "{{ LMS_HOST }}:8000"
LMS_ROOT_URL = "http://{}".format(LMS_BASE)

{{ patch("openedx-common-assets-settings") }}
