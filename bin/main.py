#!/usr/bin/env python3
from tutor import hooks
from tutor.commands.cli import main
from tutor.plugins.v0 import OfficialPlugin


@hooks.Actions.CORE_READY.add()
def _discover_official_plugins() -> None:
    # Manually discover plugins: that's because entrypoint plugins are not properly
    # detected within the binary bundle.
    with hooks.Contexts.PLUGINS.enter():
        OfficialPlugin.discover_all()


if __name__ == "__main__":
    # Call the regular main function, which will not detect any entrypoint plugin
    main()
