from __future__ import annotations

import typing as t

from typing_extensions import Protocol

#: High priority callbacks are triggered first.
HIGH = 5
#: By default, all callbacks have the same priority and are processed in the order they
#: were added.
DEFAULT = 10
#: Low-priority callbacks are called last. Add callbacks with this priority to override previous callbacks. To add callbacks with even lower priority, use ``LOW + somevalue`` (though such behaviour is not encouraged).
LOW = 50


class PrioritizedCallback(Protocol):
    priority: int


TPrioritized = t.TypeVar("TPrioritized", bound=PrioritizedCallback)


def insert_callback(callback: TPrioritized, callbacks: list[TPrioritized]) -> None:
    # I wish we could use bisect.insort_right here but the `key=` parameter
    # is unsupported in Python 3.9
    position = 0
    while (
        position < len(callbacks) and callbacks[position].priority <= callback.priority
    ):
        position += 1
    callbacks.insert(position, callback)
