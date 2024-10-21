"""
This module provides utility methods for tutor `do` commands

Methods:
- `get_mysql_change_authentication_plugin_query`: Generates MySQL queries to update the authentication plugin for MySQL users.
"""

from typing import List

from tutor import exceptions, fmt
from tutor.types import Config, ConfigValue


def get_mysql_change_authentication_plugin_query(
    config: Config, users: List[str], all_users: bool
) -> str:
    """
    Generates MySQL queries to update the authentication plugin for MySQL users.

    This method constructs queries to change the authentication plugin to
    `caching_sha2_password`. User credentials must be provided in the tutor
    configuration under the keys `<user>_MYSQL_USERNAME` and `<user>_MYSQL_PASSWORD`.

    Args:
        config (Config): Tutor configuration object
        users (List[str]): List of specific MySQL users to update.
        all_users (bool): Flag indicating whether to include ROOT and OPENEDX users
                          in addition to those specified in the `users` list.

    Returns:
        str: A string containing the SQL queries to execute.

    Raises:
        TutorError: If any user in the `users` list does not have corresponding
                    username or password entries in the configuration.
    """

    host = "%"
    query = ""

    def generate_mysql_authentication_plugin_update_query(
        username: ConfigValue, password: ConfigValue, host: str
    ) -> str:
        fmt.echo_info(
            f"Authentication plugin of user {username} will be updated to caching_sha2_password"
        )
        return f"ALTER USER '{username}'@'{host}' IDENTIFIED with caching_sha2_password BY '{password}';"

    def generate_user_queries(users: List[str]) -> str:
        query = ""
        for user in users:
            user_uppercase = user.upper()
            if not (
                f"{user_uppercase}_MYSQL_USERNAME" in config
                and f"{user_uppercase}_MYSQL_PASSWORD" in config
            ):
                fmt.echo_warning(
                    f"Username or Password for User {user} not found in config. Skipping update process for User {user}."
                )
                continue

            query += generate_mysql_authentication_plugin_update_query(
                config[f"{user_uppercase}_MYSQL_USERNAME"],
                config[f"{user_uppercase}_MYSQL_PASSWORD"],
                host,
            )
        return query

    if not all_users:
        return generate_user_queries(users)

    query += generate_mysql_authentication_plugin_update_query(
        config["MYSQL_ROOT_USERNAME"], config["MYSQL_ROOT_PASSWORD"], host
    )
    query += generate_mysql_authentication_plugin_update_query(
        config["OPENEDX_MYSQL_USERNAME"], config["OPENEDX_MYSQL_PASSWORD"], host
    )

    return query + generate_user_queries(users)
