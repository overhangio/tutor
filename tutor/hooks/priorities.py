import typing as t

from typing_extensions import Protocol

HIGH = 5
DEFAULT = 10
LOW = 50


class PrioritizedCallback(Protocol):
    priority: int


TPrioritized = t.TypeVar("TPrioritized", bound=PrioritizedCallback)


def insert_callback(callback: TPrioritized, callbacks: t.List[TPrioritized]) -> None:
    # I wish we could use bisect.insort_right here but the `key=` parameter
    # is unsupported in Python 3.9
    position = 0
    while (
        position < len(callbacks) and callbacks[position].priority <= callback.priority
    ):
        position += 1
    callbacks.insert(position, callback)
