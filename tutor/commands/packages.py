import click
import os
import shlex
import shutil
import subprocess
from typing import cast

from tutor import config as tutor_config
from tutor.commands.context import Context
from tutor.commands.config import save as config_save_command


HERE = os.path.abspath(os.path.dirname(__file__))
DEPS_ZIP_PATH = os.path.join(HERE, "deps.zip")
DEPS_PATH = os.path.join(HERE, "deps/")


@click.group(
    name="packages",
    short_help="Manage packages",
)
def packages_command() -> None:
    """Custom persistent package manager for Tutor."""


@click.command(name="list")
@click.pass_obj
def list_command(context: Context) -> None:
    """
    List installed persistent packages.

    Entries will be fetched from the `PERSISTENT_PIP_PACKAGES` config setting.
    """
    config = tutor_config.load(context.root)
    packages = [
        package for package in cast(list[str], config["PERSISTENT_PIP_PACKAGES"])
    ]
    print(packages)


@click.command(name="build")
@click.pass_obj
def build(context: Context) -> None:
    """Rebuild dependencies from scratch."""
    config = tutor_config.load(context.root)
    DEPS = cast(list[str], config["PERSISTENT_PIP_PACKAGES"])

    build_dir = f"{context.root}/data/persistent-python-packages"

    lib_path = os.path.join(build_dir, "lib")
    bin_path = os.path.join(build_dir, "bin")

    if os.path.exists(lib_path):
        shutil.rmtree(lib_path)
    if os.path.exists(bin_path):
        shutil.rmtree(bin_path)

    _pip_install(DEPS, build_dir)


@click.command(name="append")
@click.pass_obj
@click.pass_context
@click.argument("package")
def append(click_context: click.Context, context: Context, package: str) -> None:
    """Append a new package to the list."""
    click_context.invoke(
        config_save_command,
        interactive=False,
        set_vars=[],
        append_vars=[("PERSISTENT_PIP_PACKAGES", package)],
        remove_vars=[],
        unset_vars=[],
        env_only=False,
        clean_env=False,
    )

    build_dir = f"{context.root}/data/persistent-python-packages"

    if os.path.exists(DEPS_ZIP_PATH):
        shutil.unpack_archive(DEPS_ZIP_PATH, extract_dir=build_dir)

    _pip_install([package], build_dir)


@click.command(name="remove")
@click.pass_context
@click.argument("package")
def remove(context: click.Context, package: str) -> None:
    """Remove a package and rebuild archive from scratch."""
    context.invoke(
        config_save_command,
        interactive=False,
        set_vars=[],
        append_vars=[],
        remove_vars=[("PERSISTENT_PIP_PACKAGES", package)],
        unset_vars=[],
        env_only=False,
        clean_env=False,
    )

    context.invoke(build)


def _pip_install(deps: list[str], prefix_dir: str) -> None:
    for dep in deps:
        # We use python3.11 because that's whats used in the Dockerfile
        check_call(
            "python3.11",
            "-m",
            "pip",
            "install",
            "--no-deps",
            f"--prefix={prefix_dir}",
            dep,
        )
    check_call(f'touch "{prefix_dir}/.uwsgi_trigger"', shell=True)


def check_call(*args: str, shell: bool = False) -> None:
    if shell:
        command = " ".join(args)
        print(command)
        subprocess.check_call(command, shell=True)
    else:
        print(shlex.join(args))
        subprocess.check_call(args)


packages_command.add_command(list_command)
packages_command.add_command(build)
packages_command.add_command(append)
packages_command.add_command(remove)
