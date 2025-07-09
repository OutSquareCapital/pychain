from collections.abc import Callable, Iterable, Iterator
from typing import Any, Protocol

import cytoolz as cz


class Random(Protocol):
    def random(self, *args: Any, **kwargs: Any) -> float: ...


type CheckFunc[T] = Callable[[T], bool]
type ProcessFunc[T] = Callable[[T], T]
type TransformFunc[T, T1] = Callable[[T], T1]
type AggFunc[V, V1] = Callable[[Iterable[V]], V1]
type ThreadFunc[T] = Callable[..., T] | tuple[Callable[..., T], Any]

def thread_first[T](val: T, fns: Iterable[ThreadFunc[T]]) -> T:
    """
    Thread the value through a sequence of functions, as the first argument (see cytoolz.thread_first).

    Example:
        >>> thread_first(1, [(lambda x: x + 1), (lambda x: x * 10)])
        20
    """
    return cz.functoolz.thread_first(val, *fns)


def thread_last[T](val: T, fns: Iterable[ThreadFunc[T]]) -> T:
    """
    Thread the value through a sequence of functions, as the last argument (see cytoolz.thread_last).

    Example:
        >>> thread_last([1, 2, 3], [(map, lambda x: x + 1), sum])
        9
    """
    return cz.functoolz.thread_last(val, *fns)


def merge[K, V](on: dict[K, V], others: Iterable[dict[K, V]]) -> dict[K, V]:
    """
    Merge multiple dictionaries into one (see cytoolz.merge).

    Example:
        >>> merge(on={1: "one"}, others=({2: "two"}, {3: "three"}))
        {1: 'one', 2: 'two', 3: 'three'}

        Later dictionaries have precedence

        >>> merge(on={"a": 1}, others=({"b": 2}, {"c": 3}, {"c": 4}))
        {'a': 1, 'b': 2, 'c': 4}
    """
    return cz.dicttoolz.merge(on, *others)


def merge_with[K, V](
    f: Callable[..., V], on: dict[K, V], others: Iterable[dict[K, V]]
) -> dict[K, V]:
    """
    Merge dictionaries and combine values with a function (see cytoolz.merge_with).

    Example:
        >>> merge_with(sum, {'a': 1}, [{'a': 2, 'b': 3}])
        {'a': 3, 'b': 3}
    """
    return cz.dicttoolz.merge_with(f, on, *others)


def dissoc[K, V](d: dict[K, V], keys: Iterable[K]) -> dict[K, V]:
    """
    Return a new dict with keys removed (see cytoolz.dissoc).

    Example:
        >>> dissoc({'a': 1, 'b': 2}, ['a'])
        {'b': 2}
    """
    return cz.dicttoolz.dissoc(d, *keys)


def repeat[V](value: Iterable[V], n: int) -> Iterator[V]:
    """
    Repeat each element in the iterable n times (see cytoolz.repeat, cytoolz.concat).

    Example:
        >>> list(repeat([1, 2], 2))
        [1, 1, 2, 2]
    """
    return cz.itertoolz.concat(seqs=map(lambda x: [x] * n, value))


def concat[V](on: Iterable[V], others: Iterable[Iterable[V]]) -> Iterator[V]:
    """
    Concatenate multiple iterables (see cytoolz.concat).

    Example:
        >>> list(concat([1, 2], [[3, 4], [5]]))
        [1, 2, 3, 4, 5]
    """
    return cz.itertoolz.concat([on, *others])


def interleave[V](on: Iterable[V], others: Iterable[Iterable[V]]) -> Iterator[V]:
    """
    Interleave elements from several iterables (see cytoolz.interleave).

    Example:
        >>> list(interleave([1, 2], [[10, 20]]))
        [1, 10, 2, 20]
    """
    return cz.itertoolz.interleave(seqs=[on, *others])


def merge_sorted[V](
    on: Iterable[V],
    others: Iterable[Iterable[V]],
    sort_on: Callable[[V], Any] | None = None,
) -> Iterator[V]:
    """
    Merge and sort several iterables (see cytoolz.merge_sorted).

    Example:
        >>> list(merge_sorted([1, 3], [[2, 4]]))
        [1, 2, 3, 4]
    """
    return cz.itertoolz.merge_sorted(on, *others, key=sort_on)


def peek[T](seq: Iterable[T], note: str | None = None) -> Iterator[T]:
    """
    Peek at the first element of an iterable, printing it, and return the full sequence (see cytoolz.peek).

    Example:
        >>> it = peek([1, 2, 3], note='demo')
        Peeked value (demo): 1
        >>> list(it)
        [1, 2, 3]
    """
    value, sequence = cz.itertoolz.peek(seq)
    if note:
        print(f"Peeked value ({note}): {value}")
    else:
        print(f"Peeked value: {value}")
    return sequence


def peekn[T](seq: Iterable[T], n: int, note: str | None = None) -> Iterator[T]:
    """
    Peek at the first n elements of an iterable, printing them, and return the full sequence (see cytoolz.peekn).

    Example:
        >>> it = peekn([1, 2, 3, 4], 2)
        Peeked 2 values: [1, 2]
        >>> list(it)
        [1, 2, 3, 4]
    """
    values, sequence = cz.itertoolz.peekn(n, seq)
    if note:
        print(f"Peeked {n} values ({note}): {list(values)}")
    else:
        print(f"Peeked {n} values: {list(values)}")
    return sequence


def flat_map[V, V1](
    value: Iterable[V], func: TransformFunc[V, Iterable[V1]]
) -> Iterable[V1]:
    """
    Map a function over an iterable and flatten the result (see cytoolz.concatmap).

    Example:
        >>> list(flat_map([1, 2], lambda x: [x, x+10]))
        [1, 11, 2, 12]
    """
    return cz.itertoolz.concat(map(func, value))


def diff_with[T, V](
    value: Iterable[T], others: Iterable[Iterable[T]], default: Any|None = None, key: ProcessFunc[V] | None = None
) -> Iterable[tuple[T, ...]]:
    """
    Compute the difference between iterables (see cytoolz.diff).

    Return those items that differ between sequences.

    Example:
        >>> list(diff_with(value=[1, 2, 3], others=[[1, 2, 10, 100]]))
        [(3, 10), (None, 100)]

        You can replace `None` with a custom default value:

        >>> list(diff_with(value=[1, 2, 3], others=[[1, 2, 10, 100]], default="default"))
        [(3, 10), ('default', 100)]

        A key function may also be applied to each item to use during comparisons:

        >>> list(diff_with(value=["apples", "bananas"], others=[["Apples", "Oranges"]], key=str.lower))
        [('bananas', 'Oranges')]
    """
    return cz.itertoolz.diff(*(value, *others), default=default, key=key)



def zip_with[T, V](
    value: Iterable[T], others: Iterable[Iterable[V]], strict: bool
) -> Iterable[tuple[T, V]]:
    """
    Zip several iterables together (like built-in zip).

    Example:
        >>> list(zip_with([1, 2], [[10, 20]], strict=False))
        [(1, 10), (2, 20)]
    """
    return zip(value, *others, strict=strict)


def tap[V](value: Iterable[V], func: Callable[[V], Any]) -> Iterator[V]:
    """
    Apply a side-effect function to each element, yielding the original elements (see cytoolz.do/tap).

    Example:
        >>> list(tap([1, 2], print))
        1
        2
        [1, 2]
    """
    for item in value:
        func(item)
        yield item
