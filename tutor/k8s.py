import click
import kubernetes

from . import config as tutor_config
from . import env as tutor_env
from . import exceptions
from . import fmt
from . import opts
from . import ops
from . import utils


@click.group(help="Run Open edX on Kubernetes [BETA FEATURE]")
def k8s():
    pass

@click.command(
    help="Configure and run Open edX from scratch"
)
@opts.root
def quickstart(root):
    click.echo(fmt.title("Interactive platform configuration"))
    tutor_config.interactive.callback(root, [])
    click.echo(fmt.title("Environment generation"))
    env.callback(root)
    click.echo(fmt.title("Stopping any existing platform"))
    stop.callback(root)
    click.echo(fmt.title("Starting the platform"))
    start.callback(root)

@click.command(
    short_help="Generate environment",
    help="Generate the environment files required to run Open edX",
)
@opts.root
def env(root):
    config = tutor_config.load(root)
    tutor_env.render_target(root, config, "apps")
    tutor_env.render_target(root, config, "k8s")
    click.echo(fmt.info("Environment generated in {}".format(root)))

@click.command(help="Run all configured Open edX services")
@opts.root
def start(root):
    kubectl_no_fail("create", "-f", tutor_env.pathjoin(root, "k8s", "namespace.yml"))

    kubectl("create", "configmap", "nginx-config", "--from-file", tutor_env.pathjoin(root, "apps", "nginx"))
    kubectl("create", "configmap", "mysql-config", "--from-env-file", tutor_env.pathjoin(root, "apps", "mysql", "auth.env"))
    kubectl("create", "configmap", "openedx-settings-lms", "--from-file", tutor_env.pathjoin(root, "apps", "openedx", "settings", "lms"))
    kubectl("create", "configmap", "openedx-settings-cms", "--from-file", tutor_env.pathjoin(root, "apps", "openedx", "settings", "cms"))
    kubectl("create", "configmap", "openedx-config", "--from-file", tutor_env.pathjoin(root, "apps", "openedx", "config"))

    kubectl("create", "-f", tutor_env.pathjoin(root, "k8s", "volumes.yml"))
    kubectl("create", "-f", tutor_env.pathjoin(root, "k8s", "ingress.yml"))
    kubectl("create", "-f", tutor_env.pathjoin(root, "k8s", "services.yml"))
    kubectl("create", "-f", tutor_env.pathjoin(root, "k8s", "deployments.yml"))

@click.command(help="Stop a running platform")
def stop():
    kubectl("delete", "deployments,services,ingress,configmaps", "--all")

@click.command(help="Completely delete an existing platform")
@click.option("-y", "--yes", is_flag=True, help="Do not ask for confirmation")
def delete(yes):
    if not yes:
        click.confirm('Are you sure you want to delete the platform? All data will be removed.', abort=True)
    kubectl("delete", "namespace", K8s.NAMESPACE)

@click.command(
    help="Create databases and run database migrations",
)
@opts.root
def databases(root):
    ops.migrate(root, run_bash)

@click.command(help="Create an Open edX user and interactively set their password")
@opts.root
@click.option("--superuser", is_flag=True, help="Make superuser")
@click.option("--staff", is_flag=True, help="Make staff user")
@click.argument("name")
@click.argument("email")
def createuser(root, superuser, staff, name, email):
    ops.create_user(root, run_bash, superuser, staff, name, email)

@click.command(help="Import the demo course")
@opts.root
def importdemocourse(root):
    ops.import_demo_course(root, run_bash)

@click.command(help="Re-index courses for better searching")
@opts.root
def indexcourses(root):
    # Note: this is currently broken with "pymongo.errors.ConnectionFailure: [Errno 111] Connection refused"
    # I'm not quite sure the settings are correctly picked up. Which is weird because migrations work very well.
    ops.index_courses(root, run_bash)

@click.command(
    help="Launch a shell in LMS or CMS",
)
@opts.root
@click.argument("service", type=click.Choice(["lms", "cms"]))
def shell(root, service):
    K8s().execute(service, "bash")

@click.command(help="Create a Kubernetesadmin user")
@opts.root
def adminuser(root):
    utils.kubectl("create", "-f", tutor_env.pathjoin(root, "k8s", "adminuser.yml"))

@click.command(help="Print the Kubernetes admin user token")
@opts.root
def admintoken(root):
    click.echo(K8s().admin_token())

def kubectl(*command):
    """
    Run kubectl commands in the right namespace. Also, errors are completely
    ignored, to avoid stopping on "AlreadyExists" errors.
    """
    args = list(command)
    args += [
        "--namespace", K8s.NAMESPACE
    ]
    kubectl_no_fail(*args)

def kubectl_no_fail(*command):
    """
    Run kubectl commands and ignore exceptions, to avoid stopping on
    "AlreadyExists" errors.
    """
    try:
        utils.kubectl(*command)
    except exceptions.TutorError:
        pass


class K8s:
    CLIENT = None
    NAMESPACE = "openedx"

    def __init__(self):
        pass

    @property
    def client(self):
        if self.CLIENT is None:
            kubernetes.config.load_kube_config()
            self.CLIENT = kubernetes.client.CoreV1Api()
        return self.CLIENT

    def pod_name(self, app):
        selector = "app=" + app
        try:
            return self.client.list_namespaced_pod("openedx", label_selector=selector).items[0].metadata.name
        except IndexError:
            raise exceptions.TutorError("Pod with app {} does not exist. Make sure that the pod is running.")

    def admin_token(self):
        # Note: this is a HORRIBLE way of looking for a secret
        try:
            secret = [
                s for s in self.client.list_namespaced_secret("kube-system").items if s.metadata.name.startswith("admin-user-token")
            ][0]
        except IndexError:
            raise exceptions.TutorError("Secret 'admin-user-token'. Make sure that admin user was created.")
        return self.client.read_namespaced_secret(secret.metadata.name, "kube-system").data["token"]

    def execute(self, app, *command):
        podname = self.pod_name(app)
        kubectl_no_fail("exec", "--namespace", self.NAMESPACE, "-it", podname, "--", *command)

def run_bash(root, service, command):
    K8s().execute(service, "bash", "-e", "-c", command)

k8s.add_command(quickstart)
k8s.add_command(env)
k8s.add_command(start)
k8s.add_command(stop)
k8s.add_command(delete)
k8s.add_command(databases)
k8s.add_command(createuser)
k8s.add_command(importdemocourse)
k8s.add_command(indexcourses)
k8s.add_command(shell)
k8s.add_command(adminuser)
k8s.add_command(admintoken)
