# pychain

**pychain** is a Python library for declarative, chainable, and composable data transformations, inspired by functional programming and powered by [cytoolz](https://github.com/pytoolz/cytoolz). It provides a unified, type-safe API for working with scalars, iterables, and dictionaries, making complex data manipulation pipelines concise, readable, and expressive.

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

  The `chain` singleton is the main entry point for all user operations in pychain. It provides a unified, discoverable, and consistent API for constructing, converting, and manipulating data in a functional, chainable style. All public functionality is accessible via `chain`, `fns`, and `op`.

---

#### Overview

`chain` exposes methods to:

- Wrap scalars, iterables, dicts, DataFrames, arrays, etc. into chainable objects.
- Read data from files (CSV, Parquet, JSON, NDJSON) into chainable forms.
- Convert between data representations (iterable, dict, DataFrame, etc.).
- Generate infinite or finite sequences (from_func, from_range).
- Compose and chain operations fluently, with a focus on readability and composability.

#### Usage Patterns

- Use `chain` to wrap any data structure and immediately access chain methods.
- All transformations are lazy where possible, supporting method chaining.
- Data can be unwrapped at any time using `.unwrap()` or converted to standard types with `.convert_to` or `.convert_keys_to`.
- File readers (read_csv, read_parquet, etc.) return columnar DictChain objects for easy column-wise processing.
- All methods are discoverable via tab-completion on `chain`.

#### API Structure

- Scalar: `chain(value)` wraps a scalar value.
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

#### Best Practices

- Always start with `chain` for new data pipelines.
- Prefer method chaining over intermediate variables for clarity.
- Use `.unwrap()` or `.convert_to` only at the end of a pipeline.
- For custom data sources, implement a conversion to a supported type and wrap with `chain`.

#### Performance

- Internally optimized for large data via lazy evaluation and efficient backends.
- File readers use vectorized IO where possible.

#### Limitations

- Not all methods are available for all chain types; use tab-completion to discover available methods.
- Some conversions may be lossy (e.g., DataFrame to dict for non-string keys).

#### Further Reading

- Methods have docstrings and types hints.
- For functional programming utilities, see `fns`.
- For operator utilities, see `op`.

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

For detailed examples and atomic documentation, see the notebooks and docs in the `docs/` folder.
