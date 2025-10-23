# pychain ⛓️

**_Functional-style method chaining for Python data structures._**

`pychain` brings a fluent, declarative API inspired by Rust's `Iterator` and DataFrame libraries like Polars to your everyday Python iterables and dictionaries.

Manipulate data through composable chains of operations, enhancing readability and reducing boilerplate.

## Installation 🚀

```bash
uv add git+https://github.com/OutSquareCapital/pychain.git
```

## Overview

### Philosophy ✨

* **Declarative over Imperative:** Replace explicit `for` and `while` loops with sequences of high-level operations (map, filter, group, join...).
* **Fluent Chaining:** Each method transforms the data and returns a new wrapper instance, allowing for seamless chaining.
* **Lazy and Eager:** `Iter` operates lazily for efficiency on large or infinite sequences, while `Seq` represents materialized collections for eager operations.
* **100% Type-safe:** Extensive use of generics and overloads ensures type safety and improves developer experience.
* **Documentation-first:** Each method is thoroughly documented with clear explanations, and usage examples.
* **Functional paradigm:** Design encourages building complex data transformations by composing simple, reusable functions.

### Core Components 🧱

#### `Iter[T]`

Wraps a Python `Iterator` or `Generator`. All operations are **lazy**, consuming the underlying iterator on demand.

[See full documentation →](reference/iter.md)

#### `Dict[K, V]`

Wraps a Python `dict` with chainable methods specific to dictionaries.

[See full documentation →](reference/dict.md)

## Quick Examples

```python
import pychain as pc

# Chain operations on iterables
result = (
    pc.Iter.from_(range(10))
    .filter(lambda x: x % 2 == 0)
    .map(lambda x: x ** 2)
    .collect()
    .unwrap()
)
# [0, 4, 16, 36, 64]
```

## Contributing

See [CONTRIBUTING.md](https://github.com/OutSquareCapital/pychain/blob/master/CONTRIBUTING.md)

## License

MIT License - see [LICENSE.md](https://github.com/OutSquareCapital/pychain/blob/master/LICENSE.md)
