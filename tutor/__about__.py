import os

# Increment this version number to trigger a new release. See
# docs/tutor.html#versioning for information on the versioning scheme.
__version__ = "18.1.1"

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

# Package version, as installed by pip, does not include the version suffix.
# Otherwise, nightly plugins will automatically install non-nightly Tutor
# version.
__package_version__ = __version__

if __version_suffix__:
    __version__ += "-" + __version_suffix__
    __app__ += "-" + __version_suffix__
