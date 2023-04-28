from __future__ import annotations

# The Tutor plugin system is licensed under the terms of the Apache 2.0 license.
__license__ = "Apache 2.0"

import sys
import typing as t

from typing_extensions import Concatenate, ParamSpec

from . import contexts, priorities

#: Filter generic return value, which is also the type of the first callback argument.
T1 = t.TypeVar("T1")
#: Filter generic signature for all arguments after the first one.
T2 = ParamSpec("T2")
#: Specialized typevar for list elements
L = t.TypeVar("L")

FilterCallbackFunc = t.Callable[Concatenate[T1, T2], T1]


class FilterCallback(contexts.Contextualized, t.Generic[T1, T2]):
    def __init__(
        self,
        func: FilterCallbackFunc[T1, T2],
        priority: t.Optional[int] = None,
    ):
        super().__init__()
        self.func = func
        self.priority = priority or priorities.DEFAULT

    def apply(self, value: T1, *args: T2.args, **kwargs: T2.kwargs) -> T1:
        return self.func(value, *args, **kwargs)


class Filter(t.Generic[T1, T2]):
    """
    Filter hooks have callbacks that are triggered as a chain.

    Several filters are defined across the codebase. Each filters is given a unique
    name. To each filter are associated zero or more callbacks, sorted by priority.

    This is the typical filter lifecycle:

    1. Create an action with method :py:meth:`get`.
    2. Add callbacks with method :py:meth:`add`.
    3. Call the filter callbacks with method :py:meth:`apply`.

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

    INDEX: dict[str, "Filter[t.Any, t.Any]"] = {}

    def __init__(self, name: str) -> None:
        self.name = name
        self.callbacks: list[FilterCallback[T1, T2]] = []

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
    ) -> t.Callable[[FilterCallbackFunc[T1, T2]], FilterCallbackFunc[T1, T2]]:
        """
        Decorator to add a filter callback.

        Callbacks are added by increasing priority. Highest priority score are called
        last.

        :param int priority: optional order in which the filter callbacks are called. Higher
          values mean that they will be performed later. The default value is
          ``priorities.DEFAULT`` (10). Filters that must be called last should have a
          priority of 100.

        The return value of each filter function callback will be passed as the first argument to the next one.

        Usage::

            @my_filter.add()
            def my_func(value, some_other_arg):
                # Do something with `value`
                ...
                return value

        After filters have been created, the result of calling all filter callbacks is obtained by running:

            final_value = my_filter.apply(initial_value, some_other_argument_value)
        """

        def inner(func: FilterCallbackFunc[T1, T2]) -> FilterCallbackFunc[T1, T2]:
            callback: FilterCallback[T1, T2] = FilterCallback(func, priority=priority)
            priorities.insert_callback(callback, self.callbacks)
            return func

        return inner

    def apply(
        self,
        value: T1,
        *args: T2.args,
        **kwargs: T2.kwargs,
    ) -> T1:
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
        value: T1,
        *args: T2.args,
        **kwargs: T2.kwargs,
    ) -> T1:
        """
        Same as :py:meth:`apply` but only run the callbacks that were created in a given context.

        If ``context`` is None then it is ignored.
        """
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
        Clear any previously defined filter with the given context.
        """
        self.callbacks = [
            callback
            for callback in self.callbacks
            if not callback.is_in_context(context)
        ]

    # The methods below are specific to filters which take lists as first arguments
    def add_item(
        self: "Filter[list[L], T2]", item: L, priority: t.Optional[int] = None
    ) -> None:
        """
        Convenience decorator to add a single item to a filter that returns a list of items.

        This method is only valid for filters that return list of items.

        :param object item: item that will be appended to the resulting list.
        :param int priority: see :py:data:`Filter.add`.

        Usage::

            my_filter.add_item("item1")
            my_filter.add_item("item2")

            assert ["item1", "item2"] == my_filter.apply([])
        """
        self.add_items([item], priority=priority)

    def add_items(
        self: "Filter[list[L], T2]", items: list[L], priority: t.Optional[int] = None
    ) -> None:
        """
        Convenience function to add multiple items to a filter that returns a list of items.

        This method is only valid for filters that return list of items.

        This is a similar method to :py:data:`Filter.add_item` except that it can be
        used to add multiple items at the same time. If you find yourself calling
        ``add_item`` multiple times on the same filter, then you probably want to use a
        single call to ``add_items`` instead.

        :param name: filter name.
        :param list[object] items: items that will be appended to the resulting list.

        Usage::

            my_filter.add_items(["item1", "item2"])
            my_filter.add_items(["item3", "item4"])

            assert ["item1", "item2", "item3", "item4"] == my_filter.apply([])

        The following are equivalent::

            # Single call to add_items
            my_filter.add_items(["item1", "item2"])

            # Multiple calls to add_item
            my_filter.add_item("item1")
            my_filter.add_item("item2")
        """

        @self.add(priority=priority)
        def callback(
            values: list[L], /, *_args: T2.args, **_kwargs: T2.kwargs
        ) -> list[L]:
            return values + items

    def iterate(
        self: "Filter[list[L], T2]", *args: T2.args, **kwargs: T2.kwargs
    ) -> t.Iterator[L]:
        """
        Convenient function to iterate over the results of a filter result list.

        This method is only valid for filters that return list of items.

        This pieces of code are equivalent::

            for value in my_filter.apply([], *args, **kwargs):
                ...

            for value in my_filter.iterate(*args, **kwargs):
                ...

        :rtype iterator[T]: iterator over the list of items from the filter
        """
        yield from self.iterate_from_context(None, *args, **kwargs)

    def iterate_from_context(
        self: "Filter[list[L], T2]",
        context: t.Optional[str],
        *args: T2.args,
        **kwargs: T2.kwargs,
    ) -> t.Iterator[L]:
        """
        Same as :py:func:`Filter.iterate` but apply only callbacks from a given context.
        """
        yield from self.apply_from_context(context, [], *args, **kwargs)


class FilterTemplate(t.Generic[T1, T2]):
    """
    Filter templates are for filters for which the name needs to be formatted
    before the filter can be applied.

    Similar to :py:class:`tutor.core.hooks.ActionTemplate`, filter templates are used to generate
    :py:class:`Filter` objects for which the name matches a certain template.

    Templated filters must be formatted with ``(*args)`` before being applied. For example::

        filter_template = FilterTemplate("namespace:{0}")
        named_filter = filter_template("name")

        @named_filter.add()
        def my_callback(x: int) -> int:
            ...

        named_filter.apply(42)
    """

    def __init__(self, name: str):
        self.template = name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.template}')"

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> Filter[T1, T2]:
        return get(self.template.format(*args, **kwargs))


# Syntactic sugar
get = Filter.get


def get_template(name: str) -> FilterTemplate[t.Any, t.Any]:
    """
    Create a filter with a template name.
    """
    return FilterTemplate(name)


def add(
    name: str, priority: t.Optional[int] = None
) -> t.Callable[[FilterCallbackFunc[T1, T2]], FilterCallbackFunc[T1, T2]]:
    """
    Decorator for functions that will be applied to a single named filter.
    """
    return Filter.get(name).add(priority=priority)


def add_item(name: str, item: T1, priority: t.Optional[int] = None) -> None:
    """
    Convenience function to add a single item to a filter that returns a list of items.
    """
    get(name).add_item(item, priority=priority)


def add_items(name: str, items: list[T1], priority: t.Optional[int] = None) -> None:
    """
    Convenience decorator to add multiple item to a filter that returns a list of items.
    """
    get(name).add_items(items, priority=priority)


def iterate(name: str, *args: t.Any, **kwargs: t.Any) -> t.Iterator[T1]:
    """
    Convenient function to iterate over the results of a filter result list.
    """
    yield from iterate_from_context(None, name, *args, **kwargs)


def iterate_from_context(
    context: t.Optional[str], name: str, *args: t.Any, **kwargs: t.Any
) -> t.Iterator[T1]:
    yield from Filter.get(name).iterate_from_context(context, *args, **kwargs)


def apply(name: str, value: T1, *args: t.Any, **kwargs: t.Any) -> T1:
    """
    Apply all declared filters to a single value, passing along the additional arguments.
    """
    return apply_from_context(None, name, value, *args, **kwargs)


def apply_from_context(
    context: t.Optional[str], name: str, value: T1, *args: T2.args, **kwargs: T2.kwargs
) -> T1:
    """
    Same as :py:func:`apply` but only run the callbacks that were created in a given context.
    """
    filtre: Filter[T1, T2] = Filter.get(name)
    return filtre.apply_from_context(context, value, *args, **kwargs)


def clear_all(context: t.Optional[str] = None) -> None:
    """
    Clear any previously defined filter with the given context.
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
