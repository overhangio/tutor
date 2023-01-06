import typing as t

from .actions import Action, ActionTemplate
from .actions import clear_all as _clear_all_actions
from .contexts import Context, ContextTemplate
from .filters import Filter, FilterTemplate
from .filters import clear_all as _clear_all_filters


def clear_all(context: t.Optional[str] = None) -> None:
    """
    Clear both actions and filters.
    """
    _clear_all_actions(context=context)
    _clear_all_filters(context=context)
