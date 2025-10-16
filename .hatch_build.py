# https://hatch.pypa.io/latest/how-to/config/dynamic-metadata/
import os
import typing as t

from hatchling.metadata.plugin.interface import MetadataHookInterface

HERE = os.path.dirname(__file__)


class MetaDataHook(MetadataHookInterface):
    def update(self, metadata: dict[str, t.Any]) -> None:
        about = load_about()
        metadata["version"] = about["__package_version__"]
        metadata["dependencies"] = load_requirements("base.in")
        metadata["optional-dependencies"] = {
            "dev": load_requirements("dev.txt"),
            "full": load_requirements("plugins.txt"),
        }


def load_about() -> dict[str, str]:
    about: dict[str, str] = {}
    with open(os.path.join(HERE, "tutor", "__about__.py"), "rt", encoding="utf-8") as f:
        exec(f.read(), about)
    return about


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
