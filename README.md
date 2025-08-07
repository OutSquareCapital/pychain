# pychain

**pychain** is a Python library for declarative, chainable, and composable data transformations.

It provides a unified, type-safe API for working with scalars, iterables, and dictionaries, making complex data manipulation pipelines concise and expressive.

## Installation

```bash
uv add git+https://github.com/OutSquareCapital/pychain.git
```

## Current basic example (WIP so it changes often)

````python
import src.pychain as pc
from collections.abc import Iterable

STOP = 1000


def pure_functionnal(arg: Iterable[int]) -> list[str]:
    def fn_compiled(x: int) -> str:
        return f"result is: {round(30 * (2 / (x + 5)), 3)}"

    def _filter_value(x: int) -> bool:
        return x > 5 and x % 2 != 0 and x + 5 != 0

    return list(map(fn_compiled, filter(_filter_value, arg)))


def pyfunc_opti(data: Iterable[int]) -> list[str]:
    return [
        f"result is: {round(30 * (2 / (x + 5)), 3)}"
        for x in data
        if x > 5 and x % 2 != 0 and x + 5 != 0
    ]


fn = (
    pc.expr(int)
    .into(lambda x: 30 * (2 / (x + 5)))
    .into(lambda x: round(x, 3))
    .into(lambda x: f"result is: {x}")
    .collect()
)

pychain = (
    pc.iter(int)
    .filter(lambda x: x > 5 and x % 2 != 0 and x + 5 != 0)
    .map(fn)
    .into(obj=list)
    .collect()
)

print(fn)
print(pychain)

data = range(1, STOP)
assert pure_functionnal(data) == pychain(data) == pyfunc_opti(data)

pychain.Func
-- Source --
    def generated_func_8689d33e8bbf4417af26c81f81909a6e(arg):
        return f'result is: {round(30 * (2 / (arg + 5)), 3)}'
pychain.Func
-- Source --
    def generated_func_61d52343404643e6b028c6ea6713b8ad(arg):
        return list(map(ref_func_1816989190192, filter(ref_func_1816993862720, arg)))

````
