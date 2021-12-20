import os

from . import env, exceptions, fmt, plugins, serialize, utils
from .types import Config, cast_config


def load(root: str) -> Config:
    """
    Load full configuration.

    This will raise an exception if there is no current configuration in the
    project root. A warning will also be printed if the version from disk
    differs from the package version.
    """
    if not os.path.exists(config_path(root)):
        raise exceptions.TutorError(
            "Project root does not exist. Make sure to generate the initial "
            "configuration with `tutor config save --interactive` or `tutor local "
            "quickstart` prior to running other commands."
        )
    env.check_is_up_to_date(root)
    return load_full(root)


def load_minimal(root: str) -> Config:
    """
    Load a minimal configuration composed of the user and the base config.

    This configuration is not suitable for rendering templates, as it is incomplete.
    """
    config = get_user(root)
    update_with_base(config)
    render_full(config)
    return config


def load_full(root: str) -> Config:
    """
    Load a full configuration, with user, base and defaults.
    """
    config = get_user(root)
    update_with_base(config)
    update_with_defaults(config)
    render_full(config)
    return config


def update_with_base(config: Config) -> None:
    """
    Add base configuration to the config object.

    Note that configuration entries are unrendered at this point.
    """
    base = get_base(config)
    merge(config, base)


def update_with_defaults(config: Config) -> None:
    """
    Add default configuration to the config object.

    Note that configuration entries are unrendered at this point.
    """
    defaults = get_defaults(config)
    merge(config, defaults)


def update_with_env(config: Config) -> None:
    """
    Override config values from environment variables.
    """
    overrides = {}
    for k in config.keys():
        env_var = "TUTOR_" + k
        if env_var in os.environ:
            overrides[k] = serialize.parse(os.environ[env_var])
    config.update(overrides)


def get_user(root: str) -> Config:
    """
    Get the user configuration from the tutor root.

    Overrides from environment variables are loaded as well.
    """
    convert_json2yml(root)
    path = config_path(root)
    config = {}
    if os.path.exists(path):
        config = get_yaml_file(path)
    upgrade_obsolete(config)
    update_with_env(config)
    return config


def get_base(config: Config) -> Config:
    """
    Load the base configuration.

    Entries in this configuration are unrendered.
    """
    base = get_template("base.yml")

    # Load base values from plugins
    for plugin in plugins.iter_enabled(config):
        # Add new config key/values
        for key, value in plugin.config_add.items():
            new_key = plugin.config_key(key)
            base[new_key] = value

        # Set existing config key/values
        for key, value in plugin.config_set.items():
            base[key] = value

    return base


def get_defaults(config: Config) -> Config:
    """
    Get default configuration, including from plugins.

    Entries in this configuration are unrendered.
    """
    defaults = get_template("defaults.yml")

    for plugin in plugins.iter_enabled(config):
        # Create new defaults
        for key, value in plugin.config_defaults.items():
            defaults[plugin.config_key(key)] = value

    update_with_env(defaults)
    return defaults


def get_template(filename: str) -> Config:
    """
    Get one of the configuration templates.

    Entries in this configuration are unrendered.
    """
    config = serialize.load(env.read_template_file("config", filename))
    return cast_config(config)


def get_yaml_file(path: str) -> Config:
    """
    Load config from yaml file.
    """
    with open(path) as f:
        config = serialize.load(f.read())
    return cast_config(config)


def merge(config: Config, base: Config) -> None:
    """
    Merge base values with user configuration. Values are only added if not
    already present.

    Note that this function does not perform the rendering step of the
    configuration entries.
    """
    for key, value in base.items():
        if key not in config:
            config[key] = value


def render_full(config: Config) -> None:
    """
    Fill and render an existing configuration with defaults.

    It is generally necessary to apply this function before rendering templates,
    otherwise configuration entries may not be rendered.
    """
    for key, value in config.items():
        config[key] = env.render_unknown(config, value)


def is_service_activated(config: Config, service: str) -> bool:
    return config["RUN_" + service.upper()] is not False


def upgrade_obsolete(config: Config) -> None:
    # Openedx-specific mysql passwords
    if "MYSQL_PASSWORD" in config:
        config["MYSQL_ROOT_PASSWORD"] = config["MYSQL_PASSWORD"]
        config["OPENEDX_MYSQL_PASSWORD"] = config["MYSQL_PASSWORD"]
        config.pop("MYSQL_PASSWORD")
    if "MYSQL_DATABASE" in config:
        config["OPENEDX_MYSQL_DATABASE"] = config.pop("MYSQL_DATABASE")
    if "MYSQL_USERNAME" in config:
        config["OPENEDX_MYSQL_USERNAME"] = config.pop("MYSQL_USERNAME")
    if "RUN_NOTES" in config:
        if config["RUN_NOTES"]:
            plugins.enable(config, "notes")
        config.pop("RUN_NOTES")
    if "RUN_XQUEUE" in config:
        if config["RUN_XQUEUE"]:
            plugins.enable(config, "xqueue")
        config.pop("RUN_XQUEUE")
    if "SECRET_KEY" in config:
        config["OPENEDX_SECRET_KEY"] = config.pop("SECRET_KEY")
    # Replace WEB_PROXY by RUN_CADDY
    if "WEB_PROXY" in config:
        config["RUN_CADDY"] = not config.pop("WEB_PROXY")
    # Rename ACTIVATE_HTTPS to ENABLE_HTTPS
    if "ACTIVATE_HTTPS" in config:
        config["ENABLE_HTTPS"] = config.pop("ACTIVATE_HTTPS")
    # Replace RUN_* variables by RUN_*
    for name in [
        "ACTIVATE_LMS",
        "ACTIVATE_CMS",
        "ACTIVATE_ELASTICSEARCH",
        "ACTIVATE_MONGODB",
        "ACTIVATE_MYSQL",
        "ACTIVATE_REDIS",
        "ACTIVATE_SMTP",
    ]:
        if name in config:
            config[name.replace("ACTIVATE_", "RUN_")] = config.pop(name)
    # Replace RUN_CADDY by ENABLE_WEB_PROXY
    if "RUN_CADDY" in config:
        config["ENABLE_WEB_PROXY"] = config.pop("RUN_CADDY")
    # Replace RUN_CADDY by ENABLE_WEB_PROXY
    if "NGINX_HTTP_PORT" in config:
        config["CADDY_HTTP_PORT"] = config.pop("NGINX_HTTP_PORT")


def convert_json2yml(root: str) -> None:
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
    config = get_yaml_file(json_path)
    save_config_file(root, config)
    os.remove(json_path)
    fmt.echo_info(
        "File config.json detected in {} and converted to config.yml".format(root)
    )


def save_config_file(root: str, config: Config) -> None:
    path = config_path(root)
    utils.ensure_file_directory_exists(path)
    with open(path, "w") as of:
        serialize.dump(config, of)
    fmt.echo_info("Configuration saved to {}".format(path))


def config_path(root: str) -> str:
    return os.path.join(root, "config.yml")
