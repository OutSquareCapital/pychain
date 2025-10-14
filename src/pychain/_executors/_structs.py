from __future__ import annotations

from collections.abc import Callable, Iterable
from functools import partial
from typing import TYPE_CHECKING, Self

import cytoolz as cz

from .._core import EagerWrapper

if TYPE_CHECKING:
    from .._implementations import Dict


class BaseStruct[K, V](EagerWrapper[dict[K, V]]):
    def map_keys[T](self, func: Callable[[K], T]) -> Dict[T, V]:
        """
        Return a Dict with keys transformed by func.

        >>> Dict({"Alice": [20, 15, 30], "Bob": [10, 35]}).map_keys(str.lower).unwrap()
        {'alice': [20, 15, 30], 'bob': [10, 35]}
        >>>
        >>> Dict({1: "a"}).map_keys(str).unwrap()
        {'1': 'a'}
        """
        return self.apply(partial(cz.dicttoolz.keymap, func))

    def map_values[T](self, func: Callable[[V], T]) -> Dict[K, T]:
        """
        Return a Dict with values transformed by func.

        >>> Dict({"Alice": [20, 15, 30], "Bob": [10, 35]}).map_values(sum).unwrap()
        {'Alice': 65, 'Bob': 45}
        >>>
        >>> Dict({1: 1}).map_values(lambda v: v + 1).unwrap()
        {1: 2}
        """
        return self.apply(partial(cz.dicttoolz.valmap, func))

    def map_items[KR, VR](
        self,
        func: Callable[[tuple[K, V]], tuple[KR, VR]],
    ) -> Dict[KR, VR]:
        """
        Transform (key, value) pairs using a function that takes a (key, value) tuple.

        >>> Dict({"Alice": 10, "Bob": 20}).map_items(
        ...     lambda kv: (kv[0].upper(), kv[1] * 2)
        ... ).unwrap()
        {'ALICE': 20, 'BOB': 40}
        """
        return self.apply(partial(cz.dicttoolz.itemmap, func))

    def reverse(self) -> Dict[V, K]:
        """
        Return a new Dict with keys and values swapped.

        Values in the original dict must be unique and hashable.

        >>> Dict({"a": 1, "b": 2}).reverse().unwrap()
        {1: 'a', 2: 'b'}
        """
        return self.apply(partial(cz.dicttoolz.itemmap, reversed))

    def map_kv[KR, VR](
        self,
        func: Callable[[K, V], tuple[KR, VR]],
    ) -> Dict[KR, VR]:
        """
        Transform (key, value) pairs using a function that takes key and value as separate arguments.

        >>> Dict({1: 2}).map_kv(lambda k, v: (k + 1, v * 10)).unwrap()
        {2: 20}
        """
        return self.apply(
            lambda data: cz.dicttoolz.itemmap(lambda kv: func(kv[0], kv[1]), data)
        )

    def drop(self, *keys: K) -> Self:
        """
        Return a new Dict with given keys removed.

        New dict has d[key] deleted for each supplied key.

        >>> import pychain as pc
        >>> pc.Dict({"x": 1, "y": 2}).drop("y").unwrap()
        {'x': 1}
        >>> pc.Dict({"x": 1, "y": 2}).drop("y", "x").unwrap()
        {}
        >>> pc.Dict({"x": 1}).drop("y").unwrap()  # Ignores missing keys
        {'x': 1}
        >>> pc.Dict({1: 2, 3: 4}).drop(1).unwrap()
        {3: 4}
        """
        return self._new(cz.dicttoolz.dissoc, *keys)

    def rename(self, mapping: dict[K, K]) -> Self:
        """
        Return a new Dict with keys renamed according to the mapping.

        Keys not in the mapping are kept as is.

        >>> from pychain import Dict
        >>> d = {"a": 1, "b": 2, "c": 3}
        >>> mapping = {"b": "beta", "c": "gamma"}
        >>> Dict(d).rename(mapping).unwrap()
        {'a': 1, 'beta': 2, 'gamma': 3}
        """
        return self._new(lambda data: {mapping.get(k, k): v for k, v in data.items()})

    def sort(self, reverse: bool = False) -> Self:
        """
        Sort the dictionary by its keys and return a new Dict.

        >>> from pychain import Dict
        >>> Dict({"b": 2, "a": 1}).sort().unwrap()
        {'a': 1, 'b': 2}
        """
        return self._new(lambda data: dict(sorted(data.items(), reverse=reverse)))

    def merge(self, *others: dict[K, V]) -> Self:
        """
        Merge other dicts into this one and return a new Dict.

        >>> from pychain import Dict
        >>> Dict({1: "one"}).merge({2: "two"}).unwrap()
        {1: 'one', 2: 'two'}

        Later dictionaries have precedence

        >>> Dict({1: 2, 3: 4}).merge({3: 3, 4: 4}).unwrap()
        {1: 2, 3: 3, 4: 4}
        """
        return self._new(cz.dicttoolz.merge, *others)

    def merge_with(self, *others: dict[K, V], func: Callable[[Iterable[V]], V]) -> Self:
        """
        Merge dicts using a function to combine values for duplicate keys.

        A key may occur in more than one dict, and all values mapped from the key will be passed to the function as a list, such as func([val1, val2, ...]).

        >>> from pychain import Dict
        >>> Dict({1: 1, 2: 2}).merge_with({1: 10, 2: 20}, func=sum).unwrap()
        {1: 11, 2: 22}
        >>> Dict({1: 1, 2: 2}).merge_with({2: 20, 3: 30}, func=max).unwrap()
        {1: 1, 2: 20, 3: 30}

        """
        return self._new(lambda data: cz.dicttoolz.merge_with(func, data, *others))

    def filter_keys(self, predicate: Callable[[K], bool]) -> Self:
        """
        Return a new Dict containing keys that satisfy predicate.

        >>> from pychain import Dict
        >>> d = {1: 2, 2: 3, 3: 4, 4: 5}
        >>> Dict(d).filter_keys(lambda x: x % 2 == 0).unwrap()
        {2: 3, 4: 5}
        """
        return self._new(partial(cz.dicttoolz.keyfilter, predicate))

    def filter_keys_not(self, predicate: Callable[[K], bool]) -> Self:
        """
        Return a new Dict containing keys that do not satisfy predicate.

        >>> from pychain import Dict
        >>> d = {1: 2, 2: 3, 3: 4, 4: 5}
        >>> Dict(d).filter_keys_not(lambda x: x % 2 == 0).unwrap()
        {1: 2, 3: 4}
        """

        def negate(k: K) -> bool:
            return not predicate(k)

        return self._new(partial(cz.dicttoolz.keyfilter, negate))

    def filter_values(self, predicate: Callable[[V], bool]) -> Self:
        """
        Return a new Dict containing items whose values satisfy predicate.

        >>> from pychain import Dict
        >>> d = {1: 2, 2: 3, 3: 4, 4: 5}
        >>> Dict(d).filter_values(lambda x: x % 2 == 0).unwrap()
        {1: 2, 3: 4}
        """
        return self._new(partial(cz.dicttoolz.valfilter, predicate))

    def filter_values_not(self, predicate: Callable[[V], bool]) -> Self:
        """
        Return a new Dict containing items whose values do not satisfy predicate.

        >>> from pychain import Dict
        >>> d = {1: 2, 2: 3, 3: 4, 4: 5}
        >>> Dict(d).filter_values_not(lambda x: x % 2 == 0).unwrap()
        {2: 3, 4: 5}
        """

        def negate(v: V) -> bool:
            return not predicate(v)

        return self._new(partial(cz.dicttoolz.valfilter, negate))

    def filter_items(
        self,
        predicate: Callable[[tuple[K, V]], bool],
    ) -> Self:
        """
        Filter items by predicate applied to (key, value) tuples.

        >>> from pychain import Dict
        >>> Dict({1: 2, 3: 4}).filter_items(lambda it: it[1] > 2).unwrap()
        {3: 4}
        """
        return self._new(partial(cz.dicttoolz.itemfilter, predicate))

    def filter_items_not(
        self,
        predicate: Callable[[tuple[K, V]], bool],
    ) -> Self:
        """
        Filter items by negated predicate applied to (key, value) tuples.

        >>> from pychain import Dict
        >>> Dict({1: 2, 3: 4}).filter_items_not(lambda it: it[1] > 2).unwrap()
        {1: 2}
        """

        def negate(kv: tuple[K, V]) -> bool:
            return not predicate(kv)

        return self._new(partial(cz.dicttoolz.itemfilter, negate))

    def filter_kv(
        self,
        predicate: Callable[[K, V], bool],
    ) -> Self:
        """
        Filter items by predicate applied to (key, value) tuples.

        >>> from pychain import Dict
        >>> Dict({1: 2, 3: 4}).filter_kv(lambda k, v: v > 2).unwrap()
        {3: 4}
        """

        return self._new(
            lambda data: cz.dicttoolz.itemfilter(
                lambda kv: predicate(kv[0], kv[1]), data
            )
        )

    def filter_kv_not(
        self,
        predicate: Callable[[K, V], bool],
    ) -> Self:
        """
        Filter items by negated predicate applied to (key, value) tuples.

        >>> from pychain import Dict
        >>> Dict({1: 2, 3: 4}).filter_kv_not(lambda k, v: v > 2).unwrap()
        {1: 2}
        """

        return self._new(
            lambda data: cz.dicttoolz.itemfilter(
                lambda kv: not predicate(kv[0], kv[1]), data
            )
        )
