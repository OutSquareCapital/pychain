from collections.abc import Callable, Iterable
from typing import Self

import polars as pl

from .._protocols import CheckFunc, ProcessFunc, TransformFunc

class Struct[K, V]:
    _value: dict[K, V]
    _pipeline: list[Callable[[dict[K, V]], dict[K, V]]]

    def __init__(
        self,
        _value: dict[K, V],
        _pipeline: list[Callable[[dict[K, V]], dict[K, V]]] | None = None,
    ) -> None: ...
    def clone(self) -> Self: ...
    def unwrap(self) -> dict[K, V]: ...
    def _into[K1, V1](
        self, f: Callable[[dict[K, V]], dict[K1, V1]]
    ) -> "Struct[K1, V1]": ...
    def map_keys[K1](self, f: TransformFunc[K, K1]) -> "Struct[K1, V]":
        """
        map a function over keys (see cytoolz.keymap).

        Example:
            >>> chain = BaseStruct({"a": 1})
            >>> chain.map_keys(str.upper).unwrap()
            {'A': 1}
        """
        ...

    def map_values[V1](self, f: TransformFunc[V, V1]) -> "Struct[K, V1]":
        """
        map a function over values (see cytoolz.valmap).

        Example:
            >>> chain = BaseStruct({"a": 1})
            >>> chain.map_values(lambda v: v + 10).unwrap()
            {'a': 11}
        """
        ...
    def select(self, predicate: CheckFunc[K]) -> Self:
        """
        Select keys by predicate (see cytoolz.keyfilter).

        Example:
            >>> chain = BaseStruct({"a": 1, "b": 2})
            >>> chain.select(lambda k: k == "a").unwrap()
            {'a': 1}
        """
        ...

    def filter(self, predicate: CheckFunc[V]) -> Self:
        """
        Filters values by predicate (see cytoolz.valfilter).

        Example:
            >>> BaseStruct({"a": 1, "b": 2}).filter(lambda v: v > 1).unwrap()
            {'b': 2}
        """
        ...

    def filter_on_key(self, key: K, predicate: CheckFunc[V]) -> Self:
        """
        Filter items where predicate is True for the given key.

        Example:
            >>> chain = BaseStruct({"a": 1, "b": 2, "c": 3})
            >>> chain.filter_on_key("b", lambda v: v > 1).unwrap()
            {'b': 2}
        """
        ...

    def with_key(self, key: K, value: V) -> Self:
        """
        ...

        Example:
            >>> chain = BaseStruct({"a": 1})
            >>> chain.with_key("b", 2).unwrap()
            {'a': 1, 'b': 2}
        """
        ...

    def with_nested_key(self, keys: Iterable[K] | K, value: V) -> Self:
        """
        ...

        Example:
            >>> chain = BaseStruct({"a": {"b": 1}})
            >>> chain.with_nested_key(["a", "c"], 2).unwrap()
            {'a': {'b': 1, 'c': 2}}
        """
        ...

    def update_in(self, *keys: K, f: ProcessFunc[V]) -> Self:
        """
        Updates a value at a nested path using a function (see cytoolz.update_in).

        Example:
            >>> chain = BaseStruct({"a": {"b": 1}})
            >>> chain.update_in("a", "b", f=lambda v: v + 10).unwrap()
            {'a': {'b': 11}}
        """
        ...

    def merge(self, *others: dict[K, V]) -> Self:
        """
        Merges with other dicts (see cytoolz.merge).

        Example:
            >>> BaseStruct({"a": 1}).merge({"b": 2}).unwrap()
            {'a': 1, 'b': 2}
        """
        ...

    def merge_with(self, f: Callable[..., V], *others: dict[K, V]) -> Self:
        """
        Merges with other dicts, combining values with a function (see cytoolz.merge_with).

        Example:
            >>> BaseStruct({"first": 1, "second": 2}).merge_with(
            ...     sum,
            ...     {"first": 1, "second": 2},
            ...     {"first": 1, "second": 2, "third": 3},
            ... ).unwrap()
            {'first': 3, 'second': 6, 'third': 3}
        """
        ...

    def drop(self, *keys: K) -> Self:
        """
        Removes keys from the dictionary (see cytoolz.dissoc).

        Example:
            >>> chain = BaseStruct({"a": 1, "b": 2})
            >>> chain.drop("a").unwrap()
            {'b': 2}
        """
        ...

    def flatten_keys(self) -> "Struct[str, V]": ...
    def to_obj[T](self, obj: Callable[[dict[K, V]], T]) -> T: ...
    def to_frame(self) -> pl.DataFrame: ...
