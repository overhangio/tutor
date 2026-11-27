from __future__ import annotations

import shlex

from tutor import env, exceptions, serialize

TEST_DEFAULTS: dict[str, str] = {
    "TEST_USERNAME": "tutor_test_admin",
    "TEST_EMAIL": "tutor_test_admin@example.com",
    "TEST_PASSWORD": "",
    "OAUTH2_CLIENT_ID": "tutor-tests",
    "OAUTH2_CLIENT_SECRET": "",
    "SMOKE_USERNAME": "tutor_smoke_user",
    "SMOKE_COURSE_ID": "course-v1:TutorSmokeOrg+SMOKE101+smoke",
}


def load_env_file(path: str) -> dict[str, str]:
    """Load a YAML file of KEY: value pairs for use as test env vars."""
    with open(path, encoding="utf-8") as f:
        data = serialize.load(f.read())
    if not isinstance(data, dict):
        raise exceptions.TutorError(
            f"Env file '{path}' must be a YAML mapping, got {type(data).__name__}"
        )
    return {str(k): str(v) for k, v in data.items()}


def parse_test_env_var(raw: str) -> tuple[str, str]:
    """Parse KEY=VALUE as plain strings (no YAML coercion — unlike serialize.parse_key_value)."""
    if "=" not in raw:
        raise exceptions.TutorError(
            f"Invalid env var '{raw}': expected KEY=VALUE format."
        )
    key, _, value = raw.partition("=")
    if not key:
        raise exceptions.TutorError(f"Invalid env var '{raw}': key cannot be empty.")
    return key, value


def shell_join(*words: str) -> str:
    """
    Return a shell command made of these words, for inclusion in a ``do`` job script.

    Job scripts are rendered as templates on the host, then run with ``sh`` in a
    container. Each word is quoted such that it is interpreted neither by the template
    engine nor by the shell, and the command receives it unchanged. Thus, this function
    must be used to include untrusted values, such as command line arguments, in job
    scripts.
    """
    return env.escape_template(shlex.join(words))


def mysql_string(value: str) -> str:
    """
    Quote a value as a MySQL string literal.
    """
    return "'" + value.replace("\\", "\\\\").replace("'", "''") + "'"


def mysql_identifier(value: str) -> str:
    """
    Quote a value as a MySQL identifier, such as a database name.
    """
    return "`" + value.replace("`", "``") + "`"


def create_user_template(
    superuser: str, staff: bool, username: str, email: str, password: str
) -> str:
    """
    Helper utility to generate the necessary commands to create a user in openedx
    """
    opts = []
    if superuser:
        opts.append("--superuser")
    if staff:
        opts.append("--staff")
    set_password = f"""
from django.contrib.auth import get_user_model
u = get_user_model().objects.get(username={username!r})
u.set_password({password!r})
u.save()"""
    return f"""
{shell_join("./manage.py", "lms", "manage_user", *opts, username, email)}
{shell_join("./manage.py", "lms", "shell", "-c", set_password)}
"""


def get_mysql_change_charset_query(
    database: str,
    charset: str,
    collation: str,
    query_to_append: str,
    charset_to_upgrade_from: str,
) -> str:
    """
    Helper function to generate the mysql query to upgrade the charset and collation of columns, tables, and databases

    Utilized in the `tutor local do convert-mysql-utf8mb4-charset` command
    """
    return f"""
            DROP PROCEDURE IF EXISTS UpdateColumns;
            DELIMITER $$

            CREATE PROCEDURE UpdateColumns()
            BEGIN

                DECLARE done_columns_loop INT DEFAULT FALSE;
                DECLARE _table_name VARCHAR(255);
                DECLARE _table_name_copy VARCHAR(255) DEFAULT "";
                DECLARE _column_name VARCHAR(255);
                DECLARE _column_type VARCHAR(255);
                DECLARE _collation_name VARCHAR(255);

                # We explicitly upgrade the utf8mb3_general_ci collations to utf8mb4_unicode_ci
                # The other collations are upgraded from utf8mb3_* to utf8mb4_*
                # For any other collation, we leave it as it is
                DECLARE columns_cur CURSOR FOR
                SELECT
                    TABLE_NAME,
                    COLUMN_NAME,
                    COLUMN_TYPE,
                    CASE
                        WHEN COLLATION_NAME LIKE CONCAT('{charset_to_upgrade_from}', '_general_ci') THEN 'utf8mb4_unicode_ci'
                        WHEN COLLATION_NAME LIKE CONCAT('{charset_to_upgrade_from}', '_%') THEN CONCAT('{charset}', SUBSTRING_INDEX(COLLATION_NAME, '{charset_to_upgrade_from}', -1))
                        ELSE COLLATION_NAME
                    END AS COLLATION_NAME
                FROM
                    INFORMATION_SCHEMA.COLUMNS
                WHERE
                    TABLE_SCHEMA = {mysql_string(database)}
                    AND COLLATION_NAME IS NOT NULL {query_to_append};
                DECLARE CONTINUE HANDLER FOR NOT FOUND SET done_columns_loop = TRUE;
                OPEN columns_cur;
                columns_loop: LOOP
                    FETCH columns_cur INTO _table_name, _column_name, _column_type, _collation_name;

                    IF done_columns_loop THEN
                    LEAVE columns_loop;
                    END IF;

                    # First, upgrade the default charset and collation of the table
                    If _table_name <> _table_name_copy THEN
                    select _table_name;
                    SET FOREIGN_KEY_CHECKS = 0;
                    SET @stmt = CONCAT('ALTER TABLE `', _table_name, '` CONVERT TO CHARACTER SET {charset} COLLATE {collation};');
                    PREPARE query FROM @stmt;
                    EXECUTE query;
                    DEALLOCATE PREPARE query;
                    SET FOREIGN_KEY_CHECKS = 1;
                    SET _table_name_copy = _table_name;
                    END IF;

                    # Then, upgrade the default charset and collation of each column
                    # This sequence of table -> column is necessary to preserve column defaults
                    SET FOREIGN_KEY_CHECKS = 0;
                    SET @statement = CONCAT('ALTER TABLE `', _table_name, '` MODIFY `', _column_name, '` ', _column_type,' CHARACTER SET {charset} COLLATE ', _collation_name, ';');
                    PREPARE query FROM @statement;
                    EXECUTE query;
                    DEALLOCATE PREPARE query;
                    SET FOREIGN_KEY_CHECKS = 1;

                END LOOP;
                CLOSE columns_cur;

            END$$

            DELIMITER ;

            DROP PROCEDURE IF EXISTS UpdateTables;
            DELIMITER $$

            CREATE PROCEDURE UpdateTables()
            # To upgrade the default character set and collation of any tables that were skipped from the previous procedure
            BEGIN

                DECLARE done INT DEFAULT FALSE;
                DECLARE table_name_ VARCHAR(255);
                DECLARE cur CURSOR FOR
                        SELECT table_name FROM information_schema.tables
                        WHERE table_schema = {mysql_string(database)} AND table_type = "BASE TABLE" AND table_collation not like 'utf8mb4_%' {query_to_append};
                DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

                OPEN cur;
                tables_loop: LOOP
                    FETCH cur INTO table_name_;

                    IF done THEN
                    LEAVE tables_loop;
                    END IF;

                    select table_name_;

                    SET FOREIGN_KEY_CHECKS = 0;
                    SET @stmt = CONCAT('ALTER TABLE `', table_name_, '` CONVERT TO CHARACTER SET {charset} COLLATE {collation};');
                    PREPARE query FROM @stmt;
                    EXECUTE query;
                    DEALLOCATE PREPARE query;

                    SET FOREIGN_KEY_CHECKS = 1;

                END LOOP;
                CLOSE cur;

            END$$
            DELIMITER ;

            use {mysql_identifier(database)};
            ALTER DATABASE {mysql_identifier(database)} CHARACTER SET {charset} COLLATE {collation};
            CALL UpdateColumns();
            CALL UpdateTables();
            """


def set_theme_template(theme_name: str, domain_names: list[str]) -> str:
    """
    For each domain, get or create a Site object and assign the selected theme.
    """
    python_command = """
import sys
from django.contrib.sites.models import Site
def assign_theme(name, domain):
    print('Assigning theme', name, 'to', domain)
    if len(domain) > 50:
            sys.stderr.write(
                'Assigning a theme to a site with a long (> 50 characters) domain name.'
                ' The displayed site name will be truncated to 50 characters.\\n'
            )
    site, _ = Site.objects.get_or_create(domain=domain)
    if not site.name:
        name_max_length = Site._meta.get_field('name').max_length
        site.name = domain[:name_max_length]
        site.save()
    site.themes.all().delete()
    if name != 'default':
        site.themes.create(theme_dir_name=name)
"""
    for domain_name in domain_names:
        python_command += f"assign_theme({theme_name!r}, {domain_name!r})\n"
    return shell_join("./manage.py", "lms", "shell", "-c", python_command)


def tests_teardown_lms_template(smoke_username: str) -> str:
    delete_user = f"""
from django.contrib.auth import get_user_model
n, _ = get_user_model().objects.filter(username={smoke_username!r}).delete()
print(f'Smoke user cleanup: removed {{n}} object(s)')"""
    return shell_join("./manage.py", "lms", "shell", "-c", delete_user)


def tests_teardown_cms_template(smoke_course_id: str) -> str:
    delete_course = shell_join("./manage.py", "cms", "delete_course", smoke_course_id)
    return f"yes | {delete_course} || true"


def tests_setup_template(
    admin_username: str,
    admin_email: str,
    admin_password: str,
    oauth_client_id: str,
    oauth_client_secret: str,
) -> str:
    set_admin_password = f"""
from django.contrib.auth import get_user_model
u = get_user_model().objects.get(username={admin_username!r})
u.set_password({admin_password!r})
u.save()
print('Test admin ready:', {admin_username!r})"""
    create_oauth_client = f"""
from oauth2_provider.models import Application
from django.contrib.auth import get_user_model
user = get_user_model().objects.get(username={admin_username!r})
app, created = Application.objects.update_or_create(
    client_id={oauth_client_id!r},
    defaults=dict(
        user=user,
        client_type=Application.CLIENT_CONFIDENTIAL,
        authorization_grant_type=Application.GRANT_CLIENT_CREDENTIALS,
        client_secret={oauth_client_secret!r},
        name='Tutor Tests',
    ),
)
print('OAuth2 client ' + ('created' if created else 'updated'))"""
    return f"""
# Create test admin user (idempotent: manage_user updates staff/superuser flags if user exists)
{shell_join("./manage.py", "lms", "manage_user", "--staff", "--superuser", admin_username, admin_email)}
{shell_join("./manage.py", "lms", "shell", "-c", set_admin_password)}

# Create OAuth2 client for tests (idempotent)
{shell_join("./manage.py", "lms", "shell", "-c", create_oauth_client)}
"""
