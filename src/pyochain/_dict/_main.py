from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Mapping
from functools import partial
from typing import Any, Self

import cytoolz as cz

from .._core import SupportsKeysAndGetItem
from ._exprs import IntoExpr, compute_exprs
from ._filters import FilterDict
from ._funcs import dict_repr
from ._groups import GroupsDict
from ._iter import IterDict
from ._joins import JoinsDict
from ._nested import NestedDict
from ._process import ProcessDict


class Dict[K, V](
    ProcessDict[K, V],
    IterDict[K, V],
    NestedDict[K, V],
    JoinsDict[K, V],
    FilterDict[K, V],
    GroupsDict[K, V],
):
    """
    Wrapper for Python dictionaries with chainable methods.
    """

    __slots__ = ()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({dict_repr(self.unwrap())})"

    @staticmethod
    def from_[G, I](data: Mapping[G, I] | SupportsKeysAndGetItem[G, I]) -> Dict[G, I]:
        """
        Create a Dict from a mapping or SupportsKeysAndGetItem.

        Args:
            data: A mapping or object supporting keys and item access to convert into a Dict.

        ```python
        >>> import pyochain as pc
        >>> class MyMapping:
        ...     def __init__(self):
        ...         self._data = {1: "a", 2: "b", 3: "c"}
        ...
        ...     def keys(self):
        ...         return self._data.keys()
        ...
        ...     def __getitem__(self, key):
        ...         return self._data[key]
        >>>
        >>> pc.Dict.from_(MyMapping()).unwrap()
        {1: 'a', 2: 'b', 3: 'c'}

        ```
        """
        return Dict(dict(data))

    @staticmethod
    def from_object(obj: object) -> Dict[str, Any]:
        """
        Create a Dict from an object's __dict__ attribute.

        Args:
            obj: The object whose `__dict__` attribute will be used to create the Dict.

        ```python
        >>> import pyochain as pc
        >>> class Person:
        ...     def __init__(self, name: str, age: int):
        ...         self.name = name
        ...         self.age = age
        >>> person = Person("Alice", 30)
        >>> pc.Dict.from_object(person).unwrap()
        {'name': 'Alice', 'age': 30}

        ```
        """
        return Dict(obj.__dict__)

    def select(self: Dict[str, Any], *exprs: IntoExpr) -> Dict[str, Any]:
        """
        Select and alias fields from the dict based on expressions and/or strings.

        Navigate nested fields using the `pyochain.key` function.

        - Chain `key.key()` calls to access nested fields.
        - Use `key.apply()` to transform values.
        - Use `key.alias()` to rename fields in the resulting dict.

        Args:
            *exprs: Expressions or strings to select and alias fields from the dictionary.

        ```python
        >>> import pyochain as pc
        >>> data = {
        ...     "name": "Alice",
        ...     "age": 30,
        ...     "scores": {"eng": [85, 90, 95], "math": [80, 88, 92]},
        ... }
        >>> scores_expr = pc.key("scores")  # save an expression for reuse
        >>> pc.Dict(data).select(
        ...     pc.key("name").alias("student_name"),
        ...     "age",  # shorthand for pc.key("age")
        ...     scores_expr.key("math").alias("math_scores"),
        ...     scores_expr.key("eng")
        ...     .apply(lambda v: pc.Seq(v).mean())
        ...     .alias("average_eng_score"),
        ... ).unwrap()
        {'student_name': 'Alice', 'age': 30, 'math_scores': [80, 88, 92], 'average_eng_score': 90}

        ```
        """

        def _select(data: dict[str, Any]) -> dict[str, Any]:
            return compute_exprs(exprs, data, {})

        return self.apply(_select)

    def with_fields(self: Dict[str, Any], *exprs: IntoExpr) -> Dict[str, Any]:
        """
        Merge aliased expressions into the root dict (overwrite on collision).

        Args:
            *exprs: Expressions to merge into the root dictionary.

        ```python
        >>> import pyochain as pc
        >>> data = {
        ...     "name": "Alice",
        ...     "age": 30,
        ...     "scores": {"eng": [85, 90, 95], "math": [80, 88, 92]},
        ... }
        >>> scores_expr = pc.key("scores")  # save an expression for reuse
        >>> pc.Dict(data).with_fields(
        ...     scores_expr.key("eng")
        ...     .apply(lambda v: pc.Seq(v).mean())
        ...     .alias("average_eng_score"),
        ... ).unwrap()
        {'name': 'Alice', 'age': 30, 'scores': {'eng': [85, 90, 95], 'math': [80, 88, 92]}, 'average_eng_score': 90}

        ```
        """

        def _with_fields(data: dict[str, Any]) -> dict[str, Any]:
            return compute_exprs(exprs, data, data.copy())

        return self.apply(_with_fields)

    def map_keys[T](self, func: Callable[[K], T]) -> Dict[T, V]:
        """
        Return a Dict with keys transformed by func.

        Args:
            func: Function to apply to each key in the dictionary.

        ```python
        >>> import pyochain as pc
        >>> pc.Dict({"Alice": [20, 15, 30], "Bob": [10, 35]}).map_keys(
        ...     str.lower
        ... ).unwrap()
        {'alice': [20, 15, 30], 'bob': [10, 35]}
        >>>
        >>> pc.Dict({1: "a"}).map_keys(str).unwrap()
        {'1': 'a'}

        ```
        """
        return self.apply(partial(cz.dicttoolz.keymap, func))

    def map_values[T](self, func: Callable[[V], T]) -> Dict[K, T]:
        """
        Return a Dict with values transformed by func.

        Args:
            func: Function to apply to each value in the dictionary.

        ```python
        >>> import pyochain as pc
        >>> pc.Dict({"Alice": [20, 15, 30], "Bob": [10, 35]}).map_values(sum).unwrap()
        {'Alice': 65, 'Bob': 45}
        >>>
        >>> pc.Dict({1: 1}).map_values(lambda v: v + 1).unwrap()
        {1: 2}

        ```
        """
        return self.apply(partial(cz.dicttoolz.valmap, func))

    def map_items[KR, VR](
        self,
        func: Callable[[tuple[K, V]], tuple[KR, VR]],
    ) -> Dict[KR, VR]:
        """
        Transform (key, value) pairs using a function that takes a (key, value) tuple.

        Args:
            func: Function to transform each (key, value) pair into a new (key, value) tuple.

        ```python
        >>> import pyochain as pc
        >>> pc.Dict({"Alice": 10, "Bob": 20}).map_items(
        ...     lambda kv: (kv[0].upper(), kv[1] * 2)
        ... ).unwrap()
        {'ALICE': 20, 'BOB': 40}

        ```
        """
        return self.apply(partial(cz.dicttoolz.itemmap, func))

    def map_kv[KR, VR](
        self,
        func: Callable[[K, V], tuple[KR, VR]],
    ) -> Dict[KR, VR]:
        """
        Transform (key, value) pairs using a function that takes key and value as separate arguments.

        Args:
            func: Function to transform each key and value into a new (key, value) tuple.

        ```python
        >>> import pyochain as pc
        >>> pc.Dict({1: 2}).map_kv(lambda k, v: (k + 1, v * 10)).unwrap()
        {2: 20}

        ```
        """

        def _map_kv(data: dict[K, V]) -> dict[KR, VR]:
            def _(kv: tuple[K, V]) -> tuple[KR, VR]:
                return func(kv[0], kv[1])

            return cz.dicttoolz.itemmap(_, data)

        return self.apply(_map_kv)

    def invert(self) -> Dict[V, list[K]]:
        """
        Invert the dictionary, grouping keys by common (and hashable) values.
        ```python
        >>> import pyochain as pc
        >>> d = {"a": 1, "b": 2, "c": 1}
        >>> pc.Dict(d).invert().unwrap()
        {1: ['a', 'c'], 2: ['b']}

        ```
        """

        def _invert(data: dict[K, V]) -> dict[V, list[K]]:
            inverted: dict[V, list[K]] = defaultdict(list)
            for k, v in data.items():
                inverted[v].append(k)
            return dict(inverted)

        return self.apply(_invert)

    def implode(self) -> Dict[K, list[V]]:
        """
        Nest all the values in lists.
        syntactic sugar for map_values(lambda v: [v])
        ```python
        >>> import pyochain as pc
        >>> pc.Dict({1: 2, 3: 4}).implode().unwrap()
        {1: [2], 3: [4]}

        ```
        """

        def _implode(data: dict[K, V]) -> dict[K, list[V]]:
            def _(v: V) -> list[V]:
                return [v]

            return cz.dicttoolz.valmap(_, data)

        return self.apply(_implode)

    def equals_to(self, other: Self | Mapping[Any, Any]) -> bool:
        """
        Check if two records are equal based on their data.

        Args:
            other: Another Dict or mapping to compare against.

        Example:
        ```python
        >>> import pyochain as pc
        >>> d1 = pc.Dict({"a": 1, "b": 2})
        >>> d2 = pc.Dict({"a": 1, "b": 2})
        >>> d3 = pc.Dict({"a": 1, "b": 3})
        >>> d1.equals_to(d2)
        True
        >>> d1.equals_to(d3)
        False

        ```
        """
        return (
            self.unwrap() == other.unwrap()
            if isinstance(other, Dict)
            else self.unwrap() == other
        )
