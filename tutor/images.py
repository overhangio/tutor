from tutor import fmt, hooks, utils


def build(path: str, tag: str, *args: str) -> None:
    fmt.echo_info(f"Building image {tag}")
    build_command = ["build", f"--tag={tag}", *args, path]
    # `buildx` can be removed once Tutor requires Docker v23+. At that point, BuildKit will be
    # enabled by default for all Docker users.
    build_command.insert(0, "buildx")
    command = hooks.Filters.DOCKER_BUILD_COMMAND.apply(build_command)
    utils.docker(*command)


def pull(tag: str) -> None:
    fmt.echo_info(f"Pulling image {tag}")
    utils.docker("pull", tag)


def push(tag: str) -> None:
    fmt.echo_info(f"Pushing image {tag}")
    utils.docker("push", tag)
