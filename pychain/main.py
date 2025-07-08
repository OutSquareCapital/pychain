from collections.abc import Callable, Iterable
from typing import Any, Hashable

import pandas as pd
import polars as pl
from numpy.typing import NDArray

from pychain.implementations import DictChain, IterChain, ScalarChain


def read_parquet(file_path: str) -> DictChain[str, list[Any]]:
    return from_pl(pl.read_parquet(file_path))


def read_csv(file_path: str) -> DictChain[str, list[Any]]:
    return from_pl(pl.read_csv(file_path))


def read_json(file_path: str) -> DictChain[str, list[Any]]:
    return from_pl(pl.read_json(file_path))


def read_ndjson(file_path: str) -> DictChain[str, list[Any]]:
    return from_pl(pl.read_ndjson(file_path))


def from_pl(df: pl.DataFrame) -> DictChain[str, list[Any]]:
    return from_dict(df.to_dict(as_series=False))


def from_pd(df: pd.DataFrame) -> DictChain[Hashable, list[Any]]:
    return from_dict(df.to_dict(orient="list"))  # type: ignore


def from_np[T: NDArray[Any]](arr: T) -> IterChain[T]:
    return IterChain(_value=arr)


def from_scalar[T](value: T) -> ScalarChain[T]:
    return ScalarChain(_value=value)


def from_iterable[T](data: Iterable[T]) -> IterChain[T]:
    return IterChain(_value=data)


def from_func[T, T1](value: T, f: Callable[[T], T1]) -> IterChain[T1]:
    return IterChain.from_func(value=value, f=f)


def from_range(start: int, stop: int, step: int = 1) -> IterChain[int]:
    return IterChain.from_range(start=start, stop=stop, step=step)


def from_dict[K, V](data: dict[K, V]) -> DictChain[K, V]:
    return DictChain(_value=data)


def from_dict_of_iterables[K, V](
    data: dict[K, Iterable[V]],
) -> DictChain[K, IterChain[V]]:
    return DictChain.from_dict_of_iterables(value=data)
