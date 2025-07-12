import operator
from collections.abc import Iterable, Iterator
import cytoolz as cz
from functools import partial
from .._protocols import ThreadFunc, TransformFunc

call = operator.call
attr = operator.attrgetter
item = operator.itemgetter
method = operator.methodcaller
compose = cz.functoolz.compose_left
pipe = cz.functoolz.pipe


def compose_on_iter[V, V1](*fns: TransformFunc[V, V1]) -> partial[Iterator[V1]]:
    return partial(map, cz.functoolz.compose_left(*fns))


def _thread_first[T](val: T, fns: Iterable[ThreadFunc[T]]) -> T:
    return cz.functoolz.thread_first(val, *fns)


def _thread_last[T](val: T, fns: Iterable[ThreadFunc[T]]) -> T:
    return cz.functoolz.thread_last(val, *fns)

def thread_first[T](fns: Iterable[ThreadFunc[T]]) -> partial[T]:
    return partial(_thread_first, fns=fns)

def thread_last[T](fns: Iterable[ThreadFunc[T]]) -> partial[T]:
    return partial(_thread_last, fns=fns)