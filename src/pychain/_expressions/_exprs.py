from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, Literal
from .._compilers import Compiler
from .._protocols import get_placeholder, Func, Operation, Process, Transform
from .._ast_parsers import TypeTracker


class BaseExpr[P, R](ABC):
    def __init__(
        self, pipeline: list[Operation[Any, Any]], tracker: TypeTracker
    ) -> None:
        self._pipeline = pipeline
        self._tracker = tracker

    def _new(self, op: Operation[Any, Any]) -> Any:
        self._tracker.update(op)
        return self.__class__(self._pipeline + [op], self._tracker)

    def __repr__(self):
        return f"class {self.__class__.__name__}(pipeline:\n{self._pipeline.__repr__()})\n)"

    @abstractmethod
    def _do(self, f: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    def into(self, obj: Any) -> Any:
        raise NotImplementedError

    @property
    @abstractmethod
    def _arg(self) -> Any:
        raise NotImplementedError

    def collect(
        self, backend: Literal["python", "numba", "cython"] = "python"
    ) -> Func[P, R]:
        return Compiler(self._pipeline, self._tracker).run(backend=backend)


class Expr[P, R](BaseExpr[P, R]):
    @property
    def _arg(self):
        return get_placeholder(R)

    def _do[T](self, func: Callable[..., T], *args: Any, **kwargs: Any) -> "Expr[P, T]":
        op = Operation(func=func, args=args, kwargs=kwargs)
        return self._new(op)

    def into[T](self, obj: Transform[R, T]):
        return self._do(obj, self._arg)

    def compose(self, *fns: Process[R]):
        expr = self
        for f in fns:
            expr = expr._do(f, get_placeholder(R))
        return expr
