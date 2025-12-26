from __future__ import annotations

import json
import os.path
import typing as t
from shutil import which

import click
import click.shell_completion

from tutor import config as tutor_config
from tutor import env, exceptions, fmt, hooks, serialize, utils
from tutor import interactive as interactive_config
from tutor.commands.context import Context
from tutor.commands.params import ConfigLoaderParam
from tutor.types import Config, ConfigValue


def _validate_required_config(config: Config) -> None:
    """
    Validate that required configuration items are set.
    
    Raises TutorError if any required configuration is missing.
    """
    required_vars = [
        "EDOPS_IMAGE_REGISTRY",
        "EDOPS_MASTER_NODE_IP",
    ]
    
    # Optional but recommended for production
    recommended_vars = [
        "EDOPS_MYSQL_ROOT_PASSWORD",
        "EDOPS_REDIS_PASSWORD",
    ]
    
    errors = []
    for var in required_vars:
        value = config.get(var)
        if not value or (isinstance(value, str) and not value.strip()):
            errors.append(f"必需配置项未设置: {var}")
    
    # Warn about recommended but not required vars
    warnings = []
    for var in recommended_vars:
        value = config.get(var)
        if not value or (isinstance(value, str) and not value.strip()):
            warnings.append(f"建议配置项未设置: {var} (生产环境建议设置)")
    
    if errors:
        fmt.echo_error("配置验证失败：")
        for error in errors:
            fmt.echo_error(f"  - {error}")
        raise exceptions.TutorError("配置验证失败，请设置必需的配置项")
    
    if warnings:
        fmt.echo_alert("配置警告：")
        for warning in warnings:
            fmt.echo_alert(f"  - {warning}")


def _ensure_data_directories(root: str, config: Config) -> None:
    """
    Create data/ subdirectories to ensure they exist before permissions service runs.
    
    This helps avoid permission issues when Docker creates directories as root.
    """
    import os
    from pathlib import Path
    
    data_dir = Path(root) / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # List of data subdirectories used by zhjx modules
    data_subdirs = [
        "rabbitmq",
        "redis",
        "minio",
        "elasticsearch",
        "kafka",
        "kkfileview",
    ]
    
    # Add zlmediakit subdirectories if module is enabled
    if config.get("RUN_ZHJX_ZLMEDIAKIT", False):
        data_subdirs.extend([
            "zlmediakit/conf",
            "zlmediakit/log",
            "zlmediakit/www",
        ])
    
    # Create subdirectories with appropriate permissions
    for subdir in data_subdirs:
        subdir_path = data_dir / subdir
        subdir_path.mkdir(parents=True, exist_ok=True)
        # Set permissions to 755 (rwxr-xr-x) to allow container processes to access
        try:
            os.chmod(subdir_path, 0o755)
        except OSError:
            # Ignore permission errors (may not have sufficient privileges)
            pass


@click.group(
    name="config",
    short_help="配置 EdOps",
    help="""配置 EdOps 平台并将配置值存储在 $TUTOR_ROOT/config.yml 中""",
)
def config_command() -> None:
    pass


class ConfigKeyParamType(ConfigLoaderParam):
    name = "configkey"

    def shell_complete(
        self, ctx: click.Context, param: click.Parameter, incomplete: str
    ) -> list[click.shell_completion.CompletionItem]:
        return [
            click.shell_completion.CompletionItem(key)
            for key, _value in self._shell_complete_config_items(incomplete)
        ]

    def _shell_complete_config_items(
        self, incomplete: str
    ) -> list[tuple[str, ConfigValue]]:
        return [
            (key, value)
            for key, value in self._candidate_config_items()
            if key.startswith(incomplete)
        ]

    def _candidate_config_items(self) -> t.Iterable[tuple[str, ConfigValue]]:
        yield from self.config.items()


class ConfigKeyValParamType(ConfigKeyParamType):
    """
    Parser for <KEY>=<YAML VALUE> command line arguments.
    """

    name = "configkeyval"

    def convert(self, value: str, param: t.Any, ctx: t.Any) -> tuple[str, t.Any]:
        result = serialize.parse_key_value(value)
        if result is None:
            self.fail(f"'{value}' is not of the form 'key=value'.", param, ctx)
        return result

    def shell_complete(
        self, ctx: click.Context, param: click.Parameter, incomplete: str
    ) -> list[click.shell_completion.CompletionItem]:
        """
        Nice and friendly <KEY>=<VAL> auto-completion.
        """
        if "=" not in incomplete:
            # Auto-complete with '<KEY>='. Note the single quotes which allow users to
            # further auto-complete later.
            return [
                click.shell_completion.CompletionItem(f"'{key}='")
                for key, value in self._shell_complete_config_items(incomplete)
            ]
        if incomplete.endswith("="):
            # raise ValueError(f"incomplete: <{incomplete}>")
            # Auto-complete with '<KEY>=<VALUE>'
            return [
                click.shell_completion.CompletionItem(f"{key}={json.dumps(value)}")
                for key, value in self._shell_complete_config_items(incomplete[:-1])
            ]
        # Else, don't bother
        return []


class ConfigListKeyValParamType(ConfigKeyValParamType):
    """
    Same as the parent class, but for keys of type `list`.
    """

    def _candidate_config_items(self) -> t.Iterable[tuple[str, ConfigValue]]:
        for key, val in self.config.items():
            if isinstance(val, list):
                yield key, val


@click.command(help="Create and save configuration interactively")
@click.option("-i", "--interactive", is_flag=True, help="Run interactively")
@click.option(
    "-s",
    "--set",
    "set_vars",
    type=ConfigKeyValParamType(),
    multiple=True,
    metavar="KEY=VAL",
    help="Set a configuration value (can be used multiple times)",
)
@click.option(
    "-a",
    "--append",
    "append_vars",
    type=ConfigListKeyValParamType(),
    multiple=True,
    metavar="KEY=VAL",
    help="Append an item to a configuration value of type list. The value will only be added if it is not already present. (can be used multiple times)",
)
@click.option(
    "-A",
    "--remove",
    "remove_vars",
    type=ConfigListKeyValParamType(),
    multiple=True,
    metavar="KEY=VAL",
    help="Remove an item from a configuration value of type list (can be used multiple times)",
)
@click.option(
    "-U",
    "--unset",
    "unset_vars",
    multiple=True,
    type=ConfigKeyParamType(),
    help="Remove a configuration value (can be used multiple times)",
)
@click.option(
    "-e", "--env-only", "env_only", is_flag=True, help="Skip updating config.yml"
)
@click.option(
    "-c",
    "--clean",
    "clean_env",
    is_flag=True,
    help="Remove everything in the env directory before save",
)
@click.option(
    "--init",
    "init_env",
    is_flag=True,
    help="Initialize a new environment (equivalent to --clean)",
)
@click.pass_obj
def save(
    context: Context,
    interactive: bool,
    set_vars: list[tuple[str, t.Any]],
    append_vars: list[tuple[str, t.Any]],
    remove_vars: list[tuple[str, t.Any]],
    unset_vars: list[str],
    env_only: bool,
    clean_env: bool,
    init_env: bool,
) -> None:
    # --init is equivalent to --clean
    if init_env:
        clean_env = True

    config = tutor_config.load_minimal(context.root)

    # Add question to interactive prompt, such that the environment is automatically
    # deleted if necessary in interactive mode.
    @hooks.Actions.CONFIG_INTERACTIVE.add()
    def _prompt_for_env_deletion(_config: Config) -> None:
        if clean_env:
            run_clean = click.confirm(
                fmt.question("Remove existing Tutor environment directory?"),
                prompt_suffix=" ",
                default=True,
            )
            if run_clean:
                env.delete_env_dir(context.root)

    if interactive:
        interactive_config.ask_questions(config)
    elif clean_env:
        env.delete_env_dir(context.root)
    if set_vars:
        for key, value in set_vars:
            config[key] = env.render_unknown(config, value)
    if append_vars:
        config_defaults = tutor_config.load_defaults()
        for key, value in append_vars:
            if key not in config:
                config[key] = config[key] = config.get(
                    key, config_defaults.get(key, [])
                )
            values = config[key]
            if not isinstance(values, list):
                raise exceptions.TutorError(
                    f"Could not append value to '{key}': current setting is of type '{values.__class__.__name__}', expected list."
                )
            if not isinstance(value, str):
                raise exceptions.TutorError(
                    f"Could not append value to '{key}': appended value is of type '{value.__class__.__name__}', expected str."
                )
            if value not in values:
                values.append(value)
    if remove_vars:
        for key, value in remove_vars:
            values = config.get(key, [])
            if not isinstance(values, list):
                raise exceptions.TutorError(
                    f"Could not remove value from '{key}': current setting is of type '{values.__class__.__name__}', expected list."
                )
            while value in values:
                values.remove(value)
    for key in unset_vars:
        config.pop(key, None)
    
    # Validate required configuration items before saving
    if not env_only:
        _validate_required_config(config)
    
    # Create data/ subdirectories to ensure they exist before permissions service runs
    if not env_only:
        _ensure_data_directories(context.root, config)
    
    if not env_only:
        tutor_config.save_config_file(context.root, config)

    # Reload configuration, without version checking
    config = tutor_config.load_full(context.root)
    env.save(context.root, config)


@click.command(help="Print the project root")
@click.pass_obj
def printroot(context: Context) -> None:
    click.echo(context.root)


@click.command(help="Print a configuration value")
@click.argument("key", type=ConfigKeyParamType())
@click.pass_obj
def printvalue(context: Context, key: str) -> None:
    config = tutor_config.load(context.root)
    try:
        value = config[key]
    except KeyError as e:
        raise exceptions.TutorError(f"Missing configuration value: {key}") from e
    fmt.echo(serialize.str_format(value))


@click.command(help="获取配置项的值")
@click.argument("key", type=ConfigKeyParamType())
@click.pass_obj
def get(context: Context, key: str) -> None:
    """获取单个配置项的值。"""
    printvalue.callback(context, key)


@click.command(name="list", help="列出所有配置项")
@click.option(
    "--filter",
    "filter_prefix",
    default="",
    help="按前缀过滤配置项（例如 EDOPS_）",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json", "yaml"]),
    default="text",
    help="输出格式",
)
@click.pass_obj
def list_config(
    context: Context, filter_prefix: str, output_format: str
) -> None:
    """列出所有配置项，可按前缀过滤。"""
    config = tutor_config.load(context.root)

    # 过滤配置项
    filtered_config = {
        key: value
        for key, value in config.items()
        if key.startswith(filter_prefix)
    }

    if not filtered_config:
        if filter_prefix:
            msg = f"未找到前缀为 '{filter_prefix}' 的配置项"
            fmt.echo(msg)
        else:
            fmt.echo("未找到配置项")
        return

    if output_format == "json":
        click.echo(json.dumps(filtered_config, indent=2, default=str))
    elif output_format == "yaml":
        click.echo(serialize.dump(filtered_config))
    else:
        # 文本格式: KEY=VALUE
        for key in sorted(filtered_config.keys()):
            value = filtered_config[key]
            fmt.echo(f"{key}={serialize.str_format(value)}")


@click.command(help="验证必需的配置项")
@click.pass_obj
def validate(context: Context) -> None:
    """验证所有必需的配置项已设置。"""
    config = tutor_config.load(context.root)

    # 定义 EdOps 必需的配置项
    required_keys = [
        "EDOPS_IMAGE_REGISTRY",
        "EDOPS_MASTER_NODE_IP",
        "EDOPS_NETWORK_NAME",
    ]

    missing_keys = []
    for key in required_keys:
        if key not in config or not config[key]:
            missing_keys.append(key)

    if missing_keys:
        fmt.echo(fmt.error("配置验证失败！"))
        missing_str = ", ".join(missing_keys)
        fmt.echo(fmt.error(f"缺少必需的配置项: {missing_str}"))
        hint = "\n请运行 'edops config save --interactive'"
        fmt.echo(hint + " 来设置这些值")
        raise exceptions.TutorError("配置验证失败")

    fmt.echo(fmt.info("✓ 配置验证通过"))




@click.group(name="patches", help="Commands related to patches in configurations")
def patches_command() -> None:
    pass


@click.command(name="list", help="Print all available patches")
@click.pass_obj
def patches_list(context: Context) -> None:
    config = tutor_config.load(context.root)
    renderer = env.PatchRenderer(config)
    renderer.print_patches_locations()


@click.command(name="show", help="Print the rendered contents of a template patch")
@click.argument("name")
@click.pass_obj
def patches_show(context: Context, name: str) -> None:
    config = tutor_config.load_full(context.root)
    renderer = env.Renderer(config)
    rendered = renderer.patch(name)
    if rendered:
        print(rendered)


@click.command(name="edit", help="Edit config.yml of the current environment")
@click.pass_obj
def edit(context: Context) -> None:
    config_file = tutor_config.config_path(context.root)

    if not os.path.isfile(config_file):
        raise exceptions.TutorError(
            f"Missing config file at {config_file}. Have you run 'tutor local launch' yet?"
        )

    open_cmd = []
    if which("open"):  # MacOS & linux distributions that ship `open`. eg., Ubuntu
        open_cmd = ["open", config_file]
    elif which("xdg-open"):  # Linux
        open_cmd = ["xdg-open", config_file]
    elif which("start"):  # Windows
        # Calling "start" on a regular file opens it with the default editor.
        # The second argument "" just means "don't give the window a custom title".
        open_cmd = ["start", '""', config_file]
    else:
        raise exceptions.TutorError(
            f"Failed to find utility to launch an editor. Edit {config_file} with the editor of your choice."
        )

    utils.execute(*open_cmd)


config_command.add_command(save)
config_command.add_command(printroot)
config_command.add_command(printvalue)
config_command.add_command(get)
config_command.add_command(list_config)
config_command.add_command(validate)
patches_command.add_command(patches_list)
patches_command.add_command(patches_show)
config_command.add_command(patches_command)
config_command.add_command(edit)
