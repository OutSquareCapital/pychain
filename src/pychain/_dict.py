from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Concatenate, Self, overload

import cytoolz as cz

from ._core import CommonBase, iter_factory

if TYPE_CHECKING:
    from ._core import Iter


class Dict[KT, VT](CommonBase[dict[KT, VT]]):
    """
    Wrapper for Python dictionaries with chainable methods.
    """

    _data: dict[KT, VT]
    __slots__ = ("_data",)

    @classmethod
    def from_zipped[KN, VN](
        cls, keys: Iterable[KN], values: Iterable[VN]
    ) -> "Dict[KN, VN]":
        """
        Create a Dict from two iterables of keys and values.

            >>> Dict.from_zipped([1, 2], ["a", "b"])
            {1: 'a', 2: 'b'}
        """
        return Dict(dict(zip(keys, values)))

    def pipe_into[**P, KU, VU](
        self,
        func: Callable[Concatenate[dict[KT, VT], P], dict[KU, VU]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> "Dict[KU, VU]":
        """
        Apply a function to the wrapped dict and return a new Dict wrapping the result.

            >>> def key_to_upper(d: dict[str, int]) -> dict[str, int]:
            ...     return {str(k).upper(): v for k, v in d.items()}
            >>>
            >>> data = {"theo": 20, "alice": 25, "bob": 30}
            >>>
            >>> Dict(data).pipe_into(key_to_upper).unwrap()
            {'THEO': 20, 'ALICE': 25, 'BOB': 30}
        """
        return Dict(func(self._data, *args, **kwargs))

    # BUILTINS------------------------------------------------------------------
    def iter_keys(self) -> Iter[KT]:
        """
        Return a Iter of the dict's keys.

            >>> Dict({1: 2}).iter_keys().to_list()
            [1]
        """
        return iter_factory(self._data.keys())

    def iter_values(self) -> Iter[VT]:
        """
        Return a Iter of the dict's values.

            >>> Dict({1: 2}).iter_values().to_list()
            [2]
        """
        return iter_factory(self._data.values())

    def iter_items(self) -> Iter[tuple[KT, VT]]:
        """
        Return a Iter of the dict's items.

            >>> Dict({1: 2}).iter_items().to_list()
            [(1, 2)]
        """
        return iter_factory(self._data.items())

    def copy(self) -> Self:
        """Return a shallow copy of the dict."""
        return self._new(self._data.copy())

    def update(self, *others: dict[KT, VT]) -> Self:
        """
        Update the dict with other(s) dict(s) and return self for convenience.

        **Warning** ⚠️

        This modifies the dict in place.

            >>> Dict({1: 2}).update({3: 4})
            {1: 2, 3: 4}
        """
        self._data.update(*others)
        return self

    @overload
    def get_value(self, key: KT, default: None = None) -> VT | None: ...
    @overload
    def get_value(self, key: KT, default: VT = ...) -> VT: ...
    def get_value(self, key: KT, default: VT | None = None) -> VT | None:
        """Get the value for a key, returning default if not found."""
        return self._data.get(key, default)

    def set_value(self, key: KT, value: VT) -> Self:
        """
        Set the value for a key and return self for convenience.

        **Warning** ⚠️

        This modifies the dict in place.

            >>> Dict({}).set_value("x", 1)
            {'x': 1}
        """
        self._data[key] = value
        return self

    # CYTOOLZ------------------------------------------------------------------
    def filter_keys(self, predicate: Callable[[KT], bool]) -> Self:
        """
        Return a new Dict containing keys that satisfy predicate.

            >>> Dict({1: 2, 3: 4}).filter_keys(lambda k: k % 2 == 0)
            {}
        """
        return self._new(cz.dicttoolz.keyfilter(predicate, self._data))

    def filter_values(self, predicate: Callable[[VT], bool]) -> Self:
        """
        Return a new Dict containing items whose values satisfy predicate.

            >>> Dict({1: 2, 3: 4}).filter_values(lambda v: v > 2)
            {3: 4}
        """
        return self._new(cz.dicttoolz.valfilter(predicate, self._data))

    def filter_items(
        self,
        predicate: Callable[[KT, VT], bool],
    ) -> Self:
        """
        Filter items by predicate applied to (key, value) tuples.

            >>> Dict({1: 2, 3: 4}).filter_items(lambda k, v: v > 2)
            {3: 4}
        """
        return self._new(
            cz.dicttoolz.itemfilter(lambda kv: predicate(kv[0], kv[1]), self._data)
        )

    def with_key(self, key: KT, value: VT) -> Self:
        """
        Return a new Dict with key set to value.

            >>> Dict({}).with_key("x", 1)
            {'x': 1}
        """
        return self._new(cz.dicttoolz.assoc(self._data, key=key, value=value))

    def with_nested_key(self, keys: Iterable[KT] | KT, value: VT) -> Self:
        """
        Set a nested key path and return a new Dict.

            >>> Dict({}).with_nested_key(["a", "b"], 1)
            {'a': {'b': 1}}
        """
        return self._new(cz.dicttoolz.assoc_in(self._data, keys=keys, value=value))

    def update_in(self, *keys: KT, f: Callable[[VT], VT]) -> Self:
        """
        Update a nested value via function f and return a new Dict.

            >>> Dict({"a": {"b": 1}}).update_in("a", "b", f=lambda x: x + 1)
            {'a': {'b': 2}}
        """
        return self._new(cz.dicttoolz.update_in(self._data, keys=keys, func=f))

    def merge(self, *others: dict[KT, VT]) -> Self:
        """
        Merge other dicts into this one and return a new Dict.

            >>> Dict({1: 2}).merge({3: 4})
            {1: 2, 3: 4}
        """
        return self._new(cz.dicttoolz.merge(self._data, *others))

    def merge_with(
        self, f: Callable[[Iterable[VT]], VT], *others: dict[KT, VT]
    ) -> Self:
        """
        Merge dicts using f to combine values for duplicate keys.

            >>> Dict({1: 1}).merge_with(sum, {1: 2})
            {1: 3}
        """
        return self._new(cz.dicttoolz.merge_with(f, self._data, *others))

    def drop(self, *keys: KT) -> Self:
        """
        Return a new Dict with given keys removed.

            >>> Dict({1: 2, 3: 4}).drop(1)
            {3: 4}
        """
        return self._new(cz.dicttoolz.dissoc(self._data, *keys))

    def map_keys[T](self, func: Callable[[KT], T]) -> Dict[T, VT]:
        """
        Return a Dict with keys transformed by ffunc.

            >>> Dict({1: "a"}).map_keys(str)
            {'1': 'a'}
        """
        return Dict(cz.dicttoolz.keymap(func, self._data))

    def map_values[T](self, func: Callable[[VT], T]) -> Dict[KT, T]:
        """
        Return a Dict with values transformed by func.

            >>> Dict({1: 1}).map_values(lambda v: v + 1)
            {1: 2}
        """
        return Dict(cz.dicttoolz.valmap(func, self._data))

    def map_items[KR, VR](
        self,
        func: Callable[[KT, VT], tuple[KR, VR]],
    ) -> Dict[KR, VR]:
        """
        Transform (key, value) pairs using a function that takes key and value as separate arguments.

            >>> Dict({1: 2}).map_items(lambda k, v: (k + 1, v * 10))
            {2: 20}
        """
        return Dict(cz.dicttoolz.itemmap(lambda kv: func(kv[0], kv[1]), self._data))
