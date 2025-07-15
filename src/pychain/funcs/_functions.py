import operator
from collections.abc import Iterable, Iterator, Callable
from functools import partial
from typing import Any
import cytoolz.functoolz as ftz
from copy import deepcopy
from .._protocols import ThreadFunc, TransformFunc

call = operator.call
attr = operator.attrgetter
item = operator.itemgetter
method = operator.methodcaller
compose = ftz.compose_left
pipe = ftz.pipe
identity = ftz.identity
clone = deepcopy

class Sign[R, *Ts, **P]:
    """
    Un composeur de fonctions simple et robuste.

    Prend une fonction maîtresse et une série de fonctions internes. Lorsqu'il
    est appelé, il exécute chaque fonction interne avec les arguments fournis,
    puis passe les résultats collectés à la fonction maîtresse.

    Exemple : Sign(f, g, h)(x) devient f(g(x), h(x))
    """

    __slots__ = ("_master_func", "_internal_funcs")

    def __init__(
        self, master_func: Callable[[*Ts], R], *internal_funcs: Callable[P, Any]
    ) -> None:
        self._master_func: Callable[[*Ts], R] = master_func
        self._internal_funcs: tuple[Callable[P, Any], ...] = internal_funcs

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        results: list[Any] = [f(*args, **kwargs) for f in self._internal_funcs]

        return self._master_func(*results)  # type: ignore[return-value]


def to_obj[T](obj: Callable[..., T], *args: Any, **kwargs: Any) -> partial[T]:
    return partial(obj, *args, **kwargs)

def compose_on_iter[V, V1](*fns: TransformFunc[V, V1]) -> partial[Iterator[V1]]:
    return partial(map, ftz.compose_left(*fns))


def _thread_first[T](val: T, fns: Iterable[ThreadFunc[T]]) -> T:
    return ftz.thread_first(val, *fns)


def _thread_last[T](val: T, fns: Iterable[ThreadFunc[T]]) -> T:
    return ftz.thread_last(val, *fns)


def thread_first[T](fns: Iterable[ThreadFunc[T]]) -> partial[T]:
    return partial(_thread_first, fns=fns)


def thread_last[T](fns: Iterable[ThreadFunc[T]]) -> partial[T]:
    return partial(_thread_last, fns=fns)
