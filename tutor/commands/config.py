import json
import typing as t

import click
import click.shell_completion

from .. import config as tutor_config
from .. import env, exceptions, fmt
from .. import interactive as interactive_config
from .. import serialize
from ..types import Config, ConfigValue
from .context import Context


@click.group(
    name="config",
    short_help="Configure Open edX",
    help="""Configure Open edX and store configuration values in $TUTOR_ROOT/config.yml""",
)
def config_command() -> None:
    pass


class ConfigKeyParamType(click.ParamType):

    name = "configkey"

    def shell_complete(
        self, ctx: click.Context, param: click.Parameter, incomplete: str
    ) -> t.List[click.shell_completion.CompletionItem]:
        return [
            click.shell_completion.CompletionItem(key)
            for key, _value in self._shell_complete_config_items(ctx, incomplete)
        ]

    @staticmethod
    def _shell_complete_config_items(
        ctx: click.Context, incomplete: str
    ) -> t.List[t.Tuple[str, ConfigValue]]:
        # Here we want to auto-complete the name of the config key. For that we need to
        # figure out the list of enabled plugins, and for that we need the project root.
        # The project root would ordinarily be stored in ctx.obj.root, but during
        # auto-completion we don't have access to our custom Tutor context. So we resort
        # to a dirty hack, which is to examine the grandparent context.
        root = getattr(
            getattr(getattr(ctx, "parent", None), "parent", None), "params", {}
        ).get("root", "")
        config = tutor_config.load_full(root)
        return [
            (key, value) for key, value in config.items() if key.startswith(incomplete)
        ]


class ConfigKeyValParamType(ConfigKeyParamType):
    """
    Parser for <KEY>=<YAML VALUE> command line arguments.
    """

    name = "configkeyval"

    def convert(self, value: str, param: t.Any, ctx: t.Any) -> t.Tuple[str, t.Any]:
        result = serialize.parse_key_value(value)
        if result is None:
            self.fail(f"'{value}' is not of the form 'key=value'.", param, ctx)
        return result

    def shell_complete(
        self, ctx: click.Context, param: click.Parameter, incomplete: str
    ) -> t.List[click.shell_completion.CompletionItem]:
        """
        Nice and friendly <KEY>=<VAL> auto-completion.
        """
        if "=" not in incomplete:
            # Auto-complete with '<KEY>='. Note the single quotes which allow users to
            # further auto-complete later.
            return [
                click.shell_completion.CompletionItem(f"'{key}='")
                for key, value in self._shell_complete_config_items(ctx, incomplete)
            ]
        if incomplete.endswith("="):
            # raise ValueError(f"incomplete: <{incomplete}>")
            # Auto-complete with '<KEY>=<VALUE>'
            return [
                click.shell_completion.CompletionItem(f"{key}={json.dumps(value)}")
                for key, value in self._shell_complete_config_items(
                    ctx, incomplete[:-1]
                )
            ]
        # Else, don't bother
        return []


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
    set_vars: Config,
    unset_vars: t.List[str],
    env_only: bool,
) -> None:
    config = tutor_config.load_minimal(context.root)
    if interactive:
        interactive_config.ask_questions(config)
    if set_vars:
        for key, value in dict(set_vars).items():
            config[key] = env.render_unknown(config, value)
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
        # Note that this will incorrectly print None values
        fmt.echo(str(config[key]))
    except KeyError as e:
        raise exceptions.TutorError(f"Missing configuration value: {key}") from e


config_command.add_command(save)
config_command.add_command(printroot)
config_command.add_command(printvalue)
