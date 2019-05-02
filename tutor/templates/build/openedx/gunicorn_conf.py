import os

# Set the number of gunicorn workers
workers = int(os.environ.get("GUNICORN_WORKERS", "2"))