from __future__ import annotations

import os
import typing as t
from copy import deepcopy

from tutor import env, exceptions, fmt, hooks, plugins, serialize, utils
from tutor.types import Config, ConfigValue, cast_config, get_typed

CONFIG_FILENAME = "config.yml"


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
            "launch` prior to running other commands."
        )
    env.check_is_up_to_date(root)
    return load_full(root)


def load_defaults() -> Config:
    """
    Load default configuration.
    """
    config: Config = {}
    update_with_defaults(config)
    return config


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

    Return:
        current (dict): params currently saved in config.yml
        defaults (dict): default values of params which might be missing from the
        current config
    """
    config = get_user(root)
    update_with_base(config)
    update_with_defaults(config)
    render_full(config)
    hooks.Actions.CONFIG_LOADED.do(deepcopy(config))
    return config


def update_with_base(config: Config) -> None:
    """
    Add base configuration to the config object.

    Note that configuration entries are unrendered at this point.
    """
    base = get_base()
    merge(config, base)


def update_with_defaults(config: Config) -> None:
    """
    Add default configuration to the config object.

    Note that configuration entries are unrendered at this point.
    """
    defaults = get_defaults()
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

    for name, value in hooks.Filters.CONFIG_USER.iterate():
        config[name] = value
    return config


def get_base() -> Config:
    """
    Load the base configuration.

    Entries in this configuration are unrendered.
    """
    base = get_template("base.yml")
    extra_config: list[tuple[str, ConfigValue]] = []
    extra_config = hooks.Filters.CONFIG_UNIQUE.apply(extra_config)
    extra_config = hooks.Filters.CONFIG_OVERRIDES.apply(extra_config)
    for name, value in extra_config:
        if name in base:
            fmt.echo_alert(
                f"Found conflicting values for setting '{name}': '{value}' or '{base[name]}'"
            )
        base[name] = value
    return base


def get_defaults() -> Config:
    """
    Get default configuration, including from plugins.

    Entries in this configuration are unrendered.
    """
    defaults = dict(hooks.Filters.CONFIG_DEFAULTS.iterate())
    update_with_env(defaults)
    return defaults


@hooks.Filters.CONFIG_DEFAULTS.add(priority=hooks.priorities.HIGH)
def _load_config_defaults_yml(
    items: list[tuple[str, t.Any]]
) -> list[tuple[str, t.Any]]:
    defaults = get_template("defaults.yml")
    items += list(defaults.items())
    return items


def get_template(filename: str) -> Config:
    """
    Get one of the configuration templates.

    Entries in this configuration are unrendered.
    """
    config = serialize.load(env.read_core_template_file("config", filename))
    return cast_config(config)


def get_yaml_file(path: str) -> Config:
    """
    Load config from yaml file.
    """
    with open(path, encoding="utf-8") as f:
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
            plugins.load("notes")
            save_enabled_plugins(config)
        config.pop("RUN_NOTES")
    if "RUN_XQUEUE" in config:
        if config["RUN_XQUEUE"]:
            plugins.load("xqueue")
            save_enabled_plugins(config)
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
    # Replace nginx by caddy
    if "RUN_CADDY" in config:
        config["ENABLE_WEB_PROXY"] = config.pop("RUN_CADDY")
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
            f"Both config.json and {CONFIG_FILENAME} exist in {root}: only one of these files must exist to continue"
        )
    config = get_yaml_file(json_path)
    save_config_file(root, config)
    os.remove(json_path)
    fmt.echo_info(
        f"File config.json detected in {root} and converted to {CONFIG_FILENAME}"
    )


def save_config_file(root: str, config: Config) -> None:
    path = config_path(root)
    utils.ensure_file_directory_exists(path)
    with open(path, "w", encoding="utf-8") as of:
        serialize.dump(config, of)
    fmt.echo_info(f"Configuration saved to {path}")


def config_path(root: str) -> str:
    return os.path.join(root, CONFIG_FILENAME)


# Key name under which plugins are listed
PLUGINS_CONFIG_KEY = "PLUGINS"


def enable_plugins(config: Config) -> None:
    """
    Enable all plugins listed in the configuration.
    """
    plugins.load_all(get_enabled_plugins(config))


def get_enabled_plugins(config: Config) -> list[str]:
    """
    Return the list of plugins that are enabled, as per the configuration. Note that
    this may differ from the list of loaded plugins. For instance when a plugin is
    present in the configuration but it's not installed.
    """
    return get_typed(config, PLUGINS_CONFIG_KEY, list, [])


def save_enabled_plugins(config: Config) -> None:
    """
    Save the list of enabled plugins.

    Plugins are deduplicated by name.
    """
    config[PLUGINS_CONFIG_KEY] = list(plugins.iter_loaded())


@hooks.Actions.PROJECT_ROOT_READY.add()
def _enable_plugins(root: str) -> None:
    """
    Enable plugins that are listed in the user configuration.
    """
    config = load_minimal(root)
    enable_plugins(config)


# This is run with a very high priority such that it is called before the plugin hooks
# are actually cleared.
@hooks.Actions.PLUGIN_UNLOADED.add(priority=hooks.priorities.HIGH - 1)
def _remove_plugin_config_overrides_on_unload(
    plugin: str, _root: str, config: Config
) -> None:
    # Find the configuration entries that were overridden by the plugin and
    # remove them from the current config
    for key, _value in hooks.Filters.CONFIG_OVERRIDES.iterate_from_context(
        hooks.Contexts.app(plugin).name
    ):
        value = config.pop(key, None)
        value = env.render_unknown(config, value)
        fmt.echo_info(f"    config - removing entry: {key}={value}")


@hooks.Actions.PLUGIN_UNLOADED.add(priority=hooks.priorities.LOW)
def _update_enabled_plugins_on_unload(_plugin: str, _root: str, config: Config) -> None:
    """
    Update the list of enabled plugins.

    Note that this action must be performed after the plugin has been unloaded, hence the low priority.
    """
    save_enabled_plugins(config)


@hooks.Actions.CONFIG_LOADED.add()
def _check_preview_lms_host(config: Config) -> None:
    """
    This will check if the PREVIEW_LMS_HOST is a subdomain of LMS_HOST.
    if not, prints a warning to notify the user.
    """

    lms_host = get_typed(config, "LMS_HOST", str, "")
    preview_lms_host = get_typed(config, "PREVIEW_LMS_HOST", str, "")
    if not preview_lms_host.endswith("." + lms_host):
        fmt.echo_alert(
            f'Warning: PREVIEW_LMS_HOST="{preview_lms_host}" is not a subdomain of LMS_HOST="{lms_host}". '
            "This configuration is not typically recommended and may lead to unexpected behavior."
        )
