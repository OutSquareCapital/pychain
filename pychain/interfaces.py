from functools import wraps
from typing import Protocol, Any, ParamSpec, TypeVar
from collections.abc import Callable
import polars as pl
from dataclasses import dataclass

P = ParamSpec("P")
R = TypeVar("R")

type CheckFunc[T] = Callable[[T], bool]


class RandomProtocol(Protocol):
    def random(self, *args: Any, **kwargs: Any) -> float: ...


def lazy(*func: Callable[P, R]) -> Callable[P, R]:
    def decorator(f: Callable[P, R]) -> Callable[P, R]:
        @wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            print(f"Lazy eval of {f.__name__} with args: {args}, kwargs: {kwargs}")
            return f(*args, **kwargs)

        return wrapper

    return decorator(*func)


@dataclass(slots=True, frozen=True)
class BaseTransformator[V]:
    value: V

    def series(self) -> pl.Series:
        return pl.Series(values=self.value)

    def frame(self) -> pl.DataFrame:
        return pl.DataFrame(data=self.value)

    @lazy
    def lazy_frame(self) -> pl.LazyFrame:
        return pl.LazyFrame(data=self.value)
