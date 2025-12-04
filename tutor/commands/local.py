from __future__ import annotations

import json
import typing as t

import click

from tutor import config as tutor_config
from tutor import env as tutor_env
from tutor import fmt
from tutor import hooks
from tutor.commands import compose
from tutor.edops import modules as edops_modules
from tutor.types import Config, get_typed


class LocalTaskRunner(compose.ComposeTaskRunner):
    def __init__(self, root: str, config: Config):
        """
        Load docker-compose files from local/.
        """
        super().__init__(root, config)
        self.project_name = get_typed(self.config, "LOCAL_PROJECT_NAME", str)
        module_targets = edops_modules.get_enabled_module_targets(self.config)
        if module_targets:
            self.docker_compose_files = [
                tutor_env.pathjoin(self.root, target) for target in module_targets
            ]
            self.docker_compose_job_files = []
        else:
            self.docker_compose_files += [
                tutor_env.pathjoin(self.root, "local", "docker-compose.yml"),
                tutor_env.pathjoin(self.root, "local", "docker-compose.prod.yml"),
                tutor_env.pathjoin(self.root, "local", "docker-compose.override.yml"),
                tutor_env.pathjoin(
                    self.root, "local", "docker-compose.prod.override.yml"
                ),
            ]
            self.docker_compose_job_files += [
                tutor_env.pathjoin(self.root, "local", "docker-compose.jobs.yml"),
                tutor_env.pathjoin(self.root, "local", "docker-compose.jobs.override.yml"),
            ]


class LocalContext(compose.BaseComposeContext):
    NAME = "local"
    OPENEDX_SERVICES = ["lms", "cms", "lms-worker", "cms-worker"]

    def job_runner(self, config: Config) -> LocalTaskRunner:
        return LocalTaskRunner(self.root, config)


@click.group(help="Run Open edX locally with docker-compose")
@click.pass_context
def local(context: click.Context) -> None:
    context.obj = LocalContext(context.obj.root)


@hooks.Actions.COMPOSE_PROJECT_STARTED.add()
def _stop_on_dev_start(root: str, config: Config, project_name: str) -> None:
    """
    Stop the local platform as soon as a platform with a different project name is
    started.
    """
    runner = LocalTaskRunner(root, config)
    if project_name != runner.project_name and runner.is_running():
        runner.docker_compose("stop")


@click.command(name="status", help="显示 EdOps 模块的详细状态")
@click.option(
    "--module",
    "module_filter",
    help="按模块名称过滤",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="输出格式",
)
@click.pass_obj
def edops_status(
    context: compose.LocalContext,
    module_filter: t.Optional[str],
    output_format: str,
) -> None:
    """显示详细状态，包括模块分组和健康信息。"""
    config = tutor_config.load(context.root)
    runner = LocalTaskRunner(context.root, config)

    # 获取容器状态
    try:
        ps_output = runner.docker_compose_output("ps", "--format", "json")
        containers = json.loads(ps_output.decode("utf-8"))
    except Exception:
        containers = []

    if not containers:
        fmt.echo_info("没有运行中的容器")
        return

    # 按模块分组
    modules_list = edops_modules.get_enabled_modules(config)
    module_names = {m.name for m in modules_list}

    if output_format == "json":
        click.echo(json.dumps(containers, indent=2))
    else:
        # 表格格式
        fmt.echo_info("EdOps 模块状态:\n")
        for container in containers:
            name = container.get("Service", container.get("Name", ""))
            state = container.get("State", "unknown")
            status = container.get("Status", "")

            # 尝试确定模块
            detected_module = "unknown"
            for mod_name in module_names:
                if mod_name.replace("_", "-") in name:
                    detected_module = mod_name
                    break

            if module_filter and detected_module != module_filter:
                continue

            status_icon = "✓" if state == "running" else "✗"
            fmt.echo(f"{status_icon} {name:40} {state:10} {status}")


@click.command(name="healthcheck", help="对 EdOps 模块运行健康检查")
@click.argument("module_name", required=False)
@click.pass_obj
def healthcheck(
    context: compose.LocalContext, module_name: t.Optional[str]
) -> None:
    """对指定模块或所有模块运行健康检查。"""
    from tutor.edops import health as edops_health

    config = tutor_config.load(context.root)

    if module_name:
        # 检查特定模块
        all_modules = edops_modules._load_modules()
        if module_name not in all_modules:
            available = ", ".join(all_modules.keys())
            fmt.echo_error(
                f"未知模块 '{module_name}'。可用: {available}"
            )
            return

        modules_to_check = [all_modules[module_name]]
    else:
        # 检查所有已启用的模块
        modules_to_check = edops_modules.get_enabled_modules(config)

    checker = edops_health.HealthChecker(verbose=True)
    all_passed = True

    for module in modules_to_check:
        if not hasattr(module, "health_checks") or not module.health_checks:
            fmt.echo_info(f"{module.name} 没有定义健康检查")
            continue

        fmt.echo_info(f"\n正在检查 {module.name}...")
        for check_def in module.health_checks:
            passed = checker.check(check_def)
            if not passed:
                all_passed = False

    if all_passed:
        fmt.echo_info("\n✓ 所有健康检查通过")
    else:
        fmt.echo_error("\n✗ 部分健康检查失败")


@click.command(name="history", help="查看部署历史")
@click.option(
    "--module",
    "module_filter",
    help="按模块名称过滤",
)
@click.option(
    "--service",
    "service_filter",
    help="按服务名称过滤",
)
@click.option(
    "--limit",
    type=int,
    default=20,
    help="显示的记录数",
)
@click.pass_obj
def deployment_history(
    context: compose.LocalContext,
    module_filter: t.Optional[str],
    service_filter: t.Optional[str],
    limit: int,
) -> None:
    """查看部署历史记录。"""
    from pathlib import Path
    from tutor.edops import image_registry

    history_file = Path(context.root) / "deploy-history.yml"
    history = image_registry.DeployHistory(history_file)

    if not history.records:
        fmt.echo_info("未找到部署历史")
        return

    # 过滤记录
    records = history.records
    if module_filter:
        records = [r for r in records if r.module == module_filter]
    if service_filter:
        records = [r for r in records if r.service == service_filter]

    # 限制记录数
    records = records[-limit:]

    if not records:
        fmt.echo_info("未找到匹配的部署记录")
        return

    fmt.echo_info("部署历史:\n")
    for record in reversed(records):
        timestamp = record.timestamp.split("T")[0]  # 只显示日期
        operation_icon = "→" if record.operation == "deploy" else "←"
        fmt.echo(
            f"{operation_icon} {timestamp} {record.module:15} "
            f"{record.service:30} {record.tag:10} ({record.operation})"
        )


@click.command(name="rollback", help="将模块回滚到之前的版本")
@click.argument("module_name")
@click.option(
    "--version",
    "target_version",
    help="目标版本标签（默认：上一次部署）",
)
@click.pass_obj
def rollback(
    context: compose.LocalContext,
    module_name: str,
    target_version: t.Optional[str],
) -> None:
    """将模块回滚到之前的版本。"""
    from pathlib import Path
    from tutor.edops import image_registry

    history_file = Path(context.root) / "deploy-history.yml"
    history = image_registry.DeployHistory(history_file)

    # 获取模块历史
    module_history = history.get_module_history(module_name)
    if not module_history:
        fmt.echo_error(f"未找到模块 '{module_name}' 的部署历史")
        return

    # 查找目标版本
    if target_version:
        # 在历史中查找指定版本
        target_record = None
        for record in reversed(module_history):
            if record.tag == target_version:
                target_record = record
                break
        if not target_record:
            fmt.echo_error(
                f"在 '{module_name}' 的历史中未找到版本 '{target_version}'"
            )
            return
    else:
        # 获取上一个版本（倒数第二个）
        if len(module_history) < 2:
            fmt.echo_error(
                f"'{module_name}' 没有可用于回滚的上一个版本"
            )
            return
        target_record = module_history[-2]

    # 确认回滚
    current_version = module_history[-1].tag
    fmt.echo_info(
        f"将 {module_name} 从 {current_version} 回滚到 {target_record.tag}"
    )

    # TODO: 使用目标版本更新 config.yml
    # 这需要知道哪个配置变量映射到哪个服务
    # 目前我们只在历史中记录回滚

    # 记录回滚操作
    history.add_record(
        module=module_name,
        service=target_record.service,
        image=target_record.image,
        tag=target_record.tag,
        operation="rollback",
    )

    fmt.echo_info("✓ 回滚已记录。请手动更新版本并重启。")
    fmt.echo_info(f"  服务: {target_record.service}")
    fmt.echo_info(f"  镜像: {target_record.image}:{target_record.tag}")


compose.add_commands(local)
local.add_command(edops_status)
local.add_command(healthcheck)
local.add_command(deployment_history)
local.add_command(rollback)
