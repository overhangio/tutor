#!/usr/bin/env python3
from tutor.plugins import OfficialPlugin
from tutor.commands.cli import main

# Manually install plugins (this is for creating the bundle)
for plugin_name in [
    "android",
    "discovery",
    "ecommerce",
    "forum",
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

if __name__ == "__main__":
    main()
