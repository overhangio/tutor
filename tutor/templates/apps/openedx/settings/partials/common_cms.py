{% include "apps/openedx/settings/partials/common_all.py" %}

######## Common CMS settings


STUDIO_NAME = u"{{ PLATFORM_NAME }} - Studio"

# Create folders if necessary
for folder in [LOG_DIR, MEDIA_ROOT, STATIC_ROOT_BASE]:
    if not os.path.exists(folder):
        os.makedirs(folder)

{{ patch("openedx-cms-common-settings") }}

######## End of common CMS settings