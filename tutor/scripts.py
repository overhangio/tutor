import click

from . import config as tutor_config
from . import env
from . import fmt

def migrate(root, run_func):
    config = tutor_config.load(root)
    click.echo(fmt.info("Creating lms/cms databases..."))
    run_template(root, config, "lms", "create_databases.sh", run_func)
    click.echo(fmt.info("Running lms migrations..."))
    run_template(root, config, "lms", "migrate_lms.sh", run_func)
    click.echo(fmt.info("Running cms migrations..."))
    run_template(root, config, "cms", "migrate_cms.sh", run_func)
    click.echo(fmt.info("Running forum migrations..."))
    run_template(root, config, "forum", "migrate_forum.sh", run_func)
    if config["ACTIVATE_NOTES"]:
        click.echo(fmt.info("Running notes migrations..."))
        run_template(root, config, "notes", "migrate_django.sh", run_func)
    if config["ACTIVATE_XQUEUE"]:
        click.echo(fmt.info("Running xqueue migrations..."))
        run_template(root, config, "xqueue", "migrate_django.sh", run_func)
    click.echo(fmt.info("Creating oauth2 users..."))
    run_template(root, config, "lms", "oauth2.sh", run_func)
    click.echo(fmt.info("Databases ready."))

def create_user(root, run_func, superuser, staff, name, email):
    config = {
        "OPTS": "",
        "USERNAME": name,
        "EMAIL": email,
    }
    if superuser:
        config["OPTS"] += " --superuser"
    if staff:
        config["OPTS"] += " --staff"
    run_template(root, config, "lms", "create_user.sh", run_func)

def import_demo_course(root, run_func):
    run_template(root, {}, "cms", "import_demo_course.sh", run_func)

def index_courses(root, run_func):
    run_template(root, {}, "cms", "index_courses.sh", run_func)

def run_template(root, config, service, template, run_func):
    command = render_template(config, template)
    if command:
        run_func(root, service, command)

def render_template(config, template):
    path = env.template_path("scripts", template)
    return env.render_file(config, path).strip()
