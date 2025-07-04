from functools import wraps
from typing import Protocol, Any, ParamSpec, TypeVar
from collections.abc import Callable

P = ParamSpec('P')
R = TypeVar("R")

type CheckFunc[T] = Callable[[T], bool]


class RandomProtocol(Protocol):
    def random(self, *args: Any, **kwargs: Any) -> float: ...

def collector(*func: Callable[P, R]) -> Callable[P, R]:
    def decorator(f: Callable[P, R]) -> Callable[P, R]:
        @wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            result: R = f(*args, **kwargs)
            print(f"Result of {f.__name__}: {result}")
            return result
        return wrapper
    return decorator(*func)