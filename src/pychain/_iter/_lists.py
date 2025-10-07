from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING

import more_itertools as mit

from .._core import CommonBase, iter_factory

if TYPE_CHECKING:
    from ._main import Iter


class IterList[T](CommonBase[Iterable[T]]):
    _data: Iterable[T]

    def implode(self) -> Iter[list[T]]:
        """
        Wrap each element in the iterable into a list.
        """
        return iter_factory(([x] for x in self._data))

    def split_at(
        self,
        pred: Callable[[T], bool],
        maxsplit: int = -1,
        keep_separator: bool = False,
    ) -> Iter[list[T]]:
        """
        Yield lists of items from iterable, where each list is delimited by an item where callable pred returns True.

        >>> from pychain import Iter
        >>> Iter("abcdcba").split_at(lambda x: x == "b").into(list)
        [['a'], ['c', 'd', 'c'], ['a']]
        >>> Iter(range(10)).split_at(lambda n: n % 2 == 1).into(list)
        [[0], [2], [4], [6], [8], []]

        At most *maxsplit* splits are done.

        If *maxsplit* is not specified or -1, then there is no limit on the number of splits:

        >>> Iter(range(10)).split_at(lambda n: n % 2 == 1, maxsplit=2).into(list)
        [[0], [2], [4, 5, 6, 7, 8, 9]]

        By default, the delimiting items are not included in the output.

        To include them, set *keep_separator* to `True`.

        >>> Iter("abcdcba").split_at(lambda x: x == "b", keep_separator=True).into(list)
        [['a'], ['b'], ['c', 'd', 'c'], ['b'], ['a']]
        """
        return iter_factory(mit.split_at(self._data, pred, maxsplit, keep_separator))

    def split_after(
        self, predicate: Callable[[T], bool], max_split: int = -1
    ) -> Iter[list[T]]:
        """
        Yield lists of items from iterable, where each list ends with an item where callable pred returns True:
        At most maxsplit splits are done.
        If maxsplit is not specified or -1, then there is no limit on the number of splits:

        >>> from pychain import Iter
        >>> Iter("one1two2").split_after(str.isdigit).into(list)
        [['o', 'n', 'e', '1'], ['t', 'w', 'o', '2']]

        >>> Iter(range(10)).split_after(lambda n: n % 3 == 0).into(list)
        [[0], [1, 2, 3], [4, 5, 6], [7, 8, 9]]

        >>> Iter(range(10)).split_after(lambda n: n % 3 == 0, max_split=2).into(list)
        [[0], [1, 2, 3], [4, 5, 6, 7, 8, 9]]
        """
        return iter_factory(mit.split_after(self._data, predicate, max_split))

    def split_before(
        self, predicate: Callable[[T], bool], max_split: int = -1
    ) -> Iter[list[T]]:
        """
        Yield lists of items from iterable, where each list ends with an item where callable pred returns True.

        >>> from pychain import Iter
        >>> Iter("abcdcba").split_before(lambda x: x == "b").into(list)
        [['a'], ['b', 'c', 'd', 'c'], ['b', 'a']]
        >>> Iter(range(10)).split_before(lambda n: n % 2 == 1).into(list)
        [[0], [1, 2], [3, 4], [5, 6], [7, 8], [9]]

        At most *max_split* splits are done.

        If *max_split* is not specified or -1, then there is no limit on the number of splits:

        >>> Iter(range(10)).split_before(lambda n: n % 2 == 1, max_split=2).into(list)
        [[0], [1, 2], [3, 4, 5, 6, 7, 8, 9]]
        """
        return iter_factory(mit.split_before(self._data, predicate, max_split))

    def split_into(self, sizes: Iterable[int | None]) -> Iter[list[T]]:
        """
        Yield a list of sequential items from iterable of length 'n' for each integer 'n' in sizes.

        >>> from pychain import Iter
        >>> Iter([1, 2, 3, 4, 5, 6]).split_into([1, 2, 3]).into(list)
        [[1], [2, 3], [4, 5, 6]]

        If the sum of sizes is smaller than the length of iterable, then the remaining items of iterable will not be returned.

        >>> Iter([1, 2, 3, 4, 5, 6]).split_into([2, 3]).into(list)
        [[1, 2], [3, 4, 5]]

        If the sum of sizes is larger than the length of iterable, fewer items will be returned in the iteration that overruns the iterable and further lists will be empty:

        >>> Iter([1, 2, 3, 4]).split_into([1, 2, 3, 4]).into(list)
        [[1], [2, 3], [4], []]

        When a None object is encountered in sizes, the returned list will contain items up to the end of iterable the same way that itertools.slice does:

        >>> Iter([1, 2, 3, 4, 5, 6, 7, 8, 9, 0]).split_into([2, 3, None]).into(list)
        [[1, 2], [3, 4, 5], [6, 7, 8, 9, 0]]

        split_into can be useful for grouping a series of items where the sizes of the groups are not uniform.

        An example would be where in a row from a table, multiple columns represent elements of the same feature (e.g. a point represented by x,y,z) but, the format is not the same for all columns.
        """
        return iter_factory(mit.split_into(self._data, sizes))

    def split_when(
        self, predicate: Callable[[T, T], bool], max_split: int = -1
    ) -> Iter[list[T]]:
        """
        Split iterable into pieces based on the output of pred. pred should be a function that takes successive pairs of items and returns True if the iterable should be split in between them.

        For example, to find runs of increasing numbers, split the iterable when element i is larger than element i + 1:

        >>> from pychain import Iter
        >>> Iter([1, 2, 3, 3, 2, 5, 2, 4, 2]).split_when(lambda x, y: x > y).into(list)
        [[1, 2, 3, 3], [2, 5], [2, 4], [2]]

        At most max_split splits are done.

        If max_split is not specified or -1, then there is no limit on the number of splits:

        >>> Iter([1, 2, 3, 3, 2, 5, 2, 4, 2]).split_when(
        ...     lambda x, y: x > y, max_split=2
        ... ).into(list)
        [[1, 2, 3, 3], [2, 5], [2, 4, 2]]
        """
        return iter_factory(mit.split_when(self._data, predicate, max_split))

    def chunked(self, n: int, strict: bool = False) -> Iter[list[T]]:
        """
        Break iterable into lists of length n.

        By default, the last yielded list will have fewer than *n* elements if the length of *iterable* is not divisible by *n*.

        To use a fill-in value instead, see the :func:`grouper` recipe.

        If the length of *iterable* is not divisible by *n* and *strict* is
        ``True``, then ``ValueError`` will be raised before the last
        list is yielded.

        >>> from pychain import Iter
        >>> Iter([1, 2, 3, 4, 5, 6]).chunked(3).into(list)
        [[1, 2, 3], [4, 5, 6]]
        >>> Iter([1, 2, 3, 4, 5, 6, 7, 8]).chunked(3).into(list)
        [[1, 2, 3], [4, 5, 6], [7, 8]]
        """
        return iter_factory(mit.chunked(self._data, n, strict))

    def chunked_even(self, n: int) -> Iter[list[T]]:
        """
        Break iterable into lists of approximately length n.
        Items are distributed such the lengths of the lists differ by at most 1 item.

        >>> from pychain import Iter
        >>> iterable = [1, 2, 3, 4, 5, 6, 7]
        >>> Iter(iterable).chunked_even(3).into(list)  # List lengths: 3, 2, 2
        [[1, 2, 3], [4, 5], [6, 7]]
        >>> Iter(iterable).chunked(3).into(list)  # List lengths: 3, 3, 1
        [[1, 2, 3], [4, 5, 6], [7]]
        """
        return iter_factory(mit.chunked_even(self._data, n))

    def unique_to_each(self, *others: Iterable[T]) -> Iter[list[T]]:
        """
        Return the elements from each of the input iterables that aren't in the other input iterables.

        For example, suppose you have a set of packages, each with a set of dependencies:

        **{'pkg_1': {'A', 'B'}, 'pkg_2': {'B', 'C'}, 'pkg_3': {'B', 'D'}}**

        If you remove one package, which dependencies can also be removed?

        If pkg_1 is removed, then A is no longer necessary - it is not associated with pkg_2 or pkg_3.

        Similarly, C is only needed for pkg_2, and D is only needed for pkg_3:

        >>> from pychain import Iter
        >>> Iter({"A", "B"}).unique_to_each({"B", "C"}, {"B", "D"}).into(list)
        [['A'], ['C'], ['D']]

        If there are duplicates in one input iterable that aren't in the others they will be duplicated in the output.

        Input order is preserved:

        >>> Iter("mississippi").unique_to_each("missouri").into(list)
        [['p', 'p'], ['o', 'u', 'r']]

        It is assumed that the elements of each iterable are hashable.
        """
        return iter_factory(mit.unique_to_each(self._data, *others))
