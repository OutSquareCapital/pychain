from collections.abc import Iterable

import pychain as pc

STOP = 100


def pyfunc_opti(data: Iterable[int]) -> list[str]:
    return [
        f"result is: {round(30 * (2 / (x + 5)), 3)}"
        for x in data
        if x > 5 and x % 2 != 0 and x + 5 != 0
    ]


fn = (
    pc.iter(int)
    .filter(lambda x: x > 5 and x % 2 != 0 and x + 5 != 0)
    .map(
        f=(
            pc.expr(int)
            .into(lambda x: 30 * (2 / (x + 5)))
            .into(lambda x: round(x, 3))
            .into(lambda x: f"result is: {x}")
            .collect()
        )
    )
    .into(obj=list)
    .collect("cython")
)
print(fn)
print(fn(range(10)))
