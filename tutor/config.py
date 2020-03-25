import os

from . import exceptions
from . import env
from . import fmt
from . import plugins
from . import serialize
from . import utils


def update(root):
    """
    Load and save the configuration.
    """
    config, defaults = load_all(root)
    save_config_file(root, config)
    merge(config, defaults)
    return config


def load(root):
    """
    Load full configuration. This will raise an exception if there is no current
    configuration in the project root.
    """
    check_existing_config(root)
    config, defaults = load_all(root)
    merge(config, defaults)
    return config


def load_all(root):
    """
    Return:
        current (dict): params currently saved in config.yml
        defaults (dict): default values of params which might be missing from the
        current config
    """
    defaults = load_defaults()
    current = load_current(root, defaults)
    return current, defaults


def merge(config, defaults, force=False):
    """
    Merge default values with user configuration and perform rendering of "{{...}}"
    values.
    """
    for key, value in defaults.items():
        if force or key not in config:
            config[key] = env.render_unknown(config, value)


def load_defaults():
    return serialize.load(env.read_template_file("config.yml"))


def load_config_file(path):
    with open(path) as f:
        return serialize.load(f.read())


def load_current(root, defaults):
    """
    Load the configuration currently stored on disk.
    Note: this modifies the defaults with the plugin default values.
    """
    convert_json2yml(root)
    config = load_user(root)
    load_env(config, defaults)
    load_required(config, defaults)
    load_plugins(config, defaults)
    return config


def load_user(root):
    path = config_path(root)
    if not os.path.exists(path):
        return {}

    config = load_config_file(path)
    upgrade_obsolete(config)
    return config


def load_env(config, defaults):
    for k in defaults.keys():
        env_var = "TUTOR_" + k
        if env_var in os.environ:
            config[k] = serialize.parse(os.environ[env_var])


def load_required(config, defaults):
    """
    All these keys must be present in the user's config.yml. This includes all values
    that are generated once and must be kept after that, such as passwords.
    """
    for key in [
        "OPENEDX_SECRET_KEY",
        "MYSQL_ROOT_PASSWORD",
        "OPENEDX_MYSQL_PASSWORD",
        "ANDROID_OAUTH2_SECRET",
        "ID",
    ]:
        if key not in config:
            config[key] = env.render_unknown(config, defaults[key])


def load_plugins(config, defaults):
    """
    Add, override and set new defaults from plugins.
    """
    for plugin in plugins.iter_enabled(config):
        # Add new config key/values
        for key, value in plugin.config_add.items():
            new_key = plugin.config_key(key)
            if new_key not in config:
                config[new_key] = env.render_unknown(config, value)

        # Set existing config key/values: here, we do not override existing values
        for key, value in plugin.config_set.items():
            if key not in config:
                config[key] = env.render_unknown(config, value)

        # Create new defaults
        for key, value in plugin.config_defaults.items():
            defaults[plugin.config_key(key)] = value


def is_service_activated(config, service):
    return config["ACTIVATE_" + service.upper()]


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
    if "ACTIVATE_NOTES" in config:
        if config["ACTIVATE_NOTES"]:
            plugins.enable(config, "notes")
        config.pop("ACTIVATE_NOTES")
    if "ACTIVATE_XQUEUE" in config:
        if config["ACTIVATE_XQUEUE"]:
            plugins.enable(config, "xqueue")
        config.pop("ACTIVATE_XQUEUE")
    if "SECRET_KEY" in config:
        config["OPENEDX_SECRET_KEY"] = config.pop("SECRET_KEY")


def convert_json2yml(root):
    """
    Older versions of tutor used to have json config files.
    """
    json_path = os.path.join(root, "config.json")
    if not os.path.exists(json_path):
        return
    if os.path.exists(config_path(root)):
        raise exceptions.TutorError(
            "Both config.json and config.yml exist in {}: only one of these files must exist to continue".format(
                root
            )
        )
    config = load_config_file(json_path)
    save_config_file(root, config)
    os.remove(json_path)
    fmt.echo_info(
        "File config.json detected in {} and converted to config.yml".format(root)
    )


def save_config_file(root, config):
    path = config_path(root)
    utils.ensure_file_directory_exists(path)
    with open(path, "w") as of:
        serialize.dump(config, of)
    fmt.echo_info("Configuration saved to {}".format(path))


def check_existing_config(root):
    """
    Check there is a configuration on disk and the current environment is up-to-date.
    """
    if not os.path.exists(config_path(root)):
        raise exceptions.TutorError(
            "Project root does not exist. Make sure to generate the initial "
            "configuration with `tutor config save --interactive` or `tutor config "
            "quickstart` prior to running other commands."
        )
    env.check_is_up_to_date(root)


def config_path(root):
    return os.path.join(root, "config.yml")
