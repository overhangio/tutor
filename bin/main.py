#!/usr/bin/env python3

from tutor.commands.cli import main

# Manually adding plugins to bundle
from tutor.plugins import Plugins
import tutorminio.plugin

Plugins.EXTRA_INSTALLED["minio"] = tutorminio.plugin
main()
