"""
Implement callable boolean functions using operator module and cytoolz.
larger_than, smaller_than, and other comparison functions are using the reverse operation inside the function, since this what the order of the chain will be.
"""

import operator
from collections.abc import Callable, Container
from typing import Any
from functools import partial
import cytoolz as cz


is_true = operator.truth
is_all = all
is_any = any
is_distinct = cz.itertoolz.isdistinct
is_iterable = cz.itertoolz.isiterable


def is_none() -> Callable[[Any], bool]:
    return partial(operator.is_, None)


def is_not_none() -> Callable[[Any], bool]:
    return partial(operator.is_not, None)


def is_in[T](value: Container[T]) -> Callable[[T], bool]:
    return partial(operator.contains, value)


def is_not_in[T](value: Container[T]) -> Callable[[T], bool]:
    return lambda x: not operator.contains(value, x)


def eq[T](value: T) -> Callable[[T], bool]:
    return partial(operator.eq, value)


def ne[T](value: T) -> Callable[[T], bool]:
    return partial(operator.ne, value)


def gt[T](value: T) -> Callable[[T], bool]:
    return partial(operator.lt, value) # type: ignore


def ge[T](value: T) -> Callable[[T], bool]:
    return partial(operator.le, value) # type: ignore


def lt[T](value: T) -> Callable[[T], bool]:
    return partial(operator.gt, value) # type: ignore


def le[T](value: T) -> Callable[[T], bool]:
    return partial(operator.ge, value) # type: ignore
