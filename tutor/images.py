import click

from . import config as tutor_config
from . import env as tutor_env
from . import fmt
from . import opts
from . import utils


@click.group(short_help="Manage docker images")
def images_command():
    pass


OPENEDX_IMAGES = ["openedx", "forum", "notes", "xqueue", "android"]
VENDOR_IMAGES = [
    "elasticsearch",
    "memcached",
    "mongodb",
    "mysql",
    "nginx",
    "rabbitmq",
    "smtp",
]
argument_openedx_image = click.argument(
    "image", type=click.Choice(["all"] + OPENEDX_IMAGES)
)
argument_image = click.argument(
    "image", type=click.Choice(["all"] + OPENEDX_IMAGES + VENDOR_IMAGES)
)


@click.command(
    short_help="Build docker images",
    help="Build the docker images necessary for an Open edX platform.",
)
@opts.root
@argument_openedx_image
@click.option(
    "-a",
    "--build-arg",
    multiple=True,
    help="Set build-time docker ARGS in the form 'myarg=value'. This option may be specified multiple times.",
)
def build(root, image, build_arg):
    config = tutor_config.load(root)
    for img in openedx_image_names(config, image):
        tag = get_tag(config, img)
        click.echo(fmt.info("Building image {}".format(tag)))
        command = ["build", "-t", tag, tutor_env.pathjoin(root, "build", img)]
        for arg in build_arg:
            command += ["--build-arg", arg]
        utils.docker(*command)


@click.command(short_help="Pull images from the Docker registry")
@opts.root
@argument_image
def pull(root, image):
    config = tutor_config.load(root)
    for img in image_names(config, image):
        tag = get_tag(config, img)
        click.echo(fmt.info("Pulling image {}".format(tag)))
        utils.execute("docker", "pull", tag)


@click.command(short_help="Push images to the Docker registry")
@opts.root
@argument_openedx_image
def push(root, image):
    config = tutor_config.load(root)
    for tag in openedx_image_tags(config, image):
        click.echo(fmt.info("Pushing image {}".format(tag)))
        utils.execute("docker", "push", tag)


def get_tag(config, name):
    image = config["DOCKER_IMAGE_" + name.upper()]
    return "{registry}{image}".format(registry=config["DOCKER_REGISTRY"], image=image)


def image_names(config, image):
    return openedx_image_names(config, image) + vendor_image_names(config, image)


def openedx_image_tags(config, image):
    for img in openedx_image_names(config, image):
        yield get_tag(config, img)


def openedx_image_names(config, image):
    if image == "all":
        images = OPENEDX_IMAGES[:]
        if not config["ACTIVATE_XQUEUE"]:
            images.remove("xqueue")
        if not config["ACTIVATE_NOTES"]:
            images.remove("notes")
        return images
    return [image]


def vendor_image_names(config, image):
    if image == "all":
        images = VENDOR_IMAGES[:]
        if not config["ACTIVATE_ELASTICSEARCH"]:
            images.remove("elasticsearch")
        if not config["ACTIVATE_MEMCACHED"]:
            images.remove("memcached")
        if not config["ACTIVATE_MONGODB"]:
            images.remove("mongodb")
        if not config["ACTIVATE_MYSQL"]:
            images.remove("mysql")
        if not config["ACTIVATE_RABBITMQ"]:
            images.remove("rabbitmq")
        return images
    return [image]


images_command.add_command(build)
images_command.add_command(pull)
images_command.add_command(push)
