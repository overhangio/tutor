from __future__ import annotations

import os
import re
import typing as t

from tutor import bindmount, hooks
from tutor.__about__ import __version_suffix__


@hooks.Filters.CONFIG_DEFAULTS.add()
def _set_openedx_common_version_in_nightly(
    items: list[tuple[str, t.Any]]
) -> list[tuple[str, t.Any]]:
    if __version_suffix__ == "nightly":
        items.append(("OPENEDX_COMMON_VERSION", "master"))
    return items


@hooks.Filters.APP_PUBLIC_HOSTS.add()
def _edx_platform_public_hosts(
    hosts: list[str], context_name: t.Literal["local", "dev"]
) -> list[str]:
    if context_name == "dev":
        hosts += ["{{ LMS_HOST }}:8000", "{{ CMS_HOST }}:8001"]
    else:
        hosts += ["{{ LMS_HOST }}", "{{ CMS_HOST }}"]
    return hosts


@hooks.Filters.IMAGES_BUILD_MOUNTS.add()
def _mount_edx_platform_build(
    volumes: list[tuple[str, str]], path: str
) -> list[tuple[str, str]]:
    """
    Automatically add an edx-platform repo from the host to the build context whenever
    it is added to the `MOUNTS` setting.
    """
    if os.path.basename(path) == "edx-platform":
        volumes += [
            ("openedx", "edx-platform"),
            ("openedx-dev", "edx-platform"),
        ]
    return volumes


@hooks.Filters.COMPOSE_MOUNTS.add()
def _mount_edx_platform_compose(
    volumes: list[tuple[str, str]], name: str
) -> list[tuple[str, str]]:
    """
    When mounting edx-platform with `tutor mounts add /path/to/edx-platform`,
    bind-mount the host repo in the lms/cms containers.
    """
    if name == "edx-platform":
        path = "/openedx/edx-platform"
        volumes.append(("openedx", path))
    return volumes


# Auto-magically bind-mount xblock directories and some common dependencies.
hooks.Filters.MOUNTED_DIRECTORIES.add_items(
    [
        ("openedx", r".*[xX][bB]lock.*"),
        ("openedx", "edx-enterprise"),
        ("openedx", "edx-ora2"),
        ("openedx", "edx-search"),
        ("openedx", "openedx-learning"),
        ("openedx", r"platform-plugin-.*"),
    ]
)


@hooks.Filters.MOUNTED_DIRECTORIES.add(priority=hooks.priorities.LOW)
def _add_openedx_dev_mounted_python_packages(
    image_regex: list[tuple[str, str]]
) -> list[tuple[str, str]]:
    """
    Automatically add python packages to "openedx-dev" if they are already in the
    "openedx" image.
    """
    for image, regex in image_regex:
        if image == "openedx":
            image_regex.append(("openedx-dev", regex))
    return image_regex


@hooks.Filters.IMAGES_BUILD_MOUNTS.add()
def _mount_python_requirements_build(
    volumes: list[tuple[str, str]], path: str
) -> list[tuple[str, str]]:
    """
    Automatically bind-mount directories that match MOUNTED_DIRECTORIES at build-time.
    These directories are mounted in the "mnt-{name}" layer.
    """
    name = os.path.basename(path)
    for image_name, regex in hooks.Filters.MOUNTED_DIRECTORIES.iterate():
        if re.match(regex, name):
            volumes.append((image_name, f"mnt-{name}"))
    return volumes


@hooks.Filters.COMPOSE_MOUNTS.add()
def _mount_edx_platform_python_requirements_compose(
    volumes: list[tuple[str, str]], folder_name: str
) -> list[tuple[str, str]]:
    """
    Automatically bind-mount edx-platform Python requirements at runtime.
    """
    for image_name, regex in hooks.Filters.MOUNTED_DIRECTORIES.iterate():
        if re.match(regex, folder_name):
            # Bind-mount requirement
            # TODO this is a breaking change because we associate runtime bind-mounts to
            # "openedx" and no longer to "lms", "cms", etc.
            volumes.append((image_name, f"/mnt/{folder_name}"))
    return volumes


def iter_mounted_directories(mounts: list[str], image_name: str) -> t.Iterator[str]:
    """
    Parse the list of mounted directories and yield the directory names that are for
    the request image. Returned names are sorted in alphabetical order.
    """
    mounted_dirnames: set[str] = set()
    for mount in mounts:
        for _service, host_path, _container_path in bindmount.parse_mount(mount):
            dirname = os.path.basename(host_path)
            if is_directory_mounted(image_name, dirname):
                mounted_dirnames.add(dirname)
                break

    yield from sorted(mounted_dirnames)


def is_directory_mounted(image_name: str, dirname: str) -> bool:
    for name, regex in hooks.Filters.MOUNTED_DIRECTORIES.iterate():
        if name == image_name and re.match(regex, dirname):
            return True
    return False


hooks.Filters.ENV_TEMPLATE_VARIABLES.add_item(
    ("iter_mounted_directories", iter_mounted_directories)
)
