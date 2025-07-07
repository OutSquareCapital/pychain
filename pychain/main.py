from collections.abc import Callable, Iterable

from pychain.implementations import DictChain, IterChain, ScalarChain


def from_scalar[T](value: T) -> ScalarChain[T]:
    return ScalarChain(_value=value)


def from_iterable[T](data: Iterable[T]) -> IterChain[T]:
    return IterChain(_value=data)


def from_func[T, T1](value: T, f: Callable[[T], T1]) -> IterChain[T1]:
    return IterChain.from_func(value=value, f=f)


def from_range(start: int, stop: int, step: int = 1) -> IterChain[int]:
    return IterChain.from_range(start=start, stop=stop, step=step)


def from_dict_of_iterables[K, V](
    data: dict[K, Iterable[V]],
) -> DictChain[K, IterChain[V]]:
    return DictChain.from_dict_of_iterables(value=data)


def from_dict[K, V](data: dict[K, V]) -> DictChain[K, V]:
    return DictChain(_value=data)
