import typing as t

from .actions import Action
from .contexts import Context
from .filters import Filter


def clear_all(context: t.Optional[str] = None) -> None:
    """
    Clear both actions and filters.
    """
    Action.clear_all(context=context)
    Filter.clear_all(context=context)
