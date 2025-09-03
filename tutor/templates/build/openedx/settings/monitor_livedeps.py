import datetime
import os
import time
from django.core.files.storage import storages


DEPS_DIR = "/openedx/live-dependencies/deps"
DEPS_KEY = "deps.zip"
DEPS_ZIP_PATH = DEPS_DIR[:-4] + DEPS_KEY
TRIGGER_FILE = "/openedx/live-dependencies/uwsgi_trigger"

# TODO Use a separate storage for live dependencies
storage = storages["default"]

while True:
    if storage.exists(DEPS_KEY):
        remote_ts = storage.get_modified_time(DEPS_KEY)

        if os.path.exists(DEPS_ZIP_PATH):
            local_ts = os.path.getmtime(DEPS_ZIP_PATH)
            local_ts = datetime.datetime.fromtimestamp(local_ts, tz=datetime.timezone.utc)

            if local_ts < remote_ts:
                with open(TRIGGER_FILE, "a"):
                    os.utime(TRIGGER_FILE, None)
    # TODO What happens if download takes more than 10 seconds? 
    # This could keep initiating a reload in a loop.
    time.sleep(10)
