"""
Common jobs that must be added both to local, dev and k8s commands.
"""
import functools
import typing as t

import click
from typing_extensions import ParamSpec

from tutor import config as tutor_config
from tutor import env, fmt, hooks


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
    with hooks.Contexts.APP("mysql").enter():
        hooks.Filters.CLI_DO_INIT_TASKS.add_item(
            ("mysql", env.read_core_template_file("jobs", "init", "mysql.sh"))
        )
    with hooks.Contexts.APP("lms").enter():
        hooks.Filters.CLI_DO_INIT_TASKS.add_item(
            ("lms", env.read_core_template_file("jobs", "init", "lms.sh"))
        )
    with hooks.Contexts.APP("cms").enter():
        hooks.Filters.CLI_DO_INIT_TASKS.add_item(
            ("cms", env.read_core_template_file("jobs", "init", "cms.sh"))
        )


@click.command("init", help="Initialise all applications")
@click.option("-l", "--limit", help="Limit initialisation to this service or plugin")
def initialise(limit: t.Optional[str]) -> t.Iterator[t.Tuple[str, str]]:
    fmt.echo_info("Initialising all services...")
    filter_context = hooks.Contexts.APP(limit).name if limit else None

    # Deprecated pre-init tasks
    for service, path in hooks.Filters.COMMANDS_PRE_INIT.iterate_from_context(
        filter_context
    ):
        fmt.echo_alert(
            f"Running deprecated pre-init task: {'/'.join(path)}. Init tasks should no longer be added to the COMMANDS_PRE_INIT filter. Plugin developers should use the CLI_DO_INIT_TASKS filter instead, with a high priority."
        )
        yield service, env.read_template_file(*path)

    # Init tasks
    for service, task in hooks.Filters.CLI_DO_INIT_TASKS.iterate_from_context(
        filter_context
    ):
        fmt.echo_info(f"Running init task in {service}")
        yield service, task

    # Deprecated init tasks
    for service, path in hooks.Filters.COMMANDS_INIT.iterate_from_context(
        filter_context
    ):
        fmt.echo_alert(
            f"Running deprecated init task: {'/'.join(path)}. Init tasks should no longer be added to the COMMANDS_INIT filter. Plugin developers should use the CLI_DO_INIT_TASKS filter instead."
        )
        yield service, env.read_template_file(*path)

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
) -> t.Iterable[t.Tuple[str, str]]:
    """
    Create an Open edX user

    Password can be passed as an option or will be set interactively.
    """
    yield ("lms", create_user_template(superuser, staff, name, email, password))


def create_user_template(
    superuser: str, staff: bool, username: str, email: str, password: str
) -> str:
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


@click.command(help="Import the demo course")
def importdemocourse() -> t.Iterable[t.Tuple[str, str]]:
    template = """
# Import demo course
git clone https://github.com/openedx/edx-demo-course --branch {{ OPENEDX_COMMON_VERSION }} --depth 1 ../edx-demo-course
python ./manage.py cms import ../data ../edx-demo-course

# Re-index courses
./manage.py cms reindex_course --all --setup"""
    yield ("cms", template)


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
def settheme(domains: t.List[str], theme_name: str) -> t.Iterable[t.Tuple[str, str]]:
    """
    Assign a theme to the LMS and the CMS.

    To reset to the default theme , use 'default' as the theme name.
    """
    yield ("lms", set_theme_template(theme_name, domains))


def set_theme_template(theme_name: str, domain_names: t.List[str]) -> str:
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
    job_name: str, func: t.Callable[P, t.Iterable[t.Tuple[str, str]]]
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


def do_callback(service_commands: t.Iterable[t.Tuple[str, str]]) -> None:
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
        createuser,
        importdemocourse,
        initialise,
        settheme,
    ]
)
