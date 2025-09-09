from collections.abc import Iterable

import cytoolz as cz


def peekn[T](seq: Iterable[T], n: int, note: str | None = None):
    """Return an iterator equivalent to seq after printing the first n items.

    Example:
        >>> list(peekn([0, 1, 2, 3], 2))
        Peeked 2 values: [0, 1]
        [0, 1, 2, 3]
    """
    values, sequence = cz.itertoolz.peekn(n, seq)
    if note:
        print(f"Peeked {n} values ({note}): {list(values)}")
    else:
        print(f"Peeked {n} values: {list(values)}")
    return sequence


def peek[T](seq: Iterable[T], note: str | None = None):
    value, sequence = cz.itertoolz.peek(seq)
    if note:
        print(f"Peeked value ({note}): {value}")
    else:
        print(f"Peeked value: {value}")
    return sequence
