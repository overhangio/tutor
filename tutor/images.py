from . import fmt
from . import utils


def build(path, tag, no_cache=False, build_args=None):
    fmt.echo_info("Building image {}".format(tag))
    command = ["build", "-t", tag, path]
    build_args = build_args or {}
    if no_cache:
        command.append("--no-cache")
    for arg in build_args:
        command += ["--build-arg", arg]
    utils.docker(*command)


def pull(tag):
    fmt.echo_info("Pulling image {}".format(tag))
    utils.execute("docker", "pull", tag)


def push(tag):
    fmt.echo_info("Pushing image {}".format(tag))
    utils.execute("docker", "push", tag)
