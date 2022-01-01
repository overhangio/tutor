{% include "apps/openedx/settings/partials/common_all.py" %}

######## Common CMS settings

STUDIO_NAME = u"{{ PLATFORM_NAME }} - Studio"

# Authentication
SOCIAL_AUTH_EDX_OAUTH2_SECRET = "{{ CMS_OAUTH2_SECRET }}"
SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT = "http://lms:8000"
SOCIAL_AUTH_REDIRECT_IS_HTTPS = False  # scheme is correctly included in redirect_uri

MAX_ASSET_UPLOAD_FILE_SIZE_IN_MB = 100

FRONTEND_LOGIN_URL = LMS_ROOT_URL + '/login'
FRONTEND_LOGOUT_URL = LMS_ROOT_URL + '/logout'
FRONTEND_REGISTER_URL = LMS_ROOT_URL + '/register'

# Create folders if necessary
for folder in [LOG_DIR, MEDIA_ROOT, STATIC_ROOT_BASE]:
    if not os.path.exists(folder):
        os.makedirs(folder)

{{ patch("openedx-cms-common-settings") }}

######## End of common CMS settings
