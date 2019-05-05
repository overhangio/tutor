import appdirs
import click

from . import serialize


root = click.option(
    "-r",
    "--root",
    envvar="TUTOR_ROOT",
    default=appdirs.user_data_dir(appname="tutor"),
    show_default=True,
    type=click.Path(resolve_path=True),
    help="Root project directory (environment variable: TUTOR_ROOT)",
)

edx_platform_path = click.option(
    "-P",
    "--edx-platform-path",
    envvar="TUTOR_EDX_PLATFORM_PATH",
    type=click.Path(exists=True, dir_okay=True, resolve_path=True),
    help="Mount a local edx-platform from the host (environment variable: TUTOR_EDX_PLATFORM_PATH)",
)

edx_platform_settings = click.option(
    "-S",
    "--edx-platform-settings",
    envvar="TUTOR_EDX_PLATFORM_SETTINGS",
    default="tutor.development",
    help="Mount a local edx-platform from the host (environment variable: TUTOR_EDX_PLATFORM_PATH)",
)


class YamlParamType(click.ParamType):
    name = "yaml"

    def convert(self, value, param, ctx):
        try:
            k, v = value.split("=")
        except ValueError:
            self.fail("'{}' is not of the form 'key=value'.".format(value), param, ctx)
        return k, serialize.parse_value(v)


key_value = click.option(
    "-s",
    "--set",
    "set_",
    type=YamlParamType(),
    multiple=True,
    metavar="KEY=VAL",
    help="Set a configuration value (can be used multiple times)",
)
