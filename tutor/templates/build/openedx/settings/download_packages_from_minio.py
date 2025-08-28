import datetime
import os
import shutil
import zipfile

import boto3

DEPS_DIR = "/openedx/persistent-python-packages/deps"
MINIO_KEY = "deps.zip"
DEPS_ZIP_PATH = DEPS_DIR[:-4] + MINIO_KEY
MINIO_BUCKET = "tutor-deps"
TRIGGER_FILE = "/openedx/persistent-python-packages/.uwsgi_trigger"

s3 = boto3.client(
    "s3",
    endpoint_url="http://" + os.environ.get("MINIO_HOST"),
    aws_access_key_id=os.environ.get("OPENEDX_AWS_ACCESS_KEY"),
    aws_secret_access_key=os.environ.get("OPENEDX_AWS_SECRET_ACCESS_KEY"),
)


def _download_from_minio():
    head = s3.head_object(Bucket=MINIO_BUCKET, Key=MINIO_KEY)
    remote_ts = head["LastModified"].astimezone(datetime.timezone.utc)

    if os.path.exists(DEPS_ZIP_PATH):
        local_ts = os.path.getmtime(DEPS_ZIP_PATH)
        local_ts = datetime.datetime.fromtimestamp(local_ts, tz=datetime.timezone.utc)

        if local_ts >= remote_ts:
            return

    if os.path.exists(DEPS_DIR):
        shutil.rmtree(DEPS_DIR)
    os.makedirs(DEPS_DIR, exist_ok=True)

    s3.download_file(MINIO_BUCKET, MINIO_KEY, DEPS_ZIP_PATH)

    with zipfile.ZipFile(DEPS_ZIP_PATH, "r") as zip_ref:
        zip_ref.extractall(DEPS_DIR)

    with open(TRIGGER_FILE, "a"):
        os.utime(TRIGGER_FILE, None)


_download_from_minio()
