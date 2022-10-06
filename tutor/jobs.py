import typing as t

from tutor import env, fmt, hooks
from tutor.types import Config, get_typed

BASE_OPENEDX_COMMAND = """
echo "Loading settings $DJANGO_SETTINGS_MODULE"
"""


class BaseJobRunner:
    """
    A job runner is responsible for getting a certain task to complete.
    """

    def __init__(self, root: str, config: Config):
        self.root = root
        self.config = config

    def run_job_from_template(self, service: str, *path: str) -> None:
        command = self.render(*path)
        self.run_job(service, command)

    def render(self, *path: str) -> str:
        rendered = env.render_file(self.config, *path).strip()
        if isinstance(rendered, bytes):
            raise TypeError("Cannot load job from binary file")
        return rendered

    def run_job(self, service: str, command: str) -> int:
        """
        Given a (potentially large) string command, run it with the
        corresponding service. Implementations will differ depending on the
        deployment strategy.
        """
        raise NotImplementedError


class BaseComposeJobRunner(BaseJobRunner):
    def docker_compose(self, *command: str) -> int:
        raise NotImplementedError


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


def initialise(runner: BaseJobRunner, limit_to: t.Optional[str] = None) -> None:
    fmt.echo_info("Initialising all services...")
    filter_context = hooks.Contexts.APP(limit_to).name if limit_to else None

    # Pre-init tasks
    for service, path in hooks.Filters.COMMANDS_PRE_INIT.iterate_from_context(
        filter_context
    ):
        fmt.echo_info(f"Running pre-init task: {'/'.join(path)}")
        runner.run_job_from_template(service, *path)

    # Init tasks
    for service, path in hooks.Filters.COMMANDS_INIT.iterate_from_context(
        filter_context
    ):
        fmt.echo_info(f"Running init task: {'/'.join(path)}")
        runner.run_job_from_template(service, *path)

    fmt.echo_info("All services initialised.")


def create_user_command(
    superuser: str,
    staff: bool,
    username: str,
    email: str,
    password: t.Optional[str] = None,
) -> str:
    command = BASE_OPENEDX_COMMAND

    opts = ""
    if superuser:
        opts += " --superuser"
    if staff:
        opts += " --staff"
    command += """
./manage.py lms manage_user {opts} {username} {email}
"""
    if password:
        command += """
./manage.py lms shell -c "from django.contrib.auth import get_user_model
u = get_user_model().objects.get(username='{username}')
u.set_password('{password}')
u.save()"
"""
    else:
        command += """
./manage.py lms changepassword {username}
"""

    return command.format(opts=opts, username=username, email=email, password=password)


def import_demo_course(runner: BaseJobRunner) -> None:
    runner.run_job_from_template("cms", "hooks", "cms", "importdemocourse")


def set_theme(
    theme_name: str, domain_names: t.List[str], runner: BaseJobRunner
) -> None:
    """
    For each domain, get or create a Site object and assign the selected theme.
    """
    if not domain_names:
        return
    python_code = "from django.contrib.sites.models import Site"
    for domain_name in domain_names:
        if len(domain_name) > 50:
            fmt.echo_alert(
                "Assigning a theme to a site with a long (> 50 characters) domain name."
                " The displayed site name will be truncated to 50 characters."
            )
        python_code += """
print('Assigning theme {theme_name} to {domain_name}...')
site, _ = Site.objects.get_or_create(domain='{domain_name}')
if not site.name:
    name_max_length = Site._meta.get_field('name').max_length
    name = '{domain_name}'[:name_max_length]
    site.name = name
    site.save()
site.themes.all().delete()
site.themes.create(theme_dir_name='{theme_name}')
""".format(
            theme_name=theme_name, domain_name=domain_name
        )
    command = BASE_OPENEDX_COMMAND + f'./manage.py lms shell -c "{python_code}"'
    runner.run_job("lms", command)


def get_all_openedx_domains(config: Config) -> t.List[str]:
    return [
        get_typed(config, "LMS_HOST", str),
        get_typed(config, "LMS_HOST", str) + ":8000",
        get_typed(config, "CMS_HOST", str),
        get_typed(config, "CMS_HOST", str) + ":8001",
        get_typed(config, "PREVIEW_LMS_HOST", str),
        get_typed(config, "PREVIEW_LMS_HOST", str) + ":8000",
    ]
