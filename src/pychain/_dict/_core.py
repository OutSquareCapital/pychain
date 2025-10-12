from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Any, Self

import cytoolz as cz

from .._core import CommonBase, iter_factory

if TYPE_CHECKING:
    from .._iter import Iter


class CoreDict[K, V](CommonBase[dict[K, V]]):
    def __repr__(self) -> str:
        data_formatted: str = "\n".join(
            f"  {key!r}, {type(value).__name__}: {value!r},"
            for key, value in self._data.items()
        )
        return f"{self.__class__.__name__}(\n{data_formatted}\n)"

    def iter_keys(self) -> Iter[K]:
        """
        Return a Iter of the dict's keys.

        >>> from pychain import Dict
        >>> Dict({1: 2}).iter_keys().into(list)
        [1]
        """
        return iter_factory(self._data.keys())

    def iter_values(self) -> Iter[V]:
        """
        Return a Iter of the dict's values.

        >>> from pychain import Dict
        >>> Dict({1: 2}).iter_values().into(list)
        [2]
        """
        return iter_factory(self._data.values())

    def iter_items(self) -> Iter[tuple[K, V]]:
        """
        Return a Iter of the dict's items.

        >>> from pychain import Dict
        >>> Dict({1: 2}).iter_items().into(list)
        [(1, 2)]
        """
        return iter_factory(self._data.items())

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
        return self._new(cz.dicttoolz.dissoc(self._data, *keys))

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
        return self._new({mapping.get(k, k): v for k, v in self._data.items()})

    def equals_to(self, other: Self | dict[Any, Any]) -> bool:
        """
        Check if two records are equal based on their data.
        """
        return (
            self._data == other._data
            if isinstance(other, CoreDict)
            else self._data == other
        )

    def sort(self, reverse: bool = False) -> Self:
        """
        Sort the dictionary by its keys and return a new Dict.

        >>> from pychain import Dict
        >>> Dict({"b": 2, "a": 1}).sort().unwrap()
        {'a': 1, 'b': 2}
        """
        return self._new(dict(sorted(self._data.items(), reverse=reverse)))

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
        return self._new(cz.dicttoolz.merge(self._data, *others))

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
        return self._new(cz.dicttoolz.merge_with(func, self._data, *others))
