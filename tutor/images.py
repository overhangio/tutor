from . import fmt
from . import utils


def get_tag(config, name):
    return config["DOCKER_IMAGE_" + name.upper().replace("-", "_")]


def build(path, tag, *args):
    fmt.echo_info("Building image {}".format(tag))
    utils.docker("build", "-t", tag, *args, path)


def pull(tag):
    fmt.echo_info("Pulling image {}".format(tag))
    utils.execute("docker", "pull", tag)


def push(tag):
    fmt.echo_info("Pushing image {}".format(tag))
    utils.execute("docker", "push", tag)
