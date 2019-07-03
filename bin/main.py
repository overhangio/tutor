#!/usr/bin/env python3

from tutor.commands.cli import main

# Manually adding plugins to bundle
from tutor.plugins import Plugins
import tutorminio.plugin
import tutornotes.plugin
import tutorxqueue.plugin

Plugins.EXTRA_INSTALLED["minio"] = tutorminio.plugin
Plugins.EXTRA_INSTALLED["notes"] = tutornotes.plugin
Plugins.EXTRA_INSTALLED["xqueue"] = tutorxqueue.plugin
main()
