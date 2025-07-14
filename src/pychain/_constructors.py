from collections.abc import Callable
from typing import Any
import cytoolz as cz
import pandas as pd
import polars as pl

from ._iter import Iter
from ._struct import Struct
from ._exprs import OpConstructor, When


def from_func[T, T1](value: T, f: Callable[[T], T1]):
    """
    Create an Iter by iteratively applying a function to a value (infinite iterator).

    Example:
        >>> from_func(1, lambda x: x + 1).head(3).to_list()
        [1, 2, 3]
    """
    return Iter(cz.itertoolz.iterate(func=f, x=value))


def from_range(start: int, stop: int, step: int = 1):
    """
    Create an Iter from a range of integers.

    Example:
        >>> from_range(0, 3).to_list()
        [0, 1, 2]
    """
    return Iter(range(start, stop, step))


def read_parquet(file_path: str):
    """
    Read a Parquet file into a Struct (columnar format).

    Example:
        >>> read_parquet("data.parquet").convert_keys_to.list()  # doctest: +SKIP
        ['col1', 'col2', ...]
    """
    return from_pl(pl.read_parquet(file_path))


def read_csv(file_path: str):
    """
    Read a CSV file into a Struct (columnar format).

    Example:
        >>> read_csv("data.csv").convert_keys_to.list()  # doctest: +SKIP
        ['col1', 'col2', ...]
    """
    return from_pl(pl.read_csv(file_path))


def read_json(file_path: str):
    """
    Read a JSON file into a Struct (columnar format).

    Example:
        >>> read_json("data.json").convert_keys_to.list()  # doctest: +SKIP
        ['col1', 'col2', ...]
    """
    return from_pl(pl.read_json(file_path))


def read_ndjson(file_path: str):
    """
    Read a newline-delimited JSON file into a Struct (columnar format).

    Example:
        >>> read_ndjson("data.ndjson").convert_keys_to.list()  # doctest: +SKIP
        ['col1', 'col2', ...]
    """
    return from_pl(pl.read_ndjson(file_path))


def from_pl(df: pl.DataFrame):
    """
    Convert a Polars DataFrame to a Struct (columnar format).
    """
    return Struct(df.to_dict(as_series=False))


def from_pd(df: pd.DataFrame):
    """
    Convert a pandas DataFrame to a Struct (columnar format).
    """
    return Struct(df.to_dict(orient="list"))  # type: ignore[return-value]


def when[T, R](predicate:Callable[[T], bool]) -> When[T, Any]:
    return When[T, R](predicate)


op = OpConstructor()
