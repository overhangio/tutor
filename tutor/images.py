import click

from . import config as tutor_config
from . import env as tutor_env
from . import fmt
from . import opts
from . import utils

@click.group(short_help="Manage docker images")
def images():
    pass

all_images = ["openedx", "forum", "notes", "xqueue", "android"]
argument_image = click.argument(
    "image", type=click.Choice(["all"] + all_images),
)

@click.command(
    short_help="Build docker images",
    help="Build the docker images necessary for an Open edX platform."
)
@opts.root
@argument_image
@click.option(
    "-a", "--build-arg", multiple=True,
    help="Set build-time docker ARGS in the form 'myarg=value'. This option may be specified multiple times."
)
def build(root, image, build_arg):
    config = tutor_config.load(root)
    for image in image_list(config, image):
        tag = get_tag(config, image)
        click.echo(fmt.info("Building image {}".format(tag)))
        command = [
            "build", "-t", tag,
            tutor_env.pathjoin(root, "build", image)
        ]
        for arg in build_arg:
            command += [
                "--build-arg", arg
            ]
        utils.docker(*command)

@click.command(short_help="Pull images from the docker registry")
@opts.root
@argument_image
def pull(root, image):
    config = tutor_config.load(root)
    for image in image_list(config, image):
        tag = get_tag(config, image)
        click.echo(fmt.info("Pulling image {}".format(tag)))
        utils.execute("docker", "pull", tag)

@click.command(short_help="Push images to the Docker registry")
@opts.root
@argument_image
def push(root, image):
    config = tutor_config.load(root)
    for image in image_list(config, image):
        tag = get_tag(config, image)
        click.echo(fmt.info("Pushing image {}".format(tag)))
        utils.execute("docker", "push", tag)

def get_tag(config, name):
    image = config["DOCKER_IMAGE_" + name.upper()]
    return "{registry}{image}".format(
        registry=config["DOCKER_REGISTRY"],
        image=image,
    )

def image_list(config, image):
    if image == "all":
        images = all_images[:]
        if not config['ACTIVATE_XQUEUE']:
            images.remove('xqueue')
        if not config['ACTIVATE_NOTES']:
            images.remove('notes')
        return images
    return [image]

images.add_command(build)
images.add_command(pull)
images.add_command(push)
