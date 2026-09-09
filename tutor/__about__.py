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

# The main branch is where the next Open edX release is prepared, so it carries the
# version of that upcoming release. It is derived from the RELEASE number above instead
# of being stored there, such that the __version__ line remains identical on all
# branches and merging the release branch into main never conflicts.
if __version_suffix__ == "main":
    __version__ = f"{int(__version__.split('.', maxsplit=1)[0]) + 1}.0.0"

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
