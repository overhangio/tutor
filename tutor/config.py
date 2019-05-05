import json
import os
import sys

import click

from . import exceptions
from . import env
from . import fmt
from . import opts
from . import serialize
from . import utils
from .__about__ import __version__


@click.group(
    short_help="Configure Open edX",
    help="""Configure Open edX and store configuration values in $TUTOR_ROOT/config.yml""",
)
def config_command():
    pass


@click.command(help="Create and save configuration interactively")
@opts.root
@click.option("-y", "--yes", "silent1", is_flag=True, help="Run non-interactively")
@click.option("--silent", "silent2", is_flag=True, hidden=True)
@opts.key_value
def save_command(root, silent1, silent2, set_):
    silent = silent1 or silent2
    save(root, silent=silent, keyvalues=set_)


def save(root, silent=False, keyvalues=None):
    keyvalues = keyvalues or []
    config = load_current(root)
    for k, v in keyvalues:
        config[k] = v
    if not silent:
        load_interactive(config)
    save_config(root, config)

    load_defaults(config)
    save_env(root, config)


@click.command(help="Print the project root")
@opts.root
def printroot(root):
    click.echo(root)


@click.command(help="Print a configuration value")
@opts.root
@click.argument("key")
def printvalue(root, key):
    config = load_current(root)
    load_defaults(config)
    try:
        print(config[key])
    except KeyError:
        raise exceptions.TutorError("Missing configuration value: {}".format(key))


def load(root):
    """
    Load configuration, and generate it interactively if the file does not
    exist.
    """
    config = load_current(root)

    should_update_env = False
    if not os.path.exists(config_path(root)):
        load_interactive(config)
        should_update_env = True
        save_config(root, config)

    load_defaults(config)
    if not env.is_up_to_date(root):
        should_update_env = True
        pre_upgrade_announcement(root)

    if should_update_env:
        save_env(root, config)

    return config


def pre_upgrade_announcement(root):
    """
    Inform the user that the current environment is not up-to-date. Crash if running in
    non-interactive mode.
    """
    click.echo(
        fmt.alert(
            "The current environment stored at {} is not up-to-date: it is at "
            "v{} while the 'tutor' binary is at v{}.".format(
                env.base_dir(root), env.version(root), __version__
            )
        )
    )
    if os.isatty(sys.stdin.fileno()):
        # Interactive mode: ask the user permission to proceed
        click.confirm(
            fmt.question(
                # every patch you take, every change you make, I'll be watching you
                "Would you like to upgrade the environment? If you do, any change you"
                " might have made will be overwritten."
            ),
            default=True,
            abort=True,
        )
    else:
        # Non-interactive mode with no authorization: abort
        raise exceptions.TutorError(
            "Running in non-interactive mode, the environment will not be upgraded"
            " automatically. To upgrade the environment manually, run:\n"
            "\n"
            "    tutor config save -y"
        )


def load_current(root):
    convert_json2yml(root)
    config = {}
    load_base(config)
    load_user(config, root)
    load_env(config)
    return config


def load_base(config):
    base = serialize.load(env.read("config-base.yml"))
    for k, v in base.items():
        config[k] = v


def load_env(config):
    base_config = serialize.load(env.read("config-base.yml"))
    default_config = serialize.load(env.read("config-defaults.yml"))
    keys = set(list(base_config.keys()) + list(default_config.keys()))

    for k in keys:
        env_var = "TUTOR_" + k
        if env_var in os.environ:
            config[k] = serialize.parse_value(os.environ[env_var])


def load_user(config, root):
    path = config_path(root)
    if os.path.exists(path):
        with open(path) as fi:
            loaded = serialize.load(fi.read())
        for key, value in loaded.items():
            config[key] = value
    upgrade_obsolete(config)


def upgrade_obsolete(config):
    # Openedx-specific mysql passwords
    if "MYSQL_PASSWORD" in config:
        config["MYSQL_ROOT_PASSWORD"] = config["MYSQL_PASSWORD"]
        config["OPENEDX_MYSQL_PASSWORD"] = config["MYSQL_PASSWORD"]
        config.pop("MYSQL_PASSWORD")
    if "MYSQL_DATABASE" in config:
        config["OPENEDX_MYSQL_DATABASE"] = config.pop("MYSQL_DATABASE")
    if "MYSQL_USERNAME" in config:
        config["OPENEDX_MYSQL_USERNAME"] = config.pop("MYSQL_USERNAME")


def load_interactive(config):
    ask("Your website domain name for students (LMS)", "LMS_HOST", config)
    ask("Your website domain name for teachers (CMS)", "CMS_HOST", config)
    ask("Your platform name/title", "PLATFORM_NAME", config)
    ask("Your public contact email address", "CONTACT_EMAIL", config)
    ask_choice(
        "The default language code for the platform",
        "LANGUAGE_CODE",
        config,
        [
            "en",
            "am",
            "ar",
            "az",
            "bg-bg",
            "bn-bd",
            "bn-in",
            "bs",
            "ca",
            "ca@valencia",
            "cs",
            "cy",
            "da",
            "de-de",
            "el",
            "en-uk",
            "en@lolcat",
            "en@pirate",
            "es-419",
            "es-ar",
            "es-ec",
            "es-es",
            "es-mx",
            "es-pe",
            "et-ee",
            "eu-es",
            "fa",
            "fa-ir",
            "fi-fi",
            "fil",
            "fr",
            "gl",
            "gu",
            "he",
            "hi",
            "hr",
            "hu",
            "hy-am",
            "id",
            "it-it",
            "ja-jp",
            "kk-kz",
            "km-kh",
            "kn",
            "ko-kr",
            "lt-lt",
            "ml",
            "mn",
            "mr",
            "ms",
            "nb",
            "ne",
            "nl-nl",
            "or",
            "pl",
            "pt-br",
            "pt-pt",
            "ro",
            "ru",
            "si",
            "sk",
            "sl",
            "sq",
            "sr",
            "sv",
            "sw",
            "ta",
            "te",
            "th",
            "tr-tr",
            "uk",
            "ur",
            "vi",
            "uz",
            "zh-cn",
            "zh-hk",
            "zh-tw",
        ],
    )
    ask_bool(
        (
            "Activate SSL/TLS certificates for HTTPS access? Important note:"
            "this will NOT work in a development environment."
        ),
        "ACTIVATE_HTTPS",
        config,
    )
    ask_bool(
        "Activate Student Notes service (https://open.edx.org/features/student-notes)?",
        "ACTIVATE_NOTES",
        config,
    )
    ask_bool(
        "Activate Xqueue for external grader services (https://github.com/edx/xqueue)?",
        "ACTIVATE_XQUEUE",
        config,
    )


def load_defaults(config):
    defaults = serialize.load(env.read("config-defaults.yml"))
    for k, v in defaults.items():
        if k not in config:
            config[k] = v

    # Add extra configuration parameters that need to be computed separately
    config["lms_cms_common_domain"] = utils.common_domain(
        config["LMS_HOST"], config["CMS_HOST"]
    )
    config["lms_host_reverse"] = ".".join(config["LMS_HOST"].split(".")[::-1])


def ask(question, key, config):
    default = env.render_str(config, config[key])
    config[key] = click.prompt(
        fmt.question(question), prompt_suffix=" ", default=default, show_default=True
    )


def ask_bool(question, key, config):
    return click.confirm(fmt.question(question), prompt_suffix=" ", default=config[key])


def ask_choice(question, key, config, choices):
    default = config[key]
    answer = click.prompt(
        fmt.question(question),
        type=click.Choice(choices),
        prompt_suffix=" ",
        default=default,
        show_choices=False,
    )
    config[key] = answer


def convert_json2yml(root):
    json_path = os.path.join(root, "config.json")
    if not os.path.exists(json_path):
        return
    if os.path.exists(config_path(root)):
        raise exceptions.TutorError(
            "Both config.json and config.yml exist in {}: only one of these files must exist to continue".format(
                root
            )
        )
    with open(json_path) as fi:
        config = json.load(fi)
        save_config(root, config)
    os.remove(json_path)
    click.echo(
        fmt.info(
            "File config.json detected in {} and converted to config.yml".format(root)
        )
    )


def save_config(root, config):
    env.render_dict(config)
    path = config_path(root)
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(path, "w") as of:
        serialize.dump(config, of)
    click.echo(fmt.info("Configuration saved to {}".format(path)))


def save_env(root, config):
    env.render_full(root, config)
    click.echo(fmt.info("Environment generated in {}".format(env.base_dir(root))))


def config_path(root):
    return os.path.join(root, "config.yml")


config_command.add_command(save_command, name="save")
config_command.add_command(printroot)
config_command.add_command(printvalue)
