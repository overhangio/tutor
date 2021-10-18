from datetime import datetime
from time import sleep
from typing import Any, List, Optional, Type

import click

from .. import config as tutor_config
from .. import env as tutor_env
from .. import exceptions
from .. import fmt
from .. import jobs
from .. import serialize
from ..types import Config, get_typed
from .. import utils
from .config import save as config_save_command
from .context import Context


class K8sClients:
    _instance = None

    def __init__(self) -> None:
        # Loading the kubernetes module here to avoid import overhead
        from kubernetes import client, config  # pylint: disable=import-outside-toplevel

        config.load_kube_config()
        self._batch_api = None
        self._core_api = None
        self._client = client

    @classmethod
    def instance(cls: Type["K8sClients"]) -> "K8sClients":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def batch_api(self):  # type: ignore
        if self._batch_api is None:
            self._batch_api = self._client.BatchV1Api()
        return self._batch_api

    @property
    def core_api(self):  # type: ignore
        if self._core_api is None:
            self._core_api = self._client.CoreV1Api()
        return self._core_api


class K8sJobRunner(jobs.BaseJobRunner):
    def load_job(self, name: str) -> Any:
        all_jobs = self.render("k8s", "jobs.yml")
        for job in serialize.load_all(all_jobs):
            job_name = job["metadata"]["name"]
            if not isinstance(job_name, str):
                raise exceptions.TutorError(
                    "Invalid job name: '{}'. Expected str.".format(job_name)
                )
            if job_name == name:
                return job
        raise exceptions.TutorError("Could not find job '{}'".format(name))

    def active_job_names(self) -> List[str]:
        """
        Return a list of active job names
        Docs:
        https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.18/#list-job-v1-batch
        """
        api = K8sClients.instance().batch_api
        return [
            job.metadata.name
            for job in api.list_namespaced_job(k8s_namespace(self.config)).items
            if job.status.active
        ]

    def run_job(self, service: str, command: str) -> int:
        job_name = "{}-job".format(service)
        job = self.load_job(job_name)
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
        # Define k8s entrypoint/args
        shell_command = ["sh", "-e", "-c"]
        if job["spec"]["template"]["spec"]["containers"][0].get("command") == []:
            # In some cases, we need to bypass the container entrypoint.
            # Unfortunately, AFAIK, there is no way to do so in K8s manifests. So we mark
            # some jobs with "command: []". For these jobs, the entrypoint becomes "sh -e -c".
            # We do not do this for every job, because some (most) entrypoints are actually useful.
            job["spec"]["template"]["spec"]["containers"][0]["command"] = shell_command
            container_args = [command]
        else:
            container_args = shell_command + [command]
        job["spec"]["template"]["spec"]["containers"][0]["args"] = container_args
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
        ).format(job_name=job_name, namespace=k8s_namespace(self.config))
        fmt.echo_info(message)

        # Wait for completion
        field_selector = "metadata.name={}".format(job_name)
        while True:
            namespaced_jobs = K8sClients.instance().batch_api.list_namespaced_job(
                k8s_namespace(self.config), field_selector=field_selector
            )
            if not namespaced_jobs.items:
                continue
            job = namespaced_jobs.items[0]
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
        return 0


@click.group(help="Run Open edX on Kubernetes")
def k8s() -> None:
    pass


@click.command(help="Configure and run Open edX from scratch")
@click.option("-I", "--non-interactive", is_flag=True, help="Run non-interactively")
@click.pass_context
def quickstart(context: click.Context, non_interactive: bool) -> None:
    click.echo(fmt.title("Interactive platform configuration"))
    context.invoke(
        config_save_command,
        interactive=(not non_interactive),
        set_vars=[],
        unset_vars=[],
    )
    config = tutor_config.load(context.obj.root)
    if not config["ENABLE_WEB_PROXY"]:
        fmt.echo_alert(
            "Potentially invalid configuration: ENABLE_WEB_PROXY=false\n"
            "This setting might have been defined because you previously set WEB_PROXY=true. This is no longer"
            " necessary in order to get Tutor to work on Kubernetes. In Tutor v11+ a Caddy-based load balancer is"
            " provided out of the box to handle SSL/TLS certificate generation at runtime. If you disable this"
            " service, you will have to configure an Ingress resource and a certificate manager yourself to redirect"
            " traffic to the caddy service. See the Kubernetes section in the Tutor documentation for more"
            " information."
        )
    click.echo(fmt.title("Updating the current environment"))
    tutor_env.save(context.obj.root, config)
    click.echo(fmt.title("Starting the platform"))
    context.invoke(start)
    click.echo(fmt.title("Database creation and migrations"))
    context.invoke(init, limit=None)
    fmt.echo_info(
        """Your Open edX platform is ready and can be accessed at the following urls:

    {http}://{lms_host}
    {http}://{cms_host}
    """.format(
            http="https" if config["ENABLE_HTTPS"] else "http",
            lms_host=config["LMS_HOST"],
            cms_host=config["CMS_HOST"],
        )
    )


@click.command(
    short_help="Run all configured Open edX resources",
    help=(
        "Run all configured Open edX resources. You may limit this command to "
        "some resources by passing name arguments."
    ),
)
@click.argument("names", metavar="name", nargs=-1)
@click.pass_obj
def start(context: Context, names: List[str]) -> None:
    config = tutor_config.load(context.root)
    # Create namespace, if necessary
    # Note that this step should not be run for some users, in particular those
    # who do not have permission to edit the namespace.
    try:
        utils.kubectl("get", "namespaces", k8s_namespace(config))
        fmt.echo_info("Namespace already exists: skipping creation.")
    except exceptions.TutorError:
        fmt.echo_info("Namespace does not exist: now creating it...")
        utils.kubectl(
            "apply",
            "--kustomize",
            tutor_env.pathjoin(context.root),
            "--wait",
            "--selector",
            "app.kubernetes.io/component=namespace",
        )

    names = names or ["all"]
    for name in names:
        if name == "all":
            # Create volumes
            utils.kubectl(
                "apply",
                "--kustomize",
                tutor_env.pathjoin(context.root),
                "--wait",
                "--selector",
                "app.kubernetes.io/component=volume",
            )
            # Create everything else except jobs
            utils.kubectl(
                "apply",
                "--kustomize",
                tutor_env.pathjoin(context.root),
                "--selector",
                "app.kubernetes.io/component notin (job,volume,namespace)",
            )
        else:
            utils.kubectl(
                "apply",
                "--kustomize",
                tutor_env.pathjoin(context.root),
                "--selector",
                "app.kubernetes.io/name={}".format(name),
            )


@click.command(
    short_help="Stop a running platform",
    help=(
        "Stop a running platform by deleting all resources, except for volumes. "
        "You may limit this command to some resources by passing name arguments."
    ),
)
@click.argument("names", metavar="name", nargs=-1)
@click.pass_obj
def stop(context: Context, names: List[str]) -> None:
    config = tutor_config.load(context.root)
    names = names or ["all"]
    resource_types = "deployments,services,configmaps,jobs"
    not_lb_selector = "app.kubernetes.io/component!=loadbalancer"
    for name in names:
        if name == "all":
            utils.kubectl(
                "delete",
                *resource_selector(config, not_lb_selector),
                resource_types,
            )
        else:
            utils.kubectl(
                "delete",
                *resource_selector(
                    config,
                    not_lb_selector,
                    "app.kubernetes.io/name={}".format(name),
                ),
                resource_types,
            )


@click.command(help="Reboot an existing platform")
@click.pass_context
def reboot(context: click.Context) -> None:
    context.invoke(stop)
    context.invoke(start)


@click.command(help="Completely delete an existing platform")
@click.option("-y", "--yes", is_flag=True, help="Do not ask for confirmation")
@click.pass_obj
def delete(context: Context, yes: bool) -> None:
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
def init(context: Context, limit: Optional[str]) -> None:
    config = tutor_config.load(context.root)
    runner = K8sJobRunner(context.root, config)
    wait_for_pod_ready(config, "caddy")
    for name in ["elasticsearch", "mysql", "mongodb"]:
        if tutor_config.is_service_activated(config, name):
            wait_for_pod_ready(config, name)
    jobs.initialise(runner, limit_to=limit)


@click.command(help="Scale the number of replicas of a given deployment")
@click.argument("deployment")
@click.argument("replicas", type=int)
@click.pass_obj
def scale(context: Context, deployment: str, replicas: int) -> None:
    config = tutor_config.load(context.root)
    utils.kubectl(
        "scale",
        # Note that we don't use the full resource selector because selectors
        # are not compatible with the deployment/<name> argument.
        *resource_namespace_selector(
            config,
        ),
        "--replicas={}".format(replicas),
        "deployment/{}".format(deployment),
    )


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
def createuser(
    context: Context, superuser: str, staff: bool, password: str, name: str, email: str
) -> None:
    config = tutor_config.load(context.root)
    command = jobs.create_user_command(superuser, staff, name, email, password=password)
    # This needs to be interactive in case the user needs to type a password
    kubectl_exec(config, "lms", command, attach=True)


@click.command(help="Import the demo course")
@click.pass_obj
def importdemocourse(context: Context) -> None:
    fmt.echo_info("Importing demo course")
    config = tutor_config.load(context.root)
    runner = K8sJobRunner(context.root, config)
    jobs.import_demo_course(runner)


@click.command(
    help="Assign a theme to the LMS and the CMS. To reset to the default theme , use 'default' as the theme name."
)
@click.option(
    "-d",
    "--domain",
    "domains",
    multiple=True,
    help=(
        "Limit the theme to these domain names. By default, the theme is "
        "applied to the LMS and the CMS, both in development and production mode"
    ),
)
@click.argument("theme_name")
@click.pass_obj
def settheme(context: Context, domains: List[str], theme_name: str) -> None:
    config = tutor_config.load(context.root)
    runner = K8sJobRunner(context.root, config)
    domains = domains or jobs.get_all_openedx_domains(config)
    jobs.set_theme(theme_name, domains, runner)


@click.command(name="exec", help="Execute a command in a pod of the given application")
@click.argument("service")
@click.argument("command")
@click.pass_obj
def exec_command(context: Context, service: str, command: str) -> None:
    config = tutor_config.load(context.root)
    kubectl_exec(config, service, command, attach=True)


@click.command(help="View output from containers")
@click.option("-c", "--container", help="Print the logs of this specific container")
@click.option("-f", "--follow", is_flag=True, help="Follow log output")
@click.option("--tail", type=int, help="Number of lines to show from each container")
@click.argument("service")
@click.pass_obj
def logs(
    context: Context, container: str, follow: bool, tail: bool, service: str
) -> None:
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


@click.command(help="Wait for a pod to become ready")
@click.argument("name")
@click.pass_obj
def wait(context: Context, name: str) -> None:
    config = tutor_config.load(context.root)
    wait_for_pod_ready(config, name)


@click.command(help="Upgrade from a previous Open edX named release")
@click.option(
    "--from",
    "from_version",
    default="koa",
    type=click.Choice(["ironwood", "juniper", "koa", "lilac"]),
)
@click.pass_obj
def upgrade(context: Context, from_version: str) -> None:
    config = tutor_config.load(context.root)

    running_version = from_version
    if running_version == "ironwood":
        upgrade_from_ironwood(config)
        running_version = "juniper"

    if running_version == "juniper":
        upgrade_from_juniper(config)
        running_version = "koa"

    if running_version == "koa":
        upgrade_from_koa(config)
        running_version = "lilac"

    if running_version == "lilac":
        # Nothing to do here
        running_version = "maple"


def upgrade_from_ironwood(config: Config) -> None:
    if not config["RUN_MONGODB"]:
        fmt.echo_info(
            "You are not running MongDB (RUN_MONGODB=false). It is your "
            "responsibility to upgrade your MongoDb instance to v3.6. There is "
            "nothing left to do to upgrade from Ironwood."
        )
        return
    message = """Automatic release upgrade is unsupported in Kubernetes. To upgrade from Ironwood, you should upgrade
your MongoDb cluster from v3.2 to v3.6. You should run something similar to:

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


def upgrade_from_juniper(config: Config) -> None:
    if not config["RUN_MYSQL"]:
        fmt.echo_info(
            "You are not running MySQL (RUN_MYSQL=false). It is your "
            "responsibility to upgrade your MySQL instance to v5.7. There is "
            "nothing left to do to upgrade from Juniper."
        )
        return

    message = """Automatic release upgrade is unsupported in Kubernetes. To upgrade from Juniper, you should upgrade
your MySQL database from v5.6 to v5.7. You should run something similar to:

    tutor k8s start
    tutor k8s exec mysql bash -e -c "mysql_upgrade \
        -u $(tutor config printvalue MYSQL_ROOT_USERNAME) \
        --password='$(tutor config printvalue MYSQL_ROOT_PASSWORD)'
"""
    fmt.echo_info(message)


def upgrade_from_koa(config: Config) -> None:
    if not config["RUN_MONGODB"]:
        fmt.echo_info(
            "You are not running MongDB (RUN_MONGODB=false). It is your "
            "responsibility to upgrade your MongoDb instance to v4.0. There is "
            "nothing left to do to upgrade to Lilac from Koa."
        )
        return
    message = """Automatic release upgrade is unsupported in Kubernetes. To upgrade from Koa to Lilac, you should upgrade
your MongoDb cluster from v3.6 to v4.0. You should run something similar to:

    tutor k8s stop
    tutor config save --set DOCKER_IMAGE_MONGODB=mongo:4.0.25
    tutor k8s start
    tutor k8s exec mongodb mongo --eval 'db.adminCommand({ setFeatureCompatibilityVersion: "4.0" })'
    tutor config save --unset DOCKER_IMAGE_MONGODB
    """
    fmt.echo_info(message)


def kubectl_exec(
    config: Config, service: str, command: str, attach: bool = False
) -> int:
    selector = "app.kubernetes.io/name={}".format(service)
    pods = K8sClients.instance().core_api.list_namespaced_pod(
        namespace=k8s_namespace(config), label_selector=selector
    )
    if not pods.items:
        raise exceptions.TutorError(
            "Could not find an active pod for the {} service".format(service)
        )
    pod_name = pods.items[0].metadata.name

    # Run command
    attach_opts = ["-i", "-t"] if attach else []
    return utils.kubectl(
        "exec",
        *attach_opts,
        "--namespace",
        k8s_namespace(config),
        pod_name,
        "--",
        "sh",
        "-e",
        "-c",
        command,
    )


def wait_for_pod_ready(config: Config, service: str) -> None:
    fmt.echo_info("Waiting for a {} pod to be ready...".format(service))
    utils.kubectl(
        "wait",
        *resource_selector(config, "app.kubernetes.io/name={}".format(service)),
        "--for=condition=ContainersReady",
        "--timeout=600s",
        "pod",
    )


def resource_selector(config: Config, *selectors: str) -> List[str]:
    """
    Convenient utility to filter the resources that belong to this project.
    """
    selector = ",".join(
        ["app.kubernetes.io/instance=openedx-" + get_typed(config, "ID", str)]
        + list(selectors)
    )
    return resource_namespace_selector(config) + ["--selector=" + selector]


def resource_namespace_selector(config: Config) -> List[str]:
    """
    Convenient utility to filter the resources that belong to this project namespace.
    """
    return ["--namespace", k8s_namespace(config)]


def k8s_namespace(config: Config) -> str:
    return get_typed(config, "K8S_NAMESPACE", str)


k8s.add_command(quickstart)
k8s.add_command(start)
k8s.add_command(stop)
k8s.add_command(reboot)
k8s.add_command(delete)
k8s.add_command(init)
k8s.add_command(scale)
k8s.add_command(createuser)
k8s.add_command(importdemocourse)
k8s.add_command(settheme)
k8s.add_command(exec_command)
k8s.add_command(logs)
k8s.add_command(wait)
k8s.add_command(upgrade)
