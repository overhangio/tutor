from datetime import datetime
from time import sleep

import click

from .. import config as tutor_config
from .. import env as tutor_env
from .. import exceptions
from .. import fmt
from .. import interactive as interactive_config
from .. import scripts
from .. import serialize
from .. import utils


@click.group(help="Run Open edX on Kubernetes")
def k8s():
    pass


@click.command(help="Configure and run Open edX from scratch")
@click.option("-I", "--non-interactive", is_flag=True, help="Run non-interactively")
@click.pass_obj
def quickstart(context, non_interactive):
    click.echo(fmt.title("Interactive platform configuration"))
    config = interactive_config.update(context.root, interactive=(not non_interactive))
    if config["ACTIVATE_HTTPS"] and not config["WEB_PROXY"]:
        fmt.echo_alert(
            "Potentially invalid configuration: ACTIVATE_HTTPS=true WEB_PROXY=false\n"
            "You should either disable HTTPS support or configure your platform to use"
            " a web proxy. See the Kubernetes section in the Tutor documentation for"
            " more information."
        )
    click.echo(fmt.title("Updating the current environment"))
    tutor_env.save(context.root, config)
    click.echo(fmt.title("Starting the platform"))
    start.callback()
    click.echo(fmt.title("Database creation and migrations"))
    init.callback(limit=None)


@click.command(help="Run all configured Open edX services")
@click.pass_obj
def start(context):
    # Create namespace
    utils.kubectl(
        "apply",
        "--kustomize",
        tutor_env.pathjoin(context.root),
        "--wait",
        "--selector",
        "app.kubernetes.io/component=namespace",
    )
    # Create volumes
    utils.kubectl(
        "apply",
        "--kustomize",
        tutor_env.pathjoin(context.root),
        "--wait",
        "--selector",
        "app.kubernetes.io/component=volume",
    )
    # Create everything else except jobs, ingress and issuer
    utils.kubectl(
        "apply",
        "--kustomize",
        tutor_env.pathjoin(context.root),
        "--selector",
        "app.kubernetes.io/component notin (job, ingress, issuer)",
    )


@click.command(help="Stop a running platform")
@click.pass_obj
def stop(context):
    config = tutor_config.load(context.root)
    utils.kubectl(
        "delete",
        *resource_selector(config),
        "deployments,services,ingress,configmaps,jobs",
    )


@click.command(help="Reboot an existing platform")
def reboot():
    stop.callback()
    start.callback()


def resource_selector(config, *selectors):
    """
    Convenient utility for filtering only the resources that belong to this project.
    """
    selector = ",".join(
        ["app.kubernetes.io/instance=openedx-" + config["ID"]] + list(selectors)
    )
    return ["--namespace", config["K8S_NAMESPACE"], "--selector=" + selector]


@click.command(help="Completely delete an existing platform")
@click.option("-y", "--yes", is_flag=True, help="Do not ask for confirmation")
@click.pass_obj
def delete(context, yes):
    if not yes:
        click.confirm(
            "Are you sure you want to delete the platform? All data will be removed.",
            abort=True,
        )
    utils.kubectl(
        "delete",
        "-k",
        tutor_env.pathjoin(context.root),
        "--ignore-not-found=true",
        "--wait",
    )


@click.command(help="Initialise all applications")
@click.option("-l", "--limit", help="Limit initialisation to this service or plugin")
@click.pass_obj
def init(context, limit):
    config = tutor_config.load(context.root)
    runner = K8sScriptRunner(context.root, config)
    for service in ["mysql", "elasticsearch", "mongodb"]:
        if tutor_config.is_service_activated(config, service):
            wait_for_pod_ready(config, service)
    scripts.initialise(runner, limit_to=limit)


@click.command(help="Create an Open edX user and interactively set their password")
@click.option("--superuser", is_flag=True, help="Make superuser")
@click.option("--staff", is_flag=True, help="Make staff user")
@click.option(
    "-p",
    "--password",
    help="Specify password from the command line. If undefined, you will be prompted to input a password",
)
@click.argument("name")
@click.argument("email")
@click.pass_obj
def createuser(context, superuser, staff, password, name, email):
    config = tutor_config.load(context.root)
    command = scripts.create_user_command(
        superuser, staff, name, email, password=password
    )
    # This needs to be interactive in case the user needs to type a password
    kubectl_exec(config, "lms", command, attach=True)


@click.command(help="Import the demo course")
@click.pass_obj
def importdemocourse(context):
    fmt.echo_info("Importing demo course")
    config = tutor_config.load(context.root)
    runner = K8sScriptRunner(context.root, config)
    scripts.import_demo_course(runner)


@click.command(
    help="Set a theme for a given domain name. To reset to the default theme , use 'default' as the theme name."
)
@click.argument("theme_name")
@click.argument("domain_names", metavar="domain_name", nargs=-1)
@click.pass_obj
def settheme(context, theme_name, domain_names):
    config = tutor_config.load(context.root)
    runner = K8sScriptRunner(context.root, config)
    for domain_name in domain_names:
        scripts.set_theme(theme_name, domain_name, runner)


@click.command(name="exec", help="Execute a command in a pod of the given application")
@click.argument("service")
@click.argument("command")
@click.pass_obj
def exec_command(context, service, command):
    config = tutor_config.load(context.root)
    kubectl_exec(config, service, command, attach=True)


@click.command(help="View output from containers")
@click.option("-c", "--container", help="Print the logs of this specific container")
@click.option("-f", "--follow", is_flag=True, help="Follow log output")
@click.option("--tail", type=int, help="Number of lines to show from each container")
@click.argument("service")
@click.pass_obj
def logs(context, container, follow, tail, service):
    config = tutor_config.load(context.root)

    command = ["logs"]
    selectors = ["app.kubernetes.io/name=" + service] if service else []
    command += resource_selector(config, *selectors)

    if container:
        command += ["-c", container]
    if follow:
        command += ["--follow"]
    if tail is not None:
        command += ["--tail", str(tail)]

    utils.kubectl(*command)


@click.command(help="Upgrade from a previous Open edX named release")
@click.option(
    "--from", "from_version", default="ironwood", type=click.Choice(["ironwood"])
)
@click.pass_obj
def upgrade(context, from_version):
    config = tutor_config.load(context.root)

    if from_version == "ironwood":
        if not config["ACTIVATE_MONGODB"]:
            fmt.echo_info(
                "You are not running MongDB (ACTIVATE_MONGODB=false). It is your "
                "responsibility to upgrade your MongoDb instance to v3.6. There is "
                "nothing left to do."
            )
            return
        message = """Automatic release upgrade is unsupported in Kubernetes. To upgrade from Ironwood, you should upgrade your MongoDb cluster from v3.2 to v3.6. You should run something similar to:

    # Upgrade from v3.2 to v3.4
    tutor k8s stop
    tutor config save --set DOCKER_IMAGE_MONGODB=mongo:3.4.24
    tutor k8s start
    tutor k8s exec mongodb mongo --eval 'db.adminCommand({ setFeatureCompatibilityVersion: "3.4" })'

    # Upgrade from v3.4 to v3.6
    tutor k8s stop
    tutor config save --set DOCKER_IMAGE_MONGODB=mongo:3.6.18
    tutor k8s start
    tutor k8s exec mongodb mongo --eval 'db.adminCommand({ setFeatureCompatibilityVersion: "3.6" })'

    tutor config save --unset DOCKER_IMAGE_MONGODB"""
        fmt.echo_info(message)


class K8sClients:
    _instance = None

    def __init__(self):
        # Loading the kubernetes module here to avoid import overhead
        from kubernetes import client, config  # pylint: disable=import-outside-toplevel

        config.load_kube_config()
        self._batch_api = None
        self._core_api = None
        self._client = client

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def batch_api(self):
        if self._batch_api is None:
            self._batch_api = self._client.BatchV1Api()
        return self._batch_api

    @property
    def core_api(self):
        if self._core_api is None:
            self._core_api = self._client.CoreV1Api()
        return self._core_api


class K8sScriptRunner(scripts.BaseRunner):
    def load_job(self, name):
        jobs = self.render("k8s", "jobs.yml")
        for job in serialize.load_all(jobs):
            if job["metadata"]["name"] == name:
                return job
        raise ValueError("Could not find job '{}'".format(name))

    def active_job_names(self):
        """
        Return a list of active job names
        Docs:
        https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.18/#list-job-v1-batch
        """
        api = K8sClients.instance().batch_api
        return [
            job.metadata.name
            for job in api.list_namespaced_job(self.config["K8S_NAMESPACE"]).items
            if job.status.active
        ]

    def run_job(self, service, command):
        job_name = "{}-job".format(service)
        try:
            job = self.load_job(job_name)
        except ValueError:
            message = (
                "The '{job_name}' kubernetes job does not exist in the list of job "
                "runners. This might be caused by an older plugin. Tutor switched to a"
                " job runner model for running one-time commands, such as database"
                " initialisation. For the record, this is the command that we are "
                "running:\n"
                "\n"
                "    {command}\n"
                "\n"
                "Old-style job running will be deprecated soon. Please inform "
                "your plugin maintainer!"
            ).format(
                job_name=job_name,
                command=command.replace("\n", "\n    "),
            )
            fmt.echo_alert(message)
            wait_for_pod_ready(self.config, service)
            kubectl_exec(self.config, service, command)
            return
        # Create a unique job name to make it deduplicate jobs and make it easier to
        # find later. Logs of older jobs will remain available for some time.
        job_name += "-" + datetime.now().strftime("%Y%m%d%H%M%S")

        # Wait until all other jobs are completed
        while True:
            active_jobs = self.active_job_names()
            if not active_jobs:
                break
            fmt.echo_info(
                "Waiting for active jobs to terminate: {}".format(" ".join(active_jobs))
            )
            sleep(5)

        # Configure job
        job["metadata"]["name"] = job_name
        job["metadata"].setdefault("labels", {})
        job["metadata"]["labels"]["app.kubernetes.io/name"] = job_name
        job["spec"]["template"]["spec"]["containers"][0]["args"] = [
            "sh",
            "-e",
            "-c",
            command,
        ]
        job["spec"]["backoffLimit"] = 1
        job["spec"]["ttlSecondsAfterFinished"] = 3600
        # Save patched job to "jobs.yml" file
        with open(tutor_env.pathjoin(self.root, "k8s", "jobs.yml"), "w") as job_file:
            serialize.dump(job, job_file)
        # We cannot use the k8s API to create the job: configMap and volume names need
        # to be found with the right suffixes.
        utils.kubectl(
            "apply",
            "--kustomize",
            tutor_env.pathjoin(self.root),
            "--selector",
            "app.kubernetes.io/name={}".format(job_name),
        )

        message = (
            "Job {job_name} is running. To view the logs from this job, run:\n\n"
            """    kubectl logs --namespace={namespace} --follow $(kubectl get --namespace={namespace} pods """
            """--selector=job-name={job_name} -o=jsonpath="{{.items[0].metadata.name}}")\n\n"""
            "Waiting for job completion..."
        ).format(job_name=job_name, namespace=self.config["K8S_NAMESPACE"])
        fmt.echo_info(message)

        # Wait for completion
        field_selector = "metadata.name={}".format(job_name)
        while True:
            jobs = K8sClients.instance().batch_api.list_namespaced_job(
                self.config["K8S_NAMESPACE"], field_selector=field_selector
            )
            if not jobs.items:
                continue
            job = jobs.items[0]
            if not job.status.active:
                if job.status.succeeded:
                    fmt.echo_info("Job {} successful.".format(job_name))
                    break
                if job.status.failed:
                    raise exceptions.TutorError(
                        "Job {} failed. View the job logs to debug this issue.".format(
                            job_name
                        )
                    )
            sleep(5)


def kubectl_exec(config, service, command, attach=False):
    selector = "app.kubernetes.io/name={}".format(service)
    pods = K8sClients.instance().core_api.list_namespaced_pod(
        namespace=config["K8S_NAMESPACE"], label_selector=selector
    )
    if not pods.items:
        raise exceptions.TutorError(
            "Could not find an active pod for the {} service".format(service)
        )
    pod_name = pods.items[0].metadata.name

    # Run command
    attach_opts = ["-i", "-t"] if attach else []
    utils.kubectl(
        "exec",
        *attach_opts,
        "--namespace",
        config["K8S_NAMESPACE"],
        pod_name,
        "--",
        "sh",
        "-e",
        "-c",
        command,
    )


def wait_for_pod_ready(config, service):
    fmt.echo_info("Waiting for a {} pod to be ready...".format(service))
    utils.kubectl(
        "wait",
        *resource_selector(config, "app.kubernetes.io/name={}".format(service)),
        "--for=condition=ContainersReady",
        "--timeout=600s",
        "pod",
    )


k8s.add_command(quickstart)
k8s.add_command(start)
k8s.add_command(stop)
k8s.add_command(reboot)
k8s.add_command(delete)
k8s.add_command(init)
k8s.add_command(createuser)
k8s.add_command(importdemocourse)
k8s.add_command(settheme)
k8s.add_command(exec_command)
k8s.add_command(logs)
k8s.add_command(upgrade)
