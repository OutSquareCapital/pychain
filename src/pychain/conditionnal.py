from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from functools import partial
import operator as op


@dataclass(slots=True)
class When[T, R]:
    _predicate: Callable[[T], bool]

    def then(self, result: Callable[[T], R] | R) -> "Then[T, R]":
        return Then[T, R](_conditions=[(self._predicate, result)])


@dataclass(slots=True)
class ChainedWhen[T, R]:
    _conditions: list[tuple[Callable[[T], bool], Callable[[T], R] | R]]
    _predicate: Callable[[T], bool]

    def then(self, result: Callable[[T], R] | R) -> "ChainedThen[T, R]":
        new_conditions = self._conditions + [(self._predicate, result)]
        return ChainedThen[T, R](_conditions=new_conditions)


@dataclass(slots=True)
class BaseThen[T, R]:
    _conditions: list[tuple[Callable[[T], bool], Callable[[T], R] | R]]

    def when(self, predicate: Callable[[T], bool]) -> "ChainedWhen[T, R]":
        return ChainedWhen[T, R](self._conditions, predicate)

    def otherwise(self, default_result: Callable[[T], R] | R):
        def conditional_logic(x: T):
            for predicate, result_spec in self._conditions:
                if predicate(x):
                    return result_spec(x) if callable(result_spec) else result_spec
            return default_result(x) if callable(default_result) else default_result

        return conditional_logic


@dataclass(slots=True)
class Then[T, R](BaseThen[T, R]): ...


@dataclass(slots=True)
class ChainedThen[T, R](BaseThen[T, R]): ...


def when[T, R](predicate: Callable[[T], bool]) -> When[T, Any]:
    return When[T, R](predicate)


def _runner[**P](
    p1: Callable[P, bool], p2: Callable[P, bool], *args: P.args, **kwargs: P.kwargs
):
    return op.and_(p1(*args, **kwargs), p2(*args, **kwargs))


def _binder[**P](p1: Callable[P, bool], p2: Callable[P, bool]):
    return partial(_runner, p1, p2)


def and_[**P](
    p1: Callable[P, bool],
):
    return partial(_binder, p1)
