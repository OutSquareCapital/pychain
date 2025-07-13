from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from ..._fn import fn, dc
from ..._protocols import CheckFunc, ProcessFunc, TransformFunc
from ._core import AbstractChain

if TYPE_CHECKING:
    from .._main import DictChain


@dataclass(slots=True, frozen=True, repr=False)
class BaseDictChain[K, V](AbstractChain[dict[K, V]]):

    def into[K1, V1](
        self, f: TransformFunc[dict[K, V], dict[K1, V1]]
    ) -> "DictChain[K1, V1]":
        """
        Transforms the dictionary using the provided function, returning a new chain.

        Example:
            >>> chain = BaseDictChain({"a": 1, "b": 2})
            >>> chain.into(lambda d: {k: v + 1 for k, v in d.items()}).unwrap()
            {'a': 2, 'b': 3}
        """
        return self.__class__(
            _value=self._value,
            _pipeline=[fn.compose(*self._pipeline, f)],
        )  # type: ignore

    def map_items[K1, V1](
        self,
        f: TransformFunc[tuple[K, V], tuple[K1, V1]],
    ) -> "DictChain[K1, V1]":
        """
        Maps a function over (key, value) pairs (see cytoolz.itemmap).

        Example:
            >>> chain = BaseDictChain({"a": 1})
            >>> chain.map_items(lambda kv: (kv[0].upper(), kv[1] * 2)).unwrap()
            {'A': 2}
        """
        return self.into(f=dc.map_items(f=f))

    def map_keys[K1](self, f: TransformFunc[K, K1]) -> "DictChain[K1, V]":
        """
        Maps a function over keys (see cytoolz.keymap).

        Example:
            >>> chain = BaseDictChain({"a": 1})
            >>> chain.map_keys(str.upper).unwrap()
            {'A': 1}
        """
        return self.into(f=dc.map_keys(f))

    def map_values[V1](self, f: TransformFunc[V, V1]) -> "DictChain[K, V1]":
        """
        Maps a function over values (see cytoolz.valmap).

        Example:
            >>> chain = BaseDictChain({"a": 1})
            >>> chain.map_values(lambda v: v + 10).unwrap()
            {'a': 11}
        """
        return self.into(f=dc.map_values(f=f))

    def filter_items(self, predicate: CheckFunc[tuple[K, V]]) -> Self:
        """
        Filters (key, value) pairs by predicate (see cytoolz.itemfilter).

        Example:
            >>> chain = BaseDictChain({"a": 1, "b": 2})
            >>> chain.filter_items(lambda kv: kv[1] > 1).unwrap()
            {'b': 2}
        """
        return self.do(f=dc.filter_items(predicate=predicate))

    def select(self, predicate: CheckFunc[K]) -> Self:
        """
        Select keys by predicate (see cytoolz.keyfilter).

        Example:
            >>> chain = BaseDictChain({"a": 1, "b": 2})
            >>> chain.select(lambda k: k == "a").unwrap()
            {'a': 1}
        """
        return self.do(f=dc.filter_keys(predicate=predicate))

    def filter(self, predicate: CheckFunc[V]) -> Self:
        """
        Filters values by predicate (see cytoolz.valfilter).

        Example:
            >>> BaseDictChain({"a": 1, "b": 2}).filter(lambda v: v > 1).unwrap()
            {'b': 2}
        """
        return self.do(f=dc.filter_values(predicate=predicate))

    def filter_on_key(self, key: K, predicate: CheckFunc[V]) -> Self:
        """
        Filter items where predicate is True for the given key.

        Example:
            >>> chain = BaseDictChain({"a": 1, "b": 2, "c": 3})
            >>> chain.filter_on_key("b", lambda v: v > 1).unwrap()
            {'b': 2}
        """
        return self.do(dc.filter_on_key(key=key, predicate=predicate))

    def with_key(self, key: K, value: V) -> Self:
        """
        Returns a new dict with the given key set to value (see cytoolz.assoc).

        Example:
            >>> chain = BaseDictChain({"a": 1})
            >>> chain.with_key("b", 2).unwrap()
            {'a': 1, 'b': 2}
        """
        return self.do(f=dc.with_key(key=key, value=value))

    def with_nested_key(self, keys: Iterable[K] | K, value: V) -> Self:
        """
        Returns a new dict with a nested key set to value (see cytoolz.assoc_in).

        Example:
            >>> chain = BaseDictChain({"a": {"b": 1}})
            >>> chain.with_nested_key(["a", "c"], 2).unwrap()
            {'a': {'b': 1, 'c': 2}}
        """
        return self.do(f=dc.with_nested_key(keys=keys, value=value))

    def update_in(self, *keys: K, f: ProcessFunc[V]) -> Self:
        """
        Updates a value at a nested path using a function (see cytoolz.update_in).

        Example:
            >>> chain = BaseDictChain({"a": {"b": 1}})
            >>> chain.update_in("a", "b", f=lambda v: v + 10).unwrap()
            {'a': {'b': 11}}
        """
        return self.do(f=dc.update_in(*keys, f=f))

    def merge(self, *others: dict[K, V]) -> Self:
        """
        Merges with other dicts (see cytoolz.merge).

        Example:
            >>> BaseDictChain({"a": 1}).merge({"b": 2}).unwrap()
            {'a': 1, 'b': 2}
        """
        return self.do(f=dc.merge(others=others))

    def merge_with(self, f: Callable[..., V], *others: dict[K, V]) -> Self:
        """
        Merges with other dicts, combining values with a function (see cytoolz.merge_with).

        Example:
            >>> BaseDictChain({"first": 1, "second": 2}).merge_with(
            ...     sum,
            ...     {"first": 1, "second": 2},
            ...     {"first": 1, "second": 2, "third": 3},
            ... ).unwrap()
            {'first': 3, 'second': 6, 'third': 3}
        """
        return self.do(f=dc.merge_with(f, *others))

    def drop(self, *keys: K) -> Self:
        """
        Removes keys from the dictionary (see cytoolz.dissoc).

        Example:
            >>> chain = BaseDictChain({"a": 1, "b": 2})
            >>> chain.drop("a").unwrap()
            {'b': 2}
        """
        return self.do(f=dc.drop(keys=keys))

    def flatten_keys(self) -> "DictChain[str, V]":
        return self.into(f=dc.flatten_keys())
