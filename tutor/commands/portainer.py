"""EdOps 的 Portainer / Docker Swarm 部署命令。"""
from __future__ import annotations

import click

from tutor import config as tutor_config
from tutor import env as tutor_env
from tutor import fmt
from tutor.commands import compose
from tutor.commands.context import Context
from tutor.edops import modules as edops_modules


@click.group(help="部署 EdOps 到 Portainer / Docker Swarm")
@click.pass_context
def portainer(context: click.Context) -> None:
    """Portainer 部署命令。"""
    context.obj = Context(context.obj.root)


@click.command(help="渲染 Portainer / Swarm 模板")
@click.argument("module_name", required=False)
@click.pass_obj
def render(context: Context, module_name: str | None) -> None:
    """渲染 Portainer 部署模板。

    注意：Portainer 模板支持尚未完全实现。
    此命令将在未来版本中扩展。
    """
    config = tutor_config.load(context.root)

    if module_name:
        # 渲染特定模块
        all_modules = edops_modules._load_modules()
        if module_name not in all_modules:
            available = ", ".join(all_modules.keys())
            fmt.echo_error(
                f"未知模块 '{module_name}'。可用: {available}"
            )
            return

        modules_to_render = [all_modules[module_name]]
    else:
        # 渲染所有已启用的模块
        modules_to_render = edops_modules.get_enabled_modules(config)

    fmt.echo_info("正在渲染 Portainer 模板...\n")

    # TODO: 实现 Portainer 模板渲染
    # 目前只显示将要渲染的内容
    for module in modules_to_render:
        fmt.echo(f"模块: {module.name}")
        fmt.echo(f"  模板: {module.template}")
        fmt.echo(f"  目标: {module.target}")
        fmt.echo()

    fmt.echo_info(
        "注意：Portainer 模板渲染尚未完全实现。"
    )
    fmt.echo_info(
        "请使用 'edops local' 命令进行单节点部署。"
    )
    fmt.echo_info(
        "Swarm 模板支持将在未来版本中添加。"
    )


portainer.add_command(render)

