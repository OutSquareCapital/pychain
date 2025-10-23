from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from functools import partial
from typing import TYPE_CHECKING, Any, overload

import cytoolz as cz
import more_itertools as mit

from .._core import IterWrapper

if TYPE_CHECKING:
    from .._dict import Dict
    from ._main import Iter


class BaseGroups[T](IterWrapper[T]):
    def reduce_by[K](
        self, key: Callable[[T], K], binop: Callable[[T, T], T]
    ) -> Dict[K, T]:
        """
        Perform a simultaneous groupby and reduction.

        Args:
            key: Function to compute the key for grouping.
            binop: Binary operation to reduce the grouped elements.
        Example:
        ```python
        >>> from collections.abc import Iterable
        >>> import pyochain as pc
        >>> from operator import add, mul
        >>>
        >>> def is_even(x: int) -> bool:
        ...     return x % 2 == 0
        >>>
        >>> def group_reduce(data: Iterable[int]) -> int:
        ...     return pc.Iter.from_(data).reduce(add)
        >>>
        >>> data = pc.Seq([1, 2, 3, 4, 5])
        >>> data.iter().reduce_by(is_even, add).unwrap()
        {False: 9, True: 6}
        >>> data.iter().group_by(is_even).map_values(group_reduce).unwrap()
        {False: 9, True: 6}

        ```
        But the former does not build the intermediate groups, allowing it to operate in much less space.

        This makes it suitable for larger datasets that do not fit comfortably in memory

        Simple Examples:
        ```python
        >>> pc.Iter.from_([1, 2, 3, 4, 5]).reduce_by(is_even, add).unwrap()
        {False: 9, True: 6}
        >>> pc.Iter.from_([1, 2, 3, 4, 5]).reduce_by(is_even, mul).unwrap()
        {False: 15, True: 8}

        ```
        """
        from .._dict import Dict

        return Dict(self.into(partial(cz.itertoolz.reduceby, key, binop)))

    def group_by[K](self, on: Callable[[T], K]) -> Dict[K, list[T]]:
        """
        Group elements by key function and return a Dict result.

        Args:
            on: Function to compute the key for grouping.
        Example:
        ```python
        >>> import pyochain as pc
        >>> names = [
        ...     "Alice",
        ...     "Bob",
        ...     "Charlie",
        ...     "Dan",
        ...     "Edith",
        ...     "Frank",
        ... ]
        >>> pc.Iter.from_(names).group_by(len).sort()
        ... # doctest: +NORMALIZE_WHITESPACE
        Dict({
            3: ['Bob', 'Dan'],
            5: ['Alice', 'Edith', 'Frank'],
            7: ['Charlie']
        })
        >>>
        >>> iseven = lambda x: x % 2 == 0
        >>> pc.Iter.from_([1, 2, 3, 4, 5, 6, 7, 8]).group_by(iseven)
        ... # doctest: +NORMALIZE_WHITESPACE
        Dict({
            False: [1, 3, 5, 7],
            True: [2, 4, 6, 8]
        })

        ```
        Non-callable keys imply grouping on a member.
        ```python
        >>> data = [
        ...     {"name": "Alice", "gender": "F"},
        ...     {"name": "Bob", "gender": "M"},
        ...     {"name": "Charlie", "gender": "M"},
        ... ]
        >>> pc.Iter.from_(data).group_by("gender").sort()
        ... # doctest: +NORMALIZE_WHITESPACE
        Dict({
            'F': [
                {'name': 'Alice', 'gender': 'F'}
            ],
            'M': [
                {'name': 'Bob', 'gender': 'M'},
                {'name': 'Charlie', 'gender': 'M'}
            ]
        })

        ```
        """
        from .._dict import Dict

        return Dict(self.into(partial(cz.itertoolz.groupby, on)))

    def frequencies(self) -> Dict[T, int]:
        """
        Find number of occurrences of each value in the iterable.
        ```python
        >>> import pyochain as pc
        >>> data = ["cat", "cat", "ox", "pig", "pig", "cat"]
        >>> pc.Iter.from_(data).frequencies().unwrap()
        {'cat': 3, 'ox': 1, 'pig': 2}

        ```
        """
        from .._dict import Dict

        return Dict(self.into(cz.itertoolz.frequencies))

    def count_by[K](self, key: Callable[[T], K]) -> Dict[K, int]:
        """
        Count elements of a collection by a key function.

        Args:
            key: Function to compute the key for counting.
        Example:
        ```python
        >>> import pyochain as pc
        >>> pc.Iter.from_(["cat", "mouse", "dog"]).count_by(len).unwrap()
        {3: 2, 5: 1}
        >>> def iseven(x):
        ...     return x % 2 == 0
        >>> pc.Iter.from_([1, 2, 3]).count_by(iseven).unwrap()
        {False: 2, True: 1}

        ```
        """
        from .._dict import Dict

        return Dict(self.into(partial(cz.recipes.countby, key)))

    @overload
    def group_by_transform(
        self,
        keyfunc: None = None,
        valuefunc: None = None,
        reducefunc: None = None,
    ) -> Iter[tuple[T, Iterator[T]]]: ...
    @overload
    def group_by_transform[U](
        self,
        keyfunc: Callable[[T], U],
        valuefunc: None,
        reducefunc: None,
    ) -> Iter[tuple[U, Iterator[T]]]: ...
    @overload
    def group_by_transform[V](
        self,
        keyfunc: None,
        valuefunc: Callable[[T], V],
        reducefunc: None,
    ) -> Iter[tuple[T, Iterator[V]]]: ...
    @overload
    def group_by_transform[U, V](
        self,
        keyfunc: Callable[[T], U],
        valuefunc: Callable[[T], V],
        reducefunc: None,
    ) -> Iter[tuple[U, Iterator[V]]]: ...
    @overload
    def group_by_transform[W](
        self,
        keyfunc: None,
        valuefunc: None,
        reducefunc: Callable[[Iterator[T]], W],
    ) -> Iter[tuple[T, W]]: ...
    @overload
    def group_by_transform[U, W](
        self,
        keyfunc: Callable[[T], U],
        valuefunc: None,
        reducefunc: Callable[[Iterator[T]], W],
    ) -> Iter[tuple[U, W]]: ...
    @overload
    def group_by_transform[V, W](
        self,
        keyfunc: None,
        valuefunc: Callable[[T], V],
        reducefunc: Callable[[Iterator[V]], W],
    ) -> Iter[tuple[T, W]]: ...
    @overload
    def group_by_transform[U, V, W](
        self,
        keyfunc: Callable[[T], U],
        valuefunc: Callable[[T], V],
        reducefunc: Callable[[Iterator[V]], W],
    ) -> Iter[tuple[U, W]]: ...
    def group_by_transform[U, V](
        self,
        keyfunc: Callable[[T], U] | None = None,
        valuefunc: Callable[[T], V] | None = None,
        reducefunc: Any = None,
    ) -> Iter[tuple[Any, ...]]:
        """
        An extension of itertools.groupby that can apply transformations to the grouped data.

        Args:
            keyfunc: Function to compute the key for grouping. Defaults to None.
            valuefunc: Function to transform individual items after grouping. Defaults to None.
            reducefunc: Function to transform each group of items. Defaults to None.

        Example:
        ```python
        >>> import pyochain as pc
        >>> data = pc.Iter.from_("aAAbBBcCC")
        >>> data.group_by_transform(
        ...     lambda k: k.upper(), lambda v: v.lower(), lambda g: "".join(g)
        ... ).into(list)
        [('A', 'aaa'), ('B', 'bbb'), ('C', 'ccc')]

        ```
        Each optional argument defaults to an identity function if not specified.

        group_by_transform is useful when grouping elements of an iterable using a separate iterable as the key.

        To do this, zip the iterables and pass a keyfunc that extracts the first element and a valuefunc that extracts the second element:

        Note that the order of items in the iterable is significant.

        Only adjacent items are grouped together, so if you don't want any duplicate groups, you should sort the iterable by the key function.

        Example:
        ```python
        >>> from operator import itemgetter
        >>> data = pc.Iter.from_([0, 0, 1, 1, 1, 2, 2, 2, 3])
        >>> data.zip("abcdefghi").group_by_transform(itemgetter(0), itemgetter(1)).map(
        ...     lambda kv: (kv[0], "".join(kv[1]))
        ... ).into(list)
        [(0, 'ab'), (1, 'cde'), (2, 'fgh'), (3, 'i')]

        ```
        """

        def _group_by_transform(data: Iterable[T]) -> Iterator[tuple[Any, ...]]:
            return mit.groupby_transform(data, keyfunc, valuefunc, reducefunc)

        return self.apply(_group_by_transform)
