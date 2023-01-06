from __future__ import annotations

# The Tutor plugin system is licensed under the terms of the Apache 2.0 license.
__license__ = "Apache 2.0"

import sys
import typing as t

from typing_extensions import ParamSpec

from . import priorities
from .contexts import Contextualized

#: Action generic signature.
T = ParamSpec("T")

# Similarly to CallableFilter, it should be possible to create a CallableAction alias in
# the future.
# CallableAction = t.Callable[T, None]


class ActionCallback(Contextualized, t.Generic[T]):
    def __init__(
        self,
        func: t.Callable[T, None],
        priority: t.Optional[int] = None,
    ):
        super().__init__()
        self.func = func
        self.priority = priority or priorities.DEFAULT

    def do(
        self,
        *args: T.args,
        **kwargs: T.kwargs,
    ) -> None:
        self.func(*args, **kwargs)


class Action(t.Generic[T]):
    """
    Action hooks have callbacks that are triggered independently from one another.

    Several actions are defined across the codebase. Each action is given a unique name.
    To each action are associated zero or more callbacks, sorted by priority.

    This is the typical action lifecycle:

    1. Create an action with method :py:meth:`get`.
    2. Add callbacks with method :py:meth:`add`.
    3. Call the action callbacks with method :py:meth:`do`.

    The ``P`` type parameter of the Action class corresponds to the expected signature of
    the action callbacks. For instance, ``Action[[str, int]]`` means that the action
    callbacks are expected to take two arguments: one string and one integer.

    This strong typing makes it easier for plugin developers to quickly check whether they are adding and calling action callbacks correctly.
    """

    INDEX: dict[str, "Action[t.Any]"] = {}

    def __init__(self, name: str) -> None:
        self.name = name
        self.callbacks: list[ActionCallback[T]] = []

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.name}')"

    @classmethod
    def get(cls, name: str) -> "Action[t.Any]":
        """
        Get an existing action with the given name from the index, or create one.
        """
        return cls.INDEX.setdefault(name, cls(name))

    def add(
        self, priority: t.Optional[int] = None
    ) -> t.Callable[[t.Callable[T, None]], t.Callable[T, None]]:
        """
        Decorator to add a callback to an action.

        :param priority: optional order in which the action callbacks are performed. Higher
            values mean that they will be performed later. The default value is
            ``priorities.DEFAULT`` (10). Actions that should be performed last should have a
            priority of 100.

        Usage::

            @my_action.add("my-action")
            def do_stuff(my_arg):
                ...

        The ``do_stuff`` callback function will be called on ``my_action.do(some_arg)``.

        The signature of each callback action function must match the signature of the
        corresponding :py:meth:`do` method. Callback action functions are not supposed
        to return any value. Returned values will be ignored.
        """

        def inner(func: t.Callable[T, None]) -> t.Callable[T, None]:
            callback = ActionCallback(func, priority=priority)
            priorities.insert_callback(callback, self.callbacks)
            return func

        return inner

    def do(
        self,
        *args: T.args,
        **kwargs: T.kwargs,
    ) -> None:
        """
        Run the action callbacks in sequence.

        :param name: name of the action for which callbacks will be run.

        Extra ``*args`` and ``*kwargs`` arguments will be passed as-is to
        callback functions.

        Callbacks are executed in order of priority, then FIFO. There is no error
        management here: a single exception will cause all following callbacks
        not to be run and the exception will be bubbled up.
        """
        self.do_from_context(None, *args, **kwargs)

    def do_from_context(
        self,
        context: t.Optional[str],
        *args: T.args,
        **kwargs: T.kwargs,
    ) -> None:
        """
        Same as :py:meth:`do` but only run the callbacks from a given context.

        :param name: name of the action for which callbacks will be run.
        :param context: limit the set of callback actions to those that
            were declared within a certain context (see
            :py:func:`tutor.core.hooks.contexts.enter`).
        """
        for callback in self.callbacks:
            if callback.is_in_context(context):
                try:
                    callback.do(
                        *args,
                        **kwargs,
                    )
                except:
                    sys.stderr.write(
                        f"Error applying action '{self.name}': func={callback.func} contexts={callback.contexts}'\n"
                    )
                    raise

    def clear(self, context: t.Optional[str] = None) -> None:
        """
        Clear all or part of the callbacks associated to an action

        :param name: name of the action callbacks to remove.
        :param context: when defined, will clear only the actions that were
            created within that context.

        Actions will be removed from the list of callbacks and will no longer be
        run in :py:meth:`do` calls.

        This function should almost certainly never be called by plugins. It is
        mostly useful to disable some plugins at runtime or in unit tests.
        """
        self.callbacks = [
            callback
            for callback in self.callbacks
            if not callback.is_in_context(context)
        ]


class ActionTemplate(t.Generic[T]):
    """
    Action templates are for actions for which the name needs to be formatted
    before the action can be applied.

    Action templates can generate different :py:class:`Action` objects for which the
    name matches a certain template.

    Templated actions must be formatted with ``(*args)`` before being applied. For example::

        action_template = ActionTemplate("namespace:{0}")

        # Return the action named "namespace:name"
        my_action = action_template("name")

        @my_action.add()
        def my_callback():
            ...

        my_action.do()
    """

    def __init__(self, name: str):
        self.template = name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.template}')"

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> Action[T]:
        name = self.template.format(*args, **kwargs)
        action: Action[T] = Action.get(name)
        return action


# Syntactic sugar
get = Action.get


def get_template(name: str) -> ActionTemplate[t.Any]:
    """
    Create an action with a template name.
    """
    return ActionTemplate(name)


def add(
    name: str, priority: t.Optional[int] = None
) -> t.Callable[[t.Callable[T, None]], t.Callable[T, None]]:
    """
    Decorator to add a callback action associated to a name.
    """
    return get(name).add(priority=priority)


def do(
    name: str,
    *args: T.args,
    **kwargs: T.kwargs,
) -> None:
    """
    Run action callbacks associated to a name/context.
    """
    action: Action[T] = Action.get(name)
    action.do(*args, **kwargs)


def do_from_context(
    context: str,
    name: str,
    *args: T.args,
    **kwargs: T.kwargs,
) -> None:
    """
    Same as :py:func:`do` but only run the callbacks that were created in a given context.
    """
    action: Action[T] = Action.get(name)
    action.do_from_context(context, *args, **kwargs)


def clear_all(context: t.Optional[str] = None) -> None:
    """
    Clear any previously defined filter with the  given context.

    This will call :py:func:`clear` with all action names.
    """
    for name in Action.INDEX:
        clear(name, context=context)


def clear(name: str, context: t.Optional[str] = None) -> None:
    """
    Clear any previously defined action with the given name and context.
    """
    Action.get(name).clear(context=context)
