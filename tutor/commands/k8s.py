import os
from datetime import datetime
from time import sleep
from typing import Any, Iterable, List, Optional, Type

import click

from tutor import config as tutor_config
from tutor import env as tutor_env
from tutor import exceptions, fmt, hooks
from tutor import interactive as interactive_config
from tutor import serialize, utils
from tutor.commands import jobs
from tutor.commands.config import save as config_save_command
from tutor.commands.context import BaseTaskContext
from tutor.commands.upgrade import OPENEDX_RELEASE_NAMES
from tutor.commands.upgrade.k8s import upgrade_from
from tutor.tasks import BaseTaskRunner
from tutor.types import Config, get_typed


class K8sClients:
    _instance = None

    def __init__(self) -> None:
        # Loading the kubernetes module here to avoid import overhead
        # pylint: disable=import-outside-toplevel
        from kubernetes import client, config

        if os.path.exists(
            os.path.expanduser(config.kube_config.KUBE_CONFIG_DEFAULT_LOCATION)
        ):
            # found the kubeconfig file, let's load it!
            config.load_kube_config()
        elif (
            config.incluster_config.SERVICE_HOST_ENV_NAME in os.environ
            and config.incluster_config.SERVICE_PORT_ENV_NAME in os.environ
        ):
            # We are running inside a cluster, let's load the in-cluster configuration.
            config.load_incluster_config()
        else:
            raise exceptions.TutorError(
                f"there is no Kubernetes configuration file located in {config.kube_config.KUBE_CONFIG_DEFAULT_LOCATION}, and the service environment variables {config.incluster_config.SERVICE_HOST_ENV_NAME} and {config.incluster_config.SERVICE_PORT_ENV_NAME} have not been defined. To connect to a cluster, please configure your host appropriately."
            )

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


class K8sTaskRunner(BaseTaskRunner):
    """
    Run tasks (bash commands) in Kubernetes-managed services.

    Note: a single Tutor "task" correspond to a Kubernetes "job":
    https://kubernetes.io/docs/concepts/workloads/controllers/job/
    A Tutor "job" is composed of multiple Tutor tasks run in different services.

    In Kubernetes, each task that is expected to run in a "myservice" container will
    trigger the "myservice-job" Kubernetes job. This job definition must be present in
    the "k8s/jobs.yml" template.
    """

    def run_task(self, service: str, command: str) -> int:
        canonical_job_name = f"{service}-job"
        all_jobs = list(self._load_jobs())
        job = self._find_job(canonical_job_name, all_jobs)
        # Create a unique job name to make it deduplicate jobs and make it easier to
        # find later. Logs of older jobs will remain available for some time.
        job_name = canonical_job_name + "-" + datetime.now().strftime("%Y%m%d%H%M%S")

        # Wait until all other jobs are completed
        while True:
            active_jobs = self.active_job_names()
            if not active_jobs:
                break
            fmt.echo_info(
                f"Waiting for active jobs to terminate: {' '.join(active_jobs)}"
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

        with open(
            tutor_env.pathjoin(self.root, "k8s", "jobs.yml"), "w", encoding="utf-8"
        ) as job_file:
            serialize.dump_all(all_jobs, job_file)

        # We cannot use the k8s API to create the job: configMap and volume names need
        # to be found with the right suffixes.
        kubectl_apply(
            self.root,
            "--selector",
            f"app.kubernetes.io/name={job_name}",
        )

        message = (
            "Job {job_name} is running. To view the logs from this job, run:\n\n"
            """    kubectl logs --namespace={namespace} --follow $(kubectl get --namespace={namespace} pods """
            """--selector=job-name={job_name} -o=jsonpath="{{.items[0].metadata.name}}")\n\n"""
            "Waiting for job completion..."
        ).format(job_name=job_name, namespace=k8s_namespace(self.config))
        fmt.echo_info(message)

        # Wait for completion
        field_selector = f"metadata.name={job_name}"
        while True:
            namespaced_jobs = K8sClients.instance().batch_api.list_namespaced_job(
                k8s_namespace(self.config), field_selector=field_selector
            )
            if not namespaced_jobs.items:
                continue
            job = namespaced_jobs.items[0]
            if not job.status.active:
                if job.status.succeeded:
                    fmt.echo_info(f"Job {job_name} successful.")
                    break
                if job.status.failed:
                    raise exceptions.TutorError(
                        f"Job {job_name} failed. View the job logs to debug this issue."
                    )
            sleep(5)
        return 0

    def load_job(self, name: str) -> Any:
        """
        Find a given job definition in the rendered k8s/jobs.yml template.
        """
        return self._find_job(name, self._load_jobs())

    def _find_job(self, name: str, all_jobs: Iterable[Any]) -> Any:
        """
        Find the matching job definition in the in the list of jobs provided.

        Returns the found job's manifest.
        """
        for job in all_jobs:
            job_name = job["metadata"]["name"]
            if not isinstance(job_name, str):
                raise exceptions.TutorError(
                    f"Invalid job name: '{job_name}'. Expected str."
                )
            if job_name == name:
                return job
        raise exceptions.TutorError(f"Could not find job '{name}'")

    def _load_jobs(self) -> Iterable[Any]:
        manifests = self.render("k8s", "jobs.yml")
        for manifest in serialize.load_all(manifests):
            if manifest["kind"] == "Job":
                yield manifest

    def active_job_names(self) -> List[str]:
        """
        Return a list of active job names
        Docs:
        https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.18/#list-job-v1-batch

        This is necessary to make sure that we don't run the same job multiple times at
        the same time.
        """
        api = K8sClients.instance().batch_api
        return [
            job.metadata.name
            for job in api.list_namespaced_job(k8s_namespace(self.config)).items
            if job.status.active
        ]


class K8sContext(BaseTaskContext):
    def job_runner(self, config: Config) -> K8sTaskRunner:
        return K8sTaskRunner(self.root, config)


@click.group(help="Run Open edX on Kubernetes")
@click.pass_context
def k8s(context: click.Context) -> None:
    context.obj = K8sContext(context.obj.root)


@click.command(help="Configure and run Open edX from scratch")
@click.option("-I", "--non-interactive", is_flag=True, help="Run non-interactively")
@click.pass_context
def launch(context: click.Context, non_interactive: bool) -> None:
    run_upgrade_from_release = tutor_env.should_upgrade_from_release(context.obj.root)
    if run_upgrade_from_release is not None:
        click.echo(fmt.title("Upgrading from an older release"))
        context.invoke(
            upgrade,
            from_release=tutor_env.get_env_release(context.obj.root),
        )

    click.echo(fmt.title("Interactive platform configuration"))
    config = tutor_config.load_minimal(context.obj.root)
    if not non_interactive:
        interactive_config.ask_questions(config, run_for_prod=True)
    tutor_config.save_config_file(context.obj.root, config)
    config = tutor_config.load_full(context.obj.root)
    tutor_env.save(context.obj.root, config)

    if run_upgrade_from_release and not non_interactive:
        question = f"""Your platform is being upgraded from {run_upgrade_from_release.capitalize()}.

If you run custom Docker images, you must rebuild and push them to your private repository now by running the following
commands in a different shell:

    tutor images build all # add your custom images here
    tutor images push all

Press enter when you are ready to continue"""
        click.confirm(
            fmt.question(question), default=True, abort=True, prompt_suffix=" "
        )

    click.echo(fmt.title("Starting the platform"))
    context.invoke(start)

    click.echo(fmt.title("Database creation and migrations"))
    context.invoke(init, limit=None)

    config = tutor_config.load(context.obj.root)
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
def start(context: K8sContext, names: List[str]) -> None:
    config = tutor_config.load(context.root)
    # Create namespace, if necessary
    # Note that this step should not be run for some users, in particular those
    # who do not have permission to edit the namespace.
    try:
        utils.kubectl("get", "namespaces", k8s_namespace(config))
        fmt.echo_info("Namespace already exists: skipping creation.")
    except exceptions.TutorError:
        fmt.echo_info("Namespace does not exist: now creating it...")
        kubectl_apply(
            context.root,
            "--wait",
            "--selector",
            "app.kubernetes.io/component=namespace",
        )

    names = names or ["all"]
    for name in names:
        if name == "all":
            # Create everything except jobs
            kubectl_apply(
                context.root,
                "--selector",
                "app.kubernetes.io/component notin (job,namespace)",
            )
        else:
            kubectl_apply(
                context.root,
                "--selector",
                f"app.kubernetes.io/name={name}",
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
def stop(context: K8sContext, names: List[str]) -> None:
    config = tutor_config.load(context.root)
    names = names or ["all"]
    for name in names:
        if name == "all":
            delete_resources(config)
        else:
            delete_resources(config, name=name)


def delete_resources(
    config: Config, resources: Optional[List[str]] = None, name: Optional[str] = None
) -> None:
    """
    Delete resources by type and name.

    The load balancer is never deleted.
    """
    resources = resources or ["deployments", "services", "configmaps", "jobs"]
    not_lb_selector = "app.kubernetes.io/component!=loadbalancer"
    name_selector = [f"app.kubernetes.io/name={name}"] if name else []
    utils.kubectl(
        "delete",
        *resource_selector(config, not_lb_selector, *name_selector),
        ",".join(resources),
    )


@click.command(help="Reboot an existing platform")
@click.pass_context
def reboot(context: click.Context) -> None:
    context.invoke(stop)
    context.invoke(start)


@click.command(help="Completely delete an existing platform")
@click.option("-y", "--yes", is_flag=True, help="Do not ask for confirmation")
@click.pass_obj
def delete(context: K8sContext, yes: bool) -> None:
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


@jobs.do_group
@click.pass_obj
def do(context: K8sContext) -> None:
    """
    Run a custom job in the right container(s).

    We make sure that some essential containers (databases, proxy) are up before we
    launch the jobs.
    """

    @hooks.Actions.DO_JOB.add()
    def _start_base_deployments(_job_name: str, *_args: Any, **_kwargs: Any) -> None:
        """
        We add this logic to an action callback because we do not want to trigger it
        whenever we run `tutor k8s do <job> --help`.
        """
        config = tutor_config.load(context.root)
        wait_for_deployment_ready(config, "caddy")
        for name in ["elasticsearch", "mysql", "mongodb"]:
            if tutor_config.is_service_activated(config, name):
                wait_for_deployment_ready(config, name)


@click.command(help="Initialise all applications")
@click.option("-l", "--limit", help="Limit initialisation to this service or plugin")
@click.pass_context
def init(context: click.Context, limit: Optional[str]) -> None:
    context.invoke(do.commands["init"], limit=limit)


@click.command(help="Scale the number of replicas of a given deployment")
@click.argument("deployment")
@click.argument("replicas", type=int)
@click.pass_obj
def scale(context: K8sContext, deployment: str, replicas: int) -> None:
    config = tutor_config.load(context.root)
    utils.kubectl(
        "scale",
        # Note that we don't use the full resource selector because selectors
        # are not compatible with the deployment/<name> argument.
        *resource_namespace_selector(
            config,
        ),
        f"--replicas={replicas}",
        f"deployment/{deployment}",
    )


@click.command(
    name="exec",
    help="Execute a command in a pod of the given application",
    context_settings={"ignore_unknown_options": True},
)
@click.argument("service")
@click.argument("args", nargs=-1, required=True)
@click.pass_obj
def exec_command(context: K8sContext, service: str, args: List[str]) -> None:
    config = tutor_config.load(context.root)
    kubectl_exec(config, service, args)


@click.command(help="View output from containers")
@click.option("-c", "--container", help="Print the logs of this specific container")
@click.option("-f", "--follow", is_flag=True, help="Follow log output")
@click.option("--tail", type=int, help="Number of lines to show from each container")
@click.argument("service")
@click.pass_obj
def logs(
    context: K8sContext, container: str, follow: bool, tail: bool, service: str
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
def wait(context: K8sContext, name: str) -> None:
    config = tutor_config.load(context.root)
    wait_for_deployment_ready(config, name)


@click.command(
    short_help="Perform release-specific upgrade tasks",
    help="Perform release-specific upgrade tasks. To perform a full upgrade remember to run `launch`.",
)
@click.option(
    "--from",
    "from_release",
    type=click.Choice(OPENEDX_RELEASE_NAMES),
)
@click.pass_context
def upgrade(context: click.Context, from_release: Optional[str]) -> None:
    if from_release is None:
        from_release = tutor_env.get_env_release(context.obj.root)
    if from_release is None:
        fmt.echo_info("Your environment is already up-to-date")
    else:
        fmt.echo_alert(
            "This command only performs a partial upgrade of your Open edX platform. "
            "To perform a full upgrade, you should run `tutor k8s launch`."
        )
        upgrade_from(context, from_release)
    # We update the environment to update the version
    context.invoke(config_save_command)


@click.command(
    short_help="Direct interface to `kubectl apply`.",
    help=(
        "Direct interface to `kubnectl-apply`. This is a wrapper around `kubectl apply`. A;; options and"
        " arguments passed to this command will be forwarded as-is to `kubectl apply`."
    ),
    context_settings={"ignore_unknown_options": True},
    name="apply",
)
@click.argument("args", nargs=-1)
@click.pass_obj
def apply_command(context: K8sContext, args: List[str]) -> None:
    kubectl_apply(context.root, *args)


def kubectl_apply(root: str, *args: str) -> None:
    utils.kubectl("apply", "--kustomize", tutor_env.pathjoin(root), *args)


@click.command(help="Print status information for all k8s resources")
@click.pass_obj
def status(context: K8sContext) -> int:
    config = tutor_config.load(context.root)
    return utils.kubectl("get", "all", *resource_namespace_selector(config))


def kubectl_exec(config: Config, service: str, command: List[str]) -> int:
    selector = f"app.kubernetes.io/name={service}"
    pods = K8sClients.instance().core_api.list_namespaced_pod(
        namespace=k8s_namespace(config), label_selector=selector
    )
    if not pods.items:
        raise exceptions.TutorError(
            f"Could not find an active pod for the {service} service"
        )
    pod_name = pods.items[0].metadata.name

    # Run command
    return utils.kubectl(
        "exec",
        "--stdin",
        "--tty",
        "--namespace",
        k8s_namespace(config),
        pod_name,
        "--",
        *command,
    )


def wait_for_deployment_ready(config: Config, service: str) -> None:
    fmt.echo_info(f"Waiting for a {service} deployment to be ready...")
    utils.kubectl(
        "wait",
        *resource_selector(config, f"app.kubernetes.io/name={service}"),
        "--for=condition=Available=True",
        "--timeout=600s",
        "deployment",
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


k8s.add_command(launch)
k8s.add_command(start)
k8s.add_command(stop)
k8s.add_command(reboot)
k8s.add_command(delete)
k8s.add_command(init)
k8s.add_command(scale)
k8s.add_command(exec_command)
k8s.add_command(logs)
k8s.add_command(wait)
k8s.add_command(upgrade)
k8s.add_command(apply_command)
k8s.add_command(status)


@hooks.Actions.PLUGINS_LOADED.add()
def _add_k8s_do_commands() -> None:
    jobs.add_job_commands(do)
    k8s.add_command(do)
