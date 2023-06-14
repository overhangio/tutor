from __future__ import annotations

import os

import click
import yaml

from tutor import bindmount
from tutor import config as tutor_config
from tutor import exceptions, fmt, hooks
from tutor.commands.config import save as config_save
from tutor.commands.context import Context
from tutor.commands.params import ConfigLoaderParam


class MountParamType(ConfigLoaderParam):
    name = "mount"

    def shell_complete(
        self, ctx: click.Context, param: click.Parameter, incomplete: str
    ) -> list[click.shell_completion.CompletionItem]:
        mounts = bindmount.get_mounts(self.config)
        return [
            click.shell_completion.CompletionItem(mount)
            for mount in mounts
            if mount.startswith(incomplete)
        ]


@click.group(name="mounts")
def mounts_command() -> None:
    """
    Manage host bind-mounts

    Bind-mounted folders are used both in image building, development (`dev` commands)
    and `local` deployments.
    """


@click.command(name="list")
@click.pass_obj
def mounts_list(context: Context) -> None:
    """
    List bind-mounted folders

    Entries will be fetched from the `MOUNTS` project setting.
    """
    config = tutor_config.load(context.root)
    mounts = []
    for mount_name in bindmount.get_mounts(config):
        build_mounts = [
            {"image": image_name, "context": stage_name}
            for image_name, stage_name in hooks.Filters.IMAGES_BUILD_MOUNTS.iterate(
                mount_name
            )
        ]
        compose_mounts = [
            {
                "service": service,
                "container_path": container_path,
            }
            for service, _host_path, container_path in bindmount.parse_mount(mount_name)
        ]
        mounts.append(
            {
                "name": mount_name,
                "build_mounts": build_mounts,
                "compose_mounts": compose_mounts,
            }
        )
    fmt.echo(yaml.dump(mounts, default_flow_style=False, sort_keys=False))


@click.command(name="add")
@click.argument("mounts", metavar="mount", type=click.Path(), nargs=-1)
@click.pass_context
def mounts_add(context: click.Context, mounts: list[str]) -> None:
    """
    Add a bind-mounted folder

    The bind-mounted folder will be added to the project configuration, in the ``MOUNTS``
    setting.

    Values passed to this command can take one of two forms. The first is explicit::

        tutor mounts add myservice:/host/path:/container/path

    The second is implicit::

        tutor mounts add /host/path

    With the explicit form, the value means "bind-mount the host folder /host/path to
    /container/path in the "myservice" container at run time".

    With the implicit form, plugins are in charge of automatically detecting in which
    containers and locations the /host/path folder should be bind-mounted. In this case,
    folders can be bind-mounted at build-time -- which cannot be achieved with the
    explicit form.
    """
    new_mounts = []
    for mount in mounts:
        if not bindmount.parse_explicit_mount(mount):
            # Path is implicit: check that this path is valid
            # (we don't try to validate explicit mounts)
            mount = os.path.abspath(os.path.expanduser(mount))
            if not os.path.exists(mount):
                raise exceptions.TutorError(f"Path {mount} does not exist on the host")
        new_mounts.append(mount)
        fmt.echo_info(f"Adding bind-mount: {mount}")

    context.invoke(config_save, append_vars=[("MOUNTS", mount) for mount in new_mounts])


@click.command(name="remove")
@click.argument("mounts", metavar="mount", type=MountParamType(), nargs=-1)
@click.pass_context
def mounts_remove(context: click.Context, mounts: list[str]) -> None:
    """
    Remove a bind-mounted folder

    The bind-mounted folder will be removed from the ``MOUNTS`` project setting.
    """
    removed_mounts = []
    for mount in mounts:
        if not bindmount.parse_explicit_mount(mount):
            # Path is implicit: expand it
            mount = os.path.abspath(os.path.expanduser(mount))
        removed_mounts.append(mount)
        fmt.echo_info(f"Removing bind-mount: {mount}")

    context.invoke(
        config_save, remove_vars=[("MOUNTS", mount) for mount in removed_mounts]
    )


mounts_command.add_command(mounts_list)
mounts_command.add_command(mounts_add)
mounts_command.add_command(mounts_remove)
