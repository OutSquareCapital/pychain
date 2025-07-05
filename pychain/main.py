from collections.abc import Mapping
from pychain.iterchain import (
    IterChain,
    ScalarChain,
    DictChain,
    IterDictChain,
)
from collections.abc import Iterable


def from_scalar[T](value: T) -> ScalarChain[T]:
    return ScalarChain(value=value)

def from_iterable[T](data: Iterable[T]) -> IterChain[T]:
    return IterChain(value=data)


def from_range(start: int, stop: int, step: int = 1) -> IterChain[int]:
    return IterChain(value=range(start, stop, step))


def from_dict_of_iterables[K, V](
    data: Mapping[K, Iterable[V]],
) -> IterDictChain[K, V]:
    return IterDictChain(value={k: from_iterable(data=v) for k, v in data.items()})


def from_dict[K, V](data: dict[K, V]) -> DictChain[K, V]:
    return DictChain(value=data)
