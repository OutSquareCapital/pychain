import itertools
from collections.abc import Callable, Iterable, Iterator
from functools import partial
from random import Random
from typing import Any, Concatenate, overload

import cytoolz as cz
import more_itertools as mit

from .._core import Peeked, SupportsRichComparison


def filter_[**P, T](data: Iterable[T], func: Callable[[T], bool]) -> Iterator[T]:
    return filter(func, data)


def map_[**P, R, T](
    data: Iterable[T],
    func: Callable[Concatenate[T, P], R],
    *args: P.args,
    **kwargs: P.kwargs,
) -> Iterable[R]:
    return map(partial(func, *args, **kwargs), data)


def map_flat[**P, R, T](
    data: Iterable[T],
    func: Callable[Concatenate[T, P], Iterable[R]],
    *args: P.args,
    **kwargs: P.kwargs,
) -> Iterable[R]:
    return itertools.chain.from_iterable(map(func, data, *args, **kwargs))


def map_join[T, R](
    data: Iterable[T], others: Iterable[Iterable[T]], func: Callable[[T], R]
) -> Iterable[R]:
    return map(func, itertools.chain.from_iterable((data, *others)))


def map_except[T, R](
    data: Iterable[T], func: Callable[[T], R], *exceptions: type[BaseException]
) -> Iterable[R]:
    return mit.map_except(func, data, *exceptions)


def starmap_[R, U: Iterable[Any]](
    data: Iterable[U], func: Callable[..., R]
) -> Iterable[R]:
    return itertools.starmap(func, data)


def filter_isin[T](data: Iterable[T], values: Iterable[T]) -> Iterable[T]:
    value_set: set[T] = set(values)
    return (x for x in data if x in value_set)


def filter_notin[T](data: Iterable[T], values: Iterable[T]) -> Iterable[T]:
    value_set: set[T] = set(values)
    return (x for x in data if x not in value_set)


def filter_contain(data: Iterable[str], text: str) -> Iterable[str]:
    return (x for x in data if text in x)


def filter_subclass[U: Iterable[type], R](
    data: Iterable[type], parent: type[R]
) -> Iterable[type[R]]:
    return (x for x in data if issubclass(x, parent))


def filter_type[T](data: Iterable[Any], typ: type[T]) -> Iterable[T]:
    return (x for x in data if isinstance(x, typ))


def filter_attr[T](data: Iterable[T], attr: str) -> Iterable[T]:
    return (x for x in data if hasattr(x, attr))


def filter_callable(data: Iterable[object]) -> Iterable[Callable[..., Any]]:
    return (x for x in data if callable(x))


def filter_false[**P, T](
    data: Iterable[T],
    func: Callable[Concatenate[T, P], bool],
    *args: P.args,
    **kwargs: P.kwargs,
) -> Iterator[T]:
    return itertools.filterfalse(func, data, *args, **kwargs)


def filter_except[T](
    data: Iterable[T], func: Callable[[T], object], *exceptions: type[BaseException]
) -> Iterator[T]:
    return mit.filter_except(func, data, *exceptions)


def take_while[T](data: Iterable[T], predicate: Callable[[T], bool]) -> Iterator[T]:
    return itertools.takewhile(predicate, data)


def drop_while[T](data: Iterable[T], predicate: Callable[[T], bool]) -> Iterator[T]:
    return itertools.dropwhile(predicate, data)


def head[T](data: Iterable[T], n: int) -> Iterator[T]:
    return cz.itertoolz.take(n, data)


def tail[T](data: Iterable[T], n: int) -> Iterator[T]:
    return cz.itertoolz.tail(n, data)


def drop_first[T](data: Iterable[T], n: int) -> Iterator[T]:
    return cz.itertoolz.drop(n, data)


def elements[T](data: Iterable[T]) -> Iterable[T]:
    from collections import Counter

    return Counter(data).elements()


def reverse[T](data: Iterable[T]) -> Iterable[T]:
    return reversed(list(data))


def peekn[T](data: Iterable[T], n: int) -> Iterable[T]:
    peeked = Peeked(*cz.itertoolz.peekn(n, data))
    print(f"Peeked {n} values: {peeked.value}")
    return peeked.sequence


def peek[T](data: Iterable[T]) -> Iterable[T]:
    peeked = Peeked(*cz.itertoolz.peek(data))
    print(f"Peeked value: {peeked.value}")
    return peeked.sequence


def concat[T](data: Iterable[T], *others: Iterable[T]) -> Iterator[T]:
    return itertools.chain.from_iterable((data, *others))


def interpose[T](data: Iterable[T], element: T) -> Iterable[T]:
    return cz.itertoolz.interpose(element, data)


def interleave[T](data: Iterable[T], *others: Iterable[T]) -> Iterable[T]:
    return cz.itertoolz.interleave((data, *others))


def random_sample[T](
    data: Iterable[T], probability: float, state: Random | int | None = None
) -> Iterable[T]:
    return cz.itertoolz.random_sample(probability, data, state)


def accumulate[T](data: Iterable[T], func: Callable[[T, T], T]) -> Iterable[T]:
    return cz.itertoolz.accumulate(func, data)


def insert_left[T](data: Iterable[T], value: T) -> Iterable[T]:
    return cz.itertoolz.cons(value, data)


def top_n[T](data: Iterable[T], n: int, key: Callable[[T], Any] | None = None):
    return cz.itertoolz.topk(n, data, key)


def every[T](data: Iterable[T], index: int) -> Iterator[T]:
    return cz.itertoolz.take_nth(index, data)


def slice[T](
    data: Iterable[T], start: int | None = None, stop: int | None = None
) -> Iterator[T]:
    return itertools.islice(data, start, stop)


def filter_map[T, R](data: Iterable[T], func: Callable[[T], R]) -> Iterable[R]:
    return mit.filter_map(func, data)


def sorted_[T: SupportsRichComparison[Any]](
    data: Iterable[T], key: Callable[[T], Any] | None = None, reverse: bool = False
) -> list[T]:
    return sorted(data, key=key, reverse=reverse)


def zip_offset[T, U](
    data: Iterable[T],
    *others: Iterable[T],
    offsets: list[int],
    longest: bool = False,
    fillvalue: U = None,
) -> Iterator[tuple[T | U, ...]]:
    return mit.zip_offset(
        data,
        *others,
        offsets=offsets,
        longest=longest,
        fillvalue=fillvalue,
    )


@overload
def map_juxt[T, R1, R2](
    data: Iterable[T],
    func1: Callable[[T], R1],
    func2: Callable[[T], R2],
    /,
) -> Iterable[tuple[R1, R2]]: ...
@overload
def map_juxt[T, R, R1, R2, R3](
    data: Iterable[T],
    func1: Callable[[T], R1],
    func2: Callable[[T], R2],
    func3: Callable[[T], R3],
    /,
) -> Iterable[tuple[R1, R2, R3]]: ...
@overload
def map_juxt[T, R1, R2, R3, R4](
    data: Iterable[T],
    func1: Callable[[T], R1],
    func2: Callable[[T], R2],
    func3: Callable[[T], R3],
    func4: Callable[[T], R4],
    /,
) -> Iterable[tuple[R1, R2, R3, R4]]: ...


def map_juxt[T](
    data: Iterable[T], *funcs: Callable[[T], object]
) -> Iterable[tuple[object, ...]]:
    return map(cz.functoolz.juxt(*funcs), data)


def partition_by[T](
    data: Iterable[T], predicate: Callable[[T], bool]
) -> Iterable[tuple[T, ...]]:
    return cz.recipes.partitionby(predicate, data)


def join[R, K, T](
    data: Iterable[T],
    other: Iterable[R],
    left_on: Callable[[T], K],
    right_on: Callable[[R], K],
    left_default: T | None = None,
    right_default: R | None = None,
) -> Iterable[tuple[T, R]]:
    return cz.itertoolz.join(
        leftkey=left_on,
        leftseq=data,
        rightkey=right_on,
        rightseq=other,
        left_default=left_default,
        right_default=right_default,
    )


def zip_broadcast[T](
    data: Iterable[T],
    *others: Iterable[T],
    scalar_types: tuple[type, type] | None = (str, bytes),
    strict: bool = False,
) -> Iterable[tuple[T, ...]]:
    return mit.zip_broadcast(data, *others, scalar_types=scalar_types, strict=strict)


def adjacent[T](
    data: Iterable[T], predicate: Callable[[T], bool], distance: int = 1
) -> Iterable[tuple[bool, T]]:
    return mit.adjacent(predicate, data, distance)


def most_common[T](data: Iterable[T], n: int | None = None) -> Iterable[tuple[T, int]]:
    from collections import Counter

    return Counter(data).most_common(n)


def partition[T](
    data: Iterable[T], n: int, pad: T | None = None
) -> Iterable[tuple[T, ...]]:
    return cz.itertoolz.partition(n, data, pad)


def partition_all[T](data: Iterable[T], n: int) -> Iterable[tuple[T, ...]]:
    return cz.itertoolz.partition_all(n, data)


def sliding_window[T](data: Iterable[T], length: int) -> Iterable[tuple[T, ...]]:
    return cz.itertoolz.sliding_window(length, data)


@overload
def zip_equal[T](__iter1: Iterable[T]) -> Iterator[tuple[T]]: ...
@overload
def zip_equal[T, T2](
    __iter1: Iterable[T], __iter2: Iterable[T2]
) -> Iterator[tuple[T, T2]]: ...
@overload
def zip_equal[T, T2, T3](
    __iter1: Iterable[T], __iter2: Iterable[T2], __iter3: Iterable[T3]
) -> Iterator[tuple[T, T2, T3]]: ...
@overload
def zip_equal[T, T2, T3, T4](
    __iter1: Iterable[T],
    __iter2: Iterable[T2],
    __iter3: Iterable[T3],
    __iter4: Iterable[T4],
) -> Iterator[tuple[T, T2, T3, T4]]: ...
@overload
def zip_equal[T, T2, T3, T4, T5](
    __iter1: Iterable[T],
    __iter2: Iterable[T2],
    __iter3: Iterable[T3],
    __iter4: Iterable[T4],
    __iter5: Iterable[T5],
) -> Iterator[tuple[T, T2, T3, T4, T5]]: ...
@overload
def zip_equal(
    __iter1: Iterable[Any],
    __iter2: Iterable[Any],
    __iter3: Iterable[Any],
    __iter4: Iterable[Any],
    __iter5: Iterable[Any],
    __iter6: Iterable[Any],
    *iterables: Iterable[Any],
) -> Iterator[tuple[Any, ...]]: ...
def zip_equal[T](
    data: Iterable[T], *others: Iterable[Any]
) -> Iterator[tuple[Any, ...]]:
    return mit.zip_equal(data, *others)


def product[T, U](data: Iterable[T], other: Iterable[U]) -> Iterable[tuple[T, U]]:
    return itertools.product(data, other)
