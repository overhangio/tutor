# TODO clean this up
import os
os.environ["EDXAPP_TEST_MONGO_HOST"] = "mongodb"

from ..test import *

# Fix MongoDb connection credentials
DOC_STORE_CONFIG["user"] = None
DOC_STORE_CONFIG["password"] = None
