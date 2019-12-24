#!/usr/bin/env python3
from tutor.plugins import OfficialPlugin

# Manually install plugins (this is for creating the bundle)
for plugin_name in [
    "discovery",
    "ecommerce",
    # "figures",
    "lts",
    "minio",
    "notes",
    "xqueue",
]:
    try:
        OfficialPlugin.INSTALLED.append(OfficialPlugin(plugin_name))
    except ImportError:
        pass

from tutor.commands.cli import main

main()
