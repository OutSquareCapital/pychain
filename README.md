# pychain

**pychain** is a Python library for declarative, chainable, and composable data transformations.

It provides a unified, type-safe API for working with scalars, iterables, and dictionaries, making complex data manipulation pipelines concise and expressive.

## Current basic example (WIP so it changes often)

````python
from collections.abc import Iterable
import src.pychain as pc

STOP = 100_000


# ---------------------
def _calculate_value(x: int) -> float:
    return 10 * (2 / (x + 5)) * 3


def _format_value(x: float) -> str:
    return f"v:{x}".split(":")[1]


def _format_result(x: float) -> str:
    return f"result is: {x}"


def _round_value(x: float) -> float:
    return round(x, 3)

def _filter_func(x: int) -> bool:
    return x > 5 and x % 2 != 0 and x + 5 != 0

def _map_func(x: int) -> str:
    val = 10 * (2 / (x + 5)) * 3
    val = f"v:{val}".split(":")[1]
    val = float(val)
    val = round(val, 3)
    return f"result is: {val}"

composed_func = (
    pc.expr(int)
    .into(_calculate_value)
    .into(_format_value)
    .into(float)
    .into(_round_value)
    .into(_format_result)
    .collect()
)

def pyfunc(data: Iterable[int]) -> list[str]:
    results: list[str]  = []
    for x in data:
        if _filter_func(x):
            results.append(_map_func(x))
    return results

def pyfunc_opti(data: Iterable[int]) -> list[str]:
    return [
        f"result is: {round(number=float(f'v:{10 * (2 / (x + 5)) * 3}'.split(':')[1]), ndigits=3)}"
        for x in data
        if x > 5 and x % 2 != 0 and x + 5 != 0
    ]


pychain = (
    pc.iter(int).filter(f=_filter_func).map(f=composed_func).into(obj=list).collect()
)

# -------------------------

data = range(1, STOP)
assert (
    pyfunc(data)
    == pyfunc_opti(data)
    == pychain(data)
)
````

## Performance

````bash
# with STOP = 100_000
%timeit pychain(data)
%timeit pyfunc(data)
%timeit pyfunc_opti(data)

139 ms ± 825 μs per loop (mean ± std. dev. of 7 runs, 10 loops each)
145 ms ± 1.1 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)
128 ms ± 1.4 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)
````

---

## OUTDATED DOC

## API Overview

### Core Components

- **`Iter`**: A chainable iterator designed for lazy transformations on iterable data. Ideal for processing sequences with operations like mapping, filtering, reducing, and more.
- **`Struct`**: An immutable, dictionary-like structure optimized for columnar data. Perfect for working with structured datasets where immutability and type safety are key.
- **`op`**: A powerful expression builder for creating reusable, chainable operations. It eliminates the need for repetitive lambda functions and allows for concise, readable transformations.
- **`constructors`**: A set of utility functions to create `Iter` and `Struct` objects from various sources, such as ranges, files, or existing data structures.

---

## Guidelines and Best Practices

### General Principles

- **Avoid Loops**: Do not use `for` loops, list comprehensions, or generators. Instead, rely on method chaining for all transformations.
- **Store Expressions**: Since expressions are concrete callables, store them in variables for reuse rather than wrapping them in functions. This avoids unnecessary overhead.

  ```python
  # Good Practice
  expr = pc.op().add(5).mul(2)
  result = pc.from_range(1, 6).map(expr).to_list()

  # Avoid
  def expr(x):
      return pc.op().add(5).mul(2)
  result = pc.from_range(1, 6).map(expr).to_list()
  ```

### Functional and Declarative Style

- **No Side Effects**: Ensure that all operations are side-effect free. Use `.tap()` or `.peek()` for debugging without altering the pipeline.
- **Composable Callables**: Leverage the composability of callables to build complex transformations incrementally.

  ```python
  # Example of composable callables
  expr = pc.op().add(5).mul(2)
  filter_expr = pc.op().gt(10)
  result = (
      pc.from_range(1, 6)
      .map(expr)
      .filter(filter_expr)
      .to_list()
  )
  ```

### Avoid Anti-Patterns

- **Avoid Inline Lambdas**: Use `op` expressions instead of inline lambdas for better readability and reusability. The performance is almost the same anyways.

  ```python
  # Good Practice
  expr = pc.op().add(5).mul(2)
  result = pc.from_range(1, 6).map(expr).to_list()

  # Avoid
  result = pc.from_range(1, 6).map(lambda x: (x + 5) * 2).to_list()
  ```

- **Avoid Intermediate Variables on Classes**: Chain iter/struct methods directly instead of breaking them into intermediate variables unless necessary for clarity.
- **Prefer Intermediate Variables on Expressions between maps, filters, etc...**: This will avoid repeated function generation, and promote responsibility separation.

### Debugging and Testing

- **Use `.peek()` and `.peekn()`**: For debugging, use these methods to inspect elements in the pipeline without breaking the chain.

---

## Underlying Logic

### Performance and Efficiency

- **Cython Implementation**: Core components, such as the expression builder and chainable operations, are implemented in Cython to minimize instantiation costs and improve runtime performance.
- **cytoolz Integration**: Many operations leverage `cytoolz`, a high-performance functional programming library, for tasks like mapping, filtering, and reducing.
- **Polars Backend**: For columnar data, `Struct` relies on Polars, a fast and efficient DataFrame library, to handle file I/O and data manipulation tasks.

### Callables and Composition

- **Callables Everywhere**: Most operations generate callables, which are either standard library functions or lightweight wrappers. These callables can be composed, reused, and optimized for performance.
- **Partial Functions**: Whenever possible, partial functions are used instead of lambdas to reduce overhead and improve readability.

### Lazy Evaluation

- **Pipeline Execution**: Chains of operations are stored as pipelines and executed only when explicitly unwrapped. This ensures minimal memory usage and allows for efficient processing of large datasets.
- **Interoperability**: Seamlessly integrates with Polars, pandas, and standard Python collections, making it a versatile tool for data manipulation.

---

## Installation

```bash
pip install git+https://github.com/OutSquareCapital/pychain.git
```

---

## Quick Example

```python
import pychain as pc

result = (
    pc.from_range(1, 6)  # range from 1 to 5
    .map(pc.op().mul(2).pow(2))  # [4, 16, 36, 64, 100]
    .filter(pc.op().gt(5))  # [16, 36, 64, 100]
    .cumsum()  # [16, 52, 116, 216]
    .to_list()  # [16, 52, 116, 216]
)
```

---

## License

MIT
