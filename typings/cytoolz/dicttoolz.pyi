"""
dicttoolz
========

- assoc : Return a new dict with new key value pair
- assoc_in : Return a new dict with new, potentially nested, key value pair
- dissoc : Return a new dict with the given key(s) removed.
- get_in : Returns coll[i0][i1]...[iX] where [i0, i1, ..., iX]==keys.
- itemfilter : Filter items in dictionary by item
- itemmap : Apply function to items of dictionary
- keyfilter : Filter items in dictionary by key
- keymap : Apply function to keys of dictionary
- merge : Merge a collection of dictionaries
- merge_with : Merge dictionaries and apply function to combined values
- update_in : Update value in a (potentially) nested dictionary
- valfilter : Filter items in dictionary by value
- valmap : Apply function to values of dictionary
"""

from typing import Any
from collections.abc import Callable, Iterable

def assoc[K, V](d: dict[K, V], key: K, value: V) -> dict[K, V]:
    """
    Return a new dict with new key value pair

    New dict has d[key] set to value. Does not modify the initial dictionary.

    >>> assoc({"x": 1}, "x", 2)
    {'x': 2}
    >>> assoc({"x": 1}, "y", 3)  # doctest: +SKIP
    {'x': 1, 'y': 3}
    """
    ...

def assoc_in[K, V](
    d: dict[K, V],
    keys: Iterable[K] | K,
    value: V,
    factory: Callable[[], dict[Any, Any]] = dict,
) -> dict[K, V]:
    """
    Return a new dict with new, potentially nested, key value pair

    >>> purchase = {
    ...     "name": "Alice",
    ...     "order": {"items": ["Apple", "Orange"], "costs": [0.50, 1.25]},
    ...     "credit card": "5555-1234-1234-1234",
    ... }
    >>> assoc_in(purchase, ["order", "costs"], [0.25, 1.00])  # doctest: +SKIP
    {'credit card': '5555-1234-1234-1234',
    'name': 'Alice',
    'order': {'costs': [0.25, 1.00], 'items': ['Apple', 'Orange']}}
    """
    ...

def dissoc[K, V](d: dict[K, V], *keys: K, **kwargs: Any) -> dict[K, V]:
    """
    Return a new dict with the given key(s) removed.

    New dict has d[key] deleted for each supplied key.
    Does not modify the initial dictionary.

    >>> dissoc({"x": 1, "y": 2}, "y")
    {'x': 1}
    >>> dissoc({"x": 1, "y": 2}, "y", "x")
    {}
    >>> dissoc({"x": 1}, "y")  # Ignores missing keys
    {'x': 1}
    """
    ...

def get_in[K, V](
    keys: Iterable[K] | K,
    coll: Iterable[V] | dict[K, V],
    default: Any = ...,
    no_default: bool = ...,
) -> V:
    """
    Returns coll[i0][i1]...[iX] where [i0, i1, ..., iX]==keys.

    If coll[i0][i1]...[iX] cannot be found, returns ``default``, unless
    ``no_default`` is specified, then it raises KeyError or IndexError.

    ``get_in`` is a generalization of ``operator.getitem`` for nested data
    structures such as dictionaries and lists.

    >>> transaction = {
    ...     "name": "Alice",
    ...     "purchase": {"items": ["Apple", "Orange"], "costs": [0.50, 1.25]},
    ...     "credit card": "5555-1234-1234-1234",
    ... }
    >>> get_in(["purchase", "items", 0], transaction)
    'Apple'
    >>> get_in(["name"], transaction)
    'Alice'
    >>> get_in(["purchase", "total"], transaction)
    >>> get_in(["purchase", "items", "apple"], transaction)
    >>> get_in(["purchase", "items", 10], transaction)
    >>> get_in(["purchase", "total"], transaction, 0)
    0
    >>> get_in(["y"], {}, no_default=True)
    Traceback (most recent call last):
        ...
    KeyError: 'y'

    See Also:
        itertoolz.get
        operator.getitem
    """
    ...

def itemfilter[K, V](
    predicate: Callable[[tuple[K, V]], bool], d: dict[K, V]
) -> dict[K, V]:
    """
    Filter items in dictionary by item

    >>> def isvalid(item):
    ...     k, v = item
    ...     return k % 2 == 0 and v < 4

    >>> d = {1: 2, 2: 3, 3: 4, 4: 5}
    >>> itemfilter(isvalid, d)
    {2: 3}

    See Also:
        keyfilter
        valfilter
        itemmap
    """
    ...

def itemmap[K, V, K1, V1](
    func: Callable[[tuple[K, V]], tuple[K1, V1]], d: dict[K, V]
) -> dict[K1, V1]:
    """
    Apply function to items of dictionary

    >>> accountids = {"Alice": 10, "Bob": 20}
    >>> itemmap(reversed, accountids)  # doctest: +SKIP
    {10: "Alice", 20: "Bob"}

    See Also:
        keymap
        valmap
    """
    ...

def keyfilter[K, V](
    predicate: Callable[[K], bool],
    d: dict[K, V],
    factory: Callable[[], dict[Any, Any]] = ...,
) -> dict[K, V]:
    """
    Filter items in dictionary by key

    >>> iseven = lambda x: x % 2 == 0
    >>> d = {1: 2, 2: 3, 3: 4, 4: 5}
    >>> keyfilter(iseven, d)
    {2: 3, 4: 5}

    See Also:
        valfilter
        itemfilter
        keymap
    """
    ...

def keymap[K, V, K1](
    func: Callable[[K], K1],
    d: dict[K, V],
    factory: Callable[[], dict[Any, Any]] = ...,
) -> dict[K1, V]:
    """
    Apply function to keys of dictionary

    >>> bills = {"Alice": [20, 15, 30], "Bob": [10, 35]}
    >>> keymap(str.lower, bills)  # doctest: +SKIP
    {'alice': [20, 15, 30], 'bob': [10, 35]}

    See Also:
        valmap
        itemmap
    """
    ...

def merge[K, V](*dicts: dict[K, V], **kwargs: Any) -> dict[K, V]:
    """
    Merge a collection of dictionaries

    >>> merge({1: "one"}, {2: "two"})
    {1: 'one', 2: 'two'}

    Later dictionaries have precedence

    >>> merge({1: 2, 3: 4}, {3: 3, 4: 4})
    {1: 2, 3: 3, 4: 4}

    See Also:
        merge_with
    """
    ...

def merge_with[K, V](
    func: Callable[[list[V]], V], *dicts: dict[K, V], **kwargs: Any
) -> dict[K, V]:
    """
    Merge dictionaries and apply function to combined values

    A key may occur in more than one dict, and all values mapped from the key
    will be passed to the function as a list, such as func([val1, val2, ...]).

    >>> merge_with(sum, {1: 1, 2: 2}, {1: 10, 2: 20})
    {1: 11, 2: 22}

    >>> merge_with(first, {1: 1, 2: 2}, {2: 20, 3: 30})  # doctest: +SKIP
    {1: 1, 2: 2, 3: 30}

    See Also:
        merge
    """
    ...

def update_in[K, V](
    d: dict[K, V],
    keys: Iterable[K],
    func: Callable[..., V],
    default: V | None = None,
    factory: Callable[[], dict[K, V]] = dict,
) -> dict[K, V]:
    """
    Update value in a (potentially) nested dictionary

    inputs:
    d - dictionary on which to operate
    keys - list or tuple giving the location of the value to be changed in d
    func - function to operate on that value

    If keys == [k0,..,kX] and d[k0]..[kX] == v, update_in returns a copy of the
    original dictionary with v replaced by func(v), but does not mutate the
    original dictionary.

    If k0 is not a key in d, update_in creates nested dictionaries to the depth
    specified by the keys, with the innermost value set to func(default).

    >>> inc = lambda x: x + 1
    >>> update_in({"a": 0}, ["a"], inc)
    {'a': 1}

    >>> transaction = {
    ...     "name": "Alice",
    ...     "purchase": {"items": ["Apple", "Orange"], "costs": [0.50, 1.25]},
    ...     "credit card": "5555-1234-1234-1234",
    ... }
    >>> update_in(transaction, ["purchase", "costs"], sum)  # doctest: +SKIP
    {'credit card': '5555-1234-1234-1234',
    'name': 'Alice',
    'purchase': {'costs': 1.75, 'items': ['Apple', 'Orange']}}

    >>> # updating a value when k0 is not in d
    >>> update_in({}, [1, 2, 3], str, default="bar")
    {1: {2: {3: 'bar'}}}
    >>> update_in({1: "foo"}, [2, 3, 4], inc, 0)
    {1: 'foo', 2: {3: {4: 1}}}
    """
    ...

def valfilter[K, V](
    predicate: Callable[[V], bool],
    d: dict[K, V],
    factory: Callable[[], dict[Any, Any]] = ...,
) -> dict[K, V]:
    """
    Filter items in dictionary by value

    >>> iseven = lambda x: x % 2 == 0
    >>> d = {1: 2, 2: 3, 3: 4, 4: 5}
    >>> valfilter(iseven, d)
    {1: 2, 3: 4}

    See Also:
        keyfilter
        itemfilter
        valmap
    """
    ...

def valmap[K, V, V1](
    func: Callable[[V], V1],
    d: dict[K, V],
    factory: Callable[[], dict[Any, Any]] = ...,
) -> dict[K, V1]:
    """
    Apply function to values of dictionary

    >>> bills = {"Alice": [20, 15, 30], "Bob": [10, 35]}
    >>> valmap(sum, bills)  # doctest: +SKIP
    {'Alice': 65, 'Bob': 45}

    See Also:
        keymap
        itemmap
    """
    ...
