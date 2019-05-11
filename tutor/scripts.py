import click

from . import env
from . import fmt


def migrate(root, config, run_func):
    click.echo(fmt.info("Creating all databases..."))
    run_script(root, config, "mysql-client", "create_databases.sh", run_func)

    if config["ACTIVATE_LMS"]:
        click.echo(fmt.info("Running lms migrations..."))
        run_script(root, config, "lms", "migrate_lms.sh", run_func)
    if config["ACTIVATE_CMS"]:
        click.echo(fmt.info("Running cms migrations..."))
        run_script(root, config, "cms", "migrate_cms.sh", run_func)
    if config["ACTIVATE_FORUM"]:
        click.echo(fmt.info("Running forum migrations..."))
        run_script(root, config, "forum", "migrate_forum.sh", run_func)
    if config["ACTIVATE_NOTES"]:
        click.echo(fmt.info("Running notes migrations..."))
        run_script(root, config, "notes", "migrate_django.sh", run_func)
    if config["ACTIVATE_XQUEUE"]:
        click.echo(fmt.info("Running xqueue migrations..."))
        run_script(root, config, "xqueue", "migrate_django.sh", run_func)
    if config["ACTIVATE_LMS"]:
        click.echo(fmt.info("Creating oauth2 users..."))
        run_script(root, config, "lms", "oauth2.sh", run_func)
    click.echo(fmt.info("Databases ready."))


def create_user(root, run_func, superuser, staff, name, email):
    config = {"OPTS": "", "USERNAME": name, "EMAIL": email}
    if superuser:
        config["OPTS"] += " --superuser"
    if staff:
        config["OPTS"] += " --staff"
    run_script(root, config, "lms", "create_user.sh", run_func)


def import_demo_course(root, run_func):
    run_script(root, {}, "cms", "import_demo_course.sh", run_func)


def index_courses(root, run_func):
    run_script(root, {}, "cms", "index_courses.sh", run_func)


def run_script(root, config, service, template, run_func):
    command = render_template(config, template)
    if command:
        run_func(root, service, command)


def render_template(config, template):
    return env.render_file(config, "scripts", template).strip()
