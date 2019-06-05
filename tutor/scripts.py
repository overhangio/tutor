from . import env
from . import exceptions
from . import fmt
from . import plugins


class BaseRunner:
    def __init__(self, root, config):
        self.root = root
        self.config = config

    def run(self, service, *path):
        command = self.render(*path)
        self.exec(service, command)

    def render(self, *path):
        return env.render_file(self.config, *path).strip()

    def exec(self, service, command):
        raise NotImplementedError

    def check_service_is_activated(self, service):
        if not self.is_activated(service):
            raise exceptions.TutorError(
                "This command may only be executed on the server where the {} is running".format(
                    service
                )
            )

    def is_activated(self, service):
        return self.config["ACTIVATE_" + service.upper()]

    def iter_plugin_scripts(self, script):
        yield from plugins.iter_scripts(self.config, script)


def initialise(runner):
    fmt.echo_info("Initialising all services...")
    runner.run("mysql-client", "scripts", "mysql-client", "init")
    for service in ["lms", "cms", "forum", "notes", "xqueue"]:
        if runner.is_activated(service):
            fmt.echo_info("Initialising {}...".format(service))
            runner.run(service, "scripts", service, "init")
    for plugin_name, service in runner.iter_plugin_scripts("init"):
        fmt.echo_info(
            "Plugin {}: running init for service {}...".format(plugin_name, service)
        )
        runner.run(service, plugin_name, "scripts", service, "init")
    fmt.echo_info("All services initialised.")


def create_user(runner, superuser, staff, username, email):
    runner.check_service_is_activated("lms")
    opts = ""
    if superuser:
        opts += " --superuser"
    if staff:
        opts += " --staff"
    command = (
        "./manage.py lms --settings=tutor.production manage_user {opts} {username} {email}\n"
        "./manage.py lms --settings=tutor.production changepassword {username}"
    ).format(opts=opts, username=username, email=email)
    runner.exec("lms", command)


def import_demo_course(runner):
    runner.check_service_is_activated("cms")
    runner.run("cms", "importdemocourse")


def index_courses(runner):
    runner.check_service_is_activated("cms")
    runner.run("cms", "indexcourses")
