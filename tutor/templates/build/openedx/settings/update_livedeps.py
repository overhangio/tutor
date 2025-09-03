import os
import shutil
import zipfile

from django.core.files.storage import storages

DEPS_DIR = "/openedx/live-dependencies/deps"
DEPS_KEY = "deps.zip"
DEPS_ZIP_PATH = DEPS_DIR[:-4] + DEPS_KEY

# TODO Use a separate storage for live dependencies
storage = storages["default"]

if storage.exists(DEPS_KEY):
    if os.path.exists(DEPS_DIR):
        shutil.rmtree(DEPS_DIR)
    os.makedirs(DEPS_DIR, exist_ok=True)

    with storage.open(DEPS_KEY, "rb") as remote_f, open(DEPS_ZIP_PATH, "wb") as local_f:
        shutil.copyfileobj(remote_f, local_f)

    with zipfile.ZipFile(DEPS_ZIP_PATH, "r") as zip_ref:
        zip_ref.extractall(DEPS_DIR)
