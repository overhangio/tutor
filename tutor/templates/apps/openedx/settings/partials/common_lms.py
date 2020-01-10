{% include "apps/openedx/settings/partials/common_all.py" %}

######## Common LMS settings

# Fix media files paths
VIDEO_IMAGE_SETTINGS["STORAGE_KWARGS"]["location"] = MEDIA_ROOT
VIDEO_TRANSCRIPTS_SETTINGS["STORAGE_KWARGS"]["location"] = MEDIA_ROOT
PROFILE_IMAGE_BACKEND["options"]["location"] = os.path.join(
    MEDIA_ROOT, "profile-images/"
)

ORA2_FILEUPLOAD_BACKEND = "filesystem"
ORA2_FILEUPLOAD_ROOT = "/openedx/data/ora2"
ORA2_FILEUPLOAD_CACHE_NAME = "ora2-storage"

GRADES_DOWNLOAD = {
    "STORAGE_TYPE": "",
    "STORAGE_KWARGS": {
        "base_url": "/media/grades/",
        "location": "/openedx/media/grades",
    },
}

COURSE_CATALOG_VISIBILITY_PERMISSION = "see_in_catalog"
COURSE_ABOUT_VISIBILITY_PERMISSION = "see_about_page"

# JWT is authentication for other openedx services
JWT_AUTH["JWT_ISSUER"] = "{{ JWT_COMMON_ISSUER }}"
JWT_AUTH["JWT_AUDIENCE"] = "{{ JWT_COMMON_AUDIENCE }}"
JWT_AUTH["JWT_SECRET_KEY"] = "{{ JWT_COMMON_SECRET_KEY }}"
JWT_AUTH["JWT_PRIVATE_SIGNING_JWK"] = None

# Allow insecure oauth2 for local interaction with local containers
OAUTH_ENFORCE_SECURE = False

# Create folders if necessary
for folder in [LOG_DIR, MEDIA_ROOT, STATIC_ROOT_BASE, ORA2_FILEUPLOAD_ROOT]:
    if not os.path.exists(folder):
        os.makedirs(folder)

{{ patch("openedx-lms-common-settings") }}

######## End of common LMS settings