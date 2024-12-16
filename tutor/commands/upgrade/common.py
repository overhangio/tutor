from __future__ import annotations

from typing import Optional

import click
from packaging import version

from tutor import config as tutor_config
from tutor import fmt, plugins
from tutor.types import Config, get_typed


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


def upgrade_from_redwood(context: click.Context, config: Config) -> None:
    # Forcefully enable the learning MFE's navigation sidebar.
    if plugins.is_loaded("mfe"):
        context.obj.job_runner(config).run_task(
            "lms",
            "./manage.py lms waffle_flag --create --everyone courseware.enable_navigation_sidebar",
        )

    # Prevent switching to the MySQL storage backend in forum v2
    if plugins.is_loaded("forum"):
        fmt.echo_alert(
            "Your platform is going to be configured to store forum data in MongoDB. "
            "You are STRONGLY ENCOURAGED to migrate your forum data to MySQL as soon as possible. "
            "To do so, refer to the tutor-forum plugin documentation: https://github.com/overhangio/tutor-forum/#installation"
        )
        context.obj.job_runner(config).run_task(
            "lms",
            """
(./manage.py lms waffle_flag --list | grep forum_v2.enable_mysql_backend) || ./manage.py lms waffle_flag --create --deactivate forum_v2.enable_mysql_backend
""",
        )

    fmt.echo_alert(
        """It is recommended to upgrade your character set and collation of the MySQL database after upgrading to Sumac.
You can use the convert-mysql-utf8mb4-charset do job to upgrade the collation and character set. You can find more details regarding the command at https://docs.tutor.edly.io/local.html#changing-the-mysql-charset-and-collation"""
    )


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


def get_intermediate_mysql_upgrade(config: Config) -> Optional[str]:
    """
    Checks if a MySQL upgrade is needed based on the Tutor version and MySQL setup.

    This method ensures that MySQL is running and determines if the upgrade
    process should proceed based on the Tutor version. It is intended for upgrades
    from Tutor version 15 to version 18 or later. Manual upgrade steps are not
    required for versions 16 or 17.

    Returns:
        Optional[str]: The docker image of MySQL to upgrade to or None if not applicable
    """
    if not get_typed(config, "RUN_MYSQL", bool):
        fmt.echo_info(
            "You are not running MySQL (RUN_MYSQL=false). It is your "
            "responsibility to upgrade your MySQL instance to v8.4. There is "
            "nothing left to do to upgrade from Olive."
        )
        return None
    image_tag = get_typed(config, "DOCKER_IMAGE_MYSQL", str).split(":")[-1]
    # If latest image, we assign a constant value to invalidate the condition
    # as we know that the latest image will always be greater than 8.1.0
    target_version = (
        version.Version("8.1.1") if image_tag == "latest" else version.parse(image_tag)
    )
    return "docker.io/mysql:8.1.0" if target_version > version.parse("8.1.0") else None


PALM_RENAME_ORA2_FOLDER_COMMAND = """
if stat '/openedx/data/ora2/SET-ME-PLEASE (ex. bucket-name)' 2> /dev/null; then
    echo "Renaming ora2 folder..."
    mv '/openedx/data/ora2/SET-ME-PLEASE (ex. bucket-name)' /openedx/data/ora2/openedxuploads
fi
"""
