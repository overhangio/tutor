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

derive_settings(__name__)


{{ patch("openedx-common-i18n-settings") }}
