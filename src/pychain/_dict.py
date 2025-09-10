from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Concatenate, Self

import cytoolz as cz

from ._core import Check, CommonBase, Process, Transform, iter_on

if TYPE_CHECKING:
    from pychain import Iter


class Dict[KT, VT](CommonBase[dict[KT, VT]]):
    _data: dict[KT, VT]
    __slots__ = ("_data",)
    """
    Public eager Dict wrapper providing chainable dict operations.

    Methods return Dict instances wrapping the underlying mapping.
    """

    def into[**P, KU, VU](
        self,
        func: Callable[Concatenate[dict[KT, VT], P], dict[KU, VU]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> "Dict[KU, VU]":
        return Dict(func(self._data, *args, **kwargs))

    # BUILTINS------------------------------------------------------------------

    def into_keys(self) -> "Iter[KT]":
        """Return a Iter of the dict's keys.

        **Example:**
            >>> Dict({1: 2}).into_keys().into_list()
            [1]
        """

        return iter_on(self._data.keys())

    def into_values(self) -> "Iter[VT]":
        """Return a Iter of the dict's values.

        **Example:**
            >>> Dict({1: 2}).into_values().into_list()
            [2]
        """
        return iter_on(self._data.values())

    def into_items(self) -> "Iter[tuple[KT, VT]]":
        """Return a Iter of the dict's items.

        **Example:**
            >>> Dict({1: 2}).into_items().into_list()
            [(1, 2)]
        """

        return iter_on(self._data.items())

    def copy(self) -> Self:
        """Return a shallow copy of the dict."""
        return self._new(self._data.copy())

    def update(self, *others: dict[KT, VT]) -> Self:
        """Update the dict with other(s) dict(s) and return self for convenience.

        **Warning**: This modifies the dict in place.
        """
        self._data.update(*others)
        return self

    # CYTOOLZ------------------------------------------------------------------

    def filter_keys(self, predicate: Check[KT]) -> Self:
        """Return a new Dict containing keys that satisfy predicate.

        **Example:**
            >>> Dict({1: 2, 3: 4}).filter_keys(lambda k: k % 2 == 0)
            {}
        """
        return self._new(cz.dicttoolz.keyfilter(predicate, self._data))

    def filter_values(self, predicate: Check[VT]) -> Self:
        """Return a new Dict containing items whose values satisfy predicate.

        **Example:**
            >>> Dict({1: 2, 3: 4}).filter_values(lambda v: v > 2)
            {3: 4}
        """
        return self._new(cz.dicttoolz.valfilter(predicate, self._data))

    def filter_items(
        self,
        predicate: Check[tuple[KT, VT]],
    ) -> Self:
        """Filter items by predicate applied to (key, value) tuples.

        **Example:**
            >>> Dict({1: 2, 3: 4}).filter_items(lambda kv: kv[1] > 2)
            {3: 4}
        """
        return self._new(cz.dicttoolz.itemfilter(predicate, self._data))

    def with_key(self, key: KT, value: VT) -> Self:
        """Return a new Dict with key set to value.

        **Example:**
            >>> Dict({}).with_key("x", 1)
            {'x': 1}
        """
        return self._new(cz.dicttoolz.assoc(self._data, key=key, value=value))

    def with_nested_key(self, keys: Iterable[KT] | KT, value: VT) -> Self:
        """Set a nested key path and return a new Dict.

        **Example:**
            >>> Dict({}).with_nested_key(["a", "b"], 1)
            {'a': {'b': 1}}
        """
        return self._new(cz.dicttoolz.assoc_in(self._data, keys=keys, value=value))

    def update_in(self, *keys: KT, f: Process[VT]) -> Self:
        """Update a nested value via function f and return a new Dict.

        **Example:**
            >>> Dict({"a": {"b": 1}}).update_in("a", "b", f=lambda x: x + 1)
            {'a': {'b': 2}}
        """
        return self._new(cz.dicttoolz.update_in(self._data, keys=keys, func=f))

    def merge(self, *others: dict[KT, VT]) -> Self:
        """Merge other dicts into this one and return a new Dict.

        **Example:**
            >>> Dict({1: 2}).merge({3: 4})
            {1: 2, 3: 4}
        """
        return self._new(cz.dicttoolz.merge(self._data, *others))

    def merge_with(
        self, f: Callable[[Iterable[VT]], VT], *others: dict[KT, VT]
    ) -> Self:
        """Merge dicts using f to combine values for duplicate keys.

        **Example:**
            >>> Dict({1: 1}).merge_with(sum, {1: 2})
            {1: 3}
        """
        return self._new(cz.dicttoolz.merge_with(f, self._data, *others))

    def drop(self, *keys: KT) -> Self:
        """Return a new Dict with given keys removed.

        **Example:**
            >>> Dict({1: 2, 3: 4}).drop(1)
            {3: 4}
        """
        return self._new(cz.dicttoolz.dissoc(self._data, *keys))

    def map_keys[T](self, f: Transform[KT, T]) -> "Dict[T, VT]":
        """Return a Dict with keys transformed by f.

        **Example:**
            >>> Dict({1: "a"}).map_keys(str)
            {'1': 'a'}
        """
        return Dict(cz.dicttoolz.keymap(f, self._data))

    def map_values[T](self, f: Transform[VT, T]) -> "Dict[KT, T]":
        """Return a Dict with values transformed by f.

        **Example:**
            >>> Dict({1: 1}).map_values(lambda v: v + 1)
            {1: 2}
        """
        return Dict(cz.dicttoolz.valmap(f, self._data))

    def map_items[KR, VR](
        self,
        f: Transform[tuple[KT, VT], tuple[KR, VR]],
    ) -> "Dict[KR, VR]":
        """Transform (key, value) pairs using f and return a Dict.

        **Example:**
            >>> Dict({1: 2}).map_items(lambda kv: (kv[0] + 1, kv[1] * 10))
            {2: 20}
        """
        return Dict(cz.dicttoolz.itemmap(f, self._data))
