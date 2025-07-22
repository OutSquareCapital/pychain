from typing import Any, overload
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence

def accumulate[T](
    binop: Callable[[T, T], T], seq: Iterable[T], initial: Any = ...
) -> Iterator[T]:
    """
    Repeatedly apply binary function to a sequence, accumulating results

    >>> from operator import add, mul
    >>> list(accumulate(add, [1, 2, 3, 4, 5]))
    [1, 3, 6, 10, 15]
    >>> list(accumulate(mul, [1, 2, 3, 4, 5]))
    [1, 2, 6, 24, 120]

    Accumulate is similar to ``reduce`` and is good for making functions like
    cumulative sum:

    >>> from functools import partial, reduce
    >>> sum = partial(reduce, add)
    >>> cumsum = partial(accumulate, add)

    Accumulate also takes an optional argument that will be used as the first
    value. This is similar to reduce.

    >>> list(accumulate(add, [1, 2, 3], -1))
    [-1, 0, 2, 5]
    >>> list(accumulate(add, [], 1))
    [1]

    See Also:
        itertools.accumulate :  In standard itertools for Python 3.2+
    """
    ...

def concat[T](seqs: Iterable[Iterable[T]] | Iterable[T]) -> Iterator[T]:
    """
    Concatenate zero or more iterables, any of which may be infinite.

    An infinite sequence will prevent the rest of the arguments from
    being included.

    We use chain.from_iterable rather than ``chain(*seqs)`` so that seqs
    can be a generator.

    >>> list(concat([[], [1], [2, 3]]))
    [1, 2, 3]

    See also:
        itertools.chain.from_iterable  equivalent
    """
    ...

def concatv[T](*seqs: Iterable[T]) -> Iterator[T]:
    """
    Variadic version of concat

    >>> list(concatv([], ["a"], ["b", "c"]))
    ['a', 'b', 'c']

    See also:
        itertools.chain
    """
    ...

def cons[T](el: T, seq: Iterable[T]) -> Iterator[T]:
    """
    Add el to beginning of (possibly infinite) sequence seq.

    >>> list(cons(1, [2, 3]))
    [1, 2, 3]
    """
    ...

def count(seq: Iterable[Any]) -> int:
    """
    Count the number of items in seq

    Like the builtin ``len`` but works on lazy sequences.

    Not to be confused with ``itertools.count``

    See also:
        len
    """
    ...

def diff[T](*seqs: Iterable[T], **kwargs: Any) -> Iterator[tuple[T, ...]]:
    """
    Return those items that differ between sequences

    >>> list(diff([1, 2, 3], [1, 2, 10, 100]))
    [(3, 10)]

    Shorter sequences may be padded with a ``default`` value:

    >>> list(diff([1, 2, 3], [1, 2, 10, 100], default=None))
    [(3, 10), (None, 100)]

    A ``key`` function may also be applied to each item to use during
    comparisons:

    >>> list(diff(["apples", "bananas"], ["Apples", "Oranges"], key=str.lower))
    [('bananas', 'Oranges')]
    """
    ...

def drop[T](n: int, seq: Iterable[T]) -> Iterator[T]:
    """
    The sequence following the first n elements

    >>> list(drop(2, [10, 20, 30, 40, 50]))
    [30, 40, 50]

    See Also:
        take
        tail
    """
    ...

def first[T](seq: Iterable[T]) -> T:
    """
    The first element in a sequence

    >>> first("ABC")
    'A'
    """
    ...

def frequencies[T](seq: Iterable[T]) -> dict[T, int]:
    """
    Find number of occurrences of each value in seq

    >>> frequencies(["cat", "cat", "ox", "pig", "pig", "cat"])  # doctest: +SKIP
    {'cat': 3, 'ox': 1, 'pig': 2}

    See Also:
        countby
        groupby
    """
    ...

@overload
def get[KT, VT](ind: KT, seq: Mapping[KT, VT], default: Any = ...) -> VT: ...
@overload
def get[T](ind: int, seq: Sequence[T], default: Any = ...) -> T: ...
@overload
def get[KT, VT](
    ind: Iterable[KT], seq: Mapping[KT, VT], default: Any = ...
) -> Iterator[VT]: ...
@overload
def get[T](ind: Iterable[int], seq: Sequence[T], default: Any = ...) -> Iterator[T]: ...
def groupby[T, KT](key: Callable[[T], KT], seq: Iterable[T]) -> dict[KT, list[T]]:
    """
    Group a collection by a key function

    >>> names = ["Alice", "Bob", "Charlie", "Dan", "Edith", "Frank"]
    >>> groupby(len, names)  # doctest: +SKIP
    {3: ['Bob', 'Dan'], 5: ['Alice', 'Edith', 'Frank'], 7: ['Charlie']}

    >>> iseven = lambda x: x % 2 == 0
    >>> groupby(iseven, [1, 2, 3, 4, 5, 6, 7, 8])  # doctest: +SKIP
    {False: [1, 3, 5, 7], True: [2, 4, 6, 8]}

    Non-callable keys imply grouping on a member.

    >>> groupby(
    ...     "gender",
    ...     [
    ...         {"name": "Alice", "gender": "F"},
    ...         {"name": "Bob", "gender": "M"},
    ...         {"name": "Charlie", "gender": "M"},
    ...     ],
    ... )  # doctest:+SKIP
    {'F': [{'gender': 'F', 'name': 'Alice'}],
     'M': [{'gender': 'M', 'name': 'Bob'},
           {'gender': 'M', 'name': 'Charlie'}]}

    Not to be confused with ``itertools.groupby``

    See Also:
        countby
    """
    ...

def interleave[T](seqs: Iterable[Iterable[T]]) -> Iterator[T]:
    """
    Interleave a sequence of sequences

    >>> list(interleave([[1, 2], [3, 4]]))
    [1, 3, 2, 4]

    >>> "".join(interleave(("ABC", "XY")))
    'AXBYC'

    Both the individual sequences and the sequence of sequences may be infinite

    Returns a lazy iterator
    """
    ...

def interpose[T, E](el: E, seq: Iterable[T]) -> Iterator[T | E]:
    """
    Introduce element between each pair of elements in seq

    >>> list(interpose("a", [1, 2, 3]))
    [1, 'a', 2, 'a', 3]
    """
    ...

def isdistinct(seq: Iterable[Any]) -> bool:
    """
    All values in sequence are distinct

    >>> isdistinct([1, 2, 3])
    True
    >>> isdistinct([1, 2, 1])
    False

    >>> isdistinct("Hello")
    False
    >>> isdistinct("World")
    True
    """
    ...

def isiterable(x: Any) -> bool:
    """
    Is x iterable?

    >>> isiterable([1, 2, 3])
    True
    >>> isiterable("abc")
    True
    >>> isiterable(5)
    False
    """
    ...

def iterate[T, T1](func: Callable[[T], T1], x: T) -> Iterator[T1]:
    """
    Repeatedly apply a function func onto an original input

    Yields x, then func(x), then func(func(x)), then func(func(func(x))), etc..

    >>> def inc(x):
    ...     return x + 1
    >>> counter = iterate(inc, 0)
    >>> next(counter)
    0
    >>> next(counter)
    1
    >>> next(counter)
    2

    >>> double = lambda x: x * 2
    >>> powers_of_two = iterate(double, 1)
    >>> next(powers_of_two)
    1
    >>> next(powers_of_two)
    2
    >>> next(powers_of_two)
    4
    >>> next(powers_of_two)
    8
    """
    ...

def join[T1, T2, KT](
    leftkey: Callable[[T1], KT],
    leftseq: Iterable[T1],
    rightkey: Callable[[T2], KT],
    rightseq: Iterable[T2],
    left_default: Any = ...,
    right_default: Any = ...,
) -> Iterator[tuple[T1, T2]]:
    """
    Join two sequences on common attributes

    This is a semi-streaming operation.  The LEFT sequence is fully evaluated
    and placed into memory.  The RIGHT sequence is evaluated lazily and so can
    be arbitrarily large.

    (Note: If right_default is defined, then unique keys of rightseq
        will also be stored in memory.)

    >>> friends = [
    ...     ("Alice", "Edith"),
    ...     ("Alice", "Zhao"),
    ...     ("Edith", "Alice"),
    ...     ("Zhao", "Alice"),
    ...     ("Zhao", "Edith"),
    ... ]

    >>> cities = [
    ...     ("Alice", "NYC"),
    ...     ("Alice", "Chicago"),
    ...     ("Dan", "Sydney"),
    ...     ("Edith", "Paris"),
    ...     ("Edith", "Berlin"),
    ...     ("Zhao", "Shanghai"),
    ... ]

    >>> # Vacation opportunities
    >>> # In what cities do people have friends?
    >>> result = join(second, friends, first, cities)
    >>> for (a, b), (c, d) in sorted(unique(result)):
    ...     print((a, d))
    ('Alice', 'Berlin')
    ('Alice', 'Paris')
    ('Alice', 'Shanghai')
    ('Edith', 'Chicago')
    ('Edith', 'NYC')
    ('Zhao', 'Chicago')
    ('Zhao', 'NYC')
    ('Zhao', 'Berlin')
    ('Zhao', 'Paris')

    Specify outer joins with keyword arguments ``left_default`` and/or
    ``right_default``.  Here is a full outer join in which unmatched elements
    are paired with None.

    >>> identity = lambda x: x
    >>> list(
    ...     join(
    ...         identity,
    ...         [1, 2, 3],
    ...         identity,
    ...         [2, 3, 4],
    ...         left_default=None,
    ...         right_default=None,
    ...     )
    ... )
    [(2, 2), (3, 3), (None, 4), (1, None)]

    Usually the key arguments are callables to be applied to the sequences.  If
    the keys are not obviously callable then it is assumed that indexing was
    intended, e.g. the following is a legal change.
    The join is implemented as a hash join and the keys of leftseq must be
    hashable. Additionally, if right_default is defined, then keys of rightseq
    must also be hashable.

    >>> # result = join(second, friends, first, cities)
    >>> result = join(1, friends, 0, cities)  # doctest: +SKIP
    """
    ...

def last[T](seq: Iterable[T]) -> T:
    """
    The last element in a sequence

    >>> last("ABC")
    'C'
    """
    ...

def mapcat[T1, T2](
    func: Callable[[Iterable[T1]], Iterable[T2]], seqs: Iterable[Iterable[T1]]
) -> Iterator[T2]:
    """
    Apply func to each sequence in seqs, concatenating results.

    >>> list(mapcat(lambda s: [c.upper() for c in s], [["a", "b"], ["c", "d", "e"]]))
    ['A', 'B', 'C', 'D', 'E']
    """
    ...

def merge_sorted[T](*seqs: Iterable[T], **kwargs: Any) -> Iterator[T]:
    """
    Merge and sort a collection of sorted collections

    This works lazily and only keeps one value from each iterable in memory.

    >>> list(merge_sorted([1, 3, 5], [2, 4, 6]))
    [1, 2, 3, 4, 5, 6]

    >>> "".join(merge_sorted("abc", "abc", "abc"))
    'aaabbbccc'

    The "key" function used to sort the input may be passed as a keyword.

    >>> list(merge_sorted([2, 3], [1, 3], key=lambda x: x // 3))
    [2, 1, 3, 3]
    """
    ...

def nth[T](n: int, seq: Iterable[T]) -> T:
    """
    The nth element in a sequence

    >>> nth(1, "ABC")
    'B'
    """
    ...

def partition[T](n: int, seq: Iterable[T], pad: Any = ...) -> Iterator[tuple[T, ...]]:
    """
    Partition sequence into tuples of length n

    >>> list(partition(2, [1, 2, 3, 4]))
    [(1, 2), (3, 4)]

    If the length of ``seq`` is not evenly divisible by ``n``, the final tuple
    is dropped if ``pad`` is not specified, or filled to length ``n`` by pad:

    >>> list(partition(2, [1, 2, 3, 4, 5]))
    [(1, 2), (3, 4)]

    >>> list(partition(2, [1, 2, 3, 4, 5], pad=None))
    [(1, 2), (3, 4), (5, None)]

    See Also:
        partition_all
    """
    ...

def partition_all[T](n: int, seq: Iterable[T]) -> Iterator[tuple[T, ...]]:
    """
    Partition all elements of sequence into tuples of length at most n

    The final tuple may be shorter to accommodate extra elements.

    >>> list(partition_all(2, [1, 2, 3, 4]))
    [(1, 2), (3, 4)]

    >>> list(partition_all(2, [1, 2, 3, 4, 5]))
    [(1, 2), (3, 4), (5,)]

    See Also:
        partition
    """
    ...

def peek[T](seq: Iterable[T]) -> tuple[T, Iterator[T]]:
    """
    Retrieve the next element of a sequence

    Returns the first element and an iterable equivalent to the original
    sequence, still having the element retrieved.

    >>> seq = [0, 1, 2, 3, 4]
    >>> first, seq = peek(seq)
    >>> first
    0
    >>> list(seq)
    [0, 1, 2, 3, 4]
    """
    ...

def peekn[T](n: int, seq: Iterable[T]) -> tuple[tuple[T, ...], Iterator[T]]:
    """
    Retrieve the next n elements of a sequence

    Returns a tuple of the first n elements and an iterable equivalent
    to the original, still having the elements retrieved.

    >>> seq = [0, 1, 2, 3, 4]
    >>> first_two, seq = peekn(2, seq)
    >>> first_two
    (0, 1)
    >>> list(seq)
    [0, 1, 2, 3, 4]
    """
    ...

def pluck(ind: Any, seqs: Iterable[Any], default: Any = ...) -> Iterator[Any]:
    """
    plucks an element or several elements from each item in a sequence.

    ``pluck`` maps ``itertoolz.get`` over a sequence and returns one or more
    elements of each item in the sequence.

    This is equivalent to running `map(curried.get(ind), seqs)`

    ``ind`` can be either a single string/index or a list of strings/indices.
    ``seqs`` should be sequence containing sequences or dicts.

    e.g.

    >>> data = [{"id": 1, "name": "Cheese"}, {"id": 2, "name": "Pies"}]
    >>> list(pluck("name", data))
    ['Cheese', 'Pies']
    >>> list(pluck([0, 1], [[1, 2, 3], [4, 5, 7]]))
    [(1, 2), (4, 5)]

    See Also:
        get
        map
    """
    ...

def random_sample[T](
    prob: float, seq: Iterable[T], random_state: Any = ...
) -> Iterator[T]:
    """
    Return elements from a sequence with probability of prob

    Returns a lazy iterator of random items from seq.

    ``random_sample`` considers each item independently and without
    replacement. See below how the first time it returned 13 items and the
    next time it returned 6 items.

    >>> seq = list(range(100))
    >>> list(random_sample(0.1, seq))  # doctest: +SKIP
    [6, 9, 19, 35, 45, 50, 58, 62, 68, 72, 78, 86, 95]
    >>> list(random_sample(0.1, seq))  # doctest: +SKIP
    [6, 44, 54, 61, 69, 94]

    Providing an integer seed for ``random_state`` will result in
    deterministic sampling. Given the same seed it will return the same sample
    every time.

    >>> list(random_sample(0.1, seq, random_state=2016))
    [7, 9, 19, 25, 30, 32, 34, 48, 59, 60, 81, 98]
    >>> list(random_sample(0.1, seq, random_state=2016))
    [7, 9, 19, 25, 30, 32, 34, 48, 59, 60, 81, 98]

    ``random_state`` can also be any object with a method ``random`` that
    returns floats between 0.0 and 1.0 (exclusive).

    >>> from random import Random
    >>> randobj = Random(2016)
    >>> list(random_sample(0.1, seq, random_state=randobj))
    [7, 9, 19, 25, 30, 32, 34, 48, 59, 60, 81, 98]
    """
    ...

def reduceby[T, KT, VT](
    key: Callable[[T], KT],
    binop: Callable[[VT, T], VT],
    seq: Iterable[T],
    init: Any = ...,
) -> dict[KT, VT]:
    """
    Perform a simultaneous groupby and reduction

    The computation:

    >>> result = reduceby(key, binop, seq, init)  # doctest: +SKIP

    is equivalent to the following:

    >>> def reduction(group):  # doctest: +SKIP
    ...     return reduce(binop, group, init)  # doctest: +SKIP

    >>> groups = groupby(key, seq)  # doctest: +SKIP
    >>> result = valmap(reduction, groups)  # doctest: +SKIP

    But the former does not build the intermediate groups, allowing it to
    operate in much less space.  This makes it suitable for larger datasets
    that do not fit comfortably in memory

    The ``init`` keyword argument is the default initialization of the
    reduction.  This can be either a constant value like ``0`` or a callable
    like ``lambda : 0`` as might be used in ``defaultdict``.

    Simple Examples
    ---------------

    >>> from operator import add, mul
    >>> iseven = lambda x: x % 2 == 0

    >>> data = [1, 2, 3, 4, 5]

    >>> reduceby(iseven, add, data)  # doctest: +SKIP
    {False: 9, True: 6}

    >>> reduceby(iseven, mul, data)  # doctest: +SKIP
    {False: 15, True: 8}

    Complex Example
    ---------------

    >>> projects = [
    ...     {"name": "build roads", "state": "CA", "cost": 1000000},
    ...     {"name": "fight crime", "state": "IL", "cost": 100000},
    ...     {"name": "help farmers", "state": "IL", "cost": 2000000},
    ...     {"name": "help farmers", "state": "CA", "cost": 200000},
    ... ]

    >>> reduceby(
    ...     "state",  # doctest: +SKIP
    ...     lambda acc, x: acc + x["cost"],
    ...     projects,
    ...     0,
    ... )
    {'CA': 1200000, 'IL': 2100000}

    Example Using ``init``
    ----------------------

    >>> def set_add(s, i):
    ...     s.add(i)
    ...     return s

    >>> reduceby(iseven, set_add, [1, 2, 3, 4, 1, 2, 3], set)  # doctest: +SKIP
    {True:  set([2, 4]),
     False: set([1, 3])}
    """
    ...

def remove[T](predicate: Callable[[T], bool], seq: Iterable[T]) -> Iterator[T]:
    """
    Return those items of sequence for which predicate(item) is False

    >>> def iseven(x):
    ...     return x % 2 == 0
    >>> list(remove(iseven, [1, 2, 3, 4]))
    [1, 3]
    """
    ...

def second[T](seq: Iterable[T]) -> T:
    """
    The second element in a sequence

    >>> second("ABC")
    'B'
    """
    ...

def sliding_window[T](n: int, seq: Iterable[T]) -> Iterator[tuple[T, ...]]:
    """
    A sequence of overlapping subsequences

    >>> list(sliding_window(2, [1, 2, 3, 4]))
    [(1, 2), (2, 3), (3, 4)]

    This function creates a sliding window suitable for transformations like
    sliding means / smoothing

    >>> mean = lambda seq: float(sum(seq)) / len(seq)
    >>> list(map(mean, sliding_window(2, [1, 2, 3, 4])))
    [1.5, 2.5, 3.5]
    """
    ...

def tail[T](n: int, seq: Iterable[T]) -> Iterator[T]:
    """
    The last n elements of a sequence

    >>> tail(2, [10, 20, 30, 40, 50])
    [40, 50]

    See Also:
        drop
        take
    """
    ...

def take[T](n: int, seq: Iterable[T]) -> Iterator[T]:
    """
    The first n elements of a sequence

    >>> list(take(2, [10, 20, 30, 40, 50]))
    [10, 20]

    See Also:
        drop
        tail
    """
    ...

def take_nth[T](n: int, seq: Iterable[T]) -> Iterator[T]:
    """
    Every nth item in seq

    >>> list(take_nth(2, [10, 20, 30, 40, 50]))
    [10, 30, 50]
    """
    ...

def topk[T](
    k: int, seq: Iterable[T], key: Callable[[T], Any] | None = ...
) -> tuple[T, ...]:
    """
    Find the k largest elements of a sequence

    Operates lazily in ``n*log(k)`` time

    >>> topk(2, [1, 100, 10, 1000])
    (1000, 100)

    Use a key function to change sorted order

    >>> topk(2, ["Alice", "Bob", "Charlie", "Dan"], key=len)
    ('Charlie', 'Alice')

    See also:
        heapq.nlargest
    """
    ...

def unique[T](seq: Iterable[T], key: Callable[[T], Any] | None = ...) -> Iterator[T]:
    """
    Return only unique elements of a sequence

    >>> tuple(unique((1, 2, 3)))
    (1, 2, 3)
    >>> tuple(unique((1, 2, 1, 3)))
    (1, 2, 3)

    Uniqueness can be defined by key keyword

    >>> tuple(unique(["cat", "mouse", "dog", "hen"], key=len))
    ('cat', 'mouse')
    """
    ...
