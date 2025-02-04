"""
Common jobs that must be added both to local, dev and k8s commands.
"""

from __future__ import annotations

import functools
import shlex
import typing as t

import click
from typing_extensions import ParamSpec

from tutor import config as tutor_config
from tutor import env, fmt, hooks
from tutor.commands.context import Context
from tutor.commands.jobs_utils import (
    create_user_template,
    get_mysql_change_charset_query,
    set_theme_template,
)
from tutor.hooks import priorities


class DoGroup(click.Group):
    """
    A Click group that prints subcommands under 'Jobs' instead of 'Commands' when we run
    `.. do --help`. Hackish but it works.
    """

    def get_help(self, ctx: click.Context) -> str:
        return super().get_help(ctx).replace("Commands:\n", "Jobs:\n")


# A convenient easy-to-use decorator for creating `do` commands.
do_group = click.group(cls=DoGroup, subcommand_metavar="JOB [ARGS]...")


@hooks.Actions.CORE_READY.add()
def _add_core_init_tasks() -> None:
    """
    Declare core init scripts at runtime.

    The context is important, because it allows us to select the init scripts based on
    the --limit argument.
    """
    with hooks.Contexts.app("mysql").enter():
        hooks.Filters.CLI_DO_INIT_TASKS.add_item(
            ("mysql", env.read_core_template_file("jobs", "init", "mysql.sh"))
        )
    with hooks.Contexts.app("meilisearch").enter():
        hooks.Filters.CLI_DO_INIT_TASKS.add_item(
            ("lms", env.read_core_template_file("jobs", "init", "meilisearch.sh"))
        )
    with hooks.Contexts.app("lms").enter():
        hooks.Filters.CLI_DO_INIT_TASKS.add_item(
            (
                "lms",
                env.read_core_template_file("jobs", "init", "mounted-directories.sh"),
            ),
            # If edx-platform is mounted, then we may need to perform some setup
            # before other initialization scripts can be run.
            priority=priorities.HIGH,
        )
        hooks.Filters.CLI_DO_INIT_TASKS.add_item(
            ("lms", env.read_core_template_file("jobs", "init", "lms.sh"))
        )
    with hooks.Contexts.app("cms").enter():
        hooks.Filters.CLI_DO_INIT_TASKS.add_item(
            ("cms", env.read_core_template_file("jobs", "init", "cms.sh"))
        )


@click.command("init", help="Initialise all applications")
@click.option("-l", "--limit", help="Limit initialisation to this service or plugin")
def initialise(limit: t.Optional[str]) -> t.Iterator[tuple[str, str]]:
    fmt.echo_info("Initialising all services...")
    filter_context = hooks.Contexts.app(limit).name if limit else None

    for service, task in hooks.Filters.CLI_DO_INIT_TASKS.iterate_from_context(
        filter_context
    ):
        fmt.echo_info(f"Running init task in {service}")
        yield service, task

    fmt.echo_info("All services initialised.")


@click.command(help="Create an Open edX user and interactively set their password")
@click.option("--superuser", is_flag=True, help="Make superuser")
@click.option("--staff", is_flag=True, help="Make staff user")
@click.option(
    "-p",
    "--password",
    help="Specify password from the command line. If undefined, you will be prompted to input a password",
    prompt=True,
    hide_input=True,
)
@click.argument("name")
@click.argument("email")
def createuser(
    superuser: str,
    staff: bool,
    password: str,
    name: str,
    email: str,
) -> t.Iterable[tuple[str, str]]:
    """
    Create an Open edX user

    Password can be passed as an option or will be set interactively.
    """
    yield ("lms", create_user_template(superuser, staff, name, email, password))


@click.command(help="Import the demo course")
@click.option(
    "-r",
    "--repo",
    default="https://github.com/openedx/openedx-demo-course",
    show_default=True,
    help="Git repository that contains the course to be imported",
)
@click.option(
    "-d",
    "--repo-dir",
    default="",
    show_default=True,
    help="Git relative subdirectory to import data from. If unspecified, will default to the directory containing course.xml",
)
@click.option(
    "-v",
    "--version",
    help="Git branch, tag or sha1 identifier. If unspecified, will default to the value of the OPENEDX_COMMON_VERSION setting.",
)
def importdemocourse(
    repo: str, repo_dir: str, version: t.Optional[str]
) -> t.Iterable[tuple[str, str]]:
    version = version or "{{ OPENEDX_COMMON_VERSION }}"
    template = f"""
# Clone the repo
git clone {repo} --branch {version} --depth 1 /tmp/course

# Determine root directory for course import. If one is provided, use that.
# Otherwise, use the directory containing course.xml, failing if there isn't exactly one.
if [ -n "{repo_dir}" ] ; then
    course_root=/tmp/course/{repo_dir}
else
    course_xml_first="$(find /tmp/course -name course.xml | head -n 1)"
    course_xml_extra="$(find /tmp/course -name course.xml | tail -n +2)"
    echo "INFO: Found course.xml files(s): $course_xml_first $course_xml_extra"
    if [ -z "$course_xml_first" ] ; then
        echo "ERROR: Could not find course.xml. Are you sure this is the right repository?"
        exit 1
    fi
    if [ -n "$course_xml_extra" ] ; then
        echo "ERROR: Found multiple course.xml files--course root is ambiguous!"
        echo "       Please specify a course root dir (relative to repo root) using --repo-dir."
        exit 1
    fi
    course_root="$(dirname "$course_xml_first")"
fi
echo "INFO: Will import course data at: $course_root" && echo

# Import into CMS
python ./manage.py cms import ../data "$course_root"

# Re-index courses
# We are not doing this anymore, because it doesn't make much sense to reindex *all*
# courses after a single one has been created. Thus we should # rely on course authors to
# press the "reindex" button in the studio after the course has # been imported.
#./manage.py cms reindex_course --all --setup
"""
    yield ("cms", template)


@click.command(help="Import the demo content libraries")
@click.argument("owner_username")
@click.option(
    "-r",
    "--repo",
    default="https://github.com/openedx/openedx-demo-course",
    show_default=True,
    help="Git repository that contains the library/libraries to be imported",
)
@click.option(
    "-v",
    "--version",
    help="Git branch, tag or sha1 identifier. If unspecified, will default to the value of the OPENEDX_COMMON_VERSION setting.",
)
def importdemolibraries(
    owner_username: str, repo: str, version: t.Optional[str]
) -> t.Iterable[tuple[str, str]]:
    version = version or "{{ OPENEDX_COMMON_VERSION }}"
    template = f"""
# Clone the repo
git clone {repo} --branch {version} --depth 1 /tmp/library

# Fail loudly if:
# * there no library.xml files, or
# * any library.xml is not within a directory named "library/" (upstream edx-platform expectation).
if ! find /tmp/library -name library.xml | grep -q "." ; then
    echo "ERROR: No library.xml files found in repository. Are you sure this is the right repository and version?"
    exit 1
fi

# For every library.xml file, create a tar of its parent directory, and import into CMS.
for lib_root in $(find /tmp/library -name library.xml | xargs dirname) ; do
    echo "INFO: Will import library at $lib_root"
    if [ "$(basename "$lib_root")" != "library" ] ; then
        echo "ERROR: can only import library.xml files that are within a directory named 'library'"
        exit 1
    fi
    rm -rf /tmp/library.tar.gz
    ( cd "$(dirname "$lib_root")" && tar czvf /tmp/library.tar.gz library )
    yes | ./manage.py cms import_content_library /tmp/library.tar.gz {owner_username}
done"""
    yield ("cms", template)


@click.command(
    name="print-edx-platform-setting",
    help="Print the value of an edx-platform Django setting.",
)
@click.argument("setting")
@click.option(
    "-s",
    "--service",
    type=click.Choice(["lms", "cms"]),
    default="lms",
    show_default=True,
    help="Service to fetch the setting from",
)
def print_edx_platform_setting(
    setting: str, service: str
) -> t.Iterable[tuple[str, str]]:
    command = f"./manage.py {service} shell -c 'from django.conf import settings; print(settings.{setting})'"
    yield (service, command)


@click.command()
@click.option(
    "-d",
    "--domain",
    "domains",
    multiple=True,
    help=(
        "Limit the theme to these domain names. By default, the theme is "
        "applied to the LMS and the CMS, both in development and production mode"
    ),
)
@click.argument("theme_name")
def settheme(domains: list[str], theme_name: str) -> t.Iterable[tuple[str, str]]:
    """
    Assign a theme to the LMS and the CMS.

    To reset to the default theme , use 'default' as the theme name.
    """
    yield ("lms", set_theme_template(theme_name, domains))


@click.command(context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
def sqlshell(args: list[str]) -> t.Iterable[tuple[str, str]]:
    """
    Open an SQL shell as root

    Extra arguments will be passed to the `mysql` command verbatim. For instance, to
    show tables from the "openedx" database, run `do sqlshell openedx -e 'show tables'`.
    """
    command = "mysql --user={{ MYSQL_ROOT_USERNAME }} --password={{ MYSQL_ROOT_PASSWORD }} --host={{ MYSQL_HOST }} --port={{ MYSQL_PORT }} --default-character-set=utf8mb4"
    if args:
        command += " " + shlex.join(args)  # pylint: disable=protected-access
    yield ("lms", command)


@click.command(
    short_help="Convert the charset and collation of mysql to utf8mb4.",
    help=(
        "Convert the charset and collation of mysql to utf8mb4. You can either upgrade all tables, specify only certain tables to upgrade or specify certain tables to exclude from the upgrade process"
    ),
    context_settings={"ignore_unknown_options": True},
)
@click.option(
    "--include",
    is_flag=False,
    nargs=1,
    help="Apps/Tables to include in the upgrade process. Requires comma-seperated values with no space in-between.",
)
@click.option(
    "--exclude",
    is_flag=False,
    nargs=1,
    help="Apps/Tables to exclude from the upgrade process. Requires comma-seperated values with no space in-between.",
)
@click.option(
    "--database",
    is_flag=False,
    nargs=1,
    default="{{ OPENEDX_MYSQL_DATABASE }}",
    show_default=True,
    required=True,
    type=str,
    help="The database of which the tables are to be upgraded",
)
@click.option("-I", "--non-interactive", is_flag=True, help="Run non-interactively")
@click.pass_obj
def convert_mysql_utf8mb4_charset(
    context: Context,
    include: str,
    exclude: str,
    database: str,
    non_interactive: bool,
) -> t.Iterable[tuple[str, str]]:
    """
    Do command to upgrade the charset and collation of tables in MySQL

    Can specify whether to upgrade all tables, or include certain tables/apps or to exclude certain tables/apps
    """

    config = tutor_config.load(context.root)

    if not config["RUN_MYSQL"]:
        fmt.echo_info(
            "You are not running MySQL (RUN_MYSQL=false). It is your "
            "responsibility to upgrade the charset and collation of your MySQL instance."
        )
        return

    # Prompt user for confirmation of upgrading all tables
    if not include and not exclude and not non_interactive:
        upgrade_all_tables = click.confirm(
            "Are you sure you want to upgrade all tables? This process is potentially irreversible and may take a long time.",
            prompt_suffix=" ",
        )
        if not upgrade_all_tables:
            return

    charset_to_upgrade_from = "utf8mb3"
    charset = "utf8mb4"
    collation = "utf8mb4_unicode_ci"

    query_to_append = ""
    if include or exclude:

        def generate_query_to_append(tables: list[str], exclude: bool = False) -> str:
            include = "NOT" if exclude else ""
            table_names = f"^{tables[0]}"
            for i in range(1, len(tables)):
                table_names += f"|^{tables[i]}"
            # We use regexp for pattern matching the names from the start of the tablename
            query_to_append = f"AND table_name {include} regexp '{table_names}' "
            return query_to_append

        query_to_append += (
            generate_query_to_append(include.split(",")) if include else ""
        )
        query_to_append += (
            generate_query_to_append(exclude.split(","), exclude=True)
            if exclude
            else ""
        )
    click.echo(
        fmt.title(
            f"Updating charset and collation of tables in the {database} database to {charset} and {collation} respectively."
        )
    )
    query = get_mysql_change_charset_query(
        database, charset, collation, query_to_append, charset_to_upgrade_from
    )

    mysql_command = (
        "mysql --user={{ MYSQL_ROOT_USERNAME }} --password={{ MYSQL_ROOT_PASSWORD }} --host={{ MYSQL_HOST }} --port={{ MYSQL_PORT }} --skip-column-names --silent "
        + shlex.join([f"--database={database}", "-e", query])
    )
    yield ("lms", mysql_command)
    fmt.echo_info("MySQL charset and collation successfully upgraded")


@click.command(
    short_help="Update the authentication plugin of a mysql user to caching_sha2_password.",
    help=(
        "Update the authentication plugin of a mysql user to caching_sha2_password from mysql_native_password."
    ),
)
@click.option(
    "-p",
    "--password",
    help="Specify password from the command line. Updates the password for the user if a password that is different from the current one is specified.",
)
@click.argument(
    "user",
)
@click.pass_obj
def update_mysql_authentication_plugin(
    context: Context, user: str, password: str
) -> t.Iterable[tuple[str, str]]:
    """
    Update the authentication plugin of MySQL users from mysql_native_password to caching_sha2_password
    Handy command utilized when upgrading to v8.4 of MySQL which deprecates mysql_native_password
    """

    config = tutor_config.load(context.root)

    if not config["RUN_MYSQL"]:
        fmt.echo_info(
            "You are not running MySQL (RUN_MYSQL=False). It is your "
            "responsibility to update the authentication plugin of mysql users."
        )
        return

    # Official plugins that have their own mysql user
    known_mysql_users = [
        # Plugin users
        "credentials",
        "discovery",
        "jupyter",
        "notes",
        "xqueue",
        # Core user
        "openedx",
    ]

    # Create a list of the usernames and password config variables/keys
    known_mysql_credentials_keys = [
        (f"{plugin.upper()}_MYSQL_USERNAME", f"{plugin.upper()}_MYSQL_PASSWORD")
        for plugin in known_mysql_users
    ]
    # Add the root user as it is the only one that is different from the rest
    known_mysql_credentials_keys.append(("MYSQL_ROOT_USERNAME", "MYSQL_ROOT_PASSWORD"))

    known_mysql_credentials = {}
    # Build the dictionary of known credentials from config
    for k, v in known_mysql_credentials_keys:
        if username := config.get(k):
            known_mysql_credentials[username] = config[v]

    if not password:
        password = known_mysql_credentials.get(user)  # type: ignore

    # Prompt the user if password was not found in config
    if not password:
        password = click.prompt(
            f"Please enter the password for the user {user}. Note that entering a different password here than the current one will update the password for user {user}.",
            type=str,
        )

    host = "%"

    query = f"ALTER USER IF EXISTS '{user}'@'{host}' IDENTIFIED with caching_sha2_password BY '{password}';"

    yield (
        "lms",
        shlex.join(
            [
                "mysql",
                "--user={{ MYSQL_ROOT_USERNAME }}",
                "--password={{ MYSQL_ROOT_PASSWORD }}",
                "--host={{ MYSQL_HOST }}",
                "--port={{ MYSQL_PORT }}",
                "--database={{ OPENEDX_MYSQL_DATABASE }}",
                "--show-warnings",
                "-e",
                query,
            ]
        ),
    )


def add_job_commands(do_command_group: click.Group) -> None:
    """
    This is meant to be called with the `local/dev/k8s do` group commands, to add the
    different `do` subcommands.
    """
    for subcommand in hooks.Filters.CLI_DO_COMMANDS.iterate():
        assert isinstance(subcommand, click.Command)
        do_command_group.add_command(subcommand)


@hooks.Actions.PLUGINS_LOADED.add()
def _patch_do_commands_callbacks() -> None:
    """
    After plugins have been loaded, patch `do` subcommands such that their output is
    forwarded to `do_callback`.

    This function is not called as part of add_job_commands because subcommands must be
    patched just once.
    """
    for subcommand in hooks.Filters.CLI_DO_COMMANDS.iterate():
        if not isinstance(subcommand, click.Command):
            raise ValueError(
                f"Command {subcommand} which was added to the CLI_DO_COMMANDS filter must be an instance of click.Command"
            )
        # Modify the subcommand callback such that job results are processed by do_callback
        if subcommand.callback is None:
            raise ValueError("Cannot patch None callback")
        if subcommand.name is None:
            raise ValueError("Defined job with None name")
        subcommand.callback = _patch_callback(subcommand.name, subcommand.callback)


P = ParamSpec("P")


def _patch_callback(
    job_name: str, func: t.Callable[P, t.Iterable[tuple[str, str]]]
) -> t.Callable[P, None]:
    """
    Modify a subcommand callback function such that its results are processed by `do_callback`.
    """

    def new_callback(*args: P.args, **kwargs: P.kwargs) -> None:
        hooks.Actions.DO_JOB.do(job_name, *args, **kwargs)
        do_callback(func(*args, **kwargs))

    # Make the new callback behave like the old one
    functools.update_wrapper(new_callback, func)

    return new_callback


def do_callback(service_commands: t.Iterable[tuple[str, str]]) -> None:
    """
    This function must be added as a callback to all `do` subcommands.

    `do` subcommands don't actually run any task. They just yield tuples of (service
    name, unrendered script string). This function is responsible for actually running
    the scripts. It does the following:

    - Prefix the script with a base command
    - Render the script string
    - Run a job in the right container

    This callback is added to the "do" subcommands by the `add_job_commands` function.
    """
    context = click.get_current_context().obj
    config = tutor_config.load(context.root)
    runner = context.job_runner(config)
    for service, command in service_commands:
        runner.run_task_from_str(service, command)


hooks.Filters.CLI_DO_COMMANDS.add_items(
    [
        convert_mysql_utf8mb4_charset,
        createuser,
        importdemocourse,
        importdemolibraries,
        initialise,
        print_edx_platform_setting,
        settheme,
        sqlshell,
        update_mysql_authentication_plugin,
    ]
)
