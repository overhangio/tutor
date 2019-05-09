from . import env
from . import exceptions
from . import fmt


class BaseRunner:
    def __init__(self, root, config):
        self.root = root
        self.config = config

    def render(self, script, config=None):
        config = config or self.config
        return env.render_file(config, "scripts", script).strip()

    def run(self, service, script, config=None):
        command = self.render(script, config=config)
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
    runner.run("mysql-client", "create_databases.sh")

    if runner.is_activated("lms"):
        fmt.echo_info("Running lms migrations...")
        runner.run("lms", "migrate_lms.sh")
    if runner.is_activated("cms"):
        fmt.echo_info("Running cms migrations...")
        runner.run("cms", "migrate_cms.sh")
    if runner.is_activated("forum"):
        fmt.echo_info("Running forum migrations...")
        runner.run("forum", "migrate_forum.sh")
    if runner.is_activated("notes"):
        fmt.echo_info("Running notes migrations...")
        runner.run("notes", "migrate_notes.sh")
    if runner.is_activated("xqueue"):
        fmt.echo_info("Running xqueue migrations...")
        runner.run("xqueue", "migrate_xqueue.sh")
    if runner.is_activated("lms"):
        fmt.echo_info("Creating oauth2 users...")
        runner.run("lms", "oauth2.sh")
    fmt.echo_info("Databases ready.")


def create_user(runner, superuser, staff, name, email):
    runner.check_service_is_activated("lms")
    config = {"OPTS": "", "USERNAME": name, "EMAIL": email}
    if superuser:
        config["OPTS"] += " --superuser"
    if staff:
        config["OPTS"] += " --staff"
    runner.run("lms", "create_user.sh", config=config)


def import_demo_course(runner):
    runner.check_service_is_activated("cms")
    runner.run("cms", "import_demo_course.sh")


def index_courses(runner):
    runner.check_service_is_activated("cms")
    runner.run("cms", "index_courses.sh")
