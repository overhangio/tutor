from __future__ import annotations

import click

from tutor import config as tutor_config
from tutor import fmt, plugins
from tutor.types import Config, ConfigValue


def upgrade_from_lilac(config: Config) -> None:
    if not plugins.is_installed("forum"):
        fmt.echo_alert(
            "The Open edX forum feature was moved to a separate plugin in Maple. To keep using this feature, "
            "you must install and enable the tutor-forum plugin: https://github.com/overhangio/tutor-forum"
        )
    elif not plugins.is_loaded("forum"):
        fmt.echo_info(
            "The Open edX forum feature was moved to a separate plugin in Maple. To keep using this feature, "
            "we will now enable the 'forum' plugin. If you do not want to use this feature, you should disable the "
            "plugin with: `tutor plugins disable forum`."
        )
        plugins.load("forum")
        tutor_config.save_enabled_plugins(config)

    if not plugins.is_installed("mfe"):
        fmt.echo_alert(
            "In Maple the legacy courseware is no longer supported. You need to install and enable the 'mfe' plugin "
            "to make use of the new learning microfrontend: https://github.com/overhangio/tutor-mfe"
        )
    elif not plugins.is_loaded("mfe"):
        fmt.echo_info(
            "In Maple the legacy courseware is no longer supported. To start using the new learning microfrontend, "
            "we will now enable the 'mfe' plugin. If you do not want to use this feature, you should disable the "
            "plugin with: `tutor plugins disable mfe`."
        )
        plugins.load("mfe")
        tutor_config.save_enabled_plugins(config)


def upgrade_from_nutmeg(context: click.Context, config: Config) -> None:
    context.obj.job_runner(config).run_task(
        "lms", "./manage.py lms compute_grades -v1 --all_courses"
    )


def get_mysql_change_authentication_plugin_query(config: Config) -> str:
    """Helper function to generate queries depending on the loaded plugins"""
    loaded_plugins = list(plugins.iter_loaded())

    def generate_mysql_authentication_plugin_update_query(
        username: ConfigValue, password: ConfigValue, host: str
    ) -> str:
        return f"ALTER USER '{username}'@'{host}' IDENTIFIED with caching_sha2_password BY '{password}';"

    host = "%"
    query = ""
    query += generate_mysql_authentication_plugin_update_query(
        config["MYSQL_ROOT_USERNAME"], config["MYSQL_ROOT_PASSWORD"], host
    )
    query += generate_mysql_authentication_plugin_update_query(
        config["OPENEDX_MYSQL_USERNAME"], config["OPENEDX_MYSQL_PASSWORD"], host
    )

    for plugin in loaded_plugins:
        plugin_uppercase = plugin.upper()
        if (
            f"{plugin_uppercase}_MYSQL_USERNAME" in config
            and f"{plugin_uppercase}_MYSQL_PASSWORD" in config
        ):
            query += generate_mysql_authentication_plugin_update_query(
                config[f"{plugin_uppercase}_MYSQL_USERNAME"],
                config[f"{plugin_uppercase}_MYSQL_PASSWORD"],
                host,
            )

    return query


def get_mongo_upgrade_parameters(
    docker_version: str, compatibility_version: str
) -> tuple[int, dict[str, int | str]]:
    """
    Helper utility to get parameters required during mongo upgrade.
    """
    mongo_version = int(docker_version.split(".")[0])
    admin_command: dict[str, int | str] = {
        "setFeatureCompatibilityVersion": compatibility_version
    }
    if mongo_version == 7:
        # Explicit confirmation is required to upgrade to 7 from 6
        # https://www.mongodb.com/docs/manual/reference/command/setFeatureCompatibilityVersion/#confirm
        admin_command.update({"confirm": 1})
    return mongo_version, admin_command


PALM_RENAME_ORA2_FOLDER_COMMAND = """
if stat '/openedx/data/ora2/SET-ME-PLEASE (ex. bucket-name)' 2> /dev/null; then
    echo "Renaming ora2 folder..."
    mv '/openedx/data/ora2/SET-ME-PLEASE (ex. bucket-name)' /openedx/data/ora2/openedxuploads
fi
"""
