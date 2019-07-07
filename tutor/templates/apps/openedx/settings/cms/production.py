import os
from cms.envs.production import *


# Execute the contents of common.py in this context
execfile(os.path.join(os.path.dirname(__file__), "common.py"), globals())

ALLOWED_HOSTS = [
    ENV_TOKENS.get("CMS_BASE"),
    "cms",
    "127.0.0.1",
    "localhost",
    "studio.localhost",
]

DEFAULT_FROM_EMAIL = ENV_TOKENS["CONTACT_EMAIL"]
DEFAULT_FEEDBACK_EMAIL = ENV_TOKENS["CONTACT_EMAIL"]
SERVER_EMAIL = ENV_TOKENS["CONTACT_EMAIL"]
