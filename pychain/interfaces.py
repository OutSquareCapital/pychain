from functools import wraps
from typing import Protocol, Any, ParamSpec, TypeVar
from collections.abc import Callable
from dataclasses import dataclass
from copy import deepcopy

P = ParamSpec("P")
R = TypeVar("R")

type CheckFunc[T] = Callable[[T], bool]

@dataclass(slots=True, frozen=True)
class Transformable[T]:
    value: T

    def copy(self) -> T:
        return deepcopy(self.value)


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