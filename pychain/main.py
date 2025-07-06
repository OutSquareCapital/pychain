from collections.abc import Iterable, Mapping, Iterator

from pychain.iterchain import DictChain, IterChain, ScalarChain
import pychain.lazyfuncs as lf
import cytoolz as cz


def from_scalar[T](value: T) -> ScalarChain[T]:
    return ScalarChain(_value=value)


def from_iterable[T](data: Iterable[T]) -> IterChain[T]:
    return IterChain(_value=data)


def from_range(start: int, stop: int, step: int = 1) -> IterChain[int]:
    return IterChain(_value=range(start, stop, step))


def from_dict_of_iterables[K, V](
    data: Mapping[K, Iterable[V]],
) -> DictChain[K, IterChain[V]]:
    return DictChain(_value={k: from_iterable(data=v) for k, v in data.items()})


def from_dict[K, V](data: dict[K, V]) -> DictChain[K, V]:
    return DictChain(_value=data)


def iterate[T](value: T, f: lf.ProcessFunc[T]) -> Iterator[T]:
    return cz.itertoolz.iterate(func=f, x=value)
