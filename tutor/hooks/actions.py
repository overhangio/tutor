# The Tutor plugin system is licensed under the terms of the Apache 2.0 license.
__license__ = "Apache 2.0"

import sys
import typing as t

from .contexts import Contextualized

# Similarly to CallableFilter, it should be possible to refine the definition of
# CallableAction in the future.
CallableAction = t.Callable[..., None]

DEFAULT_PRIORITY = 10


class ActionCallback(Contextualized):
    def __init__(
        self,
        func: CallableAction,
        priority: t.Optional[int] = None,
    ):
        super().__init__()
        self.func = func
        self.priority = priority or DEFAULT_PRIORITY

    def do(
        self, *args: t.Any, context: t.Optional[str] = None, **kwargs: t.Any
    ) -> None:
        if self.is_in_context(context):
            self.func(*args, **kwargs)


class Action:
    """
    Each action is associated to a name and a list of callbacks, sorted by
    priority.
    """

    INDEX: t.Dict[str, "Action"] = {}

    def __init__(self, name: str) -> None:
        self.name = name
        self.callbacks: t.List[ActionCallback] = []

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.name}')"

    @classmethod
    def get(cls, name: str) -> "Action":
        """
        Get an existing action with the given name from the index, or create one.
        """
        return cls.INDEX.setdefault(name, cls(name))

    def add(
        self, priority: t.Optional[int] = None
    ) -> t.Callable[[CallableAction], CallableAction]:
        def inner(func: CallableAction) -> CallableAction:
            callback = ActionCallback(func, priority=priority)
            # I wish we could use bisect.insort_right here but the `key=` parameter
            # is unsupported in Python 3.9
            position = 0
            while (
                position < len(self.callbacks)
                and self.callbacks[position].priority <= callback.priority
            ):
                position += 1
            self.callbacks.insert(position, callback)
            return func

        return inner

    def do(
        self, *args: t.Any, context: t.Optional[str] = None, **kwargs: t.Any
    ) -> None:
        for callback in self.callbacks:
            try:
                callback.do(*args, context=context, **kwargs)
            except:
                sys.stderr.write(
                    f"Error applying action '{self.name}': func={callback.func} contexts={callback.contexts}'\n"
                )
                raise

    def clear(self, context: t.Optional[str] = None) -> None:
        self.callbacks = [
            callback
            for callback in self.callbacks
            if not callback.is_in_context(context)
        ]


class ActionTemplate:
    """
    Action templates are for actions for which the name needs to be formatted
    before the action can be applied.
    """

    def __init__(self, name: str):
        self.template = name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.template}')"

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> Action:
        return get(self.template.format(*args, **kwargs))


# Syntactic sugar
get = Action.get


def get_template(name: str) -> ActionTemplate:
    """
    Create an action with a template name.

    Templated actions must be formatted with ``(*args)`` before being applied. For example::

        action_template = actions.get_template("namespace:{0}")

        @action_template("name").add()
        def my_callback():
            ...

        action_template("name").do()
    """
    return ActionTemplate(name)


def add(
    name: str,
    priority: t.Optional[int] = None,
) -> t.Callable[[CallableAction], CallableAction]:
    """
    Decorator to add a callback action associated to a name.

    :param name: name of the action. For forward compatibility, it is
        recommended not to hardcode any string here, but to pick a value from
        :py:class:`tutor.hooks.Actions` instead.
    :param priority: optional order in which the action callbacks are performed. Higher
        values mean that they will be performed later. The default value is
        ``DEFAULT_PRIORITY`` (10). Actions that should be performed last should
        have a priority of 100.

    Usage::

        from tutor import hooks

        @hooks.actions.add("my-action")
        def do_stuff():
            ...

    The ``do_stuff`` callback function will be called on ``hooks.actions.do("my-action")``. (see :py:func:`do`)

    The signature of each callback action function must match the signature of the corresponding ``hooks.actions.do`` call. Callback action functions are not supposed to return any value. Returned values will be ignored.
    """
    return get(name).add(priority=priority)


def do(
    name: str, *args: t.Any, context: t.Optional[str] = None, **kwargs: t.Any
) -> None:
    """
    Run action callbacks associated to a name/context.

    :param name: name of the action for which callbacks will be run.
    :param context: limit the set of callback actions to those that
        were declared within a certain context (see
        :py:func:`tutor.hooks.contexts.enter`).

    Extra ``*args`` and ``*kwargs`` arguments will be passed as-is to
    callback functions.

    Callbacks are executed in order of priority, then FIFO. There is no error
    management here: a single exception will cause all following callbacks
    not to be run and the exception to be bubbled up.
    """
    action = Action.INDEX.get(name)
    if action:
        action.do(*args, context=context, **kwargs)


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

    :param name: name of the action callbacks to remove.
    :param context: when defined, will clear only the actions that were
        created within that context.

    Actions will be removed from the list of callbacks and will no longer be
    run in :py:func:`do` calls.

    This function should almost certainly never be called by plugins. It is
    mostly useful to disable some plugins at runtime or in unit tests.
    """
    action = Action.INDEX.get(name)
    if action:
        action.clear(context=context)
