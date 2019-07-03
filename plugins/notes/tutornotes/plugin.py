from glob import glob
import os

HERE = os.path.abspath(os.path.dirname(__file__))

config = {
    "add": {
        "MYSQL_PASSWORD": "{{ 8|random_string }}",
        "SECRET_KEY": "{{ 24|random_string }}",
        "OAUTH2_SECRET": "{{ 24|random_string }}",
    },
    "defaults": {
        "DOCKER_IMAGE": "overhangio/openedx-notes:{{ TUTOR_VERSION }}",
        "HOST": "notes.{{ LMS_HOST }}",
        "MYSQL_DATABASE": "notes",
        "MYSQL_USERNAME": "notes",
    },
}

templates = os.path.join(HERE, "templates")
hooks = {
    "init": ["mysql-client", "lms", "notes"],
    "build-image": {"notes": "{{ NOTES_DOCKER_IMAGE }}"},
    "remote-image": {"notes": "{{ NOTES_DOCKER_IMAGE }}"},
}


def patches():
    all_patches = {}
    for path in glob(os.path.join(HERE, "patches", "*")):
        with open(path) as patch_file:
            name = os.path.basename(path)
            content = patch_file.read()
            all_patches[name] = content
    return all_patches
