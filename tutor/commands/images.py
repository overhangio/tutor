from __future__ import annotations

import os
import typing as t

import click

from tutor import bindmount, exceptions, fmt, hooks, images, utils
from tutor import config as tutor_config
from tutor import env as tutor_env
from tutor.commands.context import Context
from tutor.commands.params import ConfigLoaderParam
from tutor.core.hooks import Filter
from tutor.types import Config

BASE_IMAGE_NAMES = [
    ("openedx", "DOCKER_IMAGE_OPENEDX"),
    ("permissions", "DOCKER_IMAGE_PERMISSIONS"),
]


@hooks.Filters.IMAGES_BUILD.add()
def _add_core_images_to_build(
    build_images: list[tuple[str, t.Union[str, tuple[str, ...]], str, tuple[str, ...]]],
    config: Config,
) -> list[tuple[str, t.Union[str, tuple[str, ...]], str, tuple[str, ...]]]:
    """
    Add base images to the list of Docker images to build on `tutor build all`.
    """
    for image, tag in BASE_IMAGE_NAMES:
        build_images.append(
            (
                image,
                os.path.join("build", image),
                tutor_config.get_typed(config, tag, str),
                (),
            )
        )

    # Build openedx-dev image
    build_images.append(
        (
            "openedx-dev",
            os.path.join("build", "openedx"),
            tutor_config.get_typed(config, "DOCKER_IMAGE_OPENEDX_DEV", str),
            (
                "--target=development",
                f"--build-arg=APP_USER_ID={utils.get_user_id() or 1000}",
            ),
        )
    )

    return build_images


@hooks.Filters.IMAGES_PULL.add()
def _add_images_to_pull(
    remote_images: list[tuple[str, str]], config: Config
) -> list[tuple[str, str]]:
    """
    Add base and vendor images to the list of Docker images to pull on `tutor pull all`.
    """
    vendor_images = [
        ("caddy", "DOCKER_IMAGE_CADDY"),
        ("meilisearch", "DOCKER_IMAGE_MEILISEARCH"),
        ("mongodb", "DOCKER_IMAGE_MONGODB"),
        ("mysql", "DOCKER_IMAGE_MYSQL"),
        ("redis", "DOCKER_IMAGE_REDIS"),
        ("smtp", "DOCKER_IMAGE_SMTP"),
    ]
    for image, tag_name in vendor_images:
        if config.get(f"RUN_{image.upper()}", True):
            remote_images.append((image, tutor_config.get_typed(config, tag_name, str)))
    for image, tag in BASE_IMAGE_NAMES:
        remote_images.append((image, tutor_config.get_typed(config, tag, str)))
    return remote_images


@hooks.Filters.IMAGES_PUSH.add()
def _add_core_images_to_push(
    remote_images: list[tuple[str, str]], config: Config
) -> list[tuple[str, str]]:
    """
    Add base images to the list of Docker images to push on `tutor push all`.
    """
    for image, tag in BASE_IMAGE_NAMES:
        remote_images.append((image, tutor_config.get_typed(config, tag, str)))
    return remote_images


class ImageNameParam(ConfigLoaderParam):
    """
    Convenient auto-completion of image names.
    """

    def shell_complete(
        self, ctx: click.Context, param: click.Parameter, incomplete: str
    ) -> list[click.shell_completion.CompletionItem]:
        results = []
        for name in self.iter_image_names():
            if name.startswith(incomplete):
                results.append(click.shell_completion.CompletionItem(name))
        return results

    def iter_image_names(self) -> t.Iterable["str"]:
        raise NotImplementedError


class BuildImageNameParam(ImageNameParam):
    def iter_image_names(self) -> t.Iterable["str"]:
        for name, _path, _tag, _args in hooks.Filters.IMAGES_BUILD.iterate(self.config):
            yield name


class PullImageNameParam(ImageNameParam):
    def iter_image_names(self) -> t.Iterable["str"]:
        for name, _tag in hooks.Filters.IMAGES_PULL.iterate(self.config):
            yield name


class PushImageNameParam(ImageNameParam):
    def iter_image_names(self) -> t.Iterable["str"]:
        for name, _tag in hooks.Filters.IMAGES_PUSH.iterate(self.config):
            yield name


@click.group(name="images", short_help="管理 docker 镜像")
def images_command() -> None:
    pass


@click.command()
@click.argument(
    "image_names",
    metavar="image",
    nargs=-1,
    type=BuildImageNameParam(),
)
@click.option(
    "--no-cache", is_flag=True, help="构建镜像时不使用缓存"
)
@click.option(
    "--no-registry-cache",
    is_flag=True,
    help="构建镜像时不使用仓库缓存",
)
@click.option(
    "--cache-to-registry",
    is_flag=True,
    help="将构建缓存推送到远程仓库。仅当您拥有远程仓库的推送权限时才启用此选项。",
)
@click.option(
    "--output",
    "docker_output",
    # 导出镜像到 docker。这是使镜像可用于 docker-compose 所必需的。
    # `--load` 选项是 `--output=type=docker` 的简写。
    default="type=docker",
    help="与 `docker build --output=...` 相同。",
)
@click.option(
    "-a",
    "--build-arg",
    "build_args",
    multiple=True,
    help="以 'myarg=value' 形式设置构建时的 docker ARGS。此选项可以多次指定。",
)
@click.option(
    "--add-host",
    "add_hosts",
    multiple=True,
    help="设置自定义主机到 IP 的映射（host:ip）。",
)
@click.option(
    "--target",
    help="设置要构建的目标构建阶段。",
)
@click.option(
    "-d",
    "--docker-arg",
    "docker_args",
    multiple=True,
    help="为 docker build 命令设置额外选项。",
)
@click.pass_obj
def build(
    context: Context,
    image_names: list[str],
    no_cache: bool,
    no_registry_cache: bool,
    cache_to_registry: bool,
    docker_output: str,
    build_args: list[str],
    add_hosts: list[str],
    target: str,
    docker_args: list[str],
) -> None:
    """
    Build docker images

    Build the docker images necessary for an Open edX platform. By default, the remote
    registry cache will be used for better performance.
    """
    config = tutor_config.load(context.root)
    command_args = []
    if no_cache:
        command_args.append("--no-cache")
    for build_arg in build_args:
        command_args += ["--build-arg", build_arg]
    for add_host in add_hosts:
        command_args += ["--add-host", add_host]
    if target:
        command_args += ["--target", target]
    if docker_output:
        command_args.append(f"--output={docker_output}")
    if docker_args:
        command_args += docker_args
    # Build context mounts
    build_contexts = get_image_build_contexts(config)

    for image in image_names:
        for name, path, tag, custom_args in find_images_to_build(config, image):
            image_build_args = [*command_args, *custom_args]

            # Registry cache
            if not no_registry_cache:
                image_build_args.append(f"--cache-from=type=registry,ref={tag}-cache")
            if cache_to_registry:
                image_build_args.append(
                    f"--cache-to=type=registry,mode=max,ref={tag}-cache,image-manifest=true"
                )

            # Build contexts
            for host_path, stage_name in build_contexts.get(name, []):
                fmt.echo_info(
                    f"Adding {host_path} to the build context '{stage_name}' of image '{image}'"
                )
                image_build_args.append(f"--build-context={stage_name}={host_path}")

            # Build
            images.build(
                tutor_env.pathjoin(context.root, path),
                tag,
                *image_build_args,
            )


def get_image_build_contexts(config: Config) -> dict[str, list[tuple[str, str]]]:
    """
    Return all build contexts for all images.

    A build context is to bind-mount a host directory at build-time. This is useful, for
    instance to build a Docker image with a local git checkout of a remote repo.

    Users configure bind-mounts with the `MOUNTS` config setting. Plugins can then
    automatically add build contexts based on these values.
    """
    build_contexts: dict[str, list[tuple[str, str]]] = {}
    for user_mount in bindmount.get_mounts(config):
        for image_name, stage_name in hooks.Filters.IMAGES_BUILD_MOUNTS.iterate(
            user_mount
        ):
            if image_name not in build_contexts:
                build_contexts[image_name] = []
            build_contexts[image_name].append((user_mount, stage_name))
    return build_contexts


@click.command(short_help="从 Docker 仓库拉取镜像")
@click.argument("image_names", metavar="image", type=PullImageNameParam(), nargs=-1)
@click.pass_obj
def pull(context: Context, image_names: list[str]) -> None:
    config = tutor_config.load_full(context.root)
    for image in image_names:
        for tag in find_remote_image_tags(config, hooks.Filters.IMAGES_PULL, image):
            images.pull(tag)


@click.command(short_help="推送镜像到 Docker 仓库")
@click.argument("image_names", metavar="image", type=PushImageNameParam(), nargs=-1)
@click.pass_obj
def push(context: Context, image_names: list[str]) -> None:
    config = tutor_config.load_full(context.root)
    for image in image_names:
        for tag in find_remote_image_tags(config, hooks.Filters.IMAGES_PUSH, image):
            images.push(tag)


@click.command(short_help="打印 Docker 镜像关联的标签")
@click.argument("image_names", metavar="image", type=BuildImageNameParam(), nargs=-1)
@click.pass_obj
def printtag(context: Context, image_names: list[str]) -> None:
    config = tutor_config.load_full(context.root)
    for image in image_names:
        for _name, _path, tag, _args in find_images_to_build(config, image):
            print(tag)


def find_images_to_build(
    config: Config, image: str
) -> t.Iterator[tuple[str, str, str, tuple[str, ...]]]:
    """
    Iterate over all images to build.

    If no corresponding image is found, raise exception.

    Yield: (name, path, tag, build args)
    """
    found = False
    for name, path, tag, args in hooks.Filters.IMAGES_BUILD.iterate(config):
        relative_path = path if isinstance(path, str) else os.path.join(*path)
        if image in [name, "all"]:
            found = True
            tag = tutor_env.render_str(config, tag)
            yield (name, relative_path, tag, args)

    if not found:
        raise ImageNotFoundError(image)


def find_remote_image_tags(
    config: Config,
    filtre: Filter[list[tuple[str, str]], [Config]],
    image: str,
) -> t.Iterator[str]:
    """
    Iterate over all images to push or pull.

    If no corresponding image is found, raise exception.

    Yield: tag
    """
    all_remote_images = filtre.iterate(config)
    found = False
    for name, tag in all_remote_images:
        if image in [name, "all"]:
            found = True
            yield tutor_env.render_str(config, tag)
    if not found:
        raise ImageNotFoundError(image)


class ImageNotFoundError(exceptions.TutorError):
    def __init__(self, image_name: str):
        super().__init__(f"Image '{image_name}' could not be found")


@click.command(name="list", help="列出 EdOps 模块镜像")
@click.option(
    "--module",
    "module_filter",
    help="按模块名称过滤",
)
@click.pass_obj
def edops_list(context: Context, module_filter: t.Optional[str]) -> None:
    """列出所有 EdOps 模块镜像及其当前版本。"""
    from tutor.edops import modules as edops_modules

    config = tutor_config.load(context.root)
    modules_list = edops_modules.get_enabled_modules(config)

    if module_filter:
        modules_list = [m for m in modules_list if m.name == module_filter]
        if not modules_list:
            fmt.echo_error(f"模块 '{module_filter}' 未找到或未启用")
            return

    fmt.echo_info("EdOps 模块镜像:\n")
    for module in modules_list:
        if not module.images:
            continue

        fmt.echo(f"\n{module.name}:")
        for image in module.images:
            # 渲染仓库和版本变量以获取实际值
            repo = tutor_env.render_str(config, image.repository)
            version_var = image.version_var
            version = config.get(version_var, "unknown")
            fmt.echo(f"  {image.name:30} {repo}:{version}")


@click.command(name="versions", help="列出服务的可用版本")
@click.argument("service_name")
@click.option("--debug", is_flag=True, help="显示调试信息")
@click.pass_obj
def edops_versions(context: Context, service_name: str, debug: bool) -> None:
    """查询 Docker Registry 中的可用镜像版本。"""
    from tutor.edops import image_registry

    config = tutor_config.load(context.root)

    try:
        # 从模块元数据解析完整的 repository 路径
        repository = image_registry.resolve_repository_path(config, service_name)
        
        if debug:
            fmt.echo_info("=== 调试信息 ===")
            fmt.echo_info(f"Registry: {config.get('EDOPS_IMAGE_REGISTRY', '未设置')}")
            fmt.echo_info(f"Username: {config.get('EDOPS_IMAGE_REGISTRY_USER', '未设置')}")
            fmt.echo_info(f"Password: {'已设置' if config.get('EDOPS_IMAGE_REGISTRY_PASSWORD') else '未设置'}")
            fmt.echo_info(f"Token: {'已设置' if config.get('EDOPS_IMAGE_REGISTRY_TOKEN') else '未设置'}")
            fmt.echo_info(f"Repository: {repository}")
            fmt.echo_info("===============\n")
            
            # 尝试获取 WWW-Authenticate 头用于调试
            try:
                from tutor.edops import image_registry
                test_client = image_registry.get_registry_client(config)
                test_url = f"https://{config.get('EDOPS_IMAGE_REGISTRY', '')}/v2/{repository}/tags/list"
                import requests
                test_response = requests.get(test_url, timeout=5)
                if test_response.status_code == 401:
                    www_auth = test_response.headers.get("WWW-Authenticate", "")
                    fmt.echo_info(f"WWW-Authenticate: {www_auth}")
            except Exception:
                pass
        
        client = image_registry.get_registry_client(config)
        tags = client.list_tags(repository)

        if not tags:
            fmt.echo_info(f"未找到 {service_name} (repository: {repository}) 的标签")
            return

        fmt.echo_info(f"{service_name} (repository: {repository}) 的可用版本:\n")
        # 排序标签，如果存在 'latest' 则放在最前面
        sorted_tags = sorted(tags, reverse=True)
        if "latest" in sorted_tags:
            sorted_tags.remove("latest")
            sorted_tags.insert(0, "latest")

        for tag in sorted_tags:
            fmt.echo(f"  - {tag}")

    except Exception as e:
        fmt.echo_error(f"列出版本失败: {e}")
        if debug:
            import traceback
            fmt.echo_error(traceback.format_exc())


@click.command(name="inspect", help="检查镜像详情")
@click.argument("service_name")
@click.option("--tag", default="latest", help="要检查的镜像标签")
@click.pass_obj
def edops_inspect(context: Context, service_name: str, tag: str) -> None:
    """从仓库获取镜像的详细信息。"""
    from tutor.edops import image_registry
    import json

    config = tutor_config.load(context.root)

    try:
        # 从模块元数据解析完整的 repository 路径
        repository = image_registry.resolve_repository_path(config, service_name)
        
        client = image_registry.get_registry_client(config)
        manifest = client.get_manifest(repository, tag)

        if not manifest:
            fmt.echo_error(f"未找到 {service_name} (repository: {repository}):{tag} 的 manifest")
            return

        fmt.echo_info(f"镜像: {service_name} (repository: {repository}):{tag}\n")
        fmt.echo(json.dumps(manifest, indent=2))

    except Exception as e:
        fmt.echo_error(f"检查镜像失败: {e}")


images_command.add_command(build)
images_command.add_command(pull)
images_command.add_command(push)
images_command.add_command(printtag)
images_command.add_command(edops_list)
images_command.add_command(edops_versions)
images_command.add_command(edops_inspect)
