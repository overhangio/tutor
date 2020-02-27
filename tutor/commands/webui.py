import io
import os
import platform
import subprocess
import sys
import tarfile
from urllib.request import urlopen

import click

# Note: it is important that this module does not depend on config, such that
# the web ui can be launched even where there is no configuration.
from .. import fmt
from .. import env as tutor_env
from .. import serialize


@click.group(
    short_help="Web user interface", help="""Run Tutor commands from a web terminal"""
)
def webui():
    pass


@click.command(help="Start the web UI")
@click.option(
    "-p",
    "--port",
    default=3737,
    type=int,
    show_default=True,
    help="Port number to listen",
)
@click.option(
    "-h", "--host", default="0.0.0.0", show_default=True, help="Host address to listen"
)
@click.pass_obj
def start(context, port, host):
    check_gotty_binary(context.root)
    fmt.echo_info("Access the Tutor web UI at http://{}:{}".format(host, port))
    while True:
        config = load_config(context.root)
        user = config["user"]
        password = config["password"]
        command = [
            gotty_path(context.root),
            "--permit-write",
            "--address",
            host,
            "--port",
            str(port),
            "--title-format",
            "Tutor web UI - {{ .Command }} ({{ .Hostname }})",
        ]
        if user and password:
            credential = "{}:{}".format(user, password)
            command += ["--credential", credential]
        else:
            fmt.echo_alert(
                "Running web UI without user authentication. Run 'tutor webui configure' to setup authentication"
            )
        command += [sys.argv[0], "ui"]
        p = subprocess.Popen(command)
        while True:
            try:
                p.wait(timeout=2)
            except subprocess.TimeoutExpired:
                new_config = load_config(context.root)
                if new_config != config:
                    click.echo(
                        "WARNING configuration changed. Tutor web UI is now going to restart. Reload this page to continue."
                    )
                    p.kill()
                    p.wait()
                    break


@click.command(help="Configure authentication")
@click.option("-u", "--user", prompt="User name", help="Authentication user name")
@click.option(
    "-p",
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="Authentication password",
)
@click.pass_obj
def configure(context, user, password):
    save_webui_config_file(context.root, {"user": user, "password": password})
    fmt.echo_info(
        "The web UI configuration has been updated. "
        "If at any point you wish to reset your username and password, "
        "just delete the following file:\n\n    {}".format(config_path(context.root))
    )


def check_gotty_binary(root):
    path = gotty_path(root)
    if os.path.exists(path):
        return
    fmt.echo_info("Downloading gotty to {}...".format(path))

    # Generate release url
    # Note: I don't know how to handle arm
    architecture = "amd64" if platform.architecture()[0] == "64bit" else "386"
    url = "https://github.com/yudai/gotty/releases/download/v1.0.1/gotty_{system}_{architecture}.tar.gz".format(
        system=platform.system().lower(), architecture=architecture
    )

    # Download
    response = urlopen(url)

    # Decompress
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    compressed = tarfile.open(fileobj=io.BytesIO(response.read()))
    compressed.extract("./gotty", dirname)


def load_config(root):
    path = config_path(root)
    if not os.path.exists(path):
        save_webui_config_file(root, {"user": None, "password": None})
    with open(config_path(root)) as f:
        return serialize.load(f)


def save_webui_config_file(root, config):
    path = config_path(root)
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(path, "w") as of:
        serialize.dump(config, of)


def gotty_path(root):
    return get_path(root, "gotty")


def config_path(root):
    return get_path(root, "config.yml")


def get_path(root, filename):
    return tutor_env.pathjoin(root, "webui", filename)


webui.add_command(start)
webui.add_command(configure)
