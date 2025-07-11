# pychain

**pychain** is a Python library for declarative, chainable, and composable data transformations, inspired by functional programming and powered by [cytoolz](https://github.com/pytoolz/cytoolz). It provides a unified, type-safe API for working with scalars, iterables, and dictionaries, making complex data manipulation pipelines concise, readable, and expressive.

## Quickstart

````python
    result = (
        chain.from_range(1, 6)  # [1, 2, 3, 4, 5]
        .map(fn.mul(2))  # [2, 4, 6, 8, 10]
        .filter(fn.gt(5))  # [6, 8, 10]
        .cumsum()  # [6, 14, 24]
        .convert_to.list()  # [6, 14, 24]
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

### fn

pychain provide a namespace fn, containing many functions that return callable, avoiding lambda boilerplate when not necessary.

````python
from src.pychain import chain, fn

def pychain_lambdas():
    return (
        chain.from_range(1, 10)
        .filter(lambda x: x > 5)
        .map(lambda x: (x + 5) / 2)
        .map(lambda x: f"result is: {x}")
        .convert_to.list()
    )


def pychain_fn():
    return (
        chain.from_range(1, 10)
        .filter(fn.gt(5))
        .compose(fn.add(5), fn.truediv(2))
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
