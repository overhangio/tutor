import os

# Increment this version number to trigger a new release. See
# docs/tutor.html#versioning for information on the versioning scheme.
__version__ = "13.0.2"

# The version suffix will be appended to the actual version, separated by a
# dash. Use this suffix to differentiate between the actual released version and
# the versions from other branches. For instance: set the suffix to "nightly" in
# the nightly branch.
# The suffix is cleanly separated from the __version__ in this module to avoid
# conflicts when merging branches.
__version_suffix__ = ""

# The app name will be used to define the name of the default tutor root and
# plugin directory. To avoid conflicts between multiple locally-installed
# versions, if it is defined the version suffix will also be appended to the app
# name.
__app__ = os.environ.get("TUTOR_APP", "tutor")

if __version_suffix__:
    __version__ += "-" + __version_suffix__
    __app__ += "-" + __version_suffix__
