import os

import click

from . import config as tutor_config
from . import env
from . import fmt
from .__about__ import __version__


def update(root, interactive=True):
    """
    Load and save the configuration.
    """
    config, defaults = load_all(root, interactive=interactive)
    tutor_config.save(root, config)
    tutor_config.merge(config, defaults)
    return config


def load_all(root, interactive=True):
    """
    Load configuration and interactively ask questions to collect param values from the user.
    """
    defaults = tutor_config.load_defaults()
    config = tutor_config.load_current(root, defaults)
    if interactive:
        ask_questions(config, defaults)
    return config, defaults


def ask_questions(config, defaults):
    ask("Your website domain name for students (LMS)", "LMS_HOST", config, defaults)
    ask("Your website domain name for teachers (CMS)", "CMS_HOST", config, defaults)
    ask("Your platform name/title", "PLATFORM_NAME", config, defaults)
    ask("Your public contact email address", "CONTACT_EMAIL", config, defaults)
    ask_choice(
        "The default language code for the platform",
        "LANGUAGE_CODE",
        config,
        defaults,
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
            " this will NOT work in a development environment."
        ),
        "ACTIVATE_HTTPS",
        config,
        defaults,
    )


def ask(question, key, config, defaults):
    default = env.render_str(config, config.get(key, defaults[key]))
    config[key] = click.prompt(
        fmt.question(question), prompt_suffix=" ", default=default, show_default=True
    )


def ask_bool(question, key, config, defaults):
    default = config.get(key, defaults[key])
    config[key] = click.confirm(
        fmt.question(question), prompt_suffix=" ", default=default
    )


def ask_choice(question, key, config, defaults, choices):
    default = config.get(key, defaults[key])
    answer = click.prompt(
        fmt.question(question),
        type=click.Choice(choices),
        prompt_suffix=" ",
        default=default,
        show_choices=False,
    )
    config[key] = answer
