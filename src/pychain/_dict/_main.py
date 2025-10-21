from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Mapping
from functools import partial
from typing import Any, Concatenate, Self

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

    def __init__(
        self, data: SupportsKeysAndGetItem[K, V] | dict[K, V] | Mapping[K, V]
    ) -> None:
        if not isinstance(data, dict):
            data = dict(data)
        super().__init__(data)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({dict_repr(self.unwrap())})"

    @staticmethod
    def from_(obj: object) -> Dict[str, Any]:
        """
        Create a Dict from an object's __dict__ attribute.
        >>> import pychain as pc
        >>> class Person:
        ...     def __init__(self, name: str, age: int):
        ...         self.name = name
        ...         self.age = age
        >>> person = Person("Alice", 30)
        >>> pc.Dict.from_(person).unwrap()
        {'name': 'Alice', 'age': 30}
        """
        return Dict(obj.__dict__)

    def select(self: Dict[str, Any], *exprs: IntoExpr) -> Dict[str, Any]:
        """
        Select and alias fields from the dict based on expressions and/or strings.

        Navigate nested fields using the `pychain.key` function.

        - Chain `key.key()` calls to access nested fields.
        - Use `key.apply()` to transform values.
        - Use `key.alias()` to rename fields in the resulting dict.
        >>> import pychain as pc
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
        ...     .apply(lambda v: pc.Iter(v).mean())
        ...     .alias("average_eng_score"),
        ... ).unwrap()
        {'student_name': 'Alice', 'age': 30, 'math_scores': [80, 88, 92], 'average_eng_score': 90}

        """
        return Dict(compute_exprs(exprs, self.unwrap(), {}))

    def with_fields(self: Dict[str, Any], *exprs: IntoExpr) -> Dict[str, Any]:
        """
        Merge aliased expressions into the root dict (overwrite on collision).
        >>> import pychain as pc
        >>> data = {
        ...     "name": "Alice",
        ...     "age": 30,
        ...     "scores": {"eng": [85, 90, 95], "math": [80, 88, 92]},
        ... }
        >>> scores_expr = pc.key("scores")  # save an expression for reuse
        >>> pc.Dict(data).with_fields(
        ...     scores_expr.key("eng")
        ...     .apply(lambda v: pc.Iter(v).mean())
        ...     .alias("average_eng_score"),
        ... ).unwrap()
        {'name': 'Alice', 'age': 30, 'scores': {'eng': [85, 90, 95], 'math': [80, 88, 92]}, 'average_eng_score': 90}


        """
        return Dict(compute_exprs(exprs, self.unwrap(), dict(self.unwrap())))

    def apply[**P, KU, VU](
        self,
        func: Callable[Concatenate[dict[K, V], P], dict[KU, VU]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Dict[KU, VU]:
        """
        Apply a function to the underlying dict and return a new Dict.

        >>> import pychain as pc
        >>>
        >>> def mul_by_ten(d: dict[int, int]) -> dict[int, int]:
        ...     return {k: v * 10 for k, v in d.items()}
        >>>
        >>> pc.Dict({1: 20, 2: 30}).apply(mul_by_ten).unwrap()
        {1: 200, 2: 300}
        """
        return Dict(self.into(func, *args, **kwargs))

    def map_keys[T](self, func: Callable[[K], T]) -> Dict[T, V]:
        """
        Return a Dict with keys transformed by func.

        >>> import pychain as pc
        >>> pc.Dict({"Alice": [20, 15, 30], "Bob": [10, 35]}).map_keys(
        ...     str.lower
        ... ).unwrap()
        {'alice': [20, 15, 30], 'bob': [10, 35]}
        >>>
        >>> pc.Dict({1: "a"}).map_keys(str).unwrap()
        {'1': 'a'}
        """
        return self.apply(partial(cz.dicttoolz.keymap, func))

    def map_values[T](self, func: Callable[[V], T]) -> Dict[K, T]:
        """
        Return a Dict with values transformed by func.

        >>> import pychain as pc
        >>> pc.Dict({"Alice": [20, 15, 30], "Bob": [10, 35]}).map_values(sum).unwrap()
        {'Alice': 65, 'Bob': 45}
        >>>
        >>> pc.Dict({1: 1}).map_values(lambda v: v + 1).unwrap()
        {1: 2}
        """
        return self.apply(partial(cz.dicttoolz.valmap, func))

    def map_items[KR, VR](
        self,
        func: Callable[[tuple[K, V]], tuple[KR, VR]],
    ) -> Dict[KR, VR]:
        """
        Transform (key, value) pairs using a function that takes a (key, value) tuple.

        >>> import pychain as pc
        >>> pc.Dict({"Alice": 10, "Bob": 20}).map_items(
        ...     lambda kv: (kv[0].upper(), kv[1] * 2)
        ... ).unwrap()
        {'ALICE': 20, 'BOB': 40}
        """
        return self.apply(partial(cz.dicttoolz.itemmap, func))

    def map_kv[KR, VR](
        self,
        func: Callable[[K, V], tuple[KR, VR]],
    ) -> Dict[KR, VR]:
        """
        Transform (key, value) pairs using a function that takes key and value as separate arguments.

        >>> import pychain as pc
        >>> pc.Dict({1: 2}).map_kv(lambda k, v: (k + 1, v * 10)).unwrap()
        {2: 20}
        """
        return self.apply(
            lambda data: cz.dicttoolz.itemmap(lambda kv: func(kv[0], kv[1]), data)
        )

    def invert(self) -> Dict[V, list[K]]:
        """
        Invert the dictionary, grouping keys by common (and hashable) values.

        >>> import pychain as pc
        >>> d = {"a": 1, "b": 2, "c": 1}
        >>> pc.Dict(d).invert().unwrap()
        {1: ['a', 'c'], 2: ['b']}
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

        >>> import pychain as pc
        >>> pc.Dict({1: 2, 3: 4}).implode().unwrap()
        {1: [2], 3: [4]}
        """
        return self.apply(lambda v: cz.dicttoolz.valmap(lambda x: [x], v))

    def equals_to(self, other: Self | Mapping[Any, Any]) -> bool:
        """
        Check if two records are equal based on their data.
        """
        return (
            self.unwrap() == other.unwrap()
            if isinstance(other, Dict)
            else self.unwrap() == other
        )
