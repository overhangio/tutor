from __future__ import annotations

import json
import typing as t

import click
import click.shell_completion

from tutor import config as tutor_config
from tutor import env, exceptions, fmt
from tutor import interactive as interactive_config
from tutor import serialize
from tutor.commands.context import Context
from tutor.commands.params import ConfigLoaderParam
from tutor.types import ConfigValue


@click.group(
    name="config",
    short_help="Configure Open edX",
    help="""Configure Open edX and store configuration values in $TUTOR_ROOT/config.yml""",
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
@click.pass_obj
def save(
    context: Context,
    interactive: bool,
    set_vars: list[tuple[str, t.Any]],
    append_vars: list[tuple[str, t.Any]],
    remove_vars: list[tuple[str, t.Any]],
    unset_vars: list[str],
    env_only: bool,
) -> None:
    config = tutor_config.load_minimal(context.root)
    if interactive:
        interactive_config.ask_questions(config)
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


@click.group(name="patches", help="Commands related to patches in configurations")
def patches_command() -> None:
    pass


@click.command(name="list", help="Print all available patches")
@click.pass_obj
def patches_list(context: Context) -> None:
    config = tutor_config.load(context.root)
    renderer = env.PatchRenderer(config)
    renderer.print_patches_locations()


config_command.add_command(save)
config_command.add_command(printroot)
config_command.add_command(printvalue)
patches_command.add_command(patches_list)
config_command.add_command(patches_command)
