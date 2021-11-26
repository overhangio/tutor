import os
import tempfile

from tutor.commands.context import Context

CONTEXT = Context(os.path.join(tempfile.gettempdir(), "tutor"))
