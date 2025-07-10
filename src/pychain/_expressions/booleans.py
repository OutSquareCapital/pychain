import operator
from collections.abc import Callable, Container
from typing import Any
from functools import partial


def is_true() -> Callable[[Any], bool]:
    return operator.truth


def is_none() -> Callable[[Any], bool]:
    return partial(operator.is_, None)


def is_not_none() -> Callable[[Any], bool]:
    return partial(operator.is_not, None)


def is_in[T](value: Container[T]) -> Callable[[T], bool]:
    return lambda x: operator.contains(value, x)


def is_not_in[T](value: Container[T]) -> Callable[[T], bool]:
    return lambda x: not operator.contains(value, x)


def eq[T](value: T) -> Callable[[T], bool]:
    return lambda x: operator.eq(x, value)


def ne[T](value: T) -> Callable[[T], bool]:
    return lambda x: operator.ne(x, value)


def gt[T](value: T) -> Callable[[T], bool]:
    return lambda x: operator.gt(x, value)  # type: ignore[return-value]


def ge[T](value: T) -> Callable[[T], bool]:
    return lambda x: operator.ge(x, value)  # type: ignore[return-value]


def lt[T](value: T) -> Callable[[T], bool]:
    return lambda x: operator.lt(x, value)  # type: ignore[return-value]


def le[T](value: T) -> Callable[[T], bool]:
    return lambda x: operator.le(x, value)  # type: ignore[return-value]
