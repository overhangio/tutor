import json
import os
import yaml

import click

from . import exceptions
from . import env
from . import fmt
from . import opts
from . import utils
from .__about__ import __version__


@click.group(
    short_help="Configure Open edX",
    help="""Configure Open edX and store configuration values in $TUTOR_ROOT/config.yml"""
)
def config():
    pass

@click.command(help="Create and save configuration interactively")
@opts.root
@click.option("--silent", is_flag=True, help="Run non-interactively")
@opts.key_value
def save(root, silent, set_):
    config = {}
    load_current(config, root)
    for k, v in set_:
        config[k] = v
    if not silent:
        load_interactive(config)
    save_config(root, config)

    load_defaults(config)
    save_env(root, config)

@click.command(
    help="Print the project root",
)
@opts.root
def printroot(root):
    click.echo(root)

@click.command(help="Print a configuration value")
@opts.root
@click.argument("key")
def printvalue(root, key):
    config = {}
    load_current(config, root)
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
    config = {}
    load_current(config, root)

    should_update_env = False
    if not os.path.exists(config_path(root)):
        load_interactive(config)
        should_update_env = True
        save_config(root, config)

    load_defaults(config)

    if not env.is_up_to_date(root):
        click.echo(fmt.alert(
            "The current environment stored at {} is not up-to-date: it is at "
            "v{} while the 'tutor' binary is at v{}. The environment will be "
            "upgraded now. Any change you might have made will be overwritten.".format(
                env.base_dir(root), env.version(root), __version__
            )
        ))
        should_update_env = True

    if should_update_env:
        save_env(root, config)

    return config

def load_current(config, root):
    convert_json2yml(root)
    load_base(config, root)
    load_user(config, root)
    load_env(config, root)

def load_base(config, root):
    base = yaml.load(env.read("config-base.yml"))
    for k, v in base.items():
        config[k] = v

def load_env(config, root):
    base_config = yaml.load(env.read("config-base.yml"))
    default_config = yaml.load(env.read("config-defaults.yml"))
    keys = set(list(base_config.keys()) + list(default_config.keys()))

    for k in keys:
        env_var = "TUTOR_" + k
        if env_var in os.environ:
            config[k] = utils.parse_yaml_value(os.environ[env_var])

def load_user(config, root):
    path = config_path(root)
    if os.path.exists(path):
        with open(path) as fi:
            loaded = yaml.load(fi.read())
        for key, value in loaded.items():
            config[key] = value

def load_interactive(config):
    ask("Your website domain name for students (LMS)", "LMS_HOST", config)
    ask("Your website domain name for teachers (CMS)", "CMS_HOST", config)
    ask("Your platform name/title", "PLATFORM_NAME", config)
    ask("Your public contact email address", "CONTACT_EMAIL", config)
    ask_choice(
        "The default language code for the platform",
        "LANGUAGE_CODE", config,
        ['en', 'am', 'ar', 'az', 'bg-bg', 'bn-bd', 'bn-in', 'bs', 'ca',
         'ca@valencia', 'cs', 'cy', 'da', 'de-de', 'el', 'en-uk', 'en@lolcat',
         'en@pirate', 'es-419', 'es-ar', 'es-ec', 'es-es', 'es-mx', 'es-pe',
         'et-ee', 'eu-es', 'fa', 'fa-ir', 'fi-fi', 'fil', 'fr', 'gl', 'gu',
         'he', 'hi', 'hr', 'hu', 'hy-am', 'id', 'it-it', 'ja-jp', 'kk-kz',
         'km-kh', 'kn', 'ko-kr', 'lt-lt', 'ml', 'mn', 'mr', 'ms', 'nb', 'ne',
         'nl-nl', 'or', 'pl', 'pt-br', 'pt-pt', 'ro', 'ru', 'si', 'sk', 'sl',
         'sq', 'sr', 'sv', 'sw', 'ta', 'te', 'th', 'tr-tr', 'uk', 'ur', 'vi',
         'uz', 'zh-cn', 'zh-hk', 'zh-tw'],
    )
    ask_bool(
        ("Activate SSL/TLS certificates for HTTPS access? Important note:"
         "this will NOT work in a development environment."),
        "ACTIVATE_HTTPS", config
    )
    ask_bool(
        "Activate Student Notes service (https://open.edx.org/features/student-notes)?",
        "ACTIVATE_NOTES", config
    )
    ask_bool(
        "Activate Xqueue for external grader services (https://github.com/edx/xqueue)?",
        "ACTIVATE_XQUEUE", config
    )

def load_defaults(config):
    defaults = yaml.load(env.read("config-defaults.yml"))
    for k, v in defaults.items():
        if k not in config:
            config[k] = v

def ask(question, key, config):
    default = env.render_str(config[key], config)
    config[key] = click.prompt(
        fmt.question(question),
        prompt_suffix=" ", default=default, show_default=True,
    )

def ask_bool(question, key, config):
    default = "y" if config[key] else "n"
    suffix = " [Yn]" if config[key] else " [yN]"
    answer = click.prompt(
        fmt.question(question) + suffix,
        type=click.Choice(["y", "n"]),
        prompt_suffix=" ", default=default, show_default=False, show_choices=False,
    )
    config[key] = answer == "y"

def ask_choice(question, key, config, choices):
    default = config[key]
    answer = click.prompt(
        fmt.question(question),
        type=click.Choice(choices),
        prompt_suffix=" ", default=default, show_choices=False,
    )
    config[key] = answer

def convert_json2yml(root):
    json_path = os.path.join(root, "config.json")
    if not os.path.exists(json_path):
        return
    if os.path.exists(config_path(root)):
        raise exceptions.TutorError(
            "Both config.json and config.yml exist in {}: only one of these files must exist to continue".format(root)
        )
    with open(json_path) as fi:
        config = json.load(fi)
        save_config(root, config)
    os.remove(json_path)
    click.echo(fmt.info("File config.json detected in {} and converted to config.yml".format(root)))

def save_config(root, config):
    env.render_dict(config)
    path = config_path(root)
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(path, "w") as of:
        yaml.dump(config, of, default_flow_style=False)
    click.echo(fmt.info("Configuration saved to {}".format(path)))

def save_env(root, config):
    env.render_full(root, config)
    click.echo(fmt.info("Environment generated in {}".format(env.base_dir(root))))

def config_path(root):
    return os.path.join(root, "config.yml")

config.add_command(save)
config.add_command(printroot)
config.add_command(printvalue)
