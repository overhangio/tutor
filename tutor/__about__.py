import os

# Increment this version number to trigger a new release. See
# docs/tutor.html#versioning for information on the versioning scheme.
__version__ = "22.0.2"

# The version suffix will be appended to the actual version, separated by a
# dash. Use this suffix to differentiate between the actual released version and
# the versions from other branches. For instance: set the suffix to "main" in
# the main branch.
# The suffix is cleanly separated from the __version__ in this module to avoid
# conflicts when merging branches.
__version_suffix__ = "main"

# Package version, as installed by pip, does not include the version suffix.
# Otherwise, Tutor Main plugins will automatically install non-Main Tutor
# version.
__package_version__ = __version__

# The app name will be used to define the name of the default tutor root and
# plugin directory. To avoid conflicts between multiple locally-installed
# versions, the version suffix is also appended to the default app name.
__default_app__ = "tutor"

if __version_suffix__:
    __version__ += "-" + __version_suffix__
    __default_app__ += "-" + __version_suffix__

# An app name set explicitly with TUTOR_APP replaces the default.
__app__ = os.environ.get("TUTOR_APP", __default_app__)
