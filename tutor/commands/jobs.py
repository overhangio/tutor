"""
Common jobs that must be added both to local, dev and k8s commands.
"""

import typing as t

import click

from tutor import config as tutor_config
from tutor import fmt, hooks, jobs

from .context import BaseJobContext

BASE_OPENEDX_COMMAND = """
echo "Loading settings $DJANGO_SETTINGS_MODULE"
"""


@hooks.Actions.CORE_READY.add()
def _add_core_init_tasks() -> None:
    """
    Declare core init scripts at runtime.

    The context is important, because it allows us to select the init scripts based on
    the --limit argument.
    """
    with hooks.Contexts.APP("mysql").enter():
        hooks.Filters.COMMANDS_INIT.add_item(("mysql", ("hooks", "mysql", "init")))
    with hooks.Contexts.APP("lms").enter():
        hooks.Filters.COMMANDS_INIT.add_item(("lms", ("hooks", "lms", "init")))
    with hooks.Contexts.APP("cms").enter():
        hooks.Filters.COMMANDS_INIT.add_item(("cms", ("hooks", "cms", "init")))


def initialise(runner: jobs.BaseJobRunner, limit_to: t.Optional[str] = None) -> None:
    fmt.echo_info("Initialising all services...")
    filter_context = hooks.Contexts.APP(limit_to).name if limit_to else None

    # Pre-init tasks
    iter_pre_init_tasks: t.Iterator[
        t.Tuple[str, t.Iterable[str]]
    ] = hooks.Filters.COMMANDS_PRE_INIT.iterate(context=filter_context)
    for service, path in iter_pre_init_tasks:
        fmt.echo_info(f"Running pre-init task: {'/'.join(path)}")
        runner.run_job_from_template(service, *path)

    # Init tasks
    iter_init_tasks: t.Iterator[
        t.Tuple[str, t.Iterable[str]]
    ] = hooks.Filters.COMMANDS_INIT.iterate(context=filter_context)
    for service, path in iter_init_tasks:
        fmt.echo_info(f"Running init task: {'/'.join(path)}")
        runner.run_job_from_template(service, *path)

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
@click.pass_obj
def createuser(
    context: BaseJobContext,
    superuser: str,
    staff: bool,
    password: str,
    name: str,
    email: str,
) -> None:
    run_job(
        context, "lms", create_user_template(superuser, staff, name, email, password)
    )


@click.command(help="Import the demo course")
@click.pass_obj
def importdemocourse(context: BaseJobContext) -> None:
    run_job(context, "cms", import_demo_course_template())


@click.command(
    help="Assign a theme to the LMS and the CMS. To reset to the default theme , use 'default' as the theme name."
)
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
@click.pass_obj
def settheme(context: BaseJobContext, domains: t.List[str], theme_name: str) -> None:
    run_job(context, "lms", set_theme_template(theme_name, domains))


def run_job(context: BaseJobContext, service: str, command: str) -> None:
    config = tutor_config.load(context.root)
    runner = context.job_runner(config)
    runner.run_job_from_str(service, command)


def create_user_template(
    superuser: str, staff: bool, username: str, email: str, password: str
) -> str:
    opts = ""
    if superuser:
        opts += " --superuser"
    if staff:
        opts += " --staff"
    return (
        BASE_OPENEDX_COMMAND
        + f"""
./manage.py lms manage_user {opts} {username} {email}
./manage.py lms shell -c "
from django.contrib.auth import get_user_model
u = get_user_model().objects.get(username='{username}')
u.set_password('{password}')
u.save()"
"""
    )


def import_demo_course_template() -> str:
    return (
        BASE_OPENEDX_COMMAND
        + """
# Import demo course
git clone https://github.com/openedx/edx-demo-course --branch {{ OPENEDX_COMMON_VERSION }} --depth 1 ../edx-demo-course
python ./manage.py cms import ../data ../edx-demo-course

# Re-index courses
./manage.py cms reindex_course --all --setup"""
    )


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
    return BASE_OPENEDX_COMMAND + f'./manage.py lms shell -c "{python_command}"'


def add_commands(command_group: click.Group) -> None:
    for job_command in [createuser, importdemocourse, settheme]:
        command_group.add_command(job_command)
