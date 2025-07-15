import operator
from collections.abc import Iterable, Iterator, Callable
from functools import partial
from typing import Any
import cytoolz.functoolz as ftz
import cytoolz.itertoolz as itz
from copy import deepcopy
from .._protocols import CheckFunc, ThreadFunc, TransformFunc

attr = operator.attrgetter
item = operator.itemgetter
method = operator.methodcaller
compose = ftz.compose_left
pipe = ftz.pipe
identity = ftz.identity
clone = deepcopy


def partial_call[R, **P](obj: Callable[P, R]) -> Callable[P, R]:
    """
    Creates a partial function that calls the given object.

    This is useful for creating a callable that can be used in expressions
    without needing to instantiate the object first.

    Example:
        >>> class Human:
        ...     def __init__(self, name: str, age: int):
        ...     self.name = name
        ...     self.age = age
        >>> a = partial_call(Human)
        >>> a("alice", 30).age
        30
    """
    return partial(operator.call, obj)


def to_obj[T](obj: Callable[..., T], *args: Any, **kwargs: Any) -> partial[T]:
    return partial(obj, *args, **kwargs)


def partial_map[V, V1](f: TransformFunc[V, V1]) -> partial[Iterator[V1]]:
    return partial(map, f)


def flat_map[V, V1](f: TransformFunc[V, Iterable[V1]]) -> partial[Iterator[V1]]:
    return partial(_flat_map, func=f)


def partial_filter[V](f: CheckFunc[V]) -> partial[Iterator[V]]:
    return partial(filter, f)


def compose_on_iter[V, V1](*fns: TransformFunc[V, V1]) -> partial[Iterator[V1]]:
    return partial(map, ftz.compose_left(*fns))


def _thread_first[T](val: T, fns: Iterable[ThreadFunc[T]]) -> T:
    return ftz.thread_first(val, *fns)


def _thread_last[T](val: T, fns: Iterable[ThreadFunc[T]]) -> T:
    return ftz.thread_last(val, *fns)


def thread_first[T](fns: Iterable[ThreadFunc[T]]) -> partial[T]:
    return partial(_thread_first, fns=fns)


def thread_last[T](fns: Iterable[ThreadFunc[T]]) -> partial[T]:
    return partial(_thread_last, fns=fns)


def _flat_map[V, V1](
    value: Iterable[V], func: TransformFunc[V, Iterable[V1]]
) -> Iterator[V1]:
    return itz.concat(map(func, value))
