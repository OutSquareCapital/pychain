from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Self

import cytoolz.dicttoolz as dcz
import cytoolz.functoolz as ft

from . import _core as fn


@dataclass(slots=True)
class BaseDict[KT, VT]:
    """
    Dict wrapper providing fluent, eager transformations powered by cytoolz.

    Attributes:
        data: Underlying mapping stored in the UserDict base.
    """

    _data: dict[KT, VT]

    def compose(self, *funcs: fn.Process[dict[KT, VT]]) -> Self:
        """Apply a pipeline of functions to the dict and return a new Dict.

        Example:
            >>> from ._lib import Dict
            >>> Dict({"a": 1}).compose(lambda d: d).unwrap()
            {'a': 1}
        """
        return self.__class__(ft.pipe(self._data, *funcs))

    def select(self, predicate: fn.Check[KT]) -> Self:
        """Return a new Dict containing keys that satisfy predicate.

        Example:
            >>> from ._lib import Dict
            >>> Dict({1: 2, 3: 4}).select(lambda k: k % 2 == 0).unwrap()
            {}
        """
        return self.__class__(dcz.keyfilter(predicate, self._data))

    def filter(self, predicate: fn.Check[VT]) -> Self:
        """Return a new Dict containing items whose values satisfy predicate.

        Example:
            >>> from ._lib import Dict
            >>> Dict({1: 2, 3: 4}).filter(lambda v: v > 2).unwrap()
            {3: 4}
        """
        return self.__class__(dcz.valfilter(predicate, self._data))

    def filter_items(
        self,
        predicate: fn.Check[tuple[KT, VT]],
    ) -> Self:
        """Filter items by predicate applied to (key, value) tuples.

        Example:
            >>> from ._lib import Dict
            >>> Dict({1: 2, 3: 4}).filter_items(lambda kv: kv[1] > 2).unwrap()
            {3: 4}
        """
        return self.__class__(dcz.itemfilter(predicate, self._data))

    def with_key(self, key: KT, value: VT) -> Self:
        """Return a new Dict with key set to value.

        Example:
            >>> from ._lib import Dict
            >>> Dict({}).with_key("x", 1).unwrap()
            {'x': 1}
        """
        return self.__class__(dcz.assoc(self._data, key=key, value=value))

    def with_nested_key(self, keys: Iterable[KT] | KT, value: VT) -> Self:
        """Set a nested key path and return a new Dict.

        Example:
            >>> from ._lib import Dict
            >>> Dict({}).with_nested_key(["a", "b"], 1).unwrap()
            {'a': {'b': 1}}
        """
        return self.__class__(dcz.assoc_in(self._data, keys=keys, value=value))

    def update_in(self, *keys: KT, f: fn.Process[VT]) -> Self:
        """Update a nested value via function f and return a new Dict.

        Example:
            >>> from ._lib import Dict
            >>> Dict({"a": {"b": 1}}).update_in("a", "b", f=lambda x: x + 1).unwrap()
            {'a': {'b': 2}}
        """
        return self.__class__(dcz.update_in(self._data, keys=keys, func=f))

    def merge(self, *others: dict[KT, VT]) -> Self:
        """Merge other dicts into this one and return a new Dict.

        Example:
            >>> from ._lib import Dict
            >>> Dict({1: 2}).merge({3: 4}).unwrap()
            {1: 2, 3: 4}
        """
        return self.__class__(dcz.merge(self._data, *others))

    def merge_with(
        self, f: Callable[[Iterable[VT]], VT], *others: dict[KT, VT]
    ) -> Self:
        """Merge dicts using f to combine values for duplicate keys.

        Example:
            >>> from ._lib import Dict
            >>> Dict({1: 1}).merge_with(sum, {1: 2}).unwrap()
            {1: 3}
        """
        return self.__class__(dcz.merge_with(f, self._data, *others))

    def drop(self, *keys: KT) -> Self:
        """Return a new Dict with given keys removed.

        Example:
            >>> from ._lib import Dict
            >>> Dict({1: 2, 3: 4}).drop(1).unwrap()
            {3: 4}
        """
        return self.__class__(dcz.dissoc(self._data, *keys))
