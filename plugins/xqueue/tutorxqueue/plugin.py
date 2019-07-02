from glob import glob
import os

HERE = os.path.abspath(os.path.dirname(__file__))

config = {
    "add": {
        "AUTH_PASSWORD": "{{ 8|random_string }}",
        "MYSQL_PASSWORD": "{{ 8|random_string }}",
        "SECRET_KEY": "{{ 24|random_string }}",
    },
    "defaults": {
        "DOCKER_IMAGE": "overhangio/openedx-xqueue:{{ TUTOR_VERSION }}",
        "AUTH_USERNAME": "lms",
        "MYSQL_DATABASE": "xqueue",
        "MYSQL_USERNAME": "xqueue",
    },
}

templates = os.path.join(HERE, "templates")
hooks = {
    "init": ["mysql-client", "xqueue"],
    "build-image": {"xqueue": "{{ XQUEUE_DOCKER_IMAGE }}"},
    "remote-image": {"xqueue": "{{ XQUEUE_DOCKER_IMAGE }}"},
}


def patches():
    all_patches = {}
    for path in glob(os.path.join(HERE, "patches", "*")):
        with open(path) as patch_file:
            name = os.path.basename(path)
            content = patch_file.read()
            all_patches[name] = content
    return all_patches
