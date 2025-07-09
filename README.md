# pychain

**pychain** is a Python library for declarative, chainable, and composable data transformations, inspired by functional programming and powered by [cytoolz](https://github.com/pytoolz/cytoolz). It provides a unified, type-safe API for working with scalars, iterables, and dictionaries, making complex data manipulation pipelines concise, readable, and expressive.

---

## Philosophy & Design Goals

- **pychain** is not meant to replace DataFrames (pandas, Polars, etc.), but to offer a new syntax for pure Python data manipulation, focusing on readability, composability, and type safety.
- Emphasizes **declarative programming** and **functional composition**: each transformation is an explicit, chainable step.
- **Lazy evaluation**: pipelines are only executed when explicitly unwrapped, avoiding unnecessary intermediate allocations.
- **Uniformity**: a consistent interface for scalars, iterables, and mappings, with generic, type-safe methods.
- **Interoperability**: designed to integrate easily with NumPy, pandas, Polars, and functional libraries (toolz/cytoolz).
- **Strongly typed**: All steps will (most of the time) infer the correct type, so you don't have to fight with the type checkers.

---

## Core Principles & Guidelines

1. **Maximize chaining**: prefer chain methods (`.map()`, `.filter()`, `.flat_map()`, etc.) over list comprehensions or intermediate loops.
2. **Leverage lazy evaluation**: build pipelines without materializing data until the final step (e.g., `.convert_to.list()`, `.convert_to.set()`, etc.).
3. **Favor composability**: write pure, reusable functions to pass into chain methods.
4. **Avoid mixing paradigms**: stay within the chain/functional paradigm in a given block, without alternating with loops or comprehensions.
5. **Immutability**: pychain favors transformations without side effects, for safe and predictable pipelines.
6. **Readability first**: each pipeline step should be explicit and easy to understand.

---

## Key Features

- **Chainable transformations** for scalars, iterables, and dictionaries
- **Declarative pipelines**: compose, map, filter, group, aggregate, and more
- **Type safety** with static typing and generics
- **Integration** with NumPy, pandas, Polars, and functional libraries
- **Lazy evaluation**: execution is deferred until conversion or iteration
- **Rich conversion and checking utilities** for all data types

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

### Constructors

- `from_range(start, stop, step=1)` — Create an IterChain from a range
- `from_dict_of_iterables(d)` — Transform a dict of iterables into a DictChain of IterChains
- `from_np(arr)` — NumPy array to IterChain
- `from_pd(df)` — pandas DataFrame to DictChain
- `from_pl(df)` — Polars DataFrame to DictChain
- `from_func(value, f)` — Infinite IterChain by iterating `f`
- `read_csv(path)` / `read_json(path)` / `read_parquet(path)` — File readers

### Chain Types

- **ScalarChain**: for non-iterables (scalars, objects)
- **IterChain**: for iterables (lists, arrays, generators, etc.)
- **DictChain**: for dictionaries (key/value mappings)

## Integration & Interoperability

- **NumPy**: easy conversion via `from_np()` and `.convert_to.array()`
- **pandas**: conversion via `from_pd()`
- **Polars**: conversion via `from_pl()` and `.convert_to.dataframe()`
- **cytoolz/toolz**: Almost all the library is wrapped inside pychain methods.
- **Files**: direct reading of CSV, JSON, Parquet into chainable pipelines. Use polars engine.

---

## Patterns & Best Practices

- **Data cleaning**: normalize and filter lists or dicts before converting to a DataFrame
- **Streaming**: connect `from_func()` or `from_range()` with `.filter()` and `.map()` without materializing the full dataset
- **Avoid side effects**: each step should be deterministic

---

## Limitations & When Not to Use

- **Very large datasets** (use a DataFrame engine)
- **Complex joins, windowing, SQL analytics** (use a DataFrame engine)
- **Scenarios requiring in-place updates**: pychain favors immutability

---

## How to Think in pychain

- **Decompose** each transformation into an explicit step
- **Compose** functions, avoid complex inline lambdas
- **Keep the pipeline readable**: each step = clear intent
- **Anti-patterns**:
  - Mixing chain and list comprehensions
  - Trying to replace a full DataFrame with a DictChain for advanced analytics

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

For detailed examples and atomic documentation, see the notebooks and docs in the `docs/` folder.
