import json
import os
import yaml

import click

from . import exceptions
from . import env
from . import fmt
from . import opts


@click.group(
    short_help="Configure Open edX",
    help="""Configure Open edX and store configuration values in $TUTOR_ROOT/config.yml"""
)
@opts.root
def config(root):
    pass

@click.command(
    help="Create and save configuration interactively",
)
@opts.root
@opts.key_value
def interactive(root, s):
    config = {}
    load_files(config, root)
    for k, v in s:
        config[k] = v
    load_interactive(config)
    save(config, root)

@click.command(
    help="Create and save configuration without user interaction",
)
@opts.root
@opts.key_value
def noninteractive(root, s):
    config = {}
    load_files(config, root)
    for k, v in s:
        config[k] = v
    save(config, root)

@click.command(
    help="Print the tutor project root",
)
@opts.root
def printroot(root):
    click.echo(root)

def load(root):
    """
    Load configuration, and generate it interactively if the file does not
    exist.
    """
    config = {}
    load_files(config, root)

    if not os.path.exists(config_path(root)):
        load_interactive(config)
        save(config, root)

    load_defaults(config)

    return config

def load_files(config, root):
    convert_json2yml(root)

    # Load base values
    base = yaml.load(env.read("config.yml"))
    for k, v in base.items():
        config[k] = v

    # Load user file
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
        save(config, root)
    os.remove(json_path)
    click.echo(fmt.info("File config.json detected in {} and converted to config.yml".format(root)))

def save(config, root):
    env.render_dict(config)
    path = config_path(root)
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(path, "w") as of:
        yaml.dump(config, of, default_flow_style=False)
    click.echo(fmt.info("Configuration saved to {}".format(path)))

def config_path(root):
    return os.path.join(root, "config.yml")

config.add_command(interactive)
config.add_command(noninteractive)
config.add_command(printroot)
