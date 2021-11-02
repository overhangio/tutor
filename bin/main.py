#!/usr/bin/env python3
from tutor.plugins import OfficialPlugin

# Manually install plugins (this is for creating the bundle)
for plugin_name in [
    "android",
    "discovery",
    "ecommerce",
    "license",
    "mfe",
    "minio",
    "notes",
    "richie",
    "webui",
    "xqueue",
]:
    try:
        OfficialPlugin.load(plugin_name)
    except ImportError:
        pass

from tutor.commands.cli import main

main()
