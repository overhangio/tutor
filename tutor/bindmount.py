from __future__ import annotations

import os
import re
import typing as t
from functools import lru_cache

from tutor import hooks, types


def get_mounts(config: types.Config) -> list[str]:
    return types.get_typed(config, "MOUNTS", list)


def iter_mounts(user_mounts: list[str], *names: str) -> t.Iterable[str]:
    """
    Iterate on the bind-mounts that are available to any given compose service. The list
    of bind-mounts is parsed from `user_mounts` and we yield only those for service
    `name`.

    Calling this function multiple times makes repeated calls to the parsing functions,
    but that's OK because their result is cached.
    """
    for user_mount in user_mounts:
        for service, host_path, container_path in parse_mount(user_mount):
            if service in names:
                yield f"{host_path}:{container_path}"


def parse_mount(value: str) -> list[tuple[str, str, str]]:
    """
    Parser for mount arguments of the form
    "service1[,service2,...]:/host/path:/container/path" (explicit) or "/host/path".

    Returns a list of (service, host_path, container_path) tuples.
    """
    mounts = parse_explicit_mount(value) or parse_implicit_mount(value)
    return mounts


@lru_cache(maxsize=None)
def parse_explicit_mount(value: str) -> list[tuple[str, str, str]]:
    """
    Argument is of the form "containers:/host/path:/container/path".
    """
    # Note that this syntax does not allow us to include colon ':' characters in paths
    match = re.match(
        r"(?P<services>[a-zA-Z0-9-_, ]+):(?P<host_path>[^:]+):(?P<container_path>[^:]+)",
        value,
    )
    if not match:
        return []

    mounts: list[tuple[str, str, str]] = []
    services: list[str] = [service.strip() for service in match["services"].split(",")]
    host_path = os.path.abspath(os.path.expanduser(match["host_path"]))
    host_path = host_path.replace(os.path.sep, "/")
    container_path = match["container_path"]
    for service in services:
        if service:
            mounts.append((service, host_path, container_path))
    return mounts


@lru_cache(maxsize=None)
def parse_implicit_mount(value: str) -> list[tuple[str, str, str]]:
    """
    Argument is of the form "/path/to/host/directory"
    """
    mounts: list[tuple[str, str, str]] = []
    host_path = os.path.abspath(os.path.expanduser(value))
    for service, container_path in hooks.Filters.COMPOSE_MOUNTS.iterate(
        os.path.basename(host_path)
    ):
        mounts.append((service, host_path, container_path))
    return mounts
