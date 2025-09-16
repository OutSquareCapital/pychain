# pychain

## Installation

```bash
uv add git+https://github.com/OutSquareCapital/pychain.git
```

## Testing

```bash
uv run tests/doctests.py
```

## Build docs

```bash
uv run scripts/docgen.py pychain docs_md
```

## Overview

### 1. Core Philosophy & Summary

PyChain is a Python library that provides functional-style chaining operations for data structures.

* **Primary Goal**: To provide a fluent, declarative, and functional method-chaining API for data manipulation in Python.
* **Philosophy**: Eliminate imperative loops (`for`, `while`) in favor of a sequence of high-level operations. Each method transforms the data and returns a new wrapper instance, enabling continuous chaining until a terminal method is called to extract the result.
* **Key Dependencies**: `itertools`, `cytoolz`, `more-itertools`, `numpy`. The library acts as a unifying and simplifying API layer over these powerful tools.
* **Design**: Based on wrapper classes that encapsulate native Python data structures or third-party library objects.
  * **`Iter[T]`**: For any `Iterable`. This is the most generic and powerful wrapper. Most operations are **lazy**.
  * **`Seq[T]` / `SeqMut[T]`**: For `Sequence` (immutable) and `MutableSequence` (mutable) objects.
  * **`Dict[KT, VT]`**: For `dict` objects.
  * **`Array[T]`**: For `numpy.ndarray` objects.
* **Interoperability**: Designed to integrate seamlessly with other data manipulation libraries, like `polars`, using the `pipe_into` and `unwrap` methods.

Most of the computations are done with implementations from the cytoolz library.
<https://github.com/pytoolz/cytoolz>

The stubs used for the developpement can be found here:
<https://github.com/py-stubs/cytoolz-stubs>

---

### 2. Foundational Concepts (`_core.CommonBase`)

All wrapper classes (`Iter`, `Dict`, `Seq`, `Array`) inherit from `CommonBase[T]` and share this base API. `T` represents the underlying data type (e.g., `Iterable[int]`, `dict[str, str]`).

* `__init__(self, data: T)`
  * **Description**: Constructor. Stores the input `data` in the internal `_data` attribute.

* `unwrap() -> T`
  * **Description**: A terminal method. Extracts and returns the raw, underlying data structure, ending the chain.

* `pipe[**P, R](self, func: Callable[Concatenate[Self, P], R], ...) -> R`
  * **Description**: Passes the **wrapper instance** itself as the first argument to `func`. Allows custom functions to be inserted into a chain.

* `pipe_into[**P, R](self, func: Callable[Concatenate[T, P], R], ...) -> R`
  * **Description**: Passes the **underlying data** (`self._data`) as the first argument to `func`. This is the primary method for integrating external libraries (e.g., `polars.LazyFrame`, `list`, `dict`).

* `pipe_unwrap[**P](self, func: Callable[Concatenate[Self, P], Any], ...) -> Any`
  * **Description**: Abstract method, redefined in each subclass. Applies `func` to the underlying data and re-wraps the result in a new, appropriate wrapper instance. This is the core engine of chaining.

* `pipe_chain(self, *funcs: Process[T]) -> Self`
  * **Description**: Applies a sequence of functions to the underlying data. An optimization to avoid multiple `pipe_unwrap` calls when the data type doesn't change. Logic: `h(g(f(data)))`.

* `println(self, pretty: bool = True) -> Self`
  * **Description**: Prints or pretty prints the object's representation and returns `self` to allow for continued chaining. Useful for debugging.

---

### 3. `Iter[T]` API Reference

Wrapper for `collections.abc.Iterable[T]`. Most operations are lazy and return new iterators.

#### 3.1. Constructors (Class Methods)

* `Iter.from_count(start: int = 0, step: int = 1) -> Iter[int]`
  * **Description**: Creates an infinite iterator of evenly spaced integers.
  * **Underlying**: `itertools.count`

* `Iter.from_range(start: int, stop: int, step: int = 1) -> Iter[int]`
  * **Description**: Creates an iterator from a range.
  * **Underlying**: `range`

* `Iter.from_elements[U](*elements: U) -> Iter[U]`
  * **Description**: Creates an `Iter` from individual arguments.

* `Iter.from_func[U](func: Process[U], n: U) -> Iter[U]`
  * **Description**: Creates an infinite iterator by repeatedly applying `func`.
  * **Underlying**: `cytoolz.itertoolz.iterate`

* `Iter.from_iterables(*iterables: Iterable[T]) -> Iter[T]`
  * **Description**: Creates a single `Iter` by chaining multiple iterables.
  * **Underlying**: `itertools.chain.from_iterable`

#### 3.2. Mapping Operations

* `map[R](self, func: Callable[..., R], ...) -> Iter[R]`
  * **Description**: Applies `func` to each element.
  * **Underlying**: `map`

* `map_star[U: Iterable[Any], R](self: Iter[U], func: Callable[..., R]) -> Iter[R]`
  * **Description**: For an `Iter` of iterables, applies `func` by unpacking each element as arguments (`func(*element)`).
  * **Underlying**: `itertools.starmap`

* `map_flat[R](self, func: Callable[..., Iterable[R]], ...) -> Iter[R]`
  * **Description**: Applies a function that returns an iterable to each element, then flattens the results into a single `Iter`. Shortcut for `.map(func).flatten()`.
  * **Underlying**: `itertools.chain.from_iterable(map(...))`

* `map_filter[R](self, func: Transform[T, R]) -> Iter[R]`
  * **Description**: Applies `func` and yields only the results that are not `None`.
  * **Underlying**: `more_itertools.filter_map`

* `map_juxt[R](self, *funcs: Transform[T, R]) -> Iter[tuple[R, ...]]`
  * **Description**: Applies several functions to each item, returning an `Iter` of tuples of results.
  * **Underlying**: `cytoolz.functoolz.juxt`

#### 3.3. Transformation & Combination Operations

* `zip(self, *others: Iterable[Any], strict: bool = False) -> Iter[tuple[Any, ...]]`
  * **Description**: Combines elements of `self` with elements from `others`.
  * **Underlying**: `zip`

* `zip_longest[U](self, *others: Iterable[T], fill_value: U = None) -> Iter[tuple[U | T, ...]]`
  * **Description**: Zips iterables to the length of the longest, filling missing values.
  * **Underlying**: `itertools.zip_longest`

* `product[U](self, other: Iterable[U]) -> Iter[tuple[T, U]]`
  * **Description**: Computes the Cartesian product with another iterable.
  * **Underlying**: `itertools.product`

* `flatten[U](self: Iter[Iterable[U]]) -> Iter[U]`
  * **Description**: Flattens one level of nesting.
  * **Underlying**: `itertools.chain.from_iterable`

* `sort(...) -> Iter[U]`
  * **Description**: Sorts the iterable. **This is a non-lazy operation** that consumes the entire iterator.
  * **Underlying**: `sorted`

* `pluck[K, V](self: Iter[core.Pluckable[K, V]], key: K) -> Iter[V]`
  * **Description**: Extracts a value by key/index from each element. Shortcut for `.map(lambda x: x[key])`.
  * **Underlying**: `cytoolz.itertoolz.pluck`

* `rolling(self, length: int) -> Iter[tuple[T, ...]]`
  * **Description**: Creates a sliding window of a given size.
  * **Underlying**: `cytoolz.itertoolz.sliding_window`

* `batch(self, n: int) -> Iter[tuple[T, ...]]`
  * **Description**: Groups elements into tuples of size `n`. The last tuple may be smaller.
  * **Underlying**: `itertools.batched`

* `chunked(self, n: int, strict: bool = False) -> Iter[list[T]]`
  * **Description**: Groups elements into lists of size `n`.
  * **Underlying**: `more_itertools.chunked`

#### 3.4. Filtering & Processing Operations

* `filter(self, func: ...) -> Self`
  * **Description**: Keeps elements for which `func` returns true.
  * **Underlying**: `filter`

* `filter_false(self, func: ...) -> Self`
  * **Description**: Keeps elements for which `func` returns false.
  * **Underlying**: `itertools.filterfalse`

* `slice(self, start: int | None = None, stop: int | None = None) -> Self`
  * **Description**: Takes a slice of the iterator.
  * **Underlying**: `itertools.islice`

* `head(self, n: int) -> Self`
  * **Description**: Takes the first `n` elements.
  * **Underlying**: `cytoolz.itertoolz.take`

* `tail(self, n: int) -> Self`
  * **Description**: Takes the last `n` elements. **Non-lazy operation**.
  * **Underlying**: `cytoolz.itertoolz.tail`

* `unique(self) -> Self`
  * **Description**: Returns unique elements while preserving order.
  * **Underlying**: `cytoolz.itertoolz.unique`

* `drop_first(self, n: int) -> Self`
  * **Description**: Skips the first `n` elements.
  * **Underlying**: `cytoolz.itertoolz.drop`

* `take_while(self, predicate: Check[T]) -> Self`
  * **Description**: Takes elements as long as `predicate` is true.
  * **Underlying**: `itertools.takewhile`

* `drop_while(self, predicate: Check[T]) -> Self`
  * **Description**: Skips elements as long as `predicate` is true, then returns the rest.
  * **Underlying**: `itertools.dropwhile`

#### 3.5. Terminal Methods (Aggregation)

These methods consume the iterator and return a single value.

* `reduce(self, func: Callable[[T, T], T]) -> T`
  * **Underlying**: `functools.reduce`
* `length() -> int`
  * **Underlying**: `cytoolz.itertoolz.count`
* `first() -> T`, `second() -> T`, `last() -> T`
  * **Underlying**: `cytoolz.itertoolz`
* `sum()`, `min()`, `max()`, `mean()`, `median()`, `mode()`, `stdev()`, `variance()`
  * **Underlying**: Built-in functions and the `statistics` module.
* `all() -> bool`, `any() -> bool`
  * **Underlying**: `all`, `any`
* `is_distinct() -> bool`
  * **Underlying**: `cytoolz.itertoolz.isdistinct`

#### 3.6. Terminal Methods (Conversion)

These methods consume the iterator and return a new wrapper or collection.

* `to_list() -> SeqMut[T]`
  * **Description**: Collects elements into a `SeqMut` (wrapping a `list`).

* `to_deque(maxlen: int | None = None) -> SeqMut[T]`
  * **Description**: Collects elements into a `SeqMut` (wrapping a `collections.deque`).

* `group_by[K](self, on: Transform[T, K]) -> Dict[K, list[T]]`
  * **Description**: Groups elements by a key function. Returns a `Dict` wrapper.
  * **Underlying**: `cytoolz.itertoolz.groupby`

* `frequencies() -> Dict[T, int]`
  * **Description**: Counts occurrences of each element. Returns a `Dict` wrapper.
  * **Underlying**: `cytoolz.itertoolz.frequencies`

---

### 4. `Dict[KT, VT]` API Reference

Wrapper for `dict[KT, VT]`.

#### 4.1. Constructors (Class Methods)

* `Dict.from_iterables[KN, VN](keys: Iterable[KN], values: Iterable[VN]) -> Dict[KN, VN]`
  * **Description**: Creates a `Dict` from two separate iterables of keys and values.
  * **Underlying**: `zip` and `dict` constructor.

#### 4.2. Conversion to `Iter`

* `iter_keys() -> Iter[KT]`
* `iter_values() -> Iter[VT]`
* `iter_items() -> Iter[tuple[KT, VT]]`

#### 4.3. Immutable Operations (return a new `Dict`)

* `filter_keys(self, predicate: Check[KT]) -> Self`
  * **Description**: Returns a new `Dict` containing only the keys that satisfy the predicate.
  * **Underlying**: `cytoolz.dicttoolz.keyfilter`
* `filter_values(self, predicate: Check[VT]) -> Self`
  * **Description**: Returns a new `Dict` containing only the items whose values satisfy the predicate.
  * **Underlying**: `cytoolz.dicttoolz.valfilter`
* `filter_items(self, predicate: Callable[[KT, VT], bool]) -> Self`
  * **Description**: Returns a new `Dict` by filtering items based on a predicate that accepts both key and value.
  * **Underlying**: `cytoolz.dicttoolz.itemfilter`
* `map_keys[T](self, func: Transform[KT, T]) -> Dict[T, VT]`
  * **Description**: Applies a function to each key and returns a new `Dict`.
  * **Underlying**: `cytoolz.dicttoolz.keymap`
* `map_values[T](self, func: Transform[VT, T]) -> Dict[KT, T]`
  * **Description**: Applies a function to each value and returns a new `Dict`.
  * **Underlying**: `cytoolz.dicttoolz.valmap`
* `map_items[KR, VR](self, func: Callable[[KT, VT], tuple[KR, VR]]) -> Dict[KR, VR]`
  * **Description**: Applies a function to each `(key, value)` pair, returning a new `Dict` of transformed pairs.
  * **Underlying**: `cytoolz.dicttoolz.itemmap`
* `merge(self, *others: dict[KT, VT]) -> Self`
  * **Description**: Merges one or more dictionaries into the current one, returning a new `Dict`. Later dictionaries override earlier ones.
  * **Underlying**: `cytoolz.dicttoolz.merge`
* `merge_with(self, f: Callable[[Iterable[VT]], VT], *others: dict[KT, VT]) -> Self`
  * **Description**: Merges dictionaries, using a function `f` to combine values for duplicate keys.
  * **Underlying**: `cytoolz.dicttoolz.merge_with`
* `drop(self, *keys: KT) -> Self`
  * **Description**: Returns a new `Dict` with the specified keys removed.
  * **Underlying**: `cytoolz.dicttoolz.dissoc`
* `with_key(self, key: KT, value: VT) -> Self`
  * **Description**: Returns a new `Dict` with a key set to a new value.
  * **Underlying**: `cytoolz.dicttoolz.assoc`
* `with_nested_key(self, keys: Iterable[KT] | KT, value: VT) -> Self`
  * **Description**: Returns a new `Dict` with a nested key path set to a new value.
  * **Underlying**: `cytoolz.dicttoolz.assoc_in`
* `update_in(self, *keys: KT, f: core.Process[VT]) -> Self`
  * **Description**: Returns a new `Dict` with a nested value updated via a function `f`.
  * **Underlying**: `cytoolz.dicttoolz.update_in`
* `copy() -> Self`
  * **Description**: Returns a shallow copy of the `Dict`.
  * **Underlying**: `dict.copy`

#### 4.4. Mutable Operations (modify in-place and return `Self`)

* `update(self, *others: dict[KT, VT]) -> Self`
  * **Description**: Updates the dictionary with items from one or more other dictionaries. Modifies the `Dict` in-place.
  * **Underlying**: `dict.update`
* `set_value(self, key: KT, value: VT) -> Self`
  * **Description**: Sets a key to a given value. Modifies the `Dict` in-place.
  * **Underlying**: `dict.__setitem__`

#### 4.5. Accessor Methods

* `get_value(self, key: KT, default: VT | None = None) -> VT | None`
  * **Description**: Retrieves the value for a key, returning a default value if the key is not found.
  * **Underlying**: `dict.get`

---

### 5. `Seq[T]` & `SeqMut[T]` API Reference

Wrappers for `Sequence` and `MutableSequence`.

* **`Seq[T]`**:
  * **Description**: Wrapper for immutable sequences (e.g., `tuple`).
  * `to_iter() -> Iter[T]`: Converts to an `Iter`.
  * `count(value: T) -> int`
  * `index(...) -> int`

* **`SeqMut[T]`**:
  * **Description**: Inherits from `Seq` and adds mutation methods for mutable sequences (e.g., `list`).
  * **Mutable Operations (return `Self`)**:
    * `clear()`
    * `insert(index: int, value: T)`
    * `append(value: T)`
    * `extend(*others: Iterable[T])`
    * `remove(value: T)`
    * `reverse()`

---

### 6. `Array[T: NumpyType]` API Reference

Wrapper for `numpy.ndarray`.

* `pipe_unwrap[**P, U: NumpyType](self, func: Callable[..., NDArray[U]], ...) -> Array[U]`
  * **Description**: Applies a function (typically from `numpy`) to the underlying `ndarray` and wraps the resulting `ndarray` in a new `Array`.
* `to_iter() -> Iter[T]`
  * **Description**: Converts the array to an `Iter` to allow for `Iter` operations.

---

### 7. Usage Patterns & Examples

```python
import pychain as pc

data = range(10)
result = (
    pc.Iter(data)
    .filter(lambda x: x % 2 == 0) # [0, 2, 4, 6, 8]
    .map(lambda x: x * x)         # [0, 4, 16, 36, 64]
    .head(3)                      # [0, 4, 16]
    .to_list()                    # -> SeqMut([0, 4, 16])
    .unwrap()                     # -> [0, 4, 16]
)
```
