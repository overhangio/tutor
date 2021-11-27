import os
from click.testing import CliRunner
from tests.test import CONTEXT
from tutor.commands.config import config_command

# Save initial tutor test environment context
if not os.path.exists(CONTEXT.root):
    runner = CliRunner()
    result = runner.invoke(config_command, ["save"], obj=CONTEXT)
