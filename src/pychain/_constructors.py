from collections.abc import Callable, Iterable
from typing import Any, Hashable

import pandas as pd
import polars as pl
from numpy.typing import NDArray
import cytoolz as cz
from ._implementations import DictChain, IterChain


def read_parquet(file_path: str) -> DictChain[str, list[Any]]:
    """
    Read a Parquet file into a DictChain (columnar format).

    Example:
        >>> read_parquet('data.parquet').convert_keys_to.list()  # doctest: +SKIP
        ['col1', 'col2', ...]
    """
    return from_pl(pl.read_parquet(file_path))


def read_csv(file_path: str) -> DictChain[str, list[Any]]:
    """
    Read a CSV file into a DictChain (columnar format).

    Example:
        >>> read_csv('data.csv').convert_keys_to.list()  # doctest: +SKIP
        ['col1', 'col2', ...]
    """
    return from_pl(pl.read_csv(file_path))


def read_json(file_path: str) -> DictChain[str, list[Any]]:
    """
    Read a JSON file into a DictChain (columnar format).

    Example:
        >>> read_json('data.json').convert_keys_to.list()  # doctest: +SKIP
        ['col1', 'col2', ...]
    """
    return from_pl(pl.read_json(file_path))


def read_ndjson(file_path: str) -> DictChain[str, list[Any]]:
    """
    Read a newline-delimited JSON file into a DictChain (columnar format).

    Example:
        >>> read_ndjson('data.ndjson').convert_keys_to.list()  # doctest: +SKIP
        ['col1', 'col2', ...]
    """
    return from_pl(pl.read_ndjson(file_path))


def from_pl(df: pl.DataFrame) -> DictChain[str, list[Any]]:
    """
    Convert a Polars DataFrame to a DictChain (columnar format).

    Example:
        >>> from_pl(pl.DataFrame({'a': [1, 2]})).unwrap()  # doctest: +SKIP
        {'a': [1, 2]}
    """
    return DictChain(df.to_dict(as_series=False))


def from_pd(df: pd.DataFrame) -> DictChain[Hashable, list[Any]]:
    """
    Convert a pandas DataFrame to a DictChain (columnar format).

    Example:
        >>> from_pd(pd.DataFrame({'a': [1, 2]})).unwrap()  # doctest: +SKIP
        {'a': [1, 2]}
    """
    return DictChain(df.to_dict(orient="list"))  # type: ignore


def from_np[T: NDArray[Any]](arr: T) -> IterChain[T]:
    """
    Convert a NumPy array to an IterChain.

    Example:
        >>> from_np(np.array([1, 2, 3])).convert_to.list()  # doctest: +SKIP
        [1, 2, 3]
    """
    return IterChain(_value=arr)


def from_func[T, T1](value: T, f: Callable[[T], T1]) -> IterChain[T1]:
    """
    Create an IterChain by iteratively applying a function to a value (infinite iterator).

    Example:
        >>> from_func(1, lambda x: x + 1).head(3).convert_to.list()
        [1, 2, 3]
    """
    return IterChain(cz.itertoolz.iterate(func=f, x=value))


def from_range(start: int, stop: int, step: int = 1) -> IterChain[int]:
    """
    Create an IterChain from a range of integers.

    Example:
        >>> from_range(0, 3).convert_to.list()
        [0, 1, 2]
    """
    return IterChain(range(start, stop, step))


def from_dict_of_iterables[K, V](
    data: dict[K, Iterable[V]],
) -> DictChain[K, IterChain[V]]:
    """
    Convert a dict of iterables to a DictChain of IterChains.

    Example:
        >>> from_dict_of_iterables({'a': [1, 2]}).unwrap()['a'].convert_to.list()
        [1, 2]
    """
    return DictChain(_value={k: IterChain(_value=v) for k, v in data.items()})
