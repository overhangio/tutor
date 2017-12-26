from .production_common import *

ALLOWED_HOSTS = [
    ENV_TOKENS.get('LMS_BASE'),
    FEATURES['PREVIEW_LMS_BASE'],
]
