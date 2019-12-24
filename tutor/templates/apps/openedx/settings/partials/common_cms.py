{% include "apps/openedx/settings/partials/common_all.py" %}

######## Common CMS settings

STUDIO_NAME = u"{{ PLATFORM_NAME }} - Studio"
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