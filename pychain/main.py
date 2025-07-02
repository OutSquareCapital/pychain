from collections.abc import Iterable

from pychain.dictchain import DictChain
from pychain.iterchain import IterChain
from pychain.scalars import ScalarChain, NumericChain


def from_scalar[T](value: T) -> ScalarChain[T]:
    return ScalarChain(value=value)


def from_numeric[T: int | float](value: T) -> NumericChain[T]:
    return NumericChain(value=value)


def from_iterable[T](data: Iterable[T]) -> IterChain[T]:
    return IterChain(value=data)

def from_range(start: int, stop: int, step: int = 1) -> IterChain[int]:
    return IterChain(value=range(start, stop, step))

def from_dict[K, V](data: dict[K, V]) -> DictChain[K, V]:
    return DictChain(value=data)
