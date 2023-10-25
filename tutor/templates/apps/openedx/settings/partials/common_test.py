# Fix MongoDb connection credentials
DOC_STORE_CONFIG["user"] = None
DOC_STORE_CONFIG["password"] = None

# In edx-platform CI, unit tests are run in-process, so many of them break if run
# async on the workers. So, we default to testing them in-process as well.
CELERY_ALWAYS_EAGER = True
