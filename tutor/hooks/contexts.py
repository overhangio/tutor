# The Tutor plugin system is licensed under the terms of the Apache 2.0 license.
__license__ = "Apache 2.0"

import typing as t
from contextlib import contextmanager


class Context:
    CURRENT: t.List[str] = []

    def __init__(self, name: str):
        self.name = name

    @contextmanager
    def enter(self) -> t.Iterator[None]:
        try:
            Context.CURRENT.append(self.name)
            yield
        finally:
            Context.CURRENT.pop()


class ContextTemplate:
    """
    Context templates are for filters for which the name needs to be formatted
    before the filter can be applied.
    """

    def __init__(self, name: str):
        self.template = name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.template}')"

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> Context:
        return Context(self.template.format(*args, **kwargs))


class Contextualized:
    """
    This is a simple class to store the current context in hooks.

    The current context is stored as a static variable.
    """

    def __init__(self) -> None:
        self.contexts = Context.CURRENT[:]

    def is_in_context(self, context: t.Optional[str]) -> bool:
        return context is None or context in self.contexts


def enter(name: str) -> t.ContextManager[None]:
    """
    Identify created hooks with one or multiple context strings.

    :param name: name of the context that will be attached to hooks.
    :rtype t.ContextManager[None]:

    Usage::

        from tutor import hooks

        with hooks.contexts.enter("my-context"):
            # declare new actions and filters
            ...

        # Later on, actions and filters can be disabled with:
        hooks.actions.clear_all(context="my-context")
        hooks.filters.clear_all(context="my-context")

    This is a context manager that will attach a context name to all hook callbacks
    created within its scope. The purpose of contexts is to solve an issue that
    is inherent to pluggable hooks: it is difficult to track in which part of the
    code each hook callback was created. This makes things hard to debug when a single
    hook callback goes wrong. It also makes it impossible to disable some hook callbacks after
    they have been created.

    We resolve this issue by storing the current contexts in a static list.
    Whenever a hook is created, the list of current contexts is copied as a
    ``contexts`` attribute. This attribute can be later examined, either for
    removal or for limiting the set of hook callbacks that should be applied.
    """
    return Context(name).enter()
