# https://hatch.pypa.io/latest/how-to/config/dynamic-metadata/
import os
import re
import typing as t

from hatchling.metadata.plugin.interface import MetadataHookInterface

HERE = os.path.dirname(__file__)

# Official plugins listed in requirements/plugins.txt are all hosted under this
# GitHub organization, in a repository that has the same name as the package.
PLUGINS_GITHUB_ORG = "https://github.com/overhangio"


class MetaDataHook(MetadataHookInterface):
    def update(self, metadata: dict[str, t.Any]) -> None:
        metadata["dependencies"] = load_requirements("base.in")
        metadata["optional-dependencies"] = {
            "dev": load_requirements("dev.txt"),
            "full": load_plugin_requirements(),
        }


def load_requirements(filename: str) -> list[str]:
    requirements = []
    with open(
        os.path.join(HERE, "requirements", filename), "rt", encoding="utf-8"
    ) as f:
        for line in f:
            line = line.strip()
            if line != "" and not line.startswith("#"):
                requirements.append(line)
    return requirements


def load_plugin_requirements() -> list[str]:
    """
    Load the official plugin requirements from requirements/plugins.txt.

    That file always pins plugins to PyPI version ranges, on every branch. In
    Tutor Main (i.e: when the version suffix is "main"), plugins are installed
    from the main branch of their GitHub repository instead. This is the same
    mechanism that sets OPENEDX_COMMON_VERSION to "master" in Tutor Main, and it
    means that plugins.txt does not differ between the main and release
    branches, so it never conflicts when one is merged into the other.
    """
    requirements = load_requirements("plugins.txt")
    if load_version_suffix() != "main":
        return requirements
    main_requirements = []
    for requirement in requirements:
        match = re.match(r"^([A-Za-z0-9][A-Za-z0-9._-]*)", requirement)
        if not match:
            raise ValueError(f"Invalid plugin requirement: '{requirement}'")
        name = match.group(1)
        main_requirements.append(f"{name}@git+{PLUGINS_GITHUB_ORG}/{name}@main")
    return main_requirements


def load_version_suffix() -> str:
    """
    Read __version_suffix__ from tutor/__about__.py without importing tutor,
    which is not installed yet at build time.
    """
    with open(os.path.join(HERE, "tutor", "__about__.py"), encoding="utf-8") as f:
        match = re.search(r'^__version_suffix__ = "([^"]*)"', f.read(), re.MULTILINE)
    if not match:
        raise ValueError("Could not find __version_suffix__ in tutor/__about__.py")
    return match.group(1)
