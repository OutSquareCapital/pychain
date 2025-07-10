import operator
from collections.abc import Callable


def add[T](value: T) -> Callable[[T], T]:
    return lambda x: operator.add(x, value)


def sub[T](value: T) -> Callable[[T], T]:
    return lambda x: operator.sub(x, value)


def mul[T](value: T) -> Callable[[T], T]:
    return lambda x: operator.mul(x, value)


def truediv[T](value: T) -> Callable[[T], T]:
    return lambda x: operator.truediv(x, value)


def floordiv[T](value: T) -> Callable[[T], T]:
    return lambda x: operator.floordiv(x, value)


def sub_r[T](value: T) -> Callable[[T], T]:
    return lambda x: operator.sub(value, x)


def truediv_r[T](value: T) -> Callable[[T], T]:
    return lambda x: operator.truediv(value, x)


def mod[T](value: T) -> Callable[[T], T]:
    return lambda x: operator.mod(x, value)


def pow[T](value: T) -> Callable[[T], T]:
    return lambda x: operator.pow(x, value)


def floordiv_r[T](value: T) -> Callable[[T], T]:
    return lambda x: operator.floordiv(value, x)


def neg[T]() -> Callable[[T], T]:
    return operator.neg  # type: ignore[return-value]
