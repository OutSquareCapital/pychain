import operator
from collections.abc import Callable
from functools import partial

def add[T](value: T) -> Callable[[T], T]:
    return partial(operator.add, value)


def sub[T](value: T) -> Callable[[T], T]:
    return lambda x: operator.sub(x, value)


def sub_r[T](value: T) -> Callable[[T], T]:
    return partial(operator.sub, value)


def mul[T](value: T) -> Callable[[T], T]:
    return partial(operator.mul, value)


def truediv[T](value: T) -> Callable[[T], T]:
    return lambda x: operator.truediv(x, value)


def truediv_r[T](value: T) -> Callable[[T], T]:
    return partial(operator.truediv, value)


def floordiv[T](value: T) -> Callable[[T], T]:
    return lambda x: operator.floordiv(x, value)


def floordiv_r[T](value: T) -> Callable[[T], T]:
    return partial(operator.floordiv, value)


def mod[T](value: T) -> Callable[[T], T]:
    return lambda x: operator.mod(x, value)

def mod_r[T](value: T) -> Callable[[T], T]:
    return partial(operator.mod, value)


def pow[T](value: T) -> Callable[[T], T]:
    return lambda x: operator.pow(x, value)

def pow_r[T](value: T) -> Callable[[T], T]:
    return partial(operator.pow, value)

