import textwrap
from collections.abc import Callable
from typing import Any, Final, NamedTuple, TypeGuard


class Signature(NamedTuple):
    params: dict[str, type]
    return_type: type


type Scope = dict[str, Any]
type SignaturesRegistery = dict[int, Signature]


class Placeholder[T](NamedTuple):
    is_pychain_arg: bool = True


class Operation[R, **P](NamedTuple):
    func: Callable[P, R]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]


class Func[P, R]:
    _is_pychain_func: Final[bool] = True

    def __init__(
        self,
        compiled_func: Callable[[P], R],
        source_code: str,
        scope: Scope,
        param_type: type,
        return_type: type,
    ):
        self.func = compiled_func
        self.source_code = source_code
        self.scope = scope
        self.param_type = param_type
        self.return_type = return_type

    def __call__(self, arg: P) -> R:
        return self.func(arg)

    def __repr__(self) -> str:
        indented_code: str = textwrap.indent(self.source_code, "    ")
        return f"pychain.Func\n-- Source --\n{indented_code}"


def get_placeholder[T](dtype: type[T] | T) -> T:
    return Placeholder()  # type: ignore


def is_placeholder(obj: Any) -> bool:
    return getattr(obj, "is_pychain_arg", False) is True


def check_func(obj: Any) -> TypeGuard[Func[Any, Any]]:
    return getattr(obj, "_is_pychain_func", False) is True
