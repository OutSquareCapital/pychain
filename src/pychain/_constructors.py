from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any, Hashable

import cytoolz as cz
import pandas as pd
import polars as pl
from numpy.typing import NDArray

from ._main import DictChain, IterChain, ScalarChain


@dataclass(slots=True)
class ChainConstructor:
    def __call__[V](self, value: V) -> ScalarChain[V]:
        """
        Wrap a scalar value in a ScalarChain for chainable operations.

        Example:
            >>> chain = ChainConstructor()
            >>> chain(42).unwrap()
            42
        """
        return ScalarChain(_value=value)

    def read_parquet(self, file_path: str) -> DictChain[str, list[Any]]:
        """
        Read a Parquet file into a DictChain (columnar format).

        Example:
            >>> chain = ChainConstructor()
            >>> chain.read_parquet("data.parquet").convert_keys_to.list()  # doctest: +SKIP
            ['col1', 'col2', ...]
        """
        return self.from_pl(pl.read_parquet(file_path))

    def read_csv(self, file_path: str) -> DictChain[str, list[Any]]:
        """
        Read a CSV file into a DictChain (columnar format).

        Example:
            >>> chain = ChainConstructor()
            >>> chain.read_csv("data.csv").convert_keys_to.list()  # doctest: +SKIP
            ['col1', 'col2', ...]
        """
        return self.from_pl(pl.read_csv(file_path))

    def read_json(self, file_path: str) -> DictChain[str, list[Any]]:
        """
        Read a JSON file into a DictChain (columnar format).

        Example:
            >>> chain = ChainConstructor()
            >>> chain.read_json("data.json").convert_keys_to.list()  # doctest: +SKIP
            ['col1', 'col2', ...]
        """
        return self.from_pl(pl.read_json(file_path))

    def read_ndjson(self, file_path: str) -> DictChain[str, list[Any]]:
        """
        Read a newline-delimited JSON file into a DictChain (columnar format).

        Example:
            >>> chain = ChainConstructor()
            >>> chain.read_ndjson("data.ndjson").convert_keys_to.list()  # doctest: +SKIP
            ['col1', 'col2', ...]
        """
        return self.from_pl(pl.read_ndjson(file_path))

    def from_iter[V](self, iterable: Iterable[V]) -> IterChain[V]:
        """
        Convert an iterable to an IterChain.

        Example:
            >>> chain = ChainConstructor()
            >>> chain.from_iter([1, 2, 3]).convert_to.list()
            [1, 2, 3]
        """
        return IterChain(iterable)

    def from_pl(self, df: pl.DataFrame) -> DictChain[str, list[Any]]:
        """
        Convert a Polars DataFrame to a DictChain (columnar format).
        """
        return DictChain(df.to_dict(as_series=False))

    def from_pd(self, df: pd.DataFrame) -> DictChain[Hashable, list[Any]]:
        """
        Convert a pandas DataFrame to a DictChain (columnar format).
        """
        return DictChain(df.to_dict(orient="list"))  # type: ignore

    def from_np[T: NDArray[Any]](self, arr: T) -> IterChain[T]:
        """
        Convert a NumPy array to an IterChain.
        """
        return IterChain(_value=arr)

    def from_func[T, T1](self, value: T, f: Callable[[T], T1]) -> IterChain[T1]:
        """
        Create an IterChain by iteratively applying a function to a value (infinite iterator).

        Example:
            >>> chain = ChainConstructor()
            >>> chain.from_func(1, lambda x: x + 1).head(3).convert_to.list()
            [1, 2, 3]
        """
        return IterChain(cz.itertoolz.iterate(func=f, x=value))

    def from_range(self, start: int, stop: int, step: int = 1) -> IterChain[int]:
        """
        Create an IterChain from a range of integers.

        Example:
            >>> chain = ChainConstructor()
            >>> chain.from_range(0, 3).convert_to.list()
            [0, 1, 2]
        """
        return IterChain(range(start, stop, step))

    def from_dict[K: Hashable, V](
        self,
        data: dict[K, V],
    ) -> DictChain[K, V]:
        """
        Convert a dict to a DictChain.

        Example:
            >>> chain = ChainConstructor()
            >>> chain.from_dict({"a": 1}).unwrap()["a"]
            1
        """
        return DictChain(_value=data)

    def from_dict_of_iterables[K, V](
        self,
        data: dict[K, Iterable[V]],
    ) -> DictChain[K, IterChain[V]]:
        """
        Convert a dict of iterables to a DictChain of IterChains.

        Example:
            >>> chain = ChainConstructor()
            >>> chain.from_dict_of_iterables({"a": [1, 2]}).unwrap()["a"].convert_to.list()
            [1, 2]
        """
        return DictChain(_value={k: IterChain(_value=v) for k, v in data.items()})


chain = ChainConstructor()
