import subprocess

import click

from .. import config as tutor_config
from .. import env as tutor_env
from .. import images
from .. import plugins

BASE_IMAGE_NAMES = ["openedx", "forum", "android"]
DEV_IMAGE_NAMES = ["openedx-dev"]


@click.group(name="images", short_help="Manage docker images")
def images_command():
    pass


@click.command(
    short_help="Build docker images",
    help="Build the docker images necessary for an Open edX platform.",
)
@click.argument("image", nargs=-1)
@click.option(
    "--no-cache", is_flag=True, help="Do not use cache when building the image"
)
@click.option(
    "-a",
    "--build-arg",
    multiple=True,
    help="Set build-time docker ARGS in the form 'myarg=value'. This option may be specified multiple times.",
)
@click.pass_obj
def build(context, image, no_cache, build_arg):
    config = tutor_config.load(context.root)
    for i in image:
        build_image(context.root, config, i, no_cache, build_arg)


def build_image(root, config, image, no_cache, build_arg):
    # Build base images
    for img in BASE_IMAGE_NAMES:
        if image in [img, "all"]:
            tag = images.get_tag(config, img)
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

    # Build dev images
    user_id = subprocess.check_output(["id", "-u"]).strip().decode()
    dev_build_args = list(build_arg) + ["USERID={}".format(user_id)]
    for img in DEV_IMAGE_NAMES:
        if image in [img, "all"]:
            tag = images.get_tag(config, img)
            images.build(
                tutor_env.pathjoin(root, "build", img),
                tag,
                no_cache=no_cache,
                build_args=dev_build_args,
            )


@click.command(short_help="Pull images from the Docker registry")
@click.argument("image", nargs=-1)
@click.pass_obj
def pull(context, image):
    config = tutor_config.load(context.root)
    for i in image:
        pull_image(config, i)


def pull_image(config, image):
    # Pull base images
    for img in image_names(config):
        if image in [img, "all"]:
            tag = images.get_tag(config, img)
            images.pull(tag)

    # Pull plugin images
    for _plugin, hook in plugins.iter_hooks(config, "remote-image"):
        for img, tag in hook.items():
            if image in [img, "all"]:
                tag = config["DOCKER_REGISTRY"] + tutor_env.render_str(config, tag)
                images.pull(tag)


@click.command(short_help="Push images to the Docker registry")
@click.argument("image", nargs=-1)
@click.pass_obj
def push(context, image):
    config = tutor_config.load(context.root)
    for i in image:
        push_image(config, i)


def push_image(config, image):
    # Push base images
    for img in BASE_IMAGE_NAMES:
        if image in [img, "all"]:
            tag = images.get_tag(config, img)
            images.push(tag)

    # Push plugin images
    for _plugin, hook in plugins.iter_hooks(config, "remote-image"):
        for img, tag in hook.items():
            if image in [img, "all"]:
                tag = config["DOCKER_REGISTRY"] + tutor_env.render_str(config, tag)
                images.push(tag)


def image_names(config):
    return BASE_IMAGE_NAMES + vendor_image_names(config)


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
