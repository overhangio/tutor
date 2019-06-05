import click

from .. import config as tutor_config
from .. import env as tutor_env
from .. import fmt
from .. import interactive as interactive_config
from .. import opts
from .. import scripts
from .. import utils


@click.group(help="Run Open edX on Kubernetes [BETA FEATURE]")
def k8s():
    pass


@click.command(help="Configure and run Open edX from scratch")
@opts.root
@click.option("-I", "--non-interactive", is_flag=True, help="Run non-interactively")
def quickstart(root, non_interactive):
    click.echo(fmt.title("Interactive platform configuration"))
    config = interactive_config.update(root, interactive=(not non_interactive))
    click.echo(fmt.title("Updating the current environment"))
    tutor_env.save(root, config)
    click.echo(fmt.title("Starting the platform"))
    start.callback(root)
    click.echo(fmt.title("Database creation and migrations"))
    init.callback(root)
    # TODO https certificates


@click.command(help="Run all configured Open edX services")
@opts.root
def start(root):
    # Create namespace
    utils.kubectl(
        "apply",
        "--kustomize",
        tutor_env.pathjoin(root),
        "--wait",
        "--selector",
        "app.kubernetes.io/component=namespace",
    )
    # Create volumes
    utils.kubectl(
        "apply",
        "--kustomize",
        tutor_env.pathjoin(root),
        "--wait",
        "--selector",
        "app.kubernetes.io/component=volume",
    )
    # Create everything else
    utils.kubectl("apply", "--kustomize", tutor_env.pathjoin(root))


@click.command(help="Stop a running platform")
@opts.root
def stop(root):
    config = tutor_config.load(root)
    utils.kubectl(
        "delete", *resource_selector(config), "deployments,services,ingress,configmaps"
    )


def resource_selector(config, *selectors):
    """
    Convenient utility for filtering only the resources that belong to this project.
    """
    selector = ",".join(
        ["app.kubernetes.io/instance=openedx-" + config["ID"]] + list(selectors)
    )
    return ["--namespace", config["K8S_NAMESPACE"], "--selector=" + selector]


@click.command(help="Completely delete an existing platform")
@opts.root
@click.option("-y", "--yes", is_flag=True, help="Do not ask for confirmation")
def delete(root, yes):
    if not yes:
        click.confirm(
            "Are you sure you want to delete the platform? All data will be removed.",
            abort=True,
        )
    utils.kubectl(
        "delete", "-k", tutor_env.pathjoin(root), "--ignore-not-found=true", "--wait"
    )


@click.command(help="Initialise all applications")
@opts.root
def init(root):
    config = tutor_config.load(root)
    runner = K8sScriptRunner(root, config)
    for service in ["mysql", "elasticsearch", "mongodb"]:
        if runner.is_activated(service):
            wait_for_pod_ready(config, service)
    scripts.initialise(runner)


@click.command(help="Create an Open edX user and interactively set their password")
@opts.root
@click.option("--superuser", is_flag=True, help="Make superuser")
@click.option("--staff", is_flag=True, help="Make staff user")
@click.argument("name")
@click.argument("email")
def createuser(root, superuser, staff, name, email):
    config = tutor_config.load(root)
    runner = K8sScriptRunner(root, config)
    scripts.create_user(runner, superuser, staff, name, email)


@click.command(help="Import the demo course")
@opts.root
def importdemocourse(root):
    fmt.echo_info("Importing demo course")
    config = tutor_config.load(root)
    runner = K8sScriptRunner(root, config)
    scripts.import_demo_course(runner)
    fmt.echo_info("Re-indexing courses")
    indexcourses.callback(root)


@click.command(help="Re-index courses for better searching")
@opts.root
def indexcourses(root):
    config = tutor_config.load(root)
    runner = K8sScriptRunner(root, config)
    scripts.index_courses(runner)


# @click.command(help="Launch a shell in LMS or CMS")
# @click.argument("service", type=click.Choice(["lms", "cms"]))
# def shell(service):
#     K8s().execute(service, "bash")


@click.command(help="View output from containers")
@opts.root
@click.option("-f", "--follow", is_flag=True, help="Follow log output")
@click.option("--tail", type=int, help="Number of lines to show from each container")
@click.argument("service")
def logs(root, follow, tail, service):
    config = tutor_config.load(root)

    command = ["logs"]
    selectors = ["app.kubernetes.io/name=" + service] if service else []
    command += resource_selector(config, *selectors)

    if follow:
        command += ["--follow"]
    if tail is not None:
        command += ["--tail", str(tail)]

    utils.kubectl(*command)


class K8sScriptRunner(scripts.BaseRunner):
    def exec(self, service, command):
        selector = "app.kubernetes.io/name={}".format(service)

        # Find pod in runner deployment
        wait_for_pod_ready(self.config, service)
        fmt.echo_info("Finding pod name for {} deployment...".format(service))
        pod = utils.check_output(
            "kubectl",
            "get",
            *resource_selector(self.config, selector),
            "pods",
            "-o=jsonpath={.items[0].metadata.name}",
        )
        # Delete any previously run jobs (completed job objects still exist)
        # utils.kubectl("delete", "-k", kustomization, "--wait", selector)
        # Run job
        utils.kubectl(
            "exec",
            "--namespace",
            self.config["K8S_NAMESPACE"],
            pod.decode(),
            "--",
            "sh",
            "-e",
            "-c",
            command,
        )
        # # Wait until complete
        # fmt.echo_info(
        #     "Waiting for job to complete. To view logs, run: \n\n    kubectl logs -n {} -l app.kubernetes.io/name={} --follow\n".format(
        #         self.config["K8S_NAMESPACE"], job_name
        #     )
        # )
        # utils.kubectl(
        #     "wait",
        #     "--namespace",
        #     self.config["K8S_NAMESPACE"],
        #     "--for=condition=complete",
        #     "--timeout=-1s",
        #     selector,
        #     "job",
        # )

def wait_for_pod_ready(config, service):
    fmt.echo_info("Waiting for a {} pod to be ready...".format(service))
    utils.kubectl(
        "wait",
        *resource_selector(config, "app.kubernetes.io/name={}".format(service)),
        "--for=condition=Ready",
        "--timeout=600s",
        "pod",
    )


k8s.add_command(quickstart)
k8s.add_command(start)
k8s.add_command(stop)
k8s.add_command(delete)
k8s.add_command(init)
k8s.add_command(createuser)
k8s.add_command(importdemocourse)
k8s.add_command(indexcourses)
# k8s.add_command(shell)
k8s.add_command(logs)
