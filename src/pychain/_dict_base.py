import functools as ft
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

import cytoolz as cz

from ._lazyfuncs import (
    TransformFunc,
    CheckFunc,
    ProcessFunc,
    merge,
    dissoc,
)
from ._core import AbstractChain
from ._executors import Checker, Converter

if TYPE_CHECKING:
    from ._implementations import DictChain


@dataclass(slots=True, frozen=True, repr=False)
class BaseDictChain[K, V](AbstractChain[dict[K, V]]):
    @property
    def convert_values_to(self) -> Converter[V]:
        """
        Returns a Converter for the dictionary's values.

        Example:
            >>> chain = BaseDictChain({"a": 1, "b": 2})
            >>> chain.convert_values_to.list()
            [1, 2]
        """
        return Converter(_value=self.unwrap().values())

    @property
    def convert_keys_to(self) -> Converter[K]:
        """
        Returns a Converter for the dictionary's keys.

        Example:
            >>> chain = BaseDictChain({"a": 1, "b": 2})
            >>> chain.convert_keys_to.list()
            ['a', 'b']
        """
        return Converter(_value=self.unwrap().keys())

    @property
    def convert_items_to(self) -> Converter[tuple[K, V]]:
        """
        Returns a Converter for the dictionary's items.

        Example:
            >>> chain = BaseDictChain({"a": 1, "b": 2})
            >>> chain.convert_items_to.list()
            [('a', 1), ('b', 2)]
        """
        return Converter(_value=self.unwrap().items())

    @property
    def check_if_values(self) -> Checker[V]:
        """
        Returns a Checker for the dictionary's values.
        """
        return Checker(_value=self.unwrap().values())

    @property
    def check_if_keys(self) -> Checker[K]:
        """
        Returns a Checker for the dictionary's keys.
        """
        return Checker(_value=self.unwrap().keys())

    @property
    def check_if_items(self) -> Checker[tuple[K, V]]:
        """
        Returns a Checker for the dictionary's items.
        """
        return Checker(_value=self.unwrap().items())

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
            _pipeline=[cz.functoolz.compose_left(*self._pipeline, f)],
        )  # type: ignore

    def filter_on_key(self, key: K, predicate: CheckFunc[V]) -> Self:
        """
        Filter items where predicate is True for the given key.
        Example:
            >>> chain = BaseDictChain({"a": 1, "b": 2, "c": 3})
            >>> chain.filter_on_key("b", lambda v: v > 1).unwrap()
            {'b': 2}
        """
        return self.filter_items(lambda kv: kv[0] == key and predicate(kv[1]))

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
        return self.into(f=ft.partial(cz.dicttoolz.itemmap, f))

    def map_keys[K1](self, f: TransformFunc[K, K1]) -> "DictChain[K1, V]":
        """
        Maps a function over keys (see cytoolz.keymap).

        Example:
            >>> chain = BaseDictChain({"a": 1})
            >>> chain.map_keys(str.upper).unwrap()
            {'A': 1}
        """
        return self.into(f=ft.partial(cz.dicttoolz.keymap, f))

    def map_values[V1](self, f: TransformFunc[V, V1]) -> "DictChain[K, V1]":
        """
        Maps a function over values (see cytoolz.valmap).

        Example:
            >>> chain = BaseDictChain({"a": 1})
            >>> chain.map_values(lambda v: v + 10).unwrap()
            {'a': 11}
        """
        return self.into(f=ft.partial(cz.dicttoolz.valmap, f))

    def filter_items(self, predicate: CheckFunc[tuple[K, V]]) -> Self:
        """
        Filters (key, value) pairs by predicate (see cytoolz.itemfilter).

        Example:
            >>> chain = BaseDictChain({"a": 1, "b": 2})
            >>> chain.filter_items(lambda kv: kv[1] > 1).unwrap()
            {'b': 2}
        """
        return self.do(f=ft.partial(cz.dicttoolz.itemfilter, predicate))

    def filter_keys(self, predicate: CheckFunc[K]) -> Self:
        """
        Filters keys by predicate (see cytoolz.keyfilter).

        Example:
            >>> chain = BaseDictChain({"a": 1, "b": 2})
            >>> chain.filter_keys(lambda k: k == "a").unwrap()
            {'a': 1}
        """
        return self.do(f=ft.partial(cz.dicttoolz.keyfilter, predicate))

    def filter_values(self, predicate: CheckFunc[V]) -> Self:
        """
        Filters values by predicate (see cytoolz.valfilter).

        Example:
            >>> BaseDictChain({"a": 1, "b": 2}).filter_values(lambda v: v > 1).unwrap()
            {'b': 2}
        """
        return self.do(f=ft.partial(cz.dicttoolz.valfilter, predicate))

    def with_key(self, key: K, value: V) -> Self:
        """
        Returns a new dict with the given key set to value (see cytoolz.assoc).

        Example:
            >>> chain = BaseDictChain({"a": 1})
            >>> chain.with_key("b", 2).unwrap()
            {'a': 1, 'b': 2}
        """
        return self.do(f=ft.partial(cz.dicttoolz.assoc, key=key, value=value))

    def with_nested_key(self, keys: Iterable[K] | K, value: V) -> Self:
        """
        Returns a new dict with a nested key set to value (see cytoolz.assoc_in).

        Example:
            >>> chain = BaseDictChain({"a": {"b": 1}})
            >>> chain.with_nested_key(["a", "c"], 2).unwrap()
            {'a': {'b': 1, 'c': 2}}
        """
        return self.do(f=ft.partial(cz.dicttoolz.assoc_in, keys=keys, value=value))

    def update_in(self, *keys: K, f: ProcessFunc[V]) -> Self:
        """
        Updates a value at a nested path using a function (see cytoolz.update_in).

        Example:
            >>> chain = BaseDictChain({"a": {"b": 1}})
            >>> chain.update_in("a", "b", f=lambda v: v + 10).unwrap()
            {'a': {'b': 11}}
        """
        return self.do(f=ft.partial(cz.dicttoolz.update_in, keys=keys, func=f))

    def merge(self, *others: dict[K, V]) -> Self:
        """
        Merges with other dicts (see cytoolz.merge).

        Example:
            >>> BaseDictChain({"a": 1}).merge({"b": 2}).unwrap()
            {'a': 1, 'b': 2}
        """
        return self.do(f=ft.partial(merge, others=others))

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
        return self.do(f=ft.partial(cz.dicttoolz.merge_with, f, *others))

    def drop(self, *keys: K) -> Self:
        """
        Removes keys from the dictionary (see cytoolz.dissoc).

        Example:
            >>> chain = BaseDictChain({"a": 1, "b": 2})
            >>> chain.drop("a").unwrap()
            {'b': 2}
        """
        return self.do(f=ft.partial(dissoc, keys=keys))
