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
# Dummy value required for the i18n build steps to run, but
# it has no impact on the output produced by those steps.
LMS_ROOT_URL = "https://lms.local"

derive_settings(__name__)


{{ patch("openedx-common-i18n-settings") }}
