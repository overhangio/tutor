import click

from . import config as tutor_config
from . import env as tutor_env
from . import fmt
from . import opts
from . import utils

@click.group(short_help="Manage docker images")
def images():
    pass

option_namespace = click.option("-n", "--namespace", default="regis", show_default=True)
option_version = click.option("-V", "--version", default="hawthorn", show_default=True)
all_images = ["openedx", "forum", "notes", "xqueue", "android"]
argument_image = click.argument(
    "image", type=click.Choice(["all"] + all_images),
)

@click.command(
    short_help="Download docker images",
    help=("""Download the docker images from hub.docker.com.
          The images will come from {namespace}/{image}:{version}.""")
)
@opts.root
@option_namespace
@option_version
@argument_image
def download(root, namespace, version, image):
    config = tutor_config.load(root)
    for image in image_list(config, image):
        utils.docker('image', 'pull', get_tag(namespace, image, version))

@click.command(
    short_help="Build docker images",
    help=("""Build the docker images necessary for an Open edX platform.
          The images will be tagged as {namespace}/{image}:{version}.""")
)
@opts.root
@option_namespace
@option_version
@argument_image
@click.option(
    "-a", "--build-arg", multiple=True,
    help="Set build-time docker ARGS in the form 'myarg=value'. This option may be specified multiple times."
)
def build(root, namespace, version, image, build_arg):
    config = tutor_config.load(root)
    for image in image_list(config, image):
        tag = get_tag(namespace, image, version)
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

@click.command(
    short_help="Pull images from hub.docker.com",
)
@opts.root
@option_namespace
@option_version
@argument_image
def pull(root, namespace, version, image):
    config = tutor_config.load(root)
    for image in image_list(config, image):
        tag = get_tag(namespace, image, version)
        click.echo(fmt.info("Pulling image {}".format(tag)))
        utils.execute("docker", "pull", tag)

@click.command(
    short_help="Push images to hub.docker.com",
)
@opts.root
@option_namespace
@option_version
@argument_image
def push(root, namespace, version, image):
    config = tutor_config.load(root)
    for image in image_list(config, image):
        tag = get_tag(namespace, image, version)
        click.echo(fmt.info("Pushing image {}".format(tag)))
        utils.execute("docker", "push", tag)

def get_tag(namespace, image, version):
    name = "openedx" if image == "openedx" else "openedx-{}".format(image)
    return "{namespace}{sep}{image}:{version}".format(
        namespace=namespace,
        sep="/" if namespace else "",
        image=name,
        version=version,
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

images.add_command(download)
images.add_command(build)
images.add_command(pull)
images.add_command(push)
