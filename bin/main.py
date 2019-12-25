#!/usr/bin/env python3
import importlib

from tutor.plugins import Plugins

# Manually install plugins (this is for creating the bundle)
for plugin in ["discovery", "ecommerce", "figures", "lts", "minio", "notes", "xqueue"]:
    try:
        module = importlib.import_module("tutor{}.plugin".format(plugin))
    except ImportError:
        pass
    else:
        Plugins.EXTRA_INSTALLED[plugin] = module

from tutor.commands.cli import main
main()
