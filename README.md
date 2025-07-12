# pychain

**pychain** is a Python library for declarative, chainable, and composable data transformations, inspired by functional programming and powered by [cytoolz](https://github.com/pytoolz/cytoolz). It provides a unified, type-safe API for working with scalars, iterables, and dictionaries, making complex data manipulation pipelines concise, readable, and expressive.
Designed to interoperate with pandas, polars, NumPy, and standard Python collections. It is NOT meant as an heavy computation dataframe/array library, but rather as a collections/iterable transformer,
for easier intermediate steps between numpy/duckdb/polars computations.

## Quickstart

````python
from pychain import chain, op

(
    chain.from_range(1, 6)  # range from 1 to 5
    .map(op().mul(2).pow(2))  # [4, 16, 36, 64, 100]
    .filter(op().gt(5))  # [16, 36, 64, 100]
    .cumsum()  # [16, 52, 116, 216]
    .enumerate()  # [(0, 16), (1, 52), (2, 116), (3, 216)]
    .flatten()  # [0, 16, 1, 52, 2, 116, 3, 216]
    .rolling(3)  # [(0, 16, 1), (16, 1, 52), (1, 52, 2), (52, 2, 116), (2, 116, 3), (116, 3, 216)]
    .map(
        lambda x: f"index: {x[0]}, value: {x[1]}"
    )
    .convert_to.list()  # Computation only happens here! Otherwise it's simply a list of functions, a range, and pychain objects (py classes with slots, or cython class)
)

['index: 0, value: 16',
'index: 16, value: 1',
'index: 1, value: 52',
'index: 52, value: 2',
'index: 2, value: 116',
'index: 116, value: 3']
````

---

## Installation

```bash
uv pip install git+https://github.com/OutSquareCapital/pychain.git
```

```bash
uv add git+https://github.com/OutSquareCapital/pychain.git
```

---

## API

### Overview

pychain provides "chain" and "op" as entry point

#### Chaining and Conversion

- All chain objects support method chaining for transformations, filtering, mapping, reducing, etc.
- Use `.convert_to` and `.convert_keys_to` for conversion to standard Python types.
- Use `.unwrap()` to extract the underlying data.
- All chains are immutable and side-effect free.

#### Usage Patterns

- Use "from pychain import ..." rather than "import pychain as ...".
- Use op expressions rather than lambda whenever possible, unless the performance is critical.
- Use `chain` to wrap any data structure and immediately access chain methods.
- All transformations are lazy where possible, supporting method chaining.
- Data can be unwrapped at any time using `.unwrap()` or converted to standard types with `.convert_to` or `.convert_keys_to`.
- Prefer method chaining over intermediate variables.
- Use `.unwrap()` or `.convert_to` only at the end of a pipeline.
- For debugging, tap, peek or peekn are the ways to go.
- Using list comprehensions, for loops and generators inside pychain methods is considered an anti-pattern.

### chain

Central factory for all chain-based data structures and conversions in pychain.

The `chain` singleton is the main entry point for all user operations in pychain. It provides a unified, discoverable, and consistent API for constructing, converting, and manipulating data in a functional, chainable style.
the `__call__` dunder method is the idiomatic way to start a chain for iterables.

`chain` exposes methods to:

- Wrap scalars, iterables, dicts, DataFrames, arrays, etc. into chainable objects.
- Read data from files (CSV, Parquet, JSON, NDJSON) into chainable forms.
- Convert between data representations (iterable, dict, DataFrame, etc.).
- Generate infinite or finite sequences (from_func, from_range).
- Compose and chain operations fluently, with a focus on readability and composability.

#### Instanciation

- Iterable: `chain(iterable)` wraps any iterable and return an Iterchain object.
- Dict: `chain.from_dict(dict_obj)` wraps a dict and return a DictChain object.
- DataFrame: `chain.from_pd(df)`, `chain.from_pl(df)` for pandas/polars.
- NumPy: `chain.from_np(array)` wraps a NumPy array.
- File IO: `chain.read_csv(path)`, `chain.read_parquet(path)`, etc.
- Infinite: `chain.from_func(seed, func)` for infinite iterators.
- Range: `chain.from_range(start, stop, step)` for integer ranges.
- Dict of iterables: `chain.from_dict_of_iterables(d)` will return a DictChain where the iterables are wrapped inside iterchain objects.

### op

pychain provide a powerful expression builder, directly inspired from polars.
Goal is to give access to common operations without the repetitive lambda syntax, and to allow expressions chaining.
All the expressions generated are reusable callables.
Each method call will generate a function, just like a lambda.

#### Examples

````python
from pychain import chain, op

def pure_python() -> list[str]:
    return [
        f"result is: {round(number=10 * (2 / (x + 5)), ndigits=3)}"
        for x in range(1, 10)
        if x > 5
    ]


def pychain_lambdas() -> list[str]:
    return (
        chain.from_range(start=1, stop=10)
        .filter(f=lambda x: x > 5)
        .compose(lambda x: 10 * (2 / (x + 5)), lambda x: round(number=x, ndigits=3))
        .map(f=lambda x: f"result is: {x}")
        .convert_to.list()
    )


def pychain_op() -> list[str]:
    return (
        chain.from_range(start=1, stop=10)
        .filter(f=op.gt(value=5))
        .compose(
            op.add(value=5).truediv_r(value=2).mul(value=10),
            lambda x: round(number=x, ndigits=3),
        )
        .map(f=lambda x: f"result is: {x}")
        .convert_to.list()
    )


['result is: 1.818',
 'result is: 1.667',
 'result is: 1.538',
 'result is: 1.429']
````

The expression builder entry point is callable to provide convenient attribute syntax when mapping objects.
The four chains below all produce the same output.
Since the first map change the underlying type, it is considered more idiomatic to write 2 separate map call, rather than one compose call.
This also preserve the types.

````python
from typing import NamedTuple
from pychain import chain, op


class Point(NamedTuple):
    x: int
    y: int

# using lambdas rather than expressions will be a bit faster.
(
    chain.from_range(1, 10)
    .map(lambda p: Point(p, p * 2))
    .map(lambda x: x.x * 2)
    .convert_to.list()
)

(
    chain.from_range(1, 10)
    .map(lambda p: Point(p, p * 2))
    .map(op("x").mul(2))
    .convert_to.list()
)

# This will warn you that x is an unknow type
(
    chain.from_range(1, 10)
    .compose(lambda p: Point(p, p * 2), lambda x: x.x * 2)
    .convert_to.list()
)

(
    chain.from_range(1, 10)
    .compose(lambda p: Point(p, p * 2), op("x").mul(2))
    .convert_to.list()
)

[2, 4, 6, 8, 10, 12, 14, 16, 18]
````

## Implementation details

The underlying classes of the expressions builder is implemented in Cython to reduce instanciation costs.
The expressions methods are returning stdlib functions, either directly, or from simple wrappers (see _fn package for details)

`chain.read_` methods are using polars engine, and the methods from IterChain or DictChain are using cytoolz functions.

For performance, whenever possible, fn functions return partials rather than lambdas.
Most of the overhead induced by pychain comes from additional functions calls.
Please note that the performance difference between two closely related computations can be surprising.

Consider the following benchmark:

````python

import operator
from collections.abc import Callable
from functools import partial

def truediv[T](value: T) -> Callable[[T], T]:
    return lambda x: operator.truediv(x, value)


def truediv_r[T](value: T) -> Callable[[T], T]:
    return partial(operator.truediv, value)

%timeit truediv(4)(2)
%timeit truediv_r(4)(2)

334 ns ± 19.8 ns per loop (mean ± std. dev. of 7 runs, 1,000,000 loops each)
270 ns ± 6.41 ns per loop (mean ± std. dev. of 7 runs, 1,000,000 loops each) 
````

---

## Tests

From the root:

```bash
python doctests.py
```

---

## License

MIT

---

## Acknowledgements

- [cytoolz](https://github.com/pytoolz/cytoolz)
- [toolz](https://github.com/pytoolz/toolz)
- [Polars](https://github.com/pola-rs/polars)
- [pandas](https://github.com/pandas-dev/pandas)

---
