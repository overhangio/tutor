import os
from glob import glob

HERE = os.path.abspath(os.path.dirname(__file__))

config = {
    "set": {
        "OPENEDX_AWS_ACCESS_KEY": "openedx",
        "OPENEDX_AWS_SECRET_ACCESS_KEY": "{{ 8|random_string }}",
    },
    "defaults": {
        "BUCKET_NAME": "openedx",
        "FILE_UPLOAD_BUCKET_NAME": "openedxuploads",
        "COURSE_IMPORT_EXPORT_BUCKET": "openedxcourseimportexport",
        "HOST": "minio.{{ LMS_HOST }}",
    },
}


def patches(*_args):
    all_patches = {}
    for path in glob(os.path.join(HERE, "patches", "*.patch")):
        with open(path) as patch_file:
            name = os.path.basename(path)[:-6]
            content = patch_file.read()
            all_patches[name] = content
    return all_patches
