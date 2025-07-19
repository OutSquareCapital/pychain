from collections.abc import Callable
from typing import Any
from ._protocols import ProcessFunc
from ._compilers import collect_ast, collect_scope
from ._func import Func
from functools import partial
from copy import deepcopy
from abc import ABC, abstractmethod

def collect_pipeline[P](pipeline: list[Callable[[P], Any]]) -> Func[P, Any]:
        try:
            compiled_func, source_code = collect_ast(pipeline)
        except Exception as e:
            print(f"Error collecting AST: {e}")
            compiled_func, source_code = collect_scope(pipeline)
        return Func(compiled_func, source_code)


class BaseExpr[P, R](ABC):
    __slots__ = "_pipeline"
    _pipeline: list[Callable[..., Any]]

    def __init__(self, pipeline: list[Callable[[P], Any]]) -> None:
        self._pipeline = pipeline

    def __repr__(self):
        return f"class {self.__class__.__name__}(pipeline:\n{self._pipeline.__repr__()})\n)"

    @abstractmethod
    def _do[T](self, f: Any) -> Any:
        raise NotImplementedError("Subclasses must implement _do method.")

    def into_partial[T](
        self, f: Callable[[P], T], *args: Any, **kwargs: Any
    ):
        return self._do(partial(f, *args, **kwargs))

    def compose(self, *fns: ProcessFunc[R]):
        for op in fns:
            self._pipeline.append(op)
        return self

    def collect(self) -> Func[P, R]:
        return collect_pipeline(self._pipeline)

    def clone(self):
        return self._do(deepcopy)
