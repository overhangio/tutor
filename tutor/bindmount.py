from __future__ import annotations

import os
import re


from tutor import hooks


def parse_mount(value: str) -> list[tuple[str, str, str]]:
    """
    Parser for mount arguments of the form "service1[,service2,...]:/host/path:/container/path".

    Returns a list of (service, host_path, container_path) tuples.
    """
    mounts = parse_explicit_mount(value) or parse_implicit_mount(value)
    return mounts


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


def parse_implicit_mount(value: str) -> list[tuple[str, str, str]]:
    """
    Argument is of the form "/host/path"
    """
    mounts: list[tuple[str, str, str]] = []
    host_path = os.path.abspath(os.path.expanduser(value))
    for service, container_path in hooks.Filters.COMPOSE_MOUNTS.iterate(
        os.path.basename(host_path)
    ):
        mounts.append((service, host_path, container_path))
    return mounts
