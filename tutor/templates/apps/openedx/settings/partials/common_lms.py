{% include "apps/openedx/settings/partials/common_all.py" %}

######## Common LMS settings
LOGIN_REDIRECT_WHITELIST = ["{{ CMS_HOST }}"]

# Better layout of honor code/tos links during registration
REGISTRATION_EXTRA_FIELDS["terms_of_service"] = "required"
REGISTRATION_EXTRA_FIELDS["honor_code"] = "hidden"

# Fix media files paths
PROFILE_IMAGE_BACKEND["options"]["location"] = os.path.join(
    MEDIA_ROOT, "profile-images/"
)

COURSE_CATALOG_VISIBILITY_PERMISSION = "see_in_catalog"
COURSE_ABOUT_VISIBILITY_PERMISSION = "see_about_page"

# Allow insecure oauth2 for local interaction with local containers
OAUTH_ENFORCE_SECURE = False

# Email settings
class LazyStaticAbsoluteUrl:
    """
    Evaluates a static asset path lazily at runtime
    """
    def __init__(self, path):
        self.path = path

    def __str__(self):
        from django.conf import settings
        from django.contrib.staticfiles.storage import staticfiles_storage
        return settings.LMS_ROOT_URL + staticfiles_storage.url(self.path)

    def to_json(self):
        # This method is required for json serialization by edx-ace, notably for
        # serialization of the registration email. See
        # edx_ace.serialization.MessageEncoder.
        return str(self)
# We need a lazily-computed logo url to capture the url of the theme-specific logo.
DEFAULT_EMAIL_LOGO_URL = LazyStaticAbsoluteUrl("images/logo.png")

# Create folders if necessary
for folder in [DATA_DIR, LOG_DIR, MEDIA_ROOT, STATIC_ROOT_BASE, ORA2_FILEUPLOAD_ROOT]:
    if not os.path.exists(folder):
        os.makedirs(folder)

{{ patch("openedx-lms-common-settings") }}

######## End of common LMS settings
