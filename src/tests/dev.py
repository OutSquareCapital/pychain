from collections.abc import Iterable

import pychain as pc

STOP = 100


def pyfunc_opti(data: Iterable[int]) -> list[str]:
    return [
        f"result is: {round(30 * (2 / (x + 5)), 3)}"
        for x in data
        if x > 5 and x % 2 != 0 and x + 5 != 0
    ]


def map_func(x: int):
    return (
        pc.Pipe(x)
        .do(lambda x: 30 * (2 / (x + 5)))
        .do(lambda x: round(x, 3))
        .do(lambda x: f"result is: {x}")
        .unwrap()
    )


(
    pc.Iter(range(STOP))
    .filter(lambda x: x > 5 and x % 2 != 0 and x + 5 != 0)
    .map(map_func)
    .do(list)
    .unwrap()
)
