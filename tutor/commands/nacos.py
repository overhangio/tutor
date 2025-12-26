"""Nacos 配置管理命令。"""

from __future__ import annotations

import os
import typing as t
from pathlib import Path

import click

from tutor import config as tutor_config
from tutor import env as tutor_env
from tutor import exceptions
from tutor import fmt
from tutor.commands.context import Context
from tutor.edops import nacos_client


@click.group(name="nacos", help="Nacos 配置管理")
def nacos_command() -> None:
    """
    Nacos 配置管理命令组。

    提供配置的渲染、推送、导出、验证等功能。
    """
    pass


@nacos_command.group(name="config", help="配置管理")
def config_command() -> None:
    """配置管理子命令组。"""
    pass


@config_command.command(name="render", help="渲染 Nacos 配置模板")
@click.option(
    "--shared",
    help="渲染共享配置（ly-config.properties, ly.yaml 等）",
    is_flag=True,
)
@click.option("--service", help="指定服务名称（例如：ly-ac-user-svc）")
@click.option(
    "--output",
    help="输出目录（默认：env/nacos/config）",
    default="",
)
@click.pass_obj
def config_render(
    context: Context,
    shared: bool,
    service: str,
    output: str,
) -> None:
    """
    渲染 Nacos 配置模板，将变量替换为实际值。

    示例：
        edops nacos config render --shared
        edops nacos config render --service ly-ac-user-svc
        edops nacos config render --output /tmp/nacos-config
    """
    config = tutor_config.load(context.root)

    if not output:
        output = os.path.join(context.root, "env", "nacos", "config")

    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)

    renderer = tutor_env.Renderer(config)

    if shared:
        # 渲染共享配置
        shared_configs = [
            "nacos/DEFAULT_GROUP/shared/ly-config.properties.j2",
            "nacos/DEFAULT_GROUP/shared/ly.yml.j2",
        ]

        for template_path in shared_configs:
            try:
                content = renderer.render_template(template_path)
                # 确定输出文件名
                if template_path.endswith(".properties.j2"):
                    filename = template_path.split("/")[-1].replace(".j2", "")
                elif template_path.endswith(".yml.j2"):
                    filename = template_path.split("/")[-1].replace(".j2", "")
                else:
                    filename = template_path.split("/")[-1]

                output_file = output_path / filename
                output_file.write_text(content, encoding="utf-8")
                fmt.echo_info(f"已渲染: {filename} -> {output_file}")
            except Exception as e:
                fmt.echo_error(f"渲染模板失败 {template_path}: {e}")

    elif service:
        # 渲染单个服务配置
        template_path = f"nacos/DEFAULT_GROUP/services/{service}.yaml.j2"
        try:
            content = renderer.render_template(template_path)
            output_file = output_path / f"{service}.yaml"
            output_file.write_text(content, encoding="utf-8")
            fmt.echo_info(f"已渲染: {service}.yaml -> {output_file}")
        except Exception as e:
            fmt.echo_error(f"渲染服务配置失败 {service}: {e}")

    else:
        # 渲染所有配置
        fmt.echo_info("渲染所有 Nacos 配置...")

        # 渲染共享配置
        shared_configs = [
            "nacos/DEFAULT_GROUP/shared/ly-config.properties.j2",
            "nacos/DEFAULT_GROUP/shared/ly.yml.j2",
        ]

        for template_path in shared_configs:
            try:
                content = renderer.render_template(template_path)
                if template_path.endswith(".properties.j2"):
                    filename = template_path.split("/")[-1].replace(".j2", "")
                elif template_path.endswith(".yml.j2"):
                    filename = template_path.split("/")[-1].replace(".j2", "")
                else:
                    filename = template_path.split("/")[-1]

                output_file = output_path / filename
                output_file.write_text(content, encoding="utf-8")
                fmt.echo_info(f"已渲染: {filename}")
            except Exception as e:
                fmt.echo_error(f"渲染模板失败 {template_path}: {e}")

        # 渲染服务配置
        services_dir = Path(tutor_env.TEMPLATES_ROOT) / "nacos" / "DEFAULT_GROUP" / "services"
        if services_dir.exists():
            for template_file in services_dir.glob("*.yaml.j2"):
                service_name = template_file.stem.replace(".yaml", "")
                template_path = f"nacos/DEFAULT_GROUP/services/{template_file.name}"

                try:
                    content = renderer.render_template(template_path)
                    output_file = output_path / f"{service_name}.yaml"
                    output_file.write_text(content, encoding="utf-8")
                    fmt.echo_info(f"已渲染: {service_name}.yaml")
                except Exception as e:
                    fmt.echo_warning(f"渲染服务配置失败 {service_name}: {e}")

    fmt.echo_info(f"配置已渲染到: {output_path}")


@config_command.command(name="push", help="推送配置到 Nacos")
@click.option("--shared", help="推送共享配置", is_flag=True)
@click.option("--service", help="指定服务名称（例如：ly-ac-user-svc）")
@click.option("--group", default="DEFAULT_GROUP", help="Nacos 分组")
@click.option("--namespace", help="Nacos 命名空间（可选）")
@click.option(
    "--source",
    help="配置源目录（默认：env/nacos/config）",
    default="",
)
@click.pass_obj
def config_push(
    context: Context,
    shared: bool,
    service: str,
    group: str,
    namespace: str,
    source: str,
) -> None:
    """
    将渲染后的配置推送到 Nacos 服务器。

    示例：
        edops nacos config push --shared
        edops nacos config push --service ly-ac-user-svc
        edops nacos config push --source /tmp/nacos-config
    """
    config = tutor_config.load(context.root)

    if namespace:
        config["EDOPS_NACOS_NAMESPACE"] = namespace

    try:
        client = nacos_client.get_nacos_client(config)
    except exceptions.TutorError as e:
        fmt.echo_error(str(e))
        return

    if not source:
        source = os.path.join(context.root, "env", "nacos", "config")

    source_path = Path(source)
    if not source_path.exists():
        fmt.echo_error(f"配置源目录不存在: {source_path}")
        fmt.echo_info("请先运行: edops nacos config render")
        return

    if shared:
        # 推送共享配置
        shared_files = ["ly-config.properties", "ly.yaml"]
        for filename in shared_files:
            file_path = source_path / filename
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8")
                config_type = "properties" if filename.endswith(".properties") else "yaml"
                client.publish_config(filename, group, content, config_type)
            else:
                fmt.echo_warning(f"配置文件不存在: {file_path}")

    elif service:
        # 推送单个服务配置
        file_path = source_path / f"{service}.yaml"
        if file_path.exists():
            content = file_path.read_text(encoding="utf-8")
            client.publish_config(f"{service}.yaml", group, content, "yaml")
        else:
            fmt.echo_error(f"配置文件不存在: {file_path}")
            fmt.echo_info(f"请先运行: edops nacos config render --service {service}")

    else:
        # 推送所有配置
        fmt.echo_info("推送所有配置到 Nacos...")

        # 推送共享配置
        shared_files = ["ly-config.properties", "ly.yaml"]
        for filename in shared_files:
            file_path = source_path / filename
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8")
                config_type = "properties" if filename.endswith(".properties") else "yaml"
                client.publish_config(filename, group, content, config_type)

        # 推送服务配置
        for yaml_file in source_path.glob("*.yaml"):
            if yaml_file.name not in ["ly.yaml"]:
                service_name = yaml_file.stem
                content = yaml_file.read_text(encoding="utf-8")
                client.publish_config(f"{service_name}.yaml", group, content, "yaml")

    fmt.echo_info("配置推送完成")


@config_command.command(name="export", help="从 Nacos 导出配置")
@click.option("--group", default="DEFAULT_GROUP", help="Nacos 分组")
@click.option("--namespace", help="Nacos 命名空间（可选）")
@click.option(
    "--output",
    help="输出目录（默认：nacos_config_export_<timestamp>）",
    default="",
)
@click.pass_obj
def config_export(
    context: Context,
    group: str,
    namespace: str,
    output: str,
) -> None:
    """
    从 Nacos 导出配置到本地文件。

    示例：
        edops nacos config export
        edops nacos config export --output /tmp/nacos-export
    """
    from datetime import datetime

    config = tutor_config.load(context.root)

    if namespace:
        config["EDOPS_NACOS_NAMESPACE"] = namespace

    try:
        client = nacos_client.get_nacos_client(config)
    except exceptions.TutorError as e:
        fmt.echo_error(str(e))
        return

    if not output:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output = f"nacos_config_export_{timestamp}"

    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)

    # 导出共享配置
    shared_configs = ["ly-config.properties", "ly.yaml"]
    for data_id in shared_configs:
        content = client.get_config(data_id, group)
        if content:
            file_path = output_path / data_id
            file_path.write_text(content, encoding="utf-8")
            fmt.echo_info(f"已导出: {data_id}")
        else:
            fmt.echo_warning(f"配置不存在: {group}/{data_id}")

    # 导出服务配置（需要知道服务列表）
    # 这里可以扩展为从元数据文件读取服务列表
    fmt.echo_info(f"配置已导出到: {output_path}")


@config_command.command(name="validate", help="验证配置完整性")
@click.option("--service", help="指定服务名称（可选）")
@click.pass_obj
def config_validate(
    context: Context,
    service: str,
) -> None:
    """
    验证 Nacos 配置是否完整和有效。

    示例：
        edops nacos config validate
        edops nacos config validate --service ly-ac-user-svc
    """
    config = tutor_config.load(context.root)
    errors = []

    # 检查必需配置项
    required_vars = [
        "EDOPS_NACOS_SERVER_ADDR",
        "EDOPS_MYSQL_HOST",
        "EDOPS_MYSQL_PORT",
        "EDOPS_MYSQL_ROOT_USER",
        "EDOPS_MYSQL_ROOT_PASSWORD",
        "EDOPS_REDIS_HOST",
        "EDOPS_REDIS_PORT",
        "EDOPS_REDIS_PASSWORD",
        "EDOPS_RABBITMQ_HOST",
        "EDOPS_RABBITMQ_PORT",
        "EDOPS_RABBITMQ_DEFAULT_USER",
        "EDOPS_RABBITMQ_DEFAULT_PASS",
    ]

    for var in required_vars:
        if not config.get(var):
            errors.append(f"必需配置项未设置: {var}")

    # 验证配置值格式
    if config.get("EDOPS_MYSQL_PORT"):
        try:
            port = int(config.get("EDOPS_MYSQL_PORT"))
            if not (1 <= port <= 65535):
                errors.append(f"MySQL 端口 {port} 超出有效范围 (1-65535)")
        except ValueError:
            errors.append("MySQL 端口必须是数字")

    if config.get("EDOPS_REDIS_PORT"):
        try:
            port = int(config.get("EDOPS_REDIS_PORT"))
            if not (1 <= port <= 65535):
                errors.append(f"Redis 端口 {port} 超出有效范围 (1-65535)")
        except ValueError:
            errors.append("Redis 端口必须是数字")

    if errors:
        fmt.echo_error("配置验证失败：")
        for error in errors:
            fmt.echo_error(f"  - {error}")
        raise exceptions.TutorError("配置验证失败")
    else:
        fmt.echo_info("配置验证通过")


# 注册命令到主命令组
def register_commands() -> None:
    """注册 Nacos 命令到主命令组。"""
    # 命令已经通过 @click.group 装饰器自动注册
    pass

