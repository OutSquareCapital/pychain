from collections.abc import Iterable, Mapping, Callable

from pychain.iterchain import DictChain, IterChain, ScalarChain
import cytoolz as cz


def from_scalar[T](value: T) -> ScalarChain[T]:
    return ScalarChain(_value=value)


def from_iterable[T](data: Iterable[T]) -> IterChain[T]:
    return IterChain(_value=data)


def from_func[T, T1](value: T, f: Callable[[T], T1]) -> IterChain[T1]:
    return IterChain(_value=cz.itertoolz.iterate(func=f, x=value))


def from_range(start: int, stop: int, step: int = 1) -> IterChain[int]:
    return IterChain(_value=range(start, stop, step))


def from_dict_of_iterables[K, V](
    data: Mapping[K, Iterable[V]],
) -> DictChain[K, IterChain[V]]:
    return DictChain(_value={k: from_iterable(data=v) for k, v in data.items()})


def from_dict[K, V](data: dict[K, V]) -> DictChain[K, V]:
    return DictChain(_value=data)
