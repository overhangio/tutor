# The Tutor plugin system is licensed under the terms of the Apache 2.0 license.
__license__ = "Apache 2.0"

import sys
import typing as t

from . import contexts

# For now, this signature is not very restrictive. In the future, we could improve it by writing:
#
# P = ParamSpec("P")
# CallableFilter = t.Callable[Concatenate[T, P], T]
#
# See PEP-612: https://www.python.org/dev/peps/pep-0612/
# Unfortunately, this piece of code fails because of a bug in mypy:
# https://github.com/python/mypy/issues/11833
# https://github.com/python/mypy/issues/8645
# https://github.com/python/mypy/issues/5876
# https://github.com/python/typing/issues/696
T = t.TypeVar("T")
CallableFilter = t.Callable[..., t.Any]


class FilterCallback(contexts.Contextualized):
    def __init__(self, func: CallableFilter):
        super().__init__()
        self.func = func

    def apply(
        self, value: T, *args: t.Any, context: t.Optional[str] = None, **kwargs: t.Any
    ) -> T:
        if self.is_in_context(context):
            value = self.func(value, *args, **kwargs)
        return value


class Filter:
    """
    Each filter is associated to a name and a list of callbacks.
    """

    INDEX: t.Dict[str, "Filter"] = {}

    def __init__(self, name: str) -> None:
        self.name = name
        self.callbacks: t.List[FilterCallback] = []

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.name}')"

    @classmethod
    def get(cls, name: str) -> "Filter":
        """
        Get an existing action with the given name from the index, or create one.
        """
        return cls.INDEX.setdefault(name, cls(name))

    def add(self) -> t.Callable[[CallableFilter], CallableFilter]:
        def inner(func: CallableFilter) -> CallableFilter:
            self.callbacks.append(FilterCallback(func))
            return func

        return inner

    def add_item(self, item: T) -> None:
        self.add_items([item])

    def add_items(self, items: t.List[T]) -> None:
        @self.add()
        def callback(value: t.List[T], *_args: t.Any, **_kwargs: t.Any) -> t.List[T]:
            return value + items

    def iterate(
        self, *args: t.Any, context: t.Optional[str] = None, **kwargs: t.Any
    ) -> t.Iterator[T]:
        yield from self.apply([], *args, context=context, **kwargs)

    def apply(
        self,
        value: T,
        *args: t.Any,
        context: t.Optional[str] = None,
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
        for callback in self.callbacks:
            try:
                value = callback.apply(value, *args, context=context, **kwargs)
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


class FilterTemplate:
    """
    Filter templates are for filters for which the name needs to be formatted
    before the filter can be applied.
    """

    def __init__(self, name: str):
        self.template = name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.template}')"

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> Filter:
        return get(self.template.format(*args, **kwargs))


# Syntactic sugar
get = Filter.get


def get_template(name: str) -> FilterTemplate:
    """
    Create a filter with a template name.

    Templated filters must be formatted with ``(*args)`` before being applied. For example::

        filter_template = filters.get_template("namespace:{0}")
        named_filter = filter_template("name")

        @named_filter.add()
        def my_callback():
            ...

        named_filter.do()
    """
    return FilterTemplate(name)


def add(name: str) -> t.Callable[[CallableFilter], CallableFilter]:
    """
    Decorator for functions that will be applied to a single named filter.

    :param name: name of the filter to which the decorated function should be added.

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
    return Filter.get(name).add()


def add_item(name: str, item: T) -> None:
    """
    Convenience function to add a single item to a filter that returns a list of items.

    :param name: filter name.
    :param object item: item that will be appended to the resulting list.

    Usage::

        from tutor import hooks

        hooks.filters.add_item("my-filter", "item1")
        hooks.filters.add_item("my-filter", "item2")

        assert ["item1", "item2"] == hooks.filters.apply("my-filter", [])
    """
    get(name).add_item(item)


def add_items(name: str, items: t.List[T]) -> None:
    """
    Convenience function to add multiple item to a filter that returns a list of items.

    :param name: filter name.
    :param list[object] items: items that will be appended to the resulting list.

    Usage::

        from tutor import hooks

        hooks.filters.add_items("my-filter", ["item1", "item2"])

        assert ["item1", "item2"] == hooks.filters.apply("my-filter", [])
    """
    get(name).add_items(items)


def iterate(
    name: str, *args: t.Any, context: t.Optional[str] = None, **kwargs: t.Any
) -> t.Iterator[T]:
    """
    Convenient function to iterate over the results of a filter result list.

    This pieces of code are equivalent::

        for value in filters.apply("my-filter", [], *args, **kwargs):
            ...

        for value in filters.iterate("my-filter", *args, **kwargs):
            ...

    :rtype iterator[T]: iterator over the list items from the filter with the same name.
    """
    yield from Filter.get(name).iterate(*args, context=context, **kwargs)


def apply(
    name: str,
    value: T,
    *args: t.Any,
    context: t.Optional[str] = None,
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
    return Filter.get(name).apply(value, *args, context=context, **kwargs)


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
