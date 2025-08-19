# pychain

## Installation

```bash
uv add git+https://github.com/OutSquareCapital/pychain.git
```

## Overview

PyChain is a Python library that provides functional-style chaining operations for data structures.

pychain.List and pychain.Dict inerhit respectively from collections.UserList and collections.UserDict.

This means that the stdlib methods (append, etc) are still available.

It leverages modern Python type hints and offers immutable transformations for lists and dictionaries through a fluent interface.

Most of the computations are done with implementations from the cytoolz library.
<https://github.com/pytoolz/cytoolz>

The stubs used for the developpement can be found here:
<https://github.com/py-stubs/cytoolz-stubs>

## Core Classes

### List[T]

`List` is a wrapper around Python lists that provides chainable, immutable operations.

```python
import pychain as pc

# Create a list with chainable operations
result: list[int] = (
    pc.List([1, 2, 3, 4])
    .filter(func=lambda x: x % 2 == 0)
    .map(func=lambda x: x * 10)
    .data
)
# result: [20, 40]
```

### Dict[KT, VT]

`Dict` is a wrapper around Python dictionaries that provides chainable, immutable operations.

```python
import pychain as pc

# Transform dict contents
result: dict[str, int] = (
    pc.Dict({"a": 1, "b": 2, "c": 3})
    .filter(lambda v: v > 1)
    .map_values(lambda v: v * 10)
    .data
)
# result: {"b": 20, "c": 30}
```

## API Reference

### Common Base Methods

These methods are available on both `List` and `Dict`:

- **pipe(func, *args, **kwargs)**: Apply a function to the data and return a new chain
- **compose(*funcs)**: Apply a pipeline of functions to the data, who take the list/dict as argument, and don't change the inner type.
- **print()**: Print the data and return self for chaining

the `data` attribute let you access at any point the underlying list/dict.

### List Methods

#### Filtering and Mapping

- **map(func, *args, **kwargs)**: Map each element through func
- **filter(func, *args, **kwargs)**: Filter elements according to func
- **flat_map(func, *args, **kwargs)**: Map and flatten results
- **reduce(func)**: Reduce the list to a single value

#### Iterating and Inspecting

- **each(func)**: Call func on each item (via tap)
- **peek(note=None)**: Print the first element
- **peekn(n, note=None)**: Print the first n elements
- **tap(func)**: Call func on each item and return unchanged list

#### Access and Aggregation

- **first()**: Return the first element
- **second()**: Return the second element
- **last()**: Return the last element
- **at_index(index)**: Return element at index
- **agg(f, *args, **kwargs)**: Apply aggregator function to the whole list
- **all()**: Return True if all elements are truthy
- **any()**: Return True if any element is truthy
- **length()**: Return the length of the list
- **is_distinct()**: Check if all elements are distinct

#### Slicing and Partitioning

- **head(n)**: Get first n elements
- **tail(n)**: Get last n elements
- **drop_first(n)**: Drop first n elements
- **take_while(predicate)**: Take elements while predicate holds
- **drop_while(predicate)**: Drop elements while predicate holds
- **every(index)**: Return every nth item
- **partition(n, pad=None)**: Partition into tuples of length n
- **partition_all(n)**: Partition into tuples of length at most n
- **rolling(length)**: Return sliding windows of the given length

#### Combining Lists

- **concat(*others)**: Concatenate with other lists
- **cross_join(other)**: Cartesian product with another list
- **interleave(*others)**: Interleave multiple lists element-wise
- **merge_sorted(*others, sort_on=None)**: Merge already-sorted lists
- **diff(*others, key=None)**: Find differences between lists
- **zip_with(*others, strict=False)**: Zip with other lists

#### Transforming and Converting

- **flatten()**: Flatten one level of nesting
- **group_by(on)**: Group elements by key function
- **unique()**: Return unique items preserving order
- **into_frequencies()**: Count occurrences of each value
- **interpose(element)**: Insert element between all items
- **reduce_by(key, binop)**: Reduce grouped elements by binary operator
- **enumerate()**: Return list of (index, value) pairs
- **to_series(name=None)**: Convert to polars Series

### Dict Methods

#### Core Operations

- **filter(predicate)**: Filter values by predicate
- **filter_items(predicate)**: Filter items by (key, value) predicate
- **select(predicate)**: Filter keys by predicate

#### Mapping Operations

- **map_keys(f)**: Transform all keys
- **map_values(f)**: Transform all values
- **map_items(f)**: Transform (key, value) pairs
- **with_key(key, value)**: Add/update a key-value pair
- **with_nested_key(keys, value)**: Set a nested key path
- **update_in(*keys, f)**: Update nested value via function
- **merge(*others)**: Merge with other dictionaries
- **merge_with(f, *others)**: Merge with other dicts using function for duplicates
- **drop(*keys)**: Remove specified keys

#### Accessing Data

- **list_keys()**: Return keys as a List
- **list_values()**: Return values as a List
- **list_items()**: Return items as a List
- **flatten_keys()**: Flatten nested dictionaries into single level

#### Conversion

- **to_df(kind="lazy")**: Convert to polars DataFrame/LazyFrame

## Utility Functions

- **peekn(seq, n, note=None)**: Print first n items of a sequence
- **peek(seq, note=None)**: Print first item of a sequence
- **tap(value, func)**: Apply a function to each item for side effects
- **flatten_recursive(d, parent_key="", sep=".")**: Flatten nested dictionaries

## Type Annotations

The library uses modern Python 3.13+ style generic type annotations:

```python
# Example of type annotations used
type Check[T] = Callable[[T], bool]
type Process[T] = Callable[[T], T]
type Transform[T, T1] = Callable[[T], T1]
type Agg[V, V1] = Callable[[Iterable[V]], V1]
```

The `py.typed` file enables static type checking support.
