# The Tutor plugin system is licensed under the terms of the Apache 2.0 license.
__license__ = "Apache 2.0"

import sys
import typing as t

from typing_extensions import Concatenate, ParamSpec

from . import contexts, priorities

T = t.TypeVar("T")
P = ParamSpec("P")
# Specialized typevar for list elements
E = t.TypeVar("E")
# I wish we could create such an alias, which would greatly simply the definitions
# below. Unfortunately this does not work, yet. It will once the following issue is
# resolved: https://github.com/python/mypy/issues/11855
# CallableFilter = t.Callable[Concatenate[T, P], T]


class FilterCallback(contexts.Contextualized, t.Generic[T, P]):
    def __init__(
        self, func: t.Callable[Concatenate[T, P], T], priority: t.Optional[int] = None
    ):
        super().__init__()
        self.func = func
        self.priority = priority or priorities.DEFAULT

    def apply(self, value: T, *args: P.args, **kwargs: P.kwargs) -> T:
        return self.func(value, *args, **kwargs)


class Filter(t.Generic[T, P]):
    """
    Filter hooks have callbacks that are triggered as a chain.

    Several filters are defined across the codebase. Each filters is given a unique
    name. To each filter are associated zero or more callbacks, sorted by priority.

    This is the typical filter lifecycle:

    1. Create an action with method :py:meth:`get` (or function :py:func:`get`).
    2. Add callbacks with method :py:meth:`add` (or function :py:func:`add`).
    3. Call the filter callbacks with method :py:meth:`apply` (or function :py:func:`apply`).

    The result of each callback is passed as the first argument to the next one. Thus,
    the type of the first argument must match the callback return type.

    The `T` and `P` type parameters of the Filter class correspond to the expected
    signature of the filter callbacks. `T` is the type of the first argument (and thus
    the return value type as well) and `P` is the signature of the other arguments.

    For instance, `Filter[str, [int]]` means that the filter callbacks are expected to
    take two arguments: one string and one integer. Each callback must then return a
    string.

    This strong typing makes it easier for plugin developers to quickly check whether
    they are adding and calling filter callbacks correctly.
    """

    INDEX: t.Dict[str, "Filter[t.Any, t.Any]"] = {}

    def __init__(self, name: str) -> None:
        self.name = name
        self.callbacks: t.List[FilterCallback[T, P]] = []

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.name}')"

    @classmethod
    def get(cls, name: str) -> "Filter[t.Any, t.Any]":
        """
        Get an existing action with the given name from the index, or create one.
        """
        return cls.INDEX.setdefault(name, cls(name))

    def add(
        self, priority: t.Optional[int] = None
    ) -> t.Callable[
        [t.Callable[Concatenate[T, P], T]], t.Callable[Concatenate[T, P], T]
    ]:
        def inner(
            func: t.Callable[Concatenate[T, P], T]
        ) -> t.Callable[Concatenate[T, P], T]:
            callback = FilterCallback(func, priority=priority)
            priorities.insert_callback(callback, self.callbacks)
            return func

        return inner

    def apply(
        self,
        value: T,
        *args: t.Any,
        **kwargs: t.Any,
    ) -> T:
        """
        Apply all declared filters to a single value, passing along the additional arguments.

        The return value of every filter is passed as the first argument to the next callback.

        Usage::

            results = filters.apply("my-filter", ["item0"])

        :type value: object
        :rtype: same as the type of ``value``.
        """
        return self.apply_from_context(None, value, *args, **kwargs)

    def apply_from_context(
        self,
        context: t.Optional[str],
        value: T,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T:
        for callback in self.callbacks:
            if callback.is_in_context(context):
                try:

                    value = callback.apply(
                        value,
                        *args,
                        **kwargs,
                    )
                except:
                    sys.stderr.write(
                        f"Error applying filter '{self.name}': func={callback.func} contexts={callback.contexts}'\n"
                    )
                    raise
        return value

    def clear(self, context: t.Optional[str] = None) -> None:
        """
        Clear any previously defined filter with the given name and context.
        """
        self.callbacks = [
            callback
            for callback in self.callbacks
            if not callback.is_in_context(context)
        ]

    # The methods below are specific to filters which take lists as first arguments
    def add_item(
        self: "Filter[t.List[E], P]", item: E, priority: t.Optional[int] = None
    ) -> None:
        self.add_items([item], priority=priority)

    def add_items(
        self: "Filter[t.List[E], P]", items: t.List[E], priority: t.Optional[int] = None
    ) -> None:
        # Unfortunately we have to type-ignore this line. If not, mypy complains with:
        #
        #   Argument 1 has incompatible type "Callable[[Arg(List[E], 'values'), **P], List[E]]"; expected "Callable[[List[E], **P], List[E]]"
        #   This is likely because "callback" has named arguments: "values". Consider marking them positional-only
        #
        # But we are unable to mark arguments positional-only (by adding / after values arg) in Python 3.7.
        # Get rid of this statement after Python 3.7 EOL.
        @self.add(priority=priority)  # type: ignore
        def callback(
            values: t.List[E], *_args: P.args, **_kwargs: P.kwargs
        ) -> t.List[E]:
            return values + items

    def iterate(
        self: "Filter[t.List[E], P]", *args: P.args, **kwargs: P.kwargs
    ) -> t.Iterator[E]:
        yield from self.iterate_from_context(None, *args, **kwargs)

    def iterate_from_context(
        self: "Filter[t.List[E], P]",
        context: t.Optional[str],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> t.Iterator[E]:
        yield from self.apply_from_context(context, [], *args, **kwargs)


class FilterTemplate(t.Generic[T, P]):
    """
    Filter templates are for filters for which the name needs to be formatted
    before the filter can be applied.

    Similar to :py:class:`tutor.hooks.actions.ActionTemplate`, filter templates are used to generate
    :py:class:`Filter` objects for which the name matches a certain template.
    """

    def __init__(self, name: str):
        self.template = name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.template}')"

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> Filter[T, P]:
        return get(self.template.format(*args, **kwargs))


# Syntactic sugar
get = Filter.get


def get_template(name: str) -> FilterTemplate[t.Any, t.Any]:
    """
    Create a filter with a template name.

    Templated filters must be formatted with ``(*args)`` before being applied. For example::

        filter_template = filters.get_template("namespace:{0}")
        named_filter = filter_template("name")

        @named_filter.add()
        def my_callback(x: int) -> int:
            ...

        named_filter.apply(42)
    """
    return FilterTemplate(name)


def add(
    name: str, priority: t.Optional[int] = None
) -> t.Callable[[t.Callable[Concatenate[T, P], T]], t.Callable[Concatenate[T, P], T]]:
    """
    Decorator for functions that will be applied to a single named filter.

    :param str name: name of the filter to which the decorated function should be added.
    :param int priority: optional order in which the filter callbacks are called. Higher
        values mean that they will be performed later. The default value is
        ``priorities.DEFAULT`` (10). Filters that should be called last should have a
        priority of 100.

    The return value of each filter function callback will be passed as the first argument to the next one.

    Usage::

        from tutor import hooks

        @hooks.filters.add("my-filter")
        def my_func(value, some_other_arg):
            # Do something with `value`
            ...
            return value

        # After filters have been created, the result of calling all filter callbacks is obtained by running:
        hooks.filters.apply("my-filter", initial_value, some_other_argument_value)
    """
    return Filter.get(name).add(priority=priority)


def add_item(name: str, item: T, priority: t.Optional[int] = None) -> None:
    """
    Convenience function to add a single item to a filter that returns a list of items.

    :param name: filter name.
    :param object item: item that will be appended to the resulting list.
    :param int priority: see :py:data:`add`.

    Usage::

        from tutor import hooks

        hooks.filters.add_item("my-filter", "item1")
        hooks.filters.add_item("my-filter", "item2")

        assert ["item1", "item2"] == hooks.filters.apply("my-filter", [])
    """
    get(name).add_item(item, priority=priority)


def add_items(name: str, items: t.List[T], priority: t.Optional[int] = None) -> None:
    """
    Convenience function to add multiple item to a filter that returns a list of items.

    :param name: filter name.
    :param list[object] items: items that will be appended to the resulting list.

    Usage::

        from tutor import hooks

        hooks.filters.add_items("my-filter", ["item1", "item2"])

        assert ["item1", "item2"] == hooks.filters.apply("my-filter", [])
    """
    get(name).add_items(items, priority=priority)


def iterate(name: str, *args: t.Any, **kwargs: t.Any) -> t.Iterator[T]:
    """
    Convenient function to iterate over the results of a filter result list.

    This pieces of code are equivalent::

        for value in filters.apply("my-filter", [], *args, **kwargs):
            ...

        for value in filters.iterate("my-filter", *args, **kwargs):
            ...

    :rtype iterator[T]: iterator over the list items from the filter with the same name.
    """
    yield from iterate_from_context(None, name, *args, **kwargs)


def iterate_from_context(
    context: t.Optional[str], name: str, *args: t.Any, **kwargs: t.Any
) -> t.Iterator[T]:
    """
    Same as :py:func:`iterate` but apply only callbacks from a given context.
    """
    yield from Filter.get(name).iterate_from_context(context, *args, **kwargs)


def apply(name: str, value: T, *args: t.Any, **kwargs: t.Any) -> T:
    """
    Apply all declared filters to a single value, passing along the additional arguments.

    The return value of every filter is passed as the first argument to the next callback.

    Usage::

        results = filters.apply("my-filter", ["item0"])

    :type value: object
    :rtype: same as the type of ``value``.
    """
    return apply_from_context(None, name, value, *args, **kwargs)


def apply_from_context(
    context: t.Optional[str], name: str, value: T, *args: P.args, **kwargs: P.kwargs
) -> T:
    """
    Same as :py:func:`apply` but only run the callbacks that were created in a given context.
    """
    filtre: Filter[T, P] = Filter.get(name)
    return filtre.apply_from_context(context, value, *args, **kwargs)


def clear_all(context: t.Optional[str] = None) -> None:
    """
    Clear any previously defined filter with the  given context.
    """
    for name in Filter.INDEX:
        clear(name, context=context)


def clear(name: str, context: t.Optional[str] = None) -> None:
    """
    Clear any previously defined filter with the given name and context.
    """
    filtre = Filter.INDEX.get(name)
    if filtre:
        filtre.clear(context=context)
