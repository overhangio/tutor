import os

import appdirs

from tutor.__about__ import __app__

PLUGINS_ROOT_ENV_VAR_NAME = "TUTOR_PLUGINS_ROOT"

# Folder path which contains *.yml and *.py file plugins.
# On linux this is typically ``~/.local/share/tutor-plugins``. On the nightly branch
# this will be ``~/.local/share/tutor-plugins-nightly``.
# The path can be overridden by defining the ``TUTOR_PLUGINS_ROOT`` environment
# variable.
PLUGINS_ROOT = os.path.expanduser(
    os.environ.get(PLUGINS_ROOT_ENV_VAR_NAME, "")
) or appdirs.user_data_dir(appname=__app__ + "-plugins")
