from collections.abc import Callable
from typing import Any, Hashable

import cytoolz as cz
import pandas as pd
import polars as pl

from ._chains import Iter, Struct
from ._exprs import ChainableOp, OpConstructor, When


def from_func[T, T1](value: T, f: Callable[[T], T1]) -> Iter[T1]:
    """
    Create an Iter by iteratively applying a function to a value (infinite iterator).

    Example:
        >>> from_func(1, lambda x: x + 1).head(3).to_list()
        [1, 2, 3]
    """
    return Iter(cz.itertoolz.iterate(func=f, x=value))


def from_range(start: int, stop: int, step: int = 1) -> Iter[int]:
    """
    Create an Iter from a range of integers.

    Example:
        >>> from_range(0, 3).to_list()
        [0, 1, 2]
    """
    return Iter(range(start, stop, step))


def read_parquet(file_path: str) -> Struct[str, list[Any]]:
    """
    Read a Parquet file into a Struct (columnar format).

    Example:
        >>> read_parquet("data.parquet").convert_keys_to.list()  # doctest: +SKIP
        ['col1', 'col2', ...]
    """
    return from_pl(pl.read_parquet(file_path))


def read_csv(file_path: str) -> Struct[str, list[Any]]:
    """
    Read a CSV file into a Struct (columnar format).

    Example:
        >>> read_csv("data.csv").convert_keys_to.list()  # doctest: +SKIP
        ['col1', 'col2', ...]
    """
    return from_pl(pl.read_csv(file_path))


def read_json(file_path: str) -> Struct[str, list[Any]]:
    """
    Read a JSON file into a Struct (columnar format).

    Example:
        >>> read_json("data.json").convert_keys_to.list()  # doctest: +SKIP
        ['col1', 'col2', ...]
    """
    return from_pl(pl.read_json(file_path))


def read_ndjson(file_path: str) -> Struct[str, list[Any]]:
    """
    Read a newline-delimited JSON file into a Struct (columnar format).

    Example:
        >>> read_ndjson("data.ndjson").convert_keys_to.list()  # doctest: +SKIP
        ['col1', 'col2', ...]
    """
    return from_pl(pl.read_ndjson(file_path))


def from_pl(df: pl.DataFrame) -> Struct[str, list[Any]]:
    """
    Convert a Polars DataFrame to a Struct (columnar format).
    """
    return Struct(df.to_dict(as_series=False))


def from_pd(df: pd.DataFrame) -> Struct[Hashable, list[Any]]:
    """
    Convert a pandas DataFrame to a Struct (columnar format).
    """
    return Struct(df.to_dict(orient="list")) # type: ignore[return-value]

def when[T, R](predicate: ChainableOp | Callable[[T], bool]) -> When[T, Any]:
    return When[T, R](predicate)


op = OpConstructor()
