from . import fmt
from . import utils


def get_tag(config, name):
    image = config["DOCKER_IMAGE_" + name.upper().replace("-", "_")]
    return "{registry}{image}".format(registry=config["DOCKER_REGISTRY"], image=image)


def build(path, tag, no_cache=False, build_args=None, add_hosts=None):
    fmt.echo_info("Building image {}".format(tag))
    command = ["build", "-t", tag, path]
    build_args = build_args or {}
    add_hosts = add_hosts or {}
    if no_cache:
        command.append("--no-cache")
    for arg in build_args:
        command += ["--build-arg", arg]
    for host in add_hosts:
        command += ["--add-host", host]
    utils.docker(*command)


def pull(tag):
    fmt.echo_info("Pulling image {}".format(tag))
    utils.execute("docker", "pull", tag)


def push(tag):
    fmt.echo_info("Pushing image {}".format(tag))
    utils.execute("docker", "push", tag)
