from __future__ import annotations

import json
import os.path
import typing as t

import click
import click.shell_completion

from shutil import which

from tutor import config as tutor_config
from tutor import env, exceptions, fmt, hooks
from tutor import interactive as interactive_config
from tutor import serialize, utils
from tutor.commands.context import Context
from tutor.commands.params import ConfigLoaderParam
from tutor.types import Config, ConfigValue


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
@click.option(
    "-c",
    "--clean",
    "clean_env",
    is_flag=True,
    help="Remove everything in the env directory before save",
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
) -> None:
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
patches_command.add_command(patches_list)
patches_command.add_command(patches_show)
config_command.add_command(patches_command)
config_command.add_command(edit)
