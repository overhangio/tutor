from ..common import *
from openedx.core.lib.derived import derive_settings

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

derive_settings(__name__)


{{ patch("openedx-common-i18n-settings") }}
