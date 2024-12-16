import click

from tutor import config as tutor_config
from tutor import env as tutor_env
from tutor import fmt, hooks
from tutor.commands import k8s
from tutor.commands.context import Context
from tutor.types import Config

from . import common as common_upgrade


def upgrade_from(context: click.Context, from_release: str) -> None:
    config = tutor_config.load(context.obj.root)

    running_release = from_release
    if running_release == "ironwood":
        upgrade_from_ironwood(config)
        running_release = "juniper"

    if running_release == "juniper":
        upgrade_from_juniper(config)
        running_release = "koa"

    if running_release == "koa":
        upgrade_from_koa(config)
        running_release = "lilac"

    if running_release == "lilac":
        upgrade_from_lilac(config)
        running_release = "maple"

    if running_release == "maple":
        upgrade_from_maple(context.obj, config)
        running_release = "nutmeg"

    if running_release == "nutmeg":
        common_upgrade.upgrade_from_nutmeg(context, config)
        running_release = "olive"

    if running_release == "olive":
        upgrade_from_olive(context, config)
        running_release = "palm"

    if running_release == "palm":
        running_release = "quince"

    if running_release == "quince":
        upgrade_from_quince(config)
        running_release = "redwood"

    if running_release == "redwood":
        common_upgrade.upgrade_from_redwood(context, config)
        running_release = "sumac"


def upgrade_from_ironwood(config: Config) -> None:
    upgrade_mongodb(config, "3.4.24", "3.4")
    upgrade_mongodb(config, "3.6.18", "3.6")


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
    upgrade_mongodb(config, "4.0.25", "4.0")


def upgrade_from_lilac(config: Config) -> None:
    common_upgrade.upgrade_from_lilac(config)
    fmt.echo_info(
        "All Kubernetes services and deployments need to be deleted during "
        "upgrade from Lilac to Maple"
    )
    k8s.delete_resources(config, resources=["deployments", "services"])


def upgrade_from_maple(context: Context, config: Config) -> None:
    fmt.echo_info("Upgrading from Maple")
    # The environment needs to be updated because the backpopulate/backfill commands are from Nutmeg
    tutor_env.save(context.root, config)

    if config["RUN_MYSQL"]:
        # Start mysql
        k8s.kubectl_apply(
            context.root,
            "--selector",
            "app.kubernetes.io/name=mysql",
        )
        k8s.wait_for_deployment_ready(config, "mysql")

    # lms upgrade
    k8s.kubectl_apply(
        context.root,
        "--selector",
        "app.kubernetes.io/name=lms",
    )
    k8s.wait_for_deployment_ready(config, "lms")

    # Command backpopulate_user_tours
    k8s.kubectl_exec(
        config, "lms", ["sh", "-e", "-c", "./manage.py lms migrate user_tours"]
    )
    k8s.kubectl_exec(
        config, "lms", ["sh", "-e", "-c", "./manage.py lms backpopulate_user_tours"]
    )

    # cms upgrade
    k8s.kubectl_apply(
        context.root,
        "--selector",
        "app.kubernetes.io/name=cms",
    )
    k8s.wait_for_deployment_ready(config, "cms")

    # Command backfill_course_tabs
    k8s.kubectl_exec(
        config, "cms", ["sh", "-e", "-c", "./manage.py cms migrate contentstore"]
    )
    k8s.kubectl_exec(
        config,
        "cms",
        ["sh", "-e", "-c", "./manage.py cms migrate split_modulestore_django"],
    )
    k8s.kubectl_exec(
        config, "cms", ["sh", "-e", "-c", "./manage.py cms backfill_course_tabs"]
    )

    # Command simulate_publish
    k8s.kubectl_exec(
        config, "cms", ["sh", "-e", "-c", "./manage.py cms migrate course_overviews"]
    )
    k8s.kubectl_exec(
        config, "cms", ["sh", "-e", "-c", "./manage.py cms simulate_publish"]
    )


def upgrade_from_olive(context: click.Context, config: Config) -> None:
    # Note that we need to exec because the ora2 folder is not bind-mounted in the job
    # services.
    k8s.kubectl_apply(
        context.obj.root,
        "--selector",
        "app.kubernetes.io/name=lms",
    )
    k8s.wait_for_deployment_ready(config, "lms")
    k8s.kubectl_exec(
        config,
        "lms",
        ["sh", "-e", "-c", common_upgrade.PALM_RENAME_ORA2_FOLDER_COMMAND],
    )
    upgrade_mongodb(config, "4.2.17", "4.2")
    upgrade_mongodb(config, "4.4.22", "4.4")

    intermediate_mysql_docker_image = common_upgrade.get_intermediate_mysql_upgrade(
        config
    )
    if not intermediate_mysql_docker_image:
        return

    click.echo(fmt.title(f"Upgrading MySQL to {intermediate_mysql_docker_image}"))

    # We start up a mysql-8.1 container to build data dictionary to preserve
    # the upgrade order of 5.7 -> 8.1 -> 8.4
    # Use the mysql-8.1 context so that we can clear these filters later on
    with hooks.Contexts.app("mysql-8.1").enter():
        hooks.Filters.ENV_PATCHES.add_items(
            [
                (
                    "k8s-deployments",
                    """
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql-81
  labels:
    app.kubernetes.io/name: mysql-81
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: mysql-81
  strategy:
    type: Recreate
  template:
    metadata:
      labels:
        app.kubernetes.io/name: mysql-81
    spec:
      securityContext:
        runAsUser: 999
        runAsGroup: 999
        fsGroup: 999
        fsGroupChangePolicy: "OnRootMismatch"
      containers:
        - name: mysql-81
          image: docker.io/mysql:8.1.0
          args:
            - "mysqld"
            - "--character-set-server=utf8mb3"
            - "--collation-server=utf8mb3_general_ci"
            - "--binlog-expire-logs-seconds=259200"
          env:
            - name: MYSQL_ROOT_PASSWORD
              value: "{{ MYSQL_ROOT_PASSWORD }}"
          ports:
            - containerPort: 3306
          volumeMounts:
            - mountPath: /var/lib/mysql
              name: data
          securityContext:
            allowPrivilegeEscalation: false
      volumes:
        - name: data
          persistentVolumeClaim:
            claimName: mysql
    """,
                ),
                (
                    "k8s-jobs",
                    """
---
apiVersion: batch/v1
kind: Job
metadata:
  name: mysql-81-job
  labels:
    app.kubernetes.io/component: job
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: mysql-81
        image: docker.io/mysql:8.1.0
        """,
                ),
            ]
        )
        hooks.Filters.ENV_PATCHES.add_item(
            (
                "k8s-services",
                """
---
apiVersion: v1
kind: Service
metadata:
  name: mysql-81
  labels:
    app.kubernetes.io/name: mysql-81
spec:
  type: ClusterIP
  ports:
    - port: 3306
      protocol: TCP
  selector:
    app.kubernetes.io/name: mysql-81
        """,
            )
        )
        hooks.Filters.CONFIG_DEFAULTS.add_item(("MYSQL_HOST", "mysql-81"))

        hooks.Filters.CLI_DO_INIT_TASKS.add_item(
            ("mysql-81", tutor_env.read_core_template_file("jobs", "init", "mysql.sh"))
        )

    tutor_env.save(context.obj.root, config)

    # Run the init command to make sure MySQL is ready for connections
    k8s.kubectl_apply(
        context.obj.root,
        "--selector",
        "app.kubernetes.io/name=mysql-81",
    )
    k8s.wait_for_deployment_ready(config, "mysql-81")
    context.invoke(k8s.do.commands["init"], limit="mysql-8.1")
    context.invoke(k8s.stop, names=["mysql-81"])

    # Clear the filters added for mysql-8.1 as we don't need them anymore
    hooks.clear_all(context="app:mysql-8.1")

    # Save environment and run init for mysql 8.4 to make sure MySQL is ready
    tutor_env.save(context.obj.root, config)
    k8s.kubectl_apply(
        context.obj.root,
        "--selector",
        "app.kubernetes.io/name=mysql",
    )
    k8s.wait_for_deployment_ready(config, "mysql")
    context.invoke(k8s.do.commands["init"], limit="mysql")
    context.invoke(k8s.stop, names=["mysql"])


def upgrade_from_quince(config: Config) -> None:
    click.echo(fmt.title("Upgrading from Quince"))
    upgrade_mongodb(config, "5.0.26", "5.0")
    upgrade_mongodb(config, "6.0.14", "6.0")
    upgrade_mongodb(config, "7.0.7", "7.0")


def upgrade_mongodb(
    config: Config, to_docker_version: str, to_compatibility_version: str
) -> None:
    if not config["RUN_MONGODB"]:
        fmt.echo_info(
            "You are not running MongoDB (RUN_MONGODB=false). It is your "
            "responsibility to upgrade your MongoDb instance to {to_docker_version}."
        )
        return
    mongo_version, admin_command = common_upgrade.get_mongo_upgrade_parameters(
        to_docker_version, to_compatibility_version
    )
    mongo_binary = "mongosh" if mongo_version >= 6 else "mongo"

    message = f"""Automatic release upgrade is unsupported in Kubernetes. You should manually upgrade
your MongoDb cluster to {to_docker_version} by running something similar to:

    tutor k8s stop
    tutor config save --set DOCKER_IMAGE_MONGODB=mongo:{to_docker_version}
    tutor k8s start
    tutor k8s exec mongodb {mongo_binary} --eval 'db.adminCommand({admin_command})'
    tutor config save --unset DOCKER_IMAGE_MONGODB
    """
    fmt.echo_info(message)
