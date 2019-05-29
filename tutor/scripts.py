from . import env
from . import exceptions
from . import fmt
from . import plugins


class BaseRunner:
    def __init__(self, root, config):
        self.root = root
        self.config = config

    def render(self, service, script, config=None):
        config = config or self.config
        return env.render_file(config, "scripts", service, script).strip()

    def run(self, service, script, config=None):
        command = self.render(service, script, config=config)
        self.exec(service, command)

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


def migrate(runner):
    fmt.echo_info("Creating all databases...")
    runner.run("mysql-client", "createdatabases")

    for service in ["lms", "cms", "forum", "notes", "xqueue"]:
        if runner.is_activated(service):
            fmt.echo_info("Running {} migrations...".format(service))
            runner.run(service, "init")
    # TODO it's really ugly to load the config from the runner
    for plugin_name, service, command in plugins.iter_scripts(runner.config, "init"):
        fmt.echo_info(
            "Plugin {}: running init for service {}...".format(plugin_name, service)
        )
        runner.run(service, "init")
    fmt.echo_info("Databases ready.")


def create_user(runner, superuser, staff, name, email):
    runner.check_service_is_activated("lms")
    config = {"OPTS": "", "USERNAME": name, "EMAIL": email}
    if superuser:
        config["OPTS"] += " --superuser"
    if staff:
        config["OPTS"] += " --staff"
    runner.run("lms", "createuser", config=config)


def import_demo_course(runner):
    runner.check_service_is_activated("cms")
    runner.run("cms", "importdemocourse")


def index_courses(runner):
    runner.check_service_is_activated("cms")
    runner.run("cms", "indexcourses")
