import os
from glob import glob

HERE = os.path.abspath(os.path.dirname(__file__))

config = {
    "set": {
        "OPENEDX_AWS_ACCESS_KEY": "openedx",
        "OPENEDX_AWS_SECRET_ACCESS_KEY": "{{ 24|random_string }}",
    },
    "defaults": {
        "BUCKET_NAME": "openedx",
        "FILE_UPLOAD_BUCKET_NAME": "openedxuploads",
        "COURSE_IMPORT_EXPORT_BUCKET": "openedxcourseimportexport",
        "HOST": "minio.{{ LMS_HOST }}",
        "DOCKER_REGISTRY": "{{ DOCKER_REGISTRY }}",
        "DOCKER_IMAGE_CLIENT": "minio/mc:RELEASE.2019-05-23T01-33-27Z",
        "DOCKER_IMAGE_SERVER": "minio/minio:RELEASE.2019-05-23T00-29-34Z",
    },
}

templates = os.path.join(HERE, "templates")

hooks = {
    "pre-init": ["minio-client"],
    "remote-image": {
        "minio-server": "{{ MINIO_DOCKER_IMAGE_SERVER }}",
        "minio-client": "{{ MINIO_DOCKER_IMAGE_CLIENT }}",
    },
}


def patches():
    all_patches = {}
    for path in glob(os.path.join(HERE, "patches", "*")):
        with open(path) as patch_file:
            name = os.path.basename(path)
            content = patch_file.read()
            all_patches[name] = content
    return all_patches
