from __future__ import annotations


def create_user_template(
    superuser: str, staff: bool, username: str, email: str, password: str
) -> str:
    """
    Helper utility to generate the necessary commands to create a user in openedx
    """
    opts = ""
    if superuser:
        opts += " --superuser"
    if staff:
        opts += " --staff"
    return f"""
./manage.py lms manage_user {opts} {username} {email}
./manage.py lms shell -c "
from django.contrib.auth import get_user_model
u = get_user_model().objects.get(username='{username}')
u.set_password('{password}')
u.save()"
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
                    TABLE_SCHEMA = '{database}'
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
                        WHERE table_schema = '{database}' AND table_type = "BASE TABLE" AND table_collation not like 'utf8mb4_%' {query_to_append};
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

            use {database};
            ALTER DATABASE {database} CHARACTER SET {charset} COLLATE {collation};
            CALL UpdateColumns();
            CALL UpdateTables();
            """


def set_theme_template(theme_name: str, domain_names: list[str]) -> str:
    """
    For each domain, get or create a Site object and assign the selected theme.
    """
    # Note that there are no double quotes " in this piece of code
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
    domain_names = domain_names or [
        "{{ LMS_HOST }}",
        "{{ LMS_HOST }}:8000",
        "{{ CMS_HOST }}",
        "{{ CMS_HOST }}:8001",
        "{{ PREVIEW_LMS_HOST }}",
        "{{ PREVIEW_LMS_HOST }}:8000",
    ]
    for domain_name in domain_names:
        python_command += f"assign_theme('{theme_name}', '{domain_name}')\n"
    return f'./manage.py lms shell -c "{python_command}"'
