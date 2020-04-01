from ..common import *
from openedx.core.lib.derived import derive_settings

STATIC_ROOT_BASE = '/openedx/staticfiles'

SECRET_KEY = 'secret'
XQUEUE_INTERFACE = {
    'django_auth': None,
    'url': None,
}
DATABASES = {
    "default": {},
}

derive_settings(__name__)

LOCALE_PATHS.append("/openedx/locale")