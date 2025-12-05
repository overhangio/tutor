from __future__ import annotations

import json
import os
import typing as t

import click

from tutor import bindmount, fmt, hooks, utils
from tutor import config as tutor_config
from tutor import env as tutor_env
from tutor import interactive as interactive_config
from tutor.commands import images, jobs
from tutor.commands.config import save as config_save_command
from tutor.commands.context import BaseTaskContext
from tutor.commands.upgrade import OPENEDX_RELEASE_NAMES
from tutor.commands.upgrade.compose import upgrade_from
from tutor.core.hooks import Filter  # noqa: F401
from tutor.exceptions import TutorError
from tutor.tasks import BaseComposeTaskRunner
from tutor.types import Config


class ComposeTaskRunner(BaseComposeTaskRunner):
    HOOK_FIRED: bool = False

    def __init__(self, root: str, config: Config):
        super().__init__(root, config)
        self.project_name = ""
        self.docker_compose_files: list[str] = []
        self.docker_compose_job_files: list[str] = []

    def _get_docker_compose_args(self, *command: str) -> list[str]:
        """
        Returns appropriate arguments (yml files) to be used with the docker compose commmand
        """
        # Trigger the action just once per runtime
        start_commands = ("start", "up", "restart", "run")
        if not ComposeTaskRunner.HOOK_FIRED and any(
            [cmd in command for cmd in start_commands]
        ):
            ComposeTaskRunner.HOOK_FIRED = True
            hooks.Actions.COMPOSE_PROJECT_STARTED.do(
                self.root, self.config, self.project_name
            )
        args = []
        for docker_compose_path in self.docker_compose_files:
            if os.path.exists(docker_compose_path):
                args += ["-f", docker_compose_path]
        args += ["--project-name", self.project_name, *command]
        return args

    def is_running(self) -> bool:
        """
        Return True if some containers from this project are running.
        """
        running_projects = [
            entry["Name"]
            for entry in json.loads(
                self.docker_compose_output("ls", "--format", "json").decode("utf-8")
            )
        ]
        return self.project_name in running_projects

    def docker_compose(self, *command: str) -> int:
        """
        Run docker-compose with the right yml files.
        """
        return utils.docker_compose(*self._get_docker_compose_args(*command))

    def docker_compose_output(self, *command: str) -> bytes:
        """
        Same as the docker_compose method except that it returns the command output.
        """
        return utils.check_output(
            "docker", "compose", *self._get_docker_compose_args(*command)
        )

    def run_task(self, service: str, command: str) -> int:
        """
        Run the "{{ service }}-job" service from local/docker-compose.jobs.yml with the
        specified command.
        """
        run_command = []
        for docker_compose_path in self.docker_compose_job_files:
            path = tutor_env.pathjoin(self.root, docker_compose_path)
            if os.path.exists(path):
                run_command += ["-f", path]
        run_command += ["run", "--rm"]
        if not utils.is_a_tty():
            run_command += ["-T"]
        job_service_name = f"{service}-job"
        return self.docker_compose(
            *run_command,
            job_service_name,
            "sh",
            "-e",
            "-c",
            command,
        )


class BaseComposeContext(BaseTaskContext):
    NAME: t.Literal["local", "dev"]
    OPENEDX_SERVICES: list[str] = ["lms", "cms"]

    def job_runner(self, config: Config) -> ComposeTaskRunner:
        raise NotImplementedError


@click.command(help="从头配置并运行 Open edX")
@click.option("-I", "--non-interactive", is_flag=True, help="非交互式运行")
@click.option("-p", "--pullimages", is_flag=True, help="更新 docker 镜像")
@click.option("--skip-build", is_flag=True, help="跳过构建 Docker 镜像")
@click.pass_context
def launch(
    context: click.Context,
    non_interactive: bool,
    pullimages: bool,
    skip_build: bool,
) -> None:
    context_name = context.obj.NAME
    run_for_prod = False if context_name == "dev" else None

    utils.warn_macos_docker_memory()

    # 升级必须在配置之前运行
    interactive_upgrade(context, not non_interactive, run_for_prod=run_for_prod)
    interactive_configuration(context, not non_interactive, run_for_prod=run_for_prod)

    config = tutor_config.load(context.obj.root)

    if not skip_build:
        click.echo(fmt.title("构建 Docker 镜像"))
        images_to_build = hooks.Filters.IMAGES_BUILD_REQUIRED.apply([], context_name)
        if not images_to_build:
            fmt.echo_info("没有需要构建的镜像")
        context.invoke(images.build, image_names=images_to_build)

    click.echo(fmt.title("停止现有平台"))
    context.invoke(stop)

    if pullimages:
        click.echo(fmt.title("更新 Docker 镜像"))
        context.invoke(dc_command, command="pull")

    click.echo(fmt.title("以分离模式启动平台"))
    context.invoke(start, detach=True)

    click.echo(fmt.title("创建数据库并执行迁移"))
    context.invoke(do.commands["init"])

    # 打印面向用户的应用 URL
    public_app_hosts = ""
    for host in hooks.Filters.APP_PUBLIC_HOSTS.iterate(context_name):
        public_app_host = tutor_env.render_str(
            config, "{% if ENABLE_HTTPS %}https{% else %}http{% endif %}://" + host
        )
        public_app_hosts += f"    {public_app_host}\n"
    if public_app_hosts:
        fmt.echo_info(
            f"""平台现已运行，可通过以下 URL 访问：

{public_app_hosts}"""
        )


def interactive_upgrade(
    context: click.Context, interactive: bool, run_for_prod: t.Optional[bool]
) -> None:
    """
    Piece of code that is only used in launch.
    """
    run_upgrade_from_release = tutor_env.should_upgrade_from_release(context.obj.root)
    if run_upgrade_from_release is not None:
        click.echo(fmt.title("Upgrading from an older release"))
        if interactive:
            to_release = tutor_env.get_current_open_edx_release_name()
            question = f"""You are about to upgrade your Open edX platform from {run_upgrade_from_release.capitalize()} to {to_release.capitalize()}

It is strongly recommended to make a backup before upgrading. To do so, run:

    tutor local stop # or 'tutor dev stop' in development
    sudo rsync -avr "$(tutor config printroot)"/ /tmp/tutor-backup/

In case of problem, to restore your backup you will then have to run: sudo rsync -avr /tmp/tutor-backup/ "$(tutor config printroot)"/

Are you sure you want to continue?"""
            click.confirm(
                fmt.question(question), default=True, abort=True, prompt_suffix=" "
            )
        context.invoke(
            upgrade,
            from_release=run_upgrade_from_release,
        )

        # Update env and configuration
        # Don't run in interactive mode, otherwise users gets prompted twice.
        interactive_configuration(context, False, run_for_prod)

        # Post upgrade
        if interactive:
            question = f"""Your platform is being upgraded from {run_upgrade_from_release.capitalize()}.

If you run custom Docker images, you must rebuild them now by running the following command in a different shell:

    tutor images build all # list your custom images here

See the documentation for more information:

    https://docs.tutor.edly.io/install.html#upgrading-to-a-new-open-edx-release

Press enter when you are ready to continue"""
            click.confirm(
                fmt.question(question), default=True, abort=True, prompt_suffix=" "
            )


def interactive_configuration(
    context: click.Context,
    interactive: bool,
    run_for_prod: t.Optional[bool] = None,
) -> None:
    config = tutor_config.load_minimal(context.obj.root)
    if interactive:
        click.echo(fmt.title("Interactive platform configuration"))
        interactive_config.ask_questions(
            config,
            run_for_prod=run_for_prod,
        )
    tutor_config.save_config_file(context.obj.root, config)
    config = tutor_config.load_full(context.obj.root)
    tutor_env.save(context.obj.root, config)


@click.command(
    short_help="执行特定版本的升级任务",
    help="执行特定版本的升级任务。要执行完整升级，请记得运行 `launch`。",
)
@click.option(
    "--from",
    "from_release",
    type=click.Choice(OPENEDX_RELEASE_NAMES),
)
@click.pass_context
def upgrade(context: click.Context, from_release: t.Optional[str]) -> None:
    fmt.echo_alert(
        "此命令仅执行 Open edX 平台的部分升级。"
        "要执行完整升级，您应该运行 `edops local launch`（或在开发环境中运行 `edops dev launch`）。"
    )
    if from_release is None:
        from_release = tutor_env.get_env_release(context.obj.root)
    if from_release is None:
        fmt.echo_info("您的环境已是最新版本")
    else:
        upgrade_from(context, from_release)
    # 我们更新环境以更新版本
    context.invoke(config_save_command)


@click.command(
    short_help="运行所有或选定的服务。",
    help="运行所有或选定的服务。必要时会重新构建 Docker 镜像。",
)
@click.option("--build", is_flag=True, help="启动时构建镜像")
@click.option("-d", "--detach", is_flag=True, help="以守护进程模式启动")
@click.argument("services", metavar="service", nargs=-1)
@click.pass_obj
def start(
    context: BaseComposeContext,
    build: bool,
    detach: bool,
    services: list[str],
) -> None:
    command = ["up", "--remove-orphans"]
    attach = len(services) == 1 and not detach
    if build:
        command.append("--build")
    # 我们必须先以分离模式运行容器才能附加到它
    if detach or attach:
        command.append("-d")
    else:
        fmt.echo_info("ℹ️  要退出日志而不停止容器，请使用 ctrl+z")

    # 启动服务
    config = tutor_config.load(context.root)
    context.job_runner(config).docker_compose(*command, *services)

    if attach:
        fmt.echo_info(
            f"""正在附加到服务 {services[0]}
ℹ️  要分离而不停止服务，请使用 ctrl+p 然后 ctrl+q"""
        )
        context.job_runner(config).docker_compose("attach", *services)


@click.command(help="停止正在运行的平台")
@click.argument("services", metavar="service", nargs=-1)
@click.pass_obj
def stop(context: BaseComposeContext, services: list[str]) -> None:
    config = tutor_config.load(context.root)
    context.job_runner(config).docker_compose("stop", *services)


@click.command(
    short_help="重启现有平台",
    help="这不仅仅是重启：使用 reboot 时，平台会完全停止后再重新启动",
)
@click.option("-d", "--detach", is_flag=True, help="以守护进程模式启动")
@click.argument("services", metavar="service", nargs=-1)
@click.pass_context
def reboot(context: click.Context, detach: bool, services: list[str]) -> None:
    context.invoke(stop, services=services)
    context.invoke(start, detach=detach, services=services)


@click.command(
    short_help="从运行中的平台重启部分组件。",
    help="""指定 'openedx' 以重启 lms、cms 和 workers，或指定 'all' 以
重启所有服务。注意这执行的是 'docker compose restart'，因此可能不会使用新镜像。
这对重新加载设置等场景很有用。要完全停止平台，请使用 'reboot' 命令。""",
)
@click.argument("services", metavar="service", nargs=-1)
@click.pass_obj
def restart(context: BaseComposeContext, services: list[str]) -> None:
    config = tutor_config.load(context.root)
    command = ["restart"]
    if "all" in services:
        pass
    else:
        for service in services:
            if service == "openedx":
                command += context.OPENEDX_SERVICES
            else:
                command.append(service)
    context.job_runner(config).docker_compose(*command)


@jobs.do_group
def do() -> None:
    """
    在正确的容器中运行自定义任务。
    """


@click.command(
    short_help="在新容器中运行命令",
    help=(
        "在新容器中运行命令。这是 `docker compose run` 的封装。传递给此命令的任何选项或参数"
        "都将转发给 docker compose。因此，您可以使用 `-v` 或 `-p` 来挂载卷和暴露端口。"
    ),
    context_settings={"ignore_unknown_options": True},
)
@click.argument("args", nargs=-1, required=True)
@click.pass_context
def run(
    context: click.Context,
    args: list[str],
) -> None:
    extra_args = ["--rm"]
    if not utils.is_a_tty():
        extra_args.append("-T")
    context.invoke(dc_command, command="run", args=[*extra_args, *args])


@click.command(
    name="copyfrom",
    help="从容器目录复制文件/文件夹到本地文件系统。",
)
@click.argument("service")
@click.argument("container_path")
@click.argument(
    "host_path",
    type=click.Path(dir_okay=True, file_okay=False, resolve_path=True),
)
@click.pass_obj
def copyfrom(
    context: BaseComposeContext, service: str, container_path: str, host_path: str
) -> None:
    # 路径管理
    container_root_path = "/tmp/mount"
    container_dst_path = container_root_path
    if not os.path.exists(host_path):
        # 模拟 cp 语义，如果目标路径不存在
        # 则复制到其父目录并重命名为目标文件夹
        container_dst_path += "/" + os.path.basename(host_path)
        host_path = os.path.dirname(host_path)
    if not os.path.exists(host_path):
        raise TutorError(
            f"无法创建目录 {host_path}。文件或目录不存在。"
        )

    # cp/mv 命令
    command = f"cp --recursive --preserve {container_path} {container_dst_path}"
    config = tutor_config.load(context.root)
    runner = context.job_runner(config)
    runner.docker_compose(
        "run",
        "--rm",
        "--no-deps",
        "--user=0",
        f"--volume={host_path}:{container_root_path}",
        service,
        "sh",
        "-e",
        "-c",
        command,
    )


@click.command(
    short_help="在运行中的容器中执行命令",
    help=(
        "在运行中的容器中执行命令。这是 `docker compose exec` 的封装。传递给此命令的任何选项"
        "或参数都将转发给 docker-compose。因此，您可以使用 `-e` 来手动定义环境变量。"
    ),
    context_settings={"ignore_unknown_options": True},
    name="exec",
)
@click.argument("args", nargs=-1, required=True)
@click.pass_context
def execute(context: click.Context, args: list[str]) -> None:
    context.invoke(dc_command, command="exec", args=args)


@click.command(
    short_help="查看容器输出",
    help="查看容器输出。这是 `docker compose logs` 的封装。",
)
@click.option("-f", "--follow", is_flag=True, help="跟踪日志输出")
@click.option("--tail", type=int, help="从每个容器显示的行数")
@click.argument("service", nargs=-1)
@click.pass_context
def logs(context: click.Context, follow: bool, tail: bool, service: str) -> None:
    args = []
    if follow:
        args.append("--follow")
    if tail is not None:
        args += ["--tail", str(tail)]
    args += service
    context.invoke(dc_command, command="logs", args=args)


@click.command(help="打印容器的状态信息")
@click.pass_context
def status(context: click.Context) -> None:
    context.invoke(dc_command, command="ps")


@click.command(
    short_help="直接操作 docker compose。",
    help=(
        "直接操作 docker compose。这是 `docker compose` 的封装。传递给此命令的大多数命令、"
        "选项和参数将按原样转发给 docker compose。"
    ),
    context_settings={"ignore_unknown_options": True},
    name="dc",
)
@click.argument("command")
@click.argument("args", nargs=-1)
@click.pass_obj
def dc_command(
    context: BaseComposeContext,
    command: str,
    args: list[str],
) -> None:
    config = tutor_config.load(context.root)
    context.job_runner(config).docker_compose(command, *args)


hooks.Filters.ENV_TEMPLATE_VARIABLES.add_item(("iter_mounts", bindmount.iter_mounts))


def add_commands(command_group: click.Group) -> None:
    command_group.add_command(launch)
    command_group.add_command(upgrade)
    command_group.add_command(start)
    command_group.add_command(stop)
    command_group.add_command(restart)
    command_group.add_command(reboot)
    command_group.add_command(dc_command)
    command_group.add_command(run)
    command_group.add_command(copyfrom)
    command_group.add_command(execute)
    command_group.add_command(logs)
    command_group.add_command(status)

    @hooks.Actions.PLUGINS_LOADED.add()
    def _add_do_commands() -> None:
        jobs.add_job_commands(do)
        command_group.add_command(do)
