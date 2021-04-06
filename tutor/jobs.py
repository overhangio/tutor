from typing import Dict, Iterator, List, Optional, Tuple, Union

from . import env, fmt, plugins
from .types import Config

BASE_OPENEDX_COMMAND = """
export DJANGO_SETTINGS_MODULE=$SERVICE_VARIANT.envs.$SETTINGS
echo "Loading settings $DJANGO_SETTINGS_MODULE"
"""


class BaseJobRunner:
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
        raise NotImplementedError

    def iter_plugin_hooks(
        self, hook: str
    ) -> Iterator[Tuple[str, Union[Dict[str, str], List[str]]]]:
        yield from plugins.iter_hooks(self.config, hook)


def initialise(runner: BaseJobRunner, limit_to: Optional[str] = None) -> None:
    fmt.echo_info("Initialising all services...")
    if limit_to is None or limit_to == "mysql":
        runner.run_job_from_template("mysql", "hooks", "mysql", "init")
    for plugin_name, hook in runner.iter_plugin_hooks("pre-init"):
        if limit_to is None or limit_to == plugin_name:
            for service in hook:
                fmt.echo_info(
                    "Plugin {}: running pre-init for service {}...".format(
                        plugin_name, service
                    )
                )
                runner.run_job_from_template(
                    service, plugin_name, "hooks", service, "pre-init"
                )
    for service in ["lms", "cms", "forum"]:
        if limit_to is None or limit_to == service:
            fmt.echo_info("Initialising {}...".format(service))
            runner.run_job_from_template(service, "hooks", service, "init")
    for plugin_name, hook in runner.iter_plugin_hooks("init"):
        if limit_to is None or limit_to == plugin_name:
            for service in hook:
                fmt.echo_info(
                    "Plugin {}: running init for service {}...".format(
                        plugin_name, service
                    )
                )
                runner.run_job_from_template(
                    service, plugin_name, "hooks", service, "init"
                )
    fmt.echo_info("All services initialised.")


def create_user_command(
    superuser: str,
    staff: bool,
    username: str,
    email: str,
    password: Optional[str] = None,
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


def set_theme(theme_name: str, domain_name: str, runner: BaseJobRunner) -> None:
    command = BASE_OPENEDX_COMMAND
    command += """
echo "Assigning theme {theme_name} to {domain_name}..."
./manage.py lms shell -c "
from django.contrib.sites.models import Site
site, _ = Site.objects.get_or_create(domain='{domain_name}')
if not site.name:
    site.name = '{domain_name}'
    site.save()
site.themes.all().delete()
site.themes.create(theme_dir_name='{theme_name}')"
"""
    command = command.format(theme_name=theme_name, domain_name=domain_name)
    runner.run_job("lms", command)
