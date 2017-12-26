from .production_common import *

ALLOWED_HOSTS = [
    ENV_TOKENS.get('CMS_BASE'),
]
