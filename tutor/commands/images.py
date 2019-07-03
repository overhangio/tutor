import click

from .. import config as tutor_config
from .. import env as tutor_env
from .. import images
from .. import opts
from .. import plugins

OPENEDX_IMAGE_NAMES = ["openedx", "forum", "android"]


@click.group(name="images", short_help="Manage docker images")
def images_command():
    pass


@click.command(
    short_help="Build docker images",
    help="Build the docker images necessary for an Open edX platform.",
)
@opts.root
@click.argument("image")
@click.option(
    "--no-cache", is_flag=True, help="Do not use cache when building the image"
)
@click.option(
    "-a",
    "--build-arg",
    multiple=True,
    help="Set build-time docker ARGS in the form 'myarg=value'. This option may be specified multiple times.",
)
def build(root, image, no_cache, build_arg):
    config = tutor_config.load(root)

    # Build base images
    for img in OPENEDX_IMAGE_NAMES:
        if image in [img, "all"]:
            tag = get_tag(config, img)
            images.build(
                tutor_env.pathjoin(root, "build", img),
                tag,
                no_cache=no_cache,
                build_args=build_arg,
            )

    # Build plugin images
    for plugin, hook in plugins.iter_hooks(config, "build-image"):
        for img, tag in hook.items():
            if image in [img, "all"]:
                tag = tutor_env.render_str(config, tag)
                images.build(
                    tutor_env.pathjoin(root, "plugins", plugin, "build", img),
                    tag,
                    no_cache=no_cache,
                    build_args=build_arg,
                )


@click.command(short_help="Pull images from the Docker registry")
@opts.root
@click.argument("image")
def pull(root, image):
    config = tutor_config.load(root)
    # Pull base images
    for img in image_names(config):
        if image in [img, "all"]:
            tag = get_tag(config, img)
            images.pull(tag)

    # Pull plugin images
    for _plugin, hook in plugins.iter_hooks(config, "remote-image"):
        for img, tag in hook.items():
            if image in [img, "all"]:
                tag = config["DOCKER_REGISTRY"] + tutor_env.render_str(config, tag)
                images.pull(tag)


@click.command(short_help="Push images to the Docker registry")
@opts.root
@click.argument("image")
def push(root, image):
    config = tutor_config.load(root)
    # Push base images
    for img in OPENEDX_IMAGE_NAMES:
        if image in [img, "all"]:
            tag = get_tag(config, img)
            images.push(tag)

    # Push plugin images
    for _plugin, hook in plugins.iter_hooks(config, "remote-image"):
        for img, tag in hook.items():
            if image in [img, "all"]:
                tag = config["DOCKER_REGISTRY"] + tutor_env.render_str(config, tag)
                images.push(tag)


def get_tag(config, name):
    image = config["DOCKER_IMAGE_" + name.upper()]
    return "{registry}{image}".format(registry=config["DOCKER_REGISTRY"], image=image)


def image_names(config):
    return OPENEDX_IMAGE_NAMES + vendor_image_names(config)


def vendor_image_names(config):
    vendor_images = [
        "elasticsearch",
        "memcached",
        "mongodb",
        "mysql",
        "nginx",
        "rabbitmq",
        "smtp",
    ]
    for image in vendor_images[:]:
        if not config.get("ACTIVATE_" + image.upper(), True):
            vendor_images.remove(image)
    return vendor_images


images_command.add_command(build)
images_command.add_command(pull)
images_command.add_command(push)
