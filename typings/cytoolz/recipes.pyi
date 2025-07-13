"""
recipes
========

- countby : Count elements of a collection by a key function
- partitionby : Partition a sequence according to a function
"""

from typing import Any
from collections.abc import Callable, Iterable, Iterator

def countby[T, K](key: Callable[[T], K], seq: Iterable[T]) -> dict[K, int]:
    """Count elements of a collection by a key function

    >>> countby(len, ["cat", "mouse", "dog"])
    {3: 2, 5: 1}

    >>> def iseven(x):
    ...     return x % 2 == 0
    >>> countby(iseven, [1, 2, 3])  # doctest:+SKIP
    {True: 1, False: 2}

    See Also:
        groupby
    """
    ...

def partitionby[T](
    func: Callable[[T], Any], seq: Iterable[T]
) -> Iterator[tuple[T, ...]]:
    """Partition a sequence according to a function

    Partition `s` into a sequence of lists such that, when traversing
    `s`, every time the output of `func` changes a new list is started
    and that and subsequent items are collected into that list.

    >>> is_space = lambda c: c == " "
    >>> list(partitionby(is_space, "I have space"))
    [('I',), (' ',), ('h', 'a', 'v', 'e'), (' ',), ('s', 'p', 'a', 'c', 'e')]

    >>> is_large = lambda x: x > 10
    >>> list(partitionby(is_large, [1, 2, 1, 99, 88, 33, 99, -1, 5]))
    [(1, 2, 1), (99, 88, 33, 99), (-1, 5)]

    See also:
        partition
        groupby
        itertools.groupby
    """
    ...
