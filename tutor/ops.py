import click

from . import config as tutor_config
from . import env
from . import fmt
from . import scripts

# TODO merge this with scripts.py

def migrate(root, run_func):
    config = tutor_config.load(root)
    click.echo(fmt.info("Creating lms/cms databases..."))
    run_template(config, root, "lms", scripts.create_databases, run_func)
    click.echo(fmt.info("Running lms migrations..."))
    run_template(config, root, "lms", scripts.migrate_lms, run_func)
    click.echo(fmt.info("Running cms migrations..."))
    run_template(config, root, "cms", scripts.migrate_cms, run_func)
    click.echo(fmt.info("Running forum migrations..."))
    run_template(config, root, "forum", scripts.migrate_forum, run_func)
    if config["ACTIVATE_NOTES"]:
        click.echo(fmt.info("Running notes migrations..."))
        run_template(config, root, "notes", scripts.migrate_notes, run_func)
    if config["ACTIVATE_XQUEUE"]:
        click.echo(fmt.info("Running xqueue migrations..."))
        run_template(config, root, "xqueue", scripts.migrate_xqueue, run_func)
    click.echo(fmt.info("Creating oauth2 users..."))
    run_template(config, root, "lms", scripts.oauth2, run_func)
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
    run_template(config, root, "lms", scripts.create_user, run_func)

def import_demo_course(root, run_func):
    run_template({}, root, "cms", scripts.import_demo_course, run_func)

def index_courses(root, run_func):
    run_template({}, root, "cms", scripts.index_courses, run_func)

def run_template(config, root, service, template, run_func):
    command = env.render_str(template, config).strip()
    if command:
        run_func(root, service, command)
