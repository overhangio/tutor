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

scripts = {
    "init": [
        {
            "service": "mysql-client",
            "command": """mc config host add minio http://minio:9000 {{ OPENEDX_AWS_ACCESS_KEY }} {{ OPENEDX_AWS_SECRET_ACCESS_KEY }} --api s3v4
            mc mb minio {{ FILE_UPLOAD_BUCKET_NAME }} {{ COURSE_IMPORT_EXPORT_BUCKET }}""",
        }
    ]
}


def patches(*_args):
    all_patches = {}
    for path in glob(os.path.join(HERE, "patches", "*.patch")):
        with open(path) as patch_file:
            name = os.path.basename(path)[:-6]
            content = patch_file.read()
            all_patches[name] = content
    return all_patches
