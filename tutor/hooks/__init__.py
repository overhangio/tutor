# The Tutor plugin system is licensed under the terms of the Apache 2.0 license.
__license__ = "Apache 2.0"

import typing as t

# These imports are the hooks API
from . import actions, contexts, filters
from .consts import *


def clear_all(context: t.Optional[str] = None) -> None:
    """
    Clear both actions and filters.
    """
    filters.clear_all(context=context)
    actions.clear_all(context=context)
