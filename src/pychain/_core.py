from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from typing import Any, Concatenate, Self

import cytoolz.itertoolz as itz

type Check[T] = Callable[[T], bool]
type Process[T] = Callable[[T], T]
type Transform[T, T1] = Callable[[T], T1]
type Agg[V, V1] = Callable[[Iterable[V]], V1]


class CommonBase[T](ABC):
    data: T

    def into[U, **P](
        self,
        func: Callable[Concatenate[T, P], U],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> U:
        """Apply func to the internal data."""
        return func(self.data, *args, **kwargs)

    @abstractmethod
    def pipe[U, **P](
        self,
        func: Callable[Concatenate[T, P], U],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> U:
        raise NotImplementedError

    @abstractmethod
    def compose(self, *funcs: Callable[[T], T]) -> Self:
        raise NotImplementedError

    def print(self) -> Self:
        """Print the contained data (side-effect) and return self."""
        print(self.data)
        return self


def peekn[T](seq: Iterable[T], n: int, note: str | None = None):
    """Return an iterator equivalent to seq after printing the first n items.

    Example:
        >>> list(peekn([0, 1, 2, 3], 2))
        Peeked 2 values: [0, 1]
        [0, 1, 2, 3]
    """
    values, sequence = itz.peekn(n, seq)
    if note:
        print(f"Peeked {n} values ({note}): {list(values)}")
    else:
        print(f"Peeked {n} values: {list(values)}")
    return sequence


def peek[T](seq: Iterable[T], note: str | None = None):
    """Return an iterator equivalent to seq after printing its first value.

    Example:
        >>> list(peek([10, 20]))
        Peeked value: 10
        [10, 20]
    """
    value, sequence = itz.peek(seq)
    if note:
        print(f"Peeked value ({note}): {value}")
    else:
        print(f"Peeked value: {value}")
    return sequence


def tap[V](value: Iterable[V], func: Callable[[V], None]):
    """Yield items from value while calling func on each item (side-effect).

    Example:
        >>> list(tap([1, 2], lambda x: None))
        [1, 2]
    """
    for item in value:
        func(item)
        yield item


def flatten_recursive[T](
    d: dict[Any, T], parent_key: str = "", sep: str = "."
) -> dict[str, T]:
    """Flatten a nested dict into a single-level dict with dotted keys.

    Example:
        >>> flatten_recursive({"a": {"b": 1}})
        {'a.b': 1}
    """
    items: dict[str, T] = {}
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if hasattr(v, "items"):
            items.update(flatten_recursive(v, new_key, sep))
        else:
            v: Any
            items[new_key] = v
    return items
