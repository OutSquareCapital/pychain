# pychain

**pychain** is a Python library for declarative, chainable, and composable data transformations, inspired by functional programming and powered by [cytoolz](https://github.com/pytoolz/cytoolz). It provides a unified, type-safe API for working with scalars, iterables, and dictionaries, making complex data manipulation pipelines concise, readable, and expressive.

## Quickstart

````python
(
    chain.from_range(1, 6)  # range from 1 to 5
    .map(op().mul(2).pow(2))  # [4, 16, 36, 64, 100]
    .filter(op().gt(5))  # [16, 36, 64, 100]
    .cumsum()  # [16, 52, 116, 216]
    .enumerate()  # [(0, 16), (1, 52), (2, 116), (3, 216)]
    .flatten()  # [0, 16, 1, 52, 2, 116, 3, 216]
    .rolling(2)  # [(0, 16), (16, 1), (1, 52), (52, 2), (2, 116), (116, 3), (3, 216)]
    .map(
        lambda x: f"index: {x[0]}, value: {x[1]}"
    )  # ['index: 0, value: 16', 'index: 1, value: 52', 'index: 2, value: 116', 'index: 3, value: 216']
    .convert_to.list()  # Computation only happens here! Otherwise it's simply a list of functions, a range, and pychain objects (py classes with slots, or cython class)
)
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

## API Overview

### chain

Central factory for all chain-based data structures and conversions in pychain.

The `chain` singleton is the main entry point for all user operations in pychain. It provides a unified, discoverable, and consistent API for constructing, converting, and manipulating data in a functional, chainable style.

It is callable, and this can allow you to directly wrap an iterable around

`chain` exposes methods to:

- Wrap scalars, iterables, dicts, DataFrames, arrays, etc. into chainable objects.
- Read data from files (CSV, Parquet, JSON, NDJSON) into chainable forms.
- Convert between data representations (iterable, dict, DataFrame, etc.).
- Generate infinite or finite sequences (from_func, from_range).
- Compose and chain operations fluently, with a focus on readability and composability.

### op

pychain provide a powerful expression builder, directly inspired from polars. Goal is to give access to common operations without the repetitive lambda syntax, and to allow expressions chaining.
All the expressions generated are reusable callables.
The underlying class is implemented in Cython to reduce instanciation costs.

````python
from src.pychain import chain, op

def pychain_lambdas():
    return (
        chain.from_range(1, 10)
        .filter(lambda x: x > 5)
        .map(lambda x: (x + 5) / 2)
        .map(lambda x: f"result is: {x}")
        .convert_to.list()
    )


def pychain_op():
    return (
        chain.from_range(1, 10)
        .filter(op().gt(5))
        .compose(op().add(5).truediv(2))
        .map(lambda x: f"result is: {x}")
        .convert_to.list()
    )


def pure_python():
    return [f"result is: {(x + 5) / 2}" for x in range(1, 10) if x > 5]

['result is: 5.5', 'result is: 6.0', 'result is: 6.5', 'result is: 7.0']
````

#### Performance

For performance, whenever possible, fn functions return partials rather than lambdas.
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

#### Usage Patterns

- Use `chain` to wrap any data structure and immediately access chain methods.
- All transformations are lazy where possible, supporting method chaining.
- Data can be unwrapped at any time using `.unwrap()` or converted to standard types with `.convert_to` or `.convert_keys_to`.
- File readers (read_csv, read_parquet, etc.) return columnar DictChain objects for easy column-wise processing.
- Always start with `chain` for new data pipelines.
- Prefer method chaining over intermediate variables for clarity.
- Use `.unwrap()` or `.convert_to` only at the end of a pipeline.
- Using list comprehensions, for loops and generators inside pychain methods is considered an anti-pattern

#### API Structure

- Iterable: `chain.from_iter(iterable)` wraps any iterable.
- Dict: `chain.from_dict(dict_obj)` wraps a dict.
- DataFrame: `chain.from_pd(df)`, `chain.from_pl(df)` for pandas/polars.
- NumPy: `chain.from_np(array)` wraps a NumPy array.
- File IO: `chain.read_csv(path)`, `chain.read_parquet(path)`, etc.
- Infinite: `chain.from_func(seed, func)` for infinite iterators.
- Range: `chain.from_range(start, stop, step)` for integer ranges.
- Dict of iterables: `chain.from_dict_of_iterables(d)` for nested chains.

#### Chaining and Conversion

- All chain objects support method chaining for transformations, filtering, mapping, reducing, etc.
- Use `.convert_to` and `.convert_keys_to` for conversion to standard Python types.
- Use `.unwrap()` to extract the underlying data.
- All chains are immutable and side-effect free.

#### Integration

- Designed to interoperate with pandas, polars, NumPy, and standard Python collections.

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
