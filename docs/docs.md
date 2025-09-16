
# index

# PyChain Documentation

# Contents

* [Iter Module](iter.md)
  * [`Iter`](iter.md#pychain.Iter)
* [Dict Module](dict.md)
  * [`Dict`](dict.md#pychain.Dict)

<a id="module-pychain"></a>

# Pychain

PyChain is a Python library that provides functional-style chaining operations for data structures.
Most of the computations are done with implementations from the cytoolz library.
<[https://github.com/pytoolz/cytoolz](https://github.com/pytoolz/cytoolz)>
The stubs used for the developpement can be found here:
<[https://github.com/py-stubs/cytoolz-stubs](https://github.com/py-stubs/cytoolz-stubs)>

## Overview

\* **Primary Goal**: To provide a fluent, declarative, and functional method-chaining API for data manipulation in Python.
\* **Philosophy**: Eliminate imperative loops (for, while) in favor of a sequence of high-level operations. Each method transforms the data and returns a new wrapper instance, enabling continuous chaining until a terminal method is called to extract the result.
\* **Key Dependencies**: itertools, cytoolz, more-itertools, numpy. The library acts as a unifying and simplifying API layer over these powerful tools.
\* **Design**: Based on wrapper classes that encapsulate native Python data structures or third-party library objects.

> * **\`Iter[T]\`**: For any Iterable. This is the most generic and powerful wrapper. Most operations are **lazy**.
> * **\`Seq[T]\` / \`SeqMut[T]\`**: For Sequence (immutable) and MutableSequence (mutable) objects.
> * **\`Dict[KT, VT]\`**: For dict objects.
> * **\`Array[T]\`**: For numpy.ndarray objects.
>
* **Interoperability**: Designed to integrate seamlessly with other data manipulation libraries, like polars, using the pipe_into and unwrap methods.

### *class* pychain.SeqMut(data)

* **Parameters:**
  **data** (*T*)

#### append(value)

Append object to the end of the sequence and return self for convenience.
**Warning**: Mutates the original sequence.

```python
>>> SeqMut([1, 2]).append(3)
[1, 2, 3]
```

* **Parameters:**
  **value** (*T*)
* **Return type:**
  *Self*

#### clear()

Clear the sequence and return self for convenience.
**Warning**: Mutates the original sequence.

```python
>>> SeqMut([1, 2]).clear()
[]
```

* **Return type:**
  *Self*

#### extend(\*others)

Extend the sequence with elements from another iterable and return self for convenience.
**Warning**: Mutates the original sequence.

```python
>>> SeqMut([1, 2]).extend([3, 4])
[1, 2, 3, 4]
```

* **Parameters:**
  **others** (*Iterable*)
* **Return type:**
  *Self*

#### insert(index, value)

Insert an object into the sequence at the specified index and return self for convenience.
**Warning**: Mutates the original sequence.

```python
>>> SeqMut([1, 2]).insert(1, 3)
[1, 3, 2]
```

* **Parameters:**
  * **index** (*int*)
  * **value** (*T*)
* **Return type:**
  *Self*

#### pipe(func, \*args, \*\*kwargs)

Pipe the instance in the function and return the result.

* **Parameters:**
  * **func** (*Callable* *[* *[**Concatenate* *[**MutableSequence* *,* *P* *]* *]* *,* *MutableSequence* *]*)
  * **args** (*P*)
  * **kwargs** (*P*)
* **Return type:**
  [*SeqMut*](#pychain.SeqMut)

#### remove(value)

Remove an object from the sequence and return self for convenience.
**Warning**: Mutates the original sequence.

```python
>>> SeqMut([1, 2]).remove(2)
[1]
```

* **Parameters:**
  **value** (*T*)
* **Return type:**
  *Self*

#### reverse()

Reverse the order of the sequence and return self for convenience.
**Warning**: Mutates the original sequence.

```python
>>> SeqMut([1, 2]).reverse()
[2, 1]
```

* **Return type:**
  *Self*

### *class* pychain.Dict(data)

* **Parameters:**
  **data** (*T*)

#### copy()

Return a shallow copy of the dict.

* **Return type:**
  *Self*

#### drop(\*keys)

Return a new Dict with given keys removed.

```python
>>> Dict({1: 2, 3: 4}).drop(1)
{3: 4}
```

* **Parameters:**
  **keys** (*KT*)
* **Return type:**
  *Self*

#### filter_items(predicate)

Filter items by predicate applied to (key, value) tuples.

```python
>>> Dict({1: 2, 3: 4}).filter_items(lambda k, v: v > 2)
{3: 4}
```

* **Parameters:**
  **predicate** (*Callable* *[* *[**KT* *,* *VT* *]* *,* *bool* *]*)
* **Return type:**
  *Self*

#### filter_keys(predicate)

Return a new Dict containing keys that satisfy predicate.

```python
>>> Dict({1: 2, 3: 4}).filter_keys(lambda k: k % 2 == 0)
{}
```

* **Parameters:**
  **predicate** (*Check*)
* **Return type:**
  *Self*

#### filter_values(predicate)

Return a new Dict containing items whose values satisfy predicate.

```python
>>> Dict({1: 2, 3: 4}).filter_values(lambda v: v > 2)
{3: 4}
```

* **Parameters:**
  **predicate** (*Check*)
* **Return type:**
  *Self*

#### *classmethod* from_zipped(keys, values)

Create a Dict from two iterables of keys and values.

```python
>>> Dict.from_zipped([1, 2], ["a", "b"])
{1: 'a', 2: 'b'}
```

* **Parameters:**
  * **keys** (*Iterable*)
  * **values** (*Iterable*)
* **Return type:**
  [*Dict*](#pychain.Dict)

#### get_value(key, default=None)

Get the value for a key, returning default if not found.

* **Parameters:**
  * **key** (*KT*)
  * **default** (*VT* *|* *None*)
* **Return type:**
  VT | None

#### iter_items()

Return a Iter of the dict’s items.

```python
>>> Dict({1: 2}).iter_items().to_list()
[(1, 2)]
```

* **Return type:**
  [Iter][#pychain.Iter](tuple[KT, VT)]

#### iter_keys()

Return a Iter of the dict’s keys.

```python
>>> Dict({1: 2}).iter_keys().to_list()
[1]
```

* **Return type:**
  [Iter][#pychain.Iter](KT)

#### iter_values()

Return a Iter of the dict’s values.

```python
>>> Dict({1: 2}).iter_values().to_list()
[2]
```

* **Return type:**
  [Iter][#pychain.Iter](VT)

#### map_items(func)

Transform (key, value) pairs using a function that takes key and value as separate arguments.

```python
>>> Dict({1: 2}).map_items(lambda k, v: (k + 1, v * 10))
{2: 20}
```

* **Parameters:**
  **func** (*Callable* *[* *[**KT* *,* *VT* *]* *,* *tuple* *[**KR* *,* *VR* *]* *]*)
* **Return type:**
  [*Dict*](#pychain.Dict)

#### map_keys(func)

Return a Dict with keys transformed by ffunc.

```python
>>> Dict({1: "a"}).map_keys(str)
{'1': 'a'}
```

* **Parameters:**
  **func** (*Transform*)
* **Return type:**
  [Dict][#pychain.Dict](T, VT)

#### map_values(func)

Return a Dict with values transformed by func.

```python
>>> Dict({1: 1}).map_values(lambda v: v + 1)
{1: 2}
```

* **Parameters:**
  **func** (*Transform*)
* **Return type:**
  [Dict][#pychain.Dict](KT, T)

#### merge(\*others)

Merge other dicts into this one and return a new Dict.

```python
>>> Dict({1: 2}).merge({3: 4})
{1: 2, 3: 4}
```

* **Parameters:**
  **others** (*dict* *[**KT* *,* *VT* *]*)
* **Return type:**
  *Self*

#### merge_with(f, \*others)

Merge dicts using f to combine values for duplicate keys.

```python
>>> Dict({1: 1}).merge_with(sum, {1: 2})
{1: 3}
```

* **Parameters:**
  * **f** (*Callable* *[* *[**Iterable* *]* *,* *VT* *]*)
  * **others** (*dict* *[**KT* *,* *VT* *]*)
* **Return type:**
  *Self*

#### pipe_unwrap(func, \*args, \*\*kwargs)

Pipe underlying data in the function and return a new wrapped instance.
This function must be implemented by subclasses.

* **Parameters:**
  * **func** (*Callable* *[* *[**Concatenate* *[**dict* *[**KT* *,* *VT* *]* *,* *P* *]* *]* *,* *dict* *[**KU* *,* *VU* *]* *]*)
  * **args** (*P*)
  * **kwargs** (*P*)
* **Return type:**
  [*Dict*](#pychain.Dict)

#### set_value(key, value)

Set the value for a key and return self for convenience.
**Warning**: This modifies the dict in place.

```python
>>> Dict({}).set_value("x", 1)
{'x': 1}
```

* **Parameters:**
  * **key** (*KT*)
  * **value** (*VT*)
* **Return type:**
  *Self*

#### update(\*others)

Update the dict with other(s) dict(s) and return self for convenience.
**Warning**: This modifies the dict in place.

* **Parameters:**
  **others** (*dict* *[**KT* *,* *VT* *]*)
* **Return type:**
  *Self*

#### update_in(\*keys, f)

Update a nested value via function f and return a new Dict.

```python
>>> Dict({"a": {"b": 1}}).update_in("a", "b", f=lambda x: x + 1)
{'a': {'b': 2}}
```

* **Parameters:**
  * **keys** (*KT*)
  * **f** (*Process*)
* **Return type:**
  *Self*

#### with_key(key, value)

Return a new Dict with key set to value.

```python
>>> Dict({}).with_key("x", 1)
{'x': 1}
```

* **Parameters:**
  * **key** (*KT*)
  * **value** (*VT*)
* **Return type:**
  *Self*

#### with_nested_key(keys, value)

Set a nested key path and return a new Dict.

```python
>>> Dict({}).with_nested_key(["a", "b"], 1)
{'a': {'b': 1}}
```

* **Parameters:**
  * **keys** (*Iterable* *|* *KT*)
  * **value** (*VT*)
* **Return type:**
  *Self*

### *class* pychain.Iter(data)

A wrapper around Python’s built-in iterable types, providing a rich set of functional programming tools.
It supports lazy evaluation, allowing for efficient processing of large datasets.
It is not a collection itself, but a wrapper that provides additional methods for working with iterables.
It can be constructed from any iterable, including lists, tuples, sets, and generators.

```python
>>> from pychain import Iter
>>> Iter([1, 2, 3]).to_list()
[1, 2, 3]
```

* **Parameters:**
  **data** (*T*)

#### adjacent(predicate, distance=1)

Return an iterable over (bool, item) tuples.
The output is a sequence of tuples where the item is drawn from iterable.

The bool indicates whether that item satisfies the predicate or is adjacent to an item that does.

For example, to find whether items are adjacent to a 3:

```python
>>> Iter(range(6)).adjacent(lambda x: x == 3).to_list()
[(False, 0), (False, 1), (True, 2), (True, 3), (True, 4), (False, 5)]
```

Set distance to change what counts as adjacent. For example, to find whether items are two places away from a 3:

```python
>>> Iter(range(6)).adjacent(lambda x: x == 3, distance=2).to_list()
[(False, 0), (True, 1), (True, 2), (True, 3), (True, 4), (True, 5)]
```

This is useful for contextualizing the results of a search function.
For example, a code comparison tool might want to identify lines that have changed, but also surrounding lines to give the viewer of the diff context.
The predicate function will only be called once for each item in the iterable.

See also groupby_transform, which can be used with this function to group ranges of items with the same bool value.

* **Parameters:**
  * **predicate** (*Check*)
  * **distance** (*int*)
* **Return type:**
  [Iter][#pychain.Iter](tuple[bool, T)]

#### batch(n)

Batch elements into tuples of length n and return a new Iter.

```python
>>> Iter("ABCDEFG").batch(3).to_list()
[('A', 'B', 'C'), ('D', 'E', 'F'), ('G',)]
```

* **Parameters:**
  **n** (*int*)
* **Return type:**
  [Iter][#pychain.Iter](tuple[T, …)]

#### chunked(n, strict=False)

Break iterable into lists of length n.

By default, the last yielded list will have fewer than *n* elements if the length of *iterable* is not divisible by *n*.

To use a fill-in value instead, see the `grouper()` recipe.

If the length of *iterable* is not divisible by *n* and *strict* is
`True`, then `ValueError` will be raised before the last
list is yielded.

```python
>>> Iter([1, 2, 3, 4, 5, 6]).chunked(3).to_list()
[[1, 2, 3], [4, 5, 6]]
>>> Iter([1, 2, 3, 4, 5, 6, 7, 8]).chunked(3).to_list()
[[1, 2, 3], [4, 5, 6], [7, 8]]
```

* **Parameters:**
  * **n** (*int*)
  * **strict** (*bool*)
* **Return type:**
  [Iter][#pychain.Iter](list[T)]

#### chunked_even(n)

Break iterable into lists of approximately length n.
Items are distributed such the lengths of the lists differ by at most 1 item.

```python
>>> iterable = [1, 2, 3, 4, 5, 6, 7]
>>> Iter(iterable).chunked_even(3).to_list()  # List lengths: 3, 2, 2
[[1, 2, 3], [4, 5], [6, 7]]
>>> Iter(iterable).chunked(3).to_list()  # List lengths: 3, 3, 1
[[1, 2, 3], [4, 5, 6], [7]]
```

* **Parameters:**
  **n** (*int*)
* **Return type:**
  [Iter][#pychain.Iter](list[T)]

#### combinations(r)

¨
Return all combinations of length r.

```python
>>> Iter([1, 2, 3]).combinations(2).to_list()
[(1, 2), (1, 3), (2, 3)]
```

* **Parameters:**
  **r** (*int*)
* **Return type:**
  [Iter][#pychain.Iter](tuple[T, …)]

#### combinations_with_replacement(r)

Return all combinations with replacement of length r.

```python
>>> Iter([1, 2, 3]).combinations_with_replacement(2).to_list()
[(1, 1), (1, 2), (1, 3), (2, 2), (2, 3), (3, 3)]
```

* **Parameters:**
  **r** (*int*)
* **Return type:**
  [Iter][#pychain.Iter](tuple[T, …)]

#### diff(\*others, key=None)

Yield differences between sequences.

```python
>>> Iter([1, 2, 3]).diff([1, 2, 10]).to_list()
[(3, 10)]
```

* **Parameters:**
  * **others** (*Iterable*)
  * **key** (*Process* *|* *None*)
* **Return type:**
  [Iter][#pychain.Iter](tuple[T, …)]

#### enumerate()

Return a Iter of (index, value) pairs.

```python
>>> Iter(["a", "b"]).enumerate().to_list()
[(0, 'a'), (1, 'b')]
```

* **Return type:**
  [Iter][#pychain.Iter](tuple[int, T)]

#### flatten()

Flatten one level of nesting and return a new Iterable wrapper.

```python
>>> Iter([[1, 2], [3]]).flatten().to_list()
[1, 2, 3]
```

* **Parameters:**
  **self** ([*Iter*](#pychain.Iter) *[**Iterable* *]*)
* **Return type:**
  [*Iter*](#pychain.Iter)

#### *classmethod* from_count(start=0, step=1)

Create an infinite iterator of evenly spaced values.
This is a class method that acts as a constructor.
Warning: This creates an infinite iterator. Be sure to use .head() or
.slice() to limit the number of items taken.

```python
>>> Iter.from_count(10, 2).head(3).to_list()
[10, 12, 14]
```

* **Parameters:**
  * **start** (*int*)
  * **step** (*int*)
* **Return type:**
  [*Iter*][#pychain.Iter](int)

#### *classmethod* from_elements(\*elements)

Create an Iter from a sequence of elements.
This is a class method that acts as a constructor from unpacked arguments.

```python
>>> Iter.from_elements(1, 2, 3).to_list()
[1, 2, 3]
```

* **Parameters:**
  **elements** (*U*)
* **Return type:**
  [*Iter*](#pychain.Iter)

#### *classmethod* from_func(func, n)

Create an infinite iterator by repeatedly applying a function.

```python
>>> Iter.from_func(lambda x: x + 1, 0).head(3).to_list()
[0, 1, 2]
```

* **Parameters:**
  * **func** (*Process*)
  * **n** (*U*)
* **Return type:**
  [*Iter*](#pychain.Iter)

#### *classmethod* from_iterables(\*iterables)

Create an Iter by chaining multiple iterables.
This is a class method that acts as a constructor from multiple iterables.

```python
>>> Iter.from_iterables([1, 2], (3, 4)).to_list()
[1, 2, 3, 4]
```

* **Parameters:**
  **iterables** (*Iterable*)
* **Return type:**
  [*Iter*](#pychain.Iter)

#### *classmethod* from_range(start, stop, step=1)

Create an iterator from a range.

```python
>>> Iter.from_range(1, 5).to_list()
[1, 2, 3, 4]
```

* **Parameters:**
  * **start** (*int*)
  * **stop** (*int*)
  * **step** (*int*)
* **Return type:**
  [*Iter*][#pychain.Iter](int)

#### join(other, left_on, right_on, left_default=None, right_default=None)

Perform a relational join with another iterable.

```python
>>> colors = Iter(["blue", "red"])
>>> sizes = ["S", "M"]
>>> colors.join(sizes, left_on=lambda c: c, right_on=lambda s: s).to_list()
[(None, 'S'), (None, 'M'), ('blue', None), ('red', None)]
```

* **Parameters:**
  * **other** (*Iterable*)
  * **left_on** (*Transform*)
  * **right_on** (*Transform*)
  * **left_default** (*T* *|* *None*)
  * **right_default** (*R* *|* *None*)
* **Return type:**
  [Iter][#pychain.Iter](tuple[T, R)]

#### map(func, \*args, \*\*kwargs)

Map each element through func and return a Iter of results.

```python
>>> Iter([1, 2]).map(lambda x: x + 1).to_list()
[2, 3]
```

* **Parameters:**
  * **func** (*Callable* *[* *[**Concatenate* *[**T* *,* *P* *]* *]* *,* *R* *]*)
  * **args** (*P*)
  * **kwargs** (*P*)
* **Return type:**
  [*Iter*](#pychain.Iter)

#### map_except(func, \*exceptions)

Transform each item from iterable with function and yield the result, unless function raises one of the specified exceptions.
function is called to transform each item in iterable.

It should accept one argument.

If an exception other than one given by exceptions is raised by function, it is raised like normal.

```python
>>> iterable = ["1", "2", "three", "4", None]
>>> Iter(iterable).map_except(int, ValueError, TypeError).to_list()
[1, 2, 4]
```

* **Parameters:**
  * **func** (*Transform*)
  * **exceptions** (*type* *[**BaseException* *]*)
* **Return type:**
  [*Iter*](#pychain.Iter)

#### map_filter(func)

Apply func to every element of iterable, yielding only those which are not None.

```python
>>> elems = ["1", "a", "2", "b", "3"]
>>> Iter(elems).map_filter(
...     lambda s: int(s) if s.isnumeric() else None
... ).to_list()
[1, 2, 3]
```

* **Parameters:**
  **func** (*Transform*)
* **Return type:**
  [*Iter*](#pychain.Iter)

#### map_flat(func, \*args, \*\*kwargs)

Maps a function over a sequence and flattens the result by one level.
It applies a function to each element, where the function must return
an iterable. The resulting iterables are then chained together into a
single, “flat” sequence.
It’s an efficient shortcut for .map(func).flatten().

```python
>>> # For each author, get a list of their books.
>>> authors = Iter(["author_A", "author_B"])
>>> def get_books(author_id):
...     # This could be an API call that returns a list of books
...     return [f"{author_id}_book1", f"{author_id}_book2"]
>>>
>>> authors.map_flat(get_books).to_list()
['author_A_book1', 'author_A_book2', 'author_B_book1', 'author_B_book2']
```

* **Parameters:**
  * **func** (*Callable* *[* *[**Concatenate* *[**T* *,* *P* *]* *]* *,* *Iterable* *]*)
  * **args** (*P*)
  * **kwargs** (*P*)
* **Return type:**
  [*Iter*](#pychain.Iter)

#### map_if(predicate, func, func_else=None)

Evaluate each item from iterable using pred. If the result is equivalent to True, transform the item with func and yield it.

Otherwise, transform the item with func_else and yield it.
predicate, func, and func_else should each be functions that accept one argument.

By default, func_else is the identity function.
: ```python
  >>> from math import sqrt
  >>> iterable = list(range(-5, 5))
  >>> iterable
  [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4]
  >>> Iter(iterable).map_if(lambda x: x > 3, lambda x: "toobig").to_list()
  [-5, -4, -3, -2, -1, 0, 1, 2, 3, 'toobig']
  >>> Iter(iterable).map_if(
  ...     lambda x: x >= 0,
  ...     lambda x: f"{sqrt(x):.2f}",
  ...     lambda x: None,
  ... ).to_list()
  [None, None, None, None, None, '0.00', '1.00', '1.41', '1.73', '2.00']

  ```

* **Parameters:**
  * **predicate** (*Check*)
  * **func** (*Transform*)
  * **func_else** (*Transform* *|* *None*)
* **Return type:**
  [*Iter*](#pychain.Iter)

#### map_join(func, \*others)

Equivalent to flat_map, but allow to join other iterables. However, it don’t take additional arguments for the function.
: ```python
  >>> left = ["a", "b"]
  >>> right = ["c", "d", "e"]
  >>> Iter(left).map_join(lambda s: [c.upper() for c in s], right).to_list()
  ['A', 'B', 'C', 'D', 'E']
  ```

* **Parameters:**
  * **func** (*Transform* *[**Iterable* *,* *Iterable* *]*)
  * **others** (*Iterable*)
* **Return type:**
  [*Iter*](#pychain.Iter)

#### map_juxt(\*funcs)

Apply several functions to each item.
Returns a new Iter where each item is a tuple of the results of
applying each function to the original item.

```python
>>> def is_even(n):
...     return n % 2 == 0
>>> def is_positive(n):
...     return n > 0
>>> Iter([1, -2, 3]).map_juxt(is_even, is_positive).to_list()
[(False, True), (True, False), (False, True)]
```

* **Parameters:**
  **funcs** (*Transform*)
* **Return type:**
  [*Iter*][#pychain.Iter](tuple[R, …)]

#### map_star(func)

Applies a function to each element, where each element is an iterable.
Unlike .map(), which passes each element as a single argument, .starmap() unpacks each element into positional arguments for the function.

In short, for each element in the sequence, it computes func(\*element).

**Tip**: It is the perfect tool to process pairs generated by .product() or .zip_with().

```python
>>> colors = Iter(["blue", "red"])
>>> sizes = ["S", "M"]
>>>
>>> def make_sku(color, size):
...     return f"{color}-{size}"
>>>
>>> colors.product(sizes).map_star(make_sku).to_list()
['blue-S', 'blue-M', 'red-S', 'red-M']
```

* **Parameters:**
  * **self** ([*Iter*](#pychain.Iter))
  * **func** (*Callable* *[* *[* *...* *]* *,* *R* *]*)
* **Return type:**
  [*Iter*](#pychain.Iter)

#### pairwise()

Return an iterator over pairs of consecutive elements.

```python
>>> Iter([1, 2, 3]).pairwise().to_list()
[(1, 2), (2, 3)]
```

* **Return type:**
  [Iter][#pychain.Iter](tuple[T, T)]

#### partition(n, pad=None)

Partition into tuples of length n, optionally padded.

```python
>>> Iter([1, 2, 3, 4]).partition(2).to_list()
[(1, 2), (3, 4)]
```

* **Parameters:**
  * **n** (*int*)
  * **pad** (*T* *|* *None*)
* **Return type:**
  [Iter][#pychain.Iter](tuple[T, …)]

#### partition_all(n)

Partition into tuples of length at most n.

```python
>>> Iter([1, 2, 3]).partition_all(2).to_list()
[(1, 2), (3,)]
```

* **Parameters:**
  **n** (*int*)
* **Return type:**
  [Iter][#pychain.Iter](tuple[T, …)]

#### permutations(r=None)

¨
Return all permutations of length r.

```python
>>> Iter([1, 2, 3]).permutations(2).to_list()
[(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)]
```

* **Parameters:**
  **r** (*int* *|* *None*)
* **Return type:**
  [Iter][#pychain.Iter](tuple[T, …)]

#### pipe_unwrap(func, \*args, \*\*kwargs)

Pipe the entire iterable into a function that takes an iterable as its first argument.
Returns a new Iter wrapping the result.

```python
>>> from pychain import Iter
>>> def func(iterable, n):
...     return (x * n for x in iterable)
>>>
>>> Iter([1, 2, 3]).pipe_unwrap(func, 10).to_list()
[10, 20, 30]
```

* **Parameters:**
  * **func** (*Callable* *[* *[**Concatenate* *[**Iterable* *,* *P* *]* *]* *,* *Iterable* *]*)
  * **args** (*P*)
  * **kwargs** (*P*)
* **Return type:**
  [*Iter*](#pychain.Iter)

#### pluck(key)

Extract a value from each element in the sequence using a key or index.
This is a shortcut for .map(lambda x: x[key]).

```python
>>> data = Iter([{"id": 1, "val": "a"}, {"id": 2, "val": "b"}])
>>> data.pluck("val").to_list()
['a', 'b']
>>> Iter([[10, 20], [30, 40]]).pluck(0).to_list()
[10, 30]
```

* **Parameters:**
  * **self** ([*Iter*](#pychain.Iter) *[**Pluckable* *]*)
  * **key** (*K*)
* **Return type:**
  [*Iter*](#pychain.Iter)

#### product(other)

Computes the Cartesian product with another iterable.
This is the declarative equivalent of nested for-loops.

It pairs every element from the source iterable with every element from the
other iterable.

**Tip**: This method is often chained with .starmap() to apply a
function to each generated pair.

```python
>>> colors = Iter(["blue", "red"])
>>> sizes = ["S", "M"]
>>> colors.product(sizes).to_list()
[('blue', 'S'), ('blue', 'M'), ('red', 'S'), ('red', 'M')]
```

* **Parameters:**
  **other** (*Iterable*)
* **Return type:**
  [Iter][#pychain.Iter](tuple[T, U)]

#### reduce_by(key, binop)

Perform a simultaneous groupby and reduction
on the elements of the sequence.

```python
>>> Iter([1, 2, 3, 4]).reduce_by(
...     key=lambda x: x % 2, binop=lambda a, b: a + b
... ).to_list()
[1, 0]
```

* **Parameters:**
  * **key** (*Transform*)
  * **binop** (*Callable* *[* *[**T* *,* *T* *]* *,* *T* *]*)
* **Return type:**
  [*Iter*](#pychain.Iter)

#### repeat(n)

Repeat the entire iterable n times (as elements) and return Iter.

```python
>>> Iter([1, 2]).repeat(2).to_list()
[[1, 2], [1, 2]]
```

* **Parameters:**
  **n** (*int*)
* **Return type:**
  [Iter][#pychain.Iter](Iterable[T)]

#### repeat_last(default=None)

After the iterable is exhausted, keep yielding its last element.

```python
>>> Iter(range(3)).repeat_last().head(5).to_list()
[0, 1, 2, 2, 2]
```

If the iterable is empty, yield default forever:

```python
>>> Iter(range(0)).repeat_last(42).head(5).to_list()
[42, 42, 42, 42, 42]
```

* **Parameters:**
  **default** (*U*)
* **Return type:**
  [Iter][#pychain.Iter](T | U)

#### rolling(length)

Return sliding windows of the given length.

```python
>>> Iter([1, 2, 3]).rolling(2).to_list()
[(1, 2), (2, 3)]
```

* **Parameters:**
  **length** (*int*)
* **Return type:**
  [Iter][#pychain.Iter](tuple[T, …)]

#### sort(key=None, reverse=False)

Sort the elements of the sequence.
Note: This method must consume the entire iterable to perform the sort.
The result is a new iterable over the sorted sequence.

```python
>>> Iter([3, 1, 2]).sort().to_list()
[1, 2, 3]
>>> data = Iter([{"age": 30}, {"age": 20}])
>>> data.sort(key=lambda x: x["age"]).to_list()
[{'age': 20}, {'age': 30}]
```

* **Parameters:**
  * **self** ([*Iter*](#pychain.Iter))
  * **key** (*Transform* *[**U* *,* *Any* *]*  *|* *None*)
  * **reverse** (*bool*)
* **Return type:**
  [*Iter*](#pychain.Iter)

#### split_after(predicate, max_split=-1)

Yield lists of items from iterable, where each list ends with an item where callable pred returns True:
At most maxsplit splits are done.
If maxsplit is not specified or -1, then there is no limit on the number of splits:

```python
>>> Iter("one1two2").split_after(lambda s: s.isdigit()).to_list()
[['o', 'n', 'e', '1'], ['t', 'w', 'o', '2']]
```

```python
>>> Iter(range(10)).split_after(lambda n: n % 3 == 0).to_list()
[[0], [1, 2, 3], [4, 5, 6], [7, 8, 9]]
```

```python
>>> Iter(range(10)).split_after(lambda n: n % 3 == 0, max_split=2).to_list()
[[0], [1, 2, 3], [4, 5, 6, 7, 8, 9]]
```

* **Parameters:**
  * **predicate** (*Check*)
  * **max_split** (*int*)
* **Return type:**
  [Iter][#pychain.Iter](list[T)]

#### zip(\*others, strict=False)

Zip with other iterables, optionally strict, wrapped in Iter.

```python
>>> Iter([1, 2]).zip([10, 20]).to_list()
[(1, 10), (2, 20)]
```

* **Parameters:**
  * **others** (*Iterable* *[**Any* *]*)
  * **strict** (*bool*)
* **Return type:**
  [*Iter*][#pychain.Iter](tuple[*Any*, …)]

#### zip_broadcast(\*others, scalar_types=(<class 'str'>, <class 'bytes'>), strict=False)

Version of zip that “broadcasts” any scalar (i.e., non-iterable) items into output tuples.

```python
>>> iterable_1 = [1, 2, 3]
>>> iterable_2 = ["a", "b", "c"]
>>> scalar = "_"
>>> Iter(iterable_1).zip_broadcast(iterable_2, scalar).to_list()
[(1, 'a', '_'), (2, 'b', '_'), (3, 'c', '_')]
```

The scalar_types keyword argument determines what types are considered scalar.
It is set to (str, bytes) by default. Set it to None to treat strings and byte strings as iterable:

```python
>>> Iter("abc").zip_broadcast(0, "xyz", scalar_types=None).to_list()
[('a', 0, 'x'), ('b', 0, 'y'), ('c', 0, 'z')]
```

If the strict keyword argument is True, then UnequalIterablesError will be raised if any of the iterables have different lengths.

* **Parameters:**
  * **others** (*Iterable*)
  * **scalar_types** (*tuple* *[**type* *,* *type* *]*  *|* *None*)
  * **strict** (*bool*)
* **Return type:**
  [Iter][#pychain.Iter](tuple[T, …)]

#### zip_equal(\*others)

* **Parameters:**
  **others** (*Iterable* *[**Any* *]*)

#### zip_longest(\*others, fill_value=None)

Zip with other iterables, filling missing values.

```python
>>> Iter([1, 2]).zip_longest([10], fill_value=0).to_list()
[(1, 10), (2, 0)]
```

* **Parameters:**
  * **others** (*Iterable*)
  * **fill_value** (*U*)
* **Return type:**
  [Iter][#pychain.Iter](tuple[U | T, …)]

#### zip_offset(\*others, offsets, longest=False, fillvalue=None)

Zip the input iterables together, but offset the i-th iterable by the i-th item in offsets.

```python
>>> Iter("0123").zip_offset("abcdef", offsets=(0, 1)).to_list()
[('0', 'b'), ('1', 'c'), ('2', 'd'), ('3', 'e')]
```

This can be used as a lightweight alternative to SciPy or pandas to analyze data sets in which some series have a lead or lag relationship.
By default, the sequence will end when the shortest iterable is exhausted. To continue until the longest iterable is exhausted, set longest to True.

```python
>>> Iter("0123").zip_offset(
...     "abcdef", offsets=(0, 1), longest=True
... ).to_list()
[('0', 'b'), ('1', 'c'), ('2', 'd'), ('3', 'e'), (None, 'f')]
```

* **Parameters:**
  * **others** (*Iterable*)
  * **offsets** (*list* *[**int* *]*)
  * **longest** (*bool*)
  * **fillvalue** (*U*)
* **Return type:**
  [Iter][#pychain.Iter](tuple[T | U, …)]

### *class* pychain.CommonBase(data)

Base class for all wrappers.
You can subclass this to create your own wrapper types.
The pipe unwrap method must be implemented to allow piping functions that transform the underlying data type, whilst retaining the wrapper.

* **Parameters:**
  **data** (*T*)

#### pipe(func, \*args, \*\*kwargs)

Pipe the instance in the function and return the result.

* **Parameters:**
  * **func** (*Callable* *[* *[**Concatenate* *[**Self* *,* *P* *]* *]* *,* *R* *]*)
  * **args** (*P*)
  * **kwargs** (*P*)
* **Return type:**
  R

#### pipe_chain(\*funcs)

Pipe a value through a sequence of functions.

Prefer this method over multiple pipe_unwrap calls when the functions don’t transform the type.

I.e. Iter(data).pipe_chain(f, g, h).unwrap() is equivalent to h(g(f(data)))

* **Parameters:**
  **funcs** (*Process*)
* **Return type:**
  *Self*

#### pipe_into(func, \*args, \*\*kwargs)

Pipe the underlying data in the function and return the result.

* **Parameters:**
  * **func** (*Callable* *[* *[**Concatenate* *[**T* *,* *P* *]* *]* *,* *R* *]*)
  * **args** (*P*)
  * **kwargs** (*P*)
* **Return type:**
  R

#### *abstractmethod* pipe_unwrap(func, \*args, \*\*kwargs)

Pipe underlying data in the function and return a new wrapped instance.
This function must be implemented by subclasses.

* **Parameters:**
  * **func** (*Callable* *[* *[**Concatenate* *[**Self* *,* *P* *]* *]* *,* *Any* *]*)
  * **args** (*P*)
  * **kwargs** (*P*)
* **Return type:**
  *Any*

#### println(pretty=True)

Print the underlying data and return self for chaining.

* **Parameters:**
  **pretty** (*bool*)
* **Return type:**
  *Self*

#### unwrap()

Return the underlying data.

* **Return type:**
  T

### *class* pychain.Seq(data)

* **Parameters:**
  **data** (*T*)

#### count(value)

Count occurrences of value in the sequence.

```python
>>> Seq([1, 2, 1]).count(1)
2
```

* **Parameters:**
  **value** (*T*)
* **Return type:**
  int

#### index(value, start=0, stop=None)

Return the index of the first occurrence of value in the sequence.

```python
>>> Seq([1, 2, 1]).index(1)
0
```

* **Parameters:**
  * **value** (*T*)
  * **start** (*int*)
  * **stop** (*int* *|* *None*)
* **Return type:**
  int

#### pipe_unwrap(func, \*args, \*\*kwargs)

Pipe underlying data in the function and return a new wrapped instance.
This function must be implemented by subclasses.

* **Parameters:**
  * **func** (*Callable* *[* *[**Concatenate* *[**Sequence* *,* *P* *]* *]* *,* *Sequence* *]*)
  * **args** (*P*)
  * **kwargs** (*P*)
* **Return type:**
  [*Seq*](#pychain.Seq)

#### to_iter()

Return an iterator over the sequence elements.

* **Return type:**
  [Iter][#pychain.Iter](T)

# dict

# Dict Module

### *class* pychain.Dict(data)

Bases: [`CommonBase`](index.md#pychain.CommonBase)[`dict`[`KT`, `VT`]], `Generic`

* **Parameters:**
  **data** (*T*)

#### *classmethod* from_zipped(keys, values)

Create a Dict from two iterables of keys and values.

```python
>>> Dict.from_zipped([1, 2], ["a", "b"])
{1: 'a', 2: 'b'}
```

* **Parameters:**
  * **keys** (*Iterable*)
  * **values** (*Iterable*)
* **Return type:**
  [*Dict*](index.md#pychain.Dict)

#### pipe_unwrap(func, \*args, \*\*kwargs)

Pipe underlying data in the function and return a new wrapped instance.

* **Parameters:**
  * **func** (*Callable* *[* *[**Concatenate* *[**dict* *[**KT* *,* *VT* *]* *,* *P* *]* *]* *,* *dict* *[**KU* *,* *VU* *]* *]*)
  * **args** (*P*)
  * **kwargs** (*P*)
* **Return type:**
  [*Dict*](index.md#pychain.Dict)

#### iter_keys()

Return a Iter of the dict’s keys.

```python
>>> Dict({1: 2}).iter_keys().to_list()
[1]
```

* **Return type:**
  [Iter][iter.md#pychain.Iter](KT)

#### iter_values()

Return a Iter of the dict’s values.

```python
>>> Dict({1: 2}).iter_values().to_list()
[2]
```

* **Return type:**
  [Iter][iter.md#pychain.Iter](VT)

#### iter_items()

Return a Iter of the dict’s items.

```python
>>> Dict({1: 2}).iter_items().to_list()
[(1, 2)]
```

* **Return type:**
  [Iter][iter.md#pychain.Iter](tuple[KT, VT)]

#### copy()

Return a shallow copy of the dict.

* **Return type:**
  *Self*

#### update(\*others)

Update the dict with other(s) dict(s) and return self for convenience.
**Warning**: This modifies the dict in place.

* **Parameters:**
  **others** (*dict* *[**KT* *,* *VT* *]*)
* **Return type:**
  *Self*

#### get_value(key: KT, default: None = None) → VT | None

#### get_value(key: KT, default: VT = None) → VT

Get the value for a key, returning default if not found.

#### set_value(key, value)

Set the value for a key and return self for convenience.
**Warning**: This modifies the dict in place.

```python
>>> Dict({}).set_value("x", 1)
{'x': 1}
```

* **Parameters:**
  * **key** (*KT*)
  * **value** (*VT*)
* **Return type:**
  *Self*

#### filter_keys(predicate)

Return a new Dict containing keys that satisfy predicate.

```python
>>> Dict({1: 2, 3: 4}).filter_keys(lambda k: k % 2 == 0)
{}
```

* **Parameters:**
  **predicate** (*Check*)
* **Return type:**
  *Self*

#### filter_values(predicate)

Return a new Dict containing items whose values satisfy predicate.

```python
>>> Dict({1: 2, 3: 4}).filter_values(lambda v: v > 2)
{3: 4}
```

* **Parameters:**
  **predicate** (*Check*)
* **Return type:**
  *Self*

#### filter_items(predicate)

Filter items by predicate applied to (key, value) tuples.

```python
>>> Dict({1: 2, 3: 4}).filter_items(lambda k, v: v > 2)
{3: 4}
```

* **Parameters:**
  **predicate** (*Callable* *[* *[**KT* *,* *VT* *]* *,* *bool* *]*)
* **Return type:**
  *Self*

#### with_key(key, value)

Return a new Dict with key set to value.

```python
>>> Dict({}).with_key("x", 1)
{'x': 1}
```

* **Parameters:**
  * **key** (*KT*)
  * **value** (*VT*)
* **Return type:**
  *Self*

#### with_nested_key(keys, value)

Set a nested key path and return a new Dict.

```python
>>> Dict({}).with_nested_key(["a", "b"], 1)
{'a': {'b': 1}}
```

* **Parameters:**
  * **keys** (*Iterable* *|* *KT*)
  * **value** (*VT*)
* **Return type:**
  *Self*

#### update_in(\*keys, f)

Update a nested value via function f and return a new Dict.

```python
>>> Dict({"a": {"b": 1}}).update_in("a", "b", f=lambda x: x + 1)
{'a': {'b': 2}}
```

* **Parameters:**
  * **keys** (*KT*)
  * **f** (*Process*)
* **Return type:**
  *Self*

#### merge(\*others)

Merge other dicts into this one and return a new Dict.

```python
>>> Dict({1: 2}).merge({3: 4})
{1: 2, 3: 4}
```

* **Parameters:**
  **others** (*dict* *[**KT* *,* *VT* *]*)
* **Return type:**
  *Self*

#### merge_with(f, \*others)

Merge dicts using f to combine values for duplicate keys.

```python
>>> Dict({1: 1}).merge_with(sum, {1: 2})
{1: 3}
```

* **Parameters:**
  * **f** (*Callable* *[* *[**Iterable* *]* *,* *VT* *]*)
  * **others** (*dict* *[**KT* *,* *VT* *]*)
* **Return type:**
  *Self*

#### drop(\*keys)

Return a new Dict with given keys removed.

```python
>>> Dict({1: 2, 3: 4}).drop(1)
{3: 4}
```

* **Parameters:**
  **keys** (*KT*)
* **Return type:**
  *Self*

#### map_keys(func)

Return a Dict with keys transformed by ffunc.

```python
>>> Dict({1: "a"}).map_keys(str)
{'1': 'a'}
```

* **Parameters:**
  **func** (*Transform*)
* **Return type:**
  [Dict][index.md#pychain.Dict](T, VT)

#### map_values(func)

Return a Dict with values transformed by func.

```python
>>> Dict({1: 1}).map_values(lambda v: v + 1)
{1: 2}
```

* **Parameters:**
  **func** (*Transform*)
* **Return type:**
  [Dict][index.md#pychain.Dict](KT, T)

#### map_items(func)

Transform (key, value) pairs using a function that takes key and value as separate arguments.

```python
>>> Dict({1: 2}).map_items(lambda k, v: (k + 1, v * 10))
{2: 20}
```

* **Parameters:**
  **func** (*Callable* *[* *[**KT* *,* *VT* *]* *,* *tuple* *[**KR* *,* *VR* *]* *]*)
* **Return type:**
  [*Dict*](index.md#pychain.Dict)

# iter

# Iter Module

### *class* pychain.Iter(data)

Bases: `IterAgg`, `IterProcess`, `IterConvert`, `Generic`

A wrapper around Python’s built-in iterable types, providing a rich set of functional programming tools.
It supports lazy evaluation, allowing for efficient processing of large datasets.
It is not a collection itself, but a wrapper that provides additional methods for working with iterables.
It can be constructed from any iterable, including lists, tuples, sets, and generators.

```python
>>> from pychain import Iter
>>> Iter([1, 2, 3]).to_list()
[1, 2, 3]
```

* **Parameters:**
  **data** (*T*)

#### pipe_unwrap(func, \*args, \*\*kwargs)

Pipe the entire iterable into a function that takes an iterable as its first argument.
Returns a new Iter wrapping the result.

```python
>>> from pychain import Iter
>>> def func(iterable, n):
...     return (x * n for x in iterable)
>>>
>>> Iter([1, 2, 3]).pipe_unwrap(func, 10).to_list()
[10, 20, 30]
```

* **Parameters:**
  * **func** (*Callable* *[* *[**Concatenate* *[**Iterable* *,* *P* *]* *]* *,* *Iterable* *]*)
  * **args** (*P*)
  * **kwargs** (*P*)
* **Return type:**
  [*Iter*](#pychain.Iter)

#### *classmethod* from_count(start=0, step=1)

Create an infinite iterator of evenly spaced values.
This is a class method that acts as a constructor.
Warning: This creates an infinite iterator. Be sure to use .head() or
.slice() to limit the number of items taken.

```python
>>> Iter.from_count(10, 2).head(3).to_list()
[10, 12, 14]
```

* **Parameters:**
  * **start** (*int*)
  * **step** (*int*)
* **Return type:**
  [*Iter*][#pychain.Iter](int)

#### *classmethod* from_range(start, stop, step=1)

Create an iterator from a range.

```python
>>> Iter.from_range(1, 5).to_list()
[1, 2, 3, 4]
```

* **Parameters:**
  * **start** (*int*)
  * **stop** (*int*)
  * **step** (*int*)
* **Return type:**
  [*Iter*][#pychain.Iter](int)

#### *classmethod* from_elements(\*elements)

Create an Iter from a sequence of elements.
This is a class method that acts as a constructor from unpacked arguments.

```python
>>> Iter.from_elements(1, 2, 3).to_list()
[1, 2, 3]
```

* **Parameters:**
  **elements** (*U*)
* **Return type:**
  [*Iter*](#pychain.Iter)

#### *classmethod* from_func(func, n)

Create an infinite iterator by repeatedly applying a function.

```python
>>> Iter.from_func(lambda x: x + 1, 0).head(3).to_list()
[0, 1, 2]
```

* **Parameters:**
  * **func** (*Process*)
  * **n** (*U*)
* **Return type:**
  [*Iter*](#pychain.Iter)

#### *classmethod* from_iterables(\*iterables)

Create an Iter by chaining multiple iterables.
This is a class method that acts as a constructor from multiple iterables.

```python
>>> Iter.from_iterables([1, 2], (3, 4)).to_list()
[1, 2, 3, 4]
```

* **Parameters:**
  **iterables** (*Iterable*)
* **Return type:**
  [*Iter*](#pychain.Iter)

#### map(func, \*args, \*\*kwargs)

Map each element through func and return a Iter of results.

```python
>>> Iter([1, 2]).map(lambda x: x + 1).to_list()
[2, 3]
```

* **Parameters:**
  * **func** (*Callable* *[* *[**Concatenate* *[**T* *,* *P* *]* *]* *,* *R* *]*)
  * **args** (*P*)
  * **kwargs** (*P*)
* **Return type:**
  [*Iter*](#pychain.Iter)

#### map_star(func)

Applies a function to each element, where each element is an iterable.
Unlike .map(), which passes each element as a single argument, .starmap() unpacks each element into positional arguments for the function.

In short, for each element in the sequence, it computes func(\*element).

**Tip**: It is the perfect tool to process pairs generated by .product() or .zip_with().

```python
>>> colors = Iter(["blue", "red"])
>>> sizes = ["S", "M"]
>>>
>>> def make_sku(color, size):
...     return f"{color}-{size}"
>>>
>>> colors.product(sizes).map_star(make_sku).to_list()
['blue-S', 'blue-M', 'red-S', 'red-M']
```

* **Parameters:**
  * **self** ([*Iter*](#pychain.Iter))
  * **func** (*Callable* *[* *[* *...* *]* *,* *R* *]*)
* **Return type:**
  [*Iter*](#pychain.Iter)

#### map_flat(func, \*args, \*\*kwargs)

Maps a function over a sequence and flattens the result by one level.
It applies a function to each element, where the function must return
an iterable. The resulting iterables are then chained together into a
single, “flat” sequence.
It’s an efficient shortcut for .map(func).flatten().

```python
>>> # For each author, get a list of their books.
>>> authors = Iter(["author_A", "author_B"])
>>> def get_books(author_id):
...     # This could be an API call that returns a list of books
...     return [f"{author_id}_book1", f"{author_id}_book2"]
>>>
>>> authors.map_flat(get_books).to_list()
['author_A_book1', 'author_A_book2', 'author_B_book1', 'author_B_book2']
```

* **Parameters:**
  * **func** (*Callable* *[* *[**Concatenate* *[**T* *,* *P* *]* *]* *,* *Iterable* *]*)
  * **args** (*P*)
  * **kwargs** (*P*)
* **Return type:**
  [*Iter*](#pychain.Iter)

#### map_join(func, \*others)

Equivalent to flat_map, but allow to join other iterables. However, it don’t take additional arguments for the function.
: ```python
  >>> left = ["a", "b"]
  >>> right = ["c", "d", "e"]
  >>> Iter(left).map_join(lambda s: [c.upper() for c in s], right).to_list()
  ['A', 'B', 'C', 'D', 'E']

  ```

* **Parameters:**
  * **func** (*Transform* *[**Iterable* *,* *Iterable* *]*)
  * **others** (*Iterable*)
* **Return type:**
  [*Iter*](#pychain.Iter)

#### map_if(predicate, func, func_else=None)

Evaluate each item from iterable using pred. If the result is equivalent to True, transform the item with func and yield it.

Otherwise, transform the item with func_else and yield it.
predicate, func, and func_else should each be functions that accept one argument.

By default, func_else is the identity function.
: ```python
  >>> from math import sqrt
  >>> iterable = list(range(-5, 5))
  >>> iterable
  [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4]
  >>> Iter(iterable).map_if(lambda x: x > 3, lambda x: "toobig").to_list()
  [-5, -4, -3, -2, -1, 0, 1, 2, 3, 'toobig']
  >>> Iter(iterable).map_if(
  ...     lambda x: x >= 0,
  ...     lambda x: f"{sqrt(x):.2f}",
  ...     lambda x: None,
  ... ).to_list()
  [None, None, None, None, None, '0.00', '1.00', '1.41', '1.73', '2.00']
  ```

* **Parameters:**
  * **predicate** (*Check*)
  * **func** (*Transform*)
  * **func_else** (*Transform* *|* *None*)
* **Return type:**
  [*Iter*](#pychain.Iter)

#### map_filter(func)

Apply func to every element of iterable, yielding only those which are not None.

```python
>>> elems = ["1", "a", "2", "b", "3"]
>>> Iter(elems).map_filter(
...     lambda s: int(s) if s.isnumeric() else None
... ).to_list()
[1, 2, 3]
```

* **Parameters:**
  **func** (*Transform*)
* **Return type:**
  [*Iter*](#pychain.Iter)

#### map_except(func, \*exceptions)

Transform each item from iterable with function and yield the result, unless function raises one of the specified exceptions.
function is called to transform each item in iterable.

It should accept one argument.

If an exception other than one given by exceptions is raised by function, it is raised like normal.

```python
>>> iterable = ["1", "2", "three", "4", None]
>>> Iter(iterable).map_except(int, ValueError, TypeError).to_list()
[1, 2, 4]
```

* **Parameters:**
  * **func** (*Transform*)
  * **exceptions** (*type* *[**BaseException* *]*)
* **Return type:**
  [*Iter*](#pychain.Iter)

#### map_juxt(\*funcs)

Apply several functions to each item.
Returns a new Iter where each item is a tuple of the results of
applying each function to the original item.

```python
>>> def is_even(n):
...     return n % 2 == 0
>>> def is_positive(n):
...     return n > 0
>>> Iter([1, -2, 3]).map_juxt(is_even, is_positive).to_list()
[(False, True), (True, False), (False, True)]
```

* **Parameters:**
  **funcs** (*Transform*)
* **Return type:**
  [*Iter*][#pychain.Iter](tuple[R, …)]

#### zip(iter1: Iterable[T1], , , strict: bool = False) → [Iter][#pychain.Iter](tuple[T, T1)]

#### zip(iter1: Iterable[T1], iter2: Iterable[T2], , , strict: bool = False) → [Iter][#pychain.Iter](tuple[T, T1, T2)]

#### zip(iter1: Iterable[T1], iter2: Iterable[T2], iter3: Iterable[T3], , , strict: bool = False) → [Iter][#pychain.Iter](tuple[T, T1, T2, T3)]

#### zip(iter1: Iterable[T1], iter2: Iterable[T2], iter3: Iterable[T3], iter4: Iterable[T4], , , strict: bool = False) → [Iter][#pychain.Iter](tuple[T, T1, T2, T3, T4)]

#### zip(iter1: Iterable[T1], iter2: Iterable[T2], iter3: Iterable[T3], iter4: Iterable[T4], iter5: Iterable[T5], , , strict: bool = False) → [Iter][#pychain.Iter](tuple[T, T1, T2, T3, T4, T5)]

Zip with other iterables, optionally strict, wrapped in Iter.

```python
>>> Iter([1, 2]).zip([10, 20]).to_list()
[(1, 10), (2, 20)]
```

#### zip_offset(\*others, offsets, longest=False, fillvalue=None)

Zip the input iterables together, but offset the i-th iterable by the i-th item in offsets.

```python
>>> Iter("0123").zip_offset("abcdef", offsets=(0, 1)).to_list()
[('0', 'b'), ('1', 'c'), ('2', 'd'), ('3', 'e')]
```

This can be used as a lightweight alternative to SciPy or pandas to analyze data sets in which some series have a lead or lag relationship.
By default, the sequence will end when the shortest iterable is exhausted. To continue until the longest iterable is exhausted, set longest to True.

```python
>>> Iter("0123").zip_offset(
...     "abcdef", offsets=(0, 1), longest=True
... ).to_list()
[('0', 'b'), ('1', 'c'), ('2', 'd'), ('3', 'e'), (None, 'f')]
```

* **Parameters:**
  * **others** (*Iterable*)
  * **offsets** (*list* *[**int* *]*)
  * **longest** (*bool*)
  * **fillvalue** (*U*)
* **Return type:**
  [Iter][#pychain.Iter](tuple[T | U, …)]

#### zip_broadcast(\*others, scalar_types=(<class 'str'>, <class 'bytes'>), strict=False)

Version of zip that “broadcasts” any scalar (i.e., non-iterable) items into output tuples.

```python
>>> iterable_1 = [1, 2, 3]
>>> iterable_2 = ["a", "b", "c"]
>>> scalar = "_"
>>> Iter(iterable_1).zip_broadcast(iterable_2, scalar).to_list()
[(1, 'a', '_'), (2, 'b', '_'), (3, 'c', '_')]
```

The scalar_types keyword argument determines what types are considered scalar.
It is set to (str, bytes) by default. Set it to None to treat strings and byte strings as iterable:

```python
>>> Iter("abc").zip_broadcast(0, "xyz", scalar_types=None).to_list()
[('a', 0, 'x'), ('b', 0, 'y'), ('c', 0, 'z')]
```

If the strict keyword argument is True, then UnequalIterablesError will be raised if any of the iterables have different lengths.

* **Parameters:**
  * **others** (*Iterable*)
  * **scalar_types** (*tuple* *[**type* *,* *type* *]*  *|* *None*)
  * **strict** (*bool*)
* **Return type:**
  [Iter][#pychain.Iter](tuple[T, …)]

#### zip_equal() → [Iter][#pychain.Iter](tuple[T)]

#### zip_equal(\_\_iter2: Iterable[T2]) → [Iter][#pychain.Iter](tuple[T, T2)]

#### zip_equal(\_\_iter2: Iterable[T2], \_\_iter3: Iterable[T3]) → [Iter][#pychain.Iter](tuple[T, T2, T3)]

#### zip_equal(\_\_iter2: Iterable[T2], \_\_iter3: Iterable[T3], \_\_iter4: Iterable[T4]) → [Iter][#pychain.Iter](tuple[T, T2, T3, T4)]

#### zip_equal(\_\_iter2: Iterable[T2], \_\_iter3: Iterable[T3], \_\_iter4: Iterable[T4], \_\_iter5: Iterable[T5]) → [Iter][#pychain.Iter](tuple[T, T2, T3, T4, T5)]

#### zip_equal(\_\_iter2: Iterable[Any], \_\_iter3: Iterable[Any], \_\_iter4: Iterable[Any], \_\_iter5: Iterable[Any], \_\_iter6: Iterable[Any], \*iterables: Iterable[Any]) → [Iter][#pychain.Iter](tuple[Any, ...)]

#### enumerate()

Return a Iter of (index, value) pairs.

```python
>>> Iter(["a", "b"]).enumerate().to_list()
[(0, 'a'), (1, 'b')]
```

* **Return type:**
  [Iter][#pychain.Iter](tuple[int, T)]

#### combinations(r: Literal[2]) → [Iter][#pychain.Iter](tuple[T, T)]

#### combinations(r: Literal[3]) → [Iter][#pychain.Iter](tuple[T, T, T)]

#### combinations(r: Literal[4]) → [Iter][#pychain.Iter](tuple[T, T, T, T)]

#### combinations(r: Literal[5]) → [Iter][#pychain.Iter](tuple[T, T, T, T, T)]

¨
Return all combinations of length r.

```python
>>> Iter([1, 2, 3]).combinations(2).to_list()
[(1, 2), (1, 3), (2, 3)]
```

#### batch(n)

Batch elements into tuples of length n and return a new Iter.

```python
>>> Iter("ABCDEFG").batch(3).to_list()
[('A', 'B', 'C'), ('D', 'E', 'F'), ('G',)]
```

* **Parameters:**
  **n** (*int*)
* **Return type:**
  [Iter][#pychain.Iter](tuple[T, …)]

#### zip_longest(\*others, fill_value=None)

Zip with other iterables, filling missing values.

```python
>>> Iter([1, 2]).zip_longest([10], fill_value=0).to_list()
[(1, 10), (2, 0)]
```

* **Parameters:**
  * **others** (*Iterable*)
  * **fill_value** (*U*)
* **Return type:**
  [Iter][#pychain.Iter](tuple[U | T, …)]

#### permutations(r=None)

¨
Return all permutations of length r.

```python
>>> Iter([1, 2, 3]).permutations(2).to_list()
[(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)]
```

* **Parameters:**
  **r** (*int* *|* *None*)
* **Return type:**
  [Iter][#pychain.Iter](tuple[T, …)]

#### product(other)

Computes the Cartesian product with another iterable.
This is the declarative equivalent of nested for-loops.

It pairs every element from the source iterable with every element from the
other iterable.

**Tip**: This method is often chained with .starmap() to apply a
function to each generated pair.

```python
>>> colors = Iter(["blue", "red"])
>>> sizes = ["S", "M"]
>>> colors.product(sizes).to_list()
[('blue', 'S'), ('blue', 'M'), ('red', 'S'), ('red', 'M')]
```

* **Parameters:**
  **other** (*Iterable*)
* **Return type:**
  [Iter][#pychain.Iter](tuple[T, U)]

#### combinations_with_replacement(r)

Return all combinations with replacement of length r.

```python
>>> Iter([1, 2, 3]).combinations_with_replacement(2).to_list()
[(1, 1), (1, 2), (1, 3), (2, 2), (2, 3), (3, 3)]
```

* **Parameters:**
  **r** (*int*)
* **Return type:**
  [Iter][#pychain.Iter](tuple[T, …)]

#### pairwise()

Return an iterator over pairs of consecutive elements.

```python
>>> Iter([1, 2, 3]).pairwise().to_list()
[(1, 2), (2, 3)]
```

* **Return type:**
  [Iter][#pychain.Iter](tuple[T, T)]

#### join(other, left_on, right_on, left_default=None, right_default=None)

Perform a relational join with another iterable.

```python
>>> colors = Iter(["blue", "red"])
>>> sizes = ["S", "M"]
>>> colors.join(sizes, left_on=lambda c: c, right_on=lambda s: s).to_list()
[(None, 'S'), (None, 'M'), ('blue', None), ('red', None)]
```

* **Parameters:**
  * **other** (*Iterable*)
  * **left_on** (*Transform*)
  * **right_on** (*Transform*)
  * **left_default** (*T* *|* *None*)
  * **right_default** (*R* *|* *None*)
* **Return type:**
  [Iter][#pychain.Iter](tuple[T, R)]

#### pluck(key)

Extract a value from each element in the sequence using a key or index.
This is a shortcut for .map(lambda x: x[key]).

```python
>>> data = Iter([{"id": 1, "val": "a"}, {"id": 2, "val": "b"}])
>>> data.pluck("val").to_list()
['a', 'b']
>>> Iter([[10, 20], [30, 40]]).pluck(0).to_list()
[10, 30]
```

* **Parameters:**
  * **self** ([*Iter*](#pychain.Iter) *[**Pluckable* *]*)
  * **key** (*K*)
* **Return type:**
  [*Iter*](#pychain.Iter)

#### partition(n, pad=None)

Partition into tuples of length n, optionally padded.

```python
>>> Iter([1, 2, 3, 4]).partition(2).to_list()
[(1, 2), (3, 4)]
```

* **Parameters:**
  * **n** (*int*)
  * **pad** (*T* *|* *None*)
* **Return type:**
  [Iter][#pychain.Iter](tuple[T, …)]

#### partition_all(n)

Partition into tuples of length at most n.

```python
>>> Iter([1, 2, 3]).partition_all(2).to_list()
[(1, 2), (3,)]
```

* **Parameters:**
  **n** (*int*)
* **Return type:**
  [Iter][#pychain.Iter](tuple[T, …)]

#### rolling(length)

Return sliding windows of the given length.

```python
>>> Iter([1, 2, 3]).rolling(2).to_list()
[(1, 2), (2, 3)]
```

* **Parameters:**
  **length** (*int*)
* **Return type:**
  [Iter][#pychain.Iter](tuple[T, …)]

#### diff(\*others, key=None)

Yield differences between sequences.

```python
>>> Iter([1, 2, 3]).diff([1, 2, 10]).to_list()
[(3, 10)]
```

* **Parameters:**
  * **others** (*Iterable*)
  * **key** (*Process* *|* *None*)
* **Return type:**
  [Iter][#pychain.Iter](tuple[T, …)]

#### reduce_by(key, binop)

Perform a simultaneous groupby and reduction
on the elements of the sequence.

```python
>>> Iter([1, 2, 3, 4]).reduce_by(
...     key=lambda x: x % 2, binop=lambda a, b: a + b
... ).to_list()
[1, 0]
```

* **Parameters:**
  * **key** (*Transform*)
  * **binop** (*Callable* *[* *[**T* *,* *T* *]* *,* *T* *]*)
* **Return type:**
  [*Iter*](#pychain.Iter)

#### adjacent(predicate, distance=1)

Return an iterable over (bool, item) tuples.
The output is a sequence of tuples where the item is drawn from iterable.

The bool indicates whether that item satisfies the predicate or is adjacent to an item that does.

For example, to find whether items are adjacent to a 3:

```python
>>> Iter(range(6)).adjacent(lambda x: x == 3).to_list()
[(False, 0), (False, 1), (True, 2), (True, 3), (True, 4), (False, 5)]
```

Set distance to change what counts as adjacent. For example, to find whether items are two places away from a 3:

```python
>>> Iter(range(6)).adjacent(lambda x: x == 3, distance=2).to_list()
[(False, 0), (True, 1), (True, 2), (True, 3), (True, 4), (True, 5)]
```

This is useful for contextualizing the results of a search function.
For example, a code comparison tool might want to identify lines that have changed, but also surrounding lines to give the viewer of the diff context.
The predicate function will only be called once for each item in the iterable.

See also groupby_transform, which can be used with this function to group ranges of items with the same bool value.

* **Parameters:**
  * **predicate** (*Check*)
  * **distance** (*int*)
* **Return type:**
  [Iter][#pychain.Iter](tuple[bool, T)]

#### repeat(n)

Repeat the entire iterable n times (as elements) and return Iter.

```python
>>> Iter([1, 2]).repeat(2).to_list()
[[1, 2], [1, 2]]
```

* **Parameters:**
  **n** (*int*)
* **Return type:**
  [Iter][#pychain.Iter](Iterable[T)]

#### repeat_last(default: T) → [Iter][#pychain.Iter](T)

#### repeat_last(default: U) → [Iter][#pychain.Iter](T | U)

After the iterable is exhausted, keep yielding its last element.

```python
>>> Iter(range(3)).repeat_last().head(5).to_list()
[0, 1, 2, 2, 2]
```

If the iterable is empty, yield default forever:

```python
>>> Iter(range(0)).repeat_last(42).head(5).to_list()
[42, 42, 42, 42, 42]
```

#### flatten()

Flatten one level of nesting and return a new Iterable wrapper.

```python
>>> Iter([[1, 2], [3]]).flatten().to_list()
[1, 2, 3]
```

* **Parameters:**
  **self** ([*Iter*](#pychain.Iter) *[**Iterable* *]*)
* **Return type:**
  [*Iter*](#pychain.Iter)

#### split_after(predicate, max_split=-1)

Yield lists of items from iterable, where each list ends with an item where callable pred returns True:
At most maxsplit splits are done.
If maxsplit is not specified or -1, then there is no limit on the number of splits:

```python
>>> Iter("one1two2").split_after(lambda s: s.isdigit()).to_list()
[['o', 'n', 'e', '1'], ['t', 'w', 'o', '2']]
```

```python
>>> Iter(range(10)).split_after(lambda n: n % 3 == 0).to_list()
[[0], [1, 2, 3], [4, 5, 6], [7, 8, 9]]
```

```python
>>> Iter(range(10)).split_after(lambda n: n % 3 == 0, max_split=2).to_list()
[[0], [1, 2, 3], [4, 5, 6, 7, 8, 9]]
```

* **Parameters:**
  * **predicate** (*Check*)
  * **max_split** (*int*)
* **Return type:**
  [Iter][#pychain.Iter](list[T)]

#### chunked(n, strict=False)

Break iterable into lists of length n.

By default, the last yielded list will have fewer than *n* elements if the length of *iterable* is not divisible by *n*.

To use a fill-in value instead, see the `grouper()` recipe.

If the length of *iterable* is not divisible by *n* and *strict* is
`True`, then `ValueError` will be raised before the last
list is yielded.

```python
>>> Iter([1, 2, 3, 4, 5, 6]).chunked(3).to_list()
[[1, 2, 3], [4, 5, 6]]
>>> Iter([1, 2, 3, 4, 5, 6, 7, 8]).chunked(3).to_list()
[[1, 2, 3], [4, 5, 6], [7, 8]]
```

* **Parameters:**
  * **n** (*int*)
  * **strict** (*bool*)
* **Return type:**
  [Iter][#pychain.Iter](list[T)]

#### chunked_even(n)

Break iterable into lists of approximately length n.
Items are distributed such the lengths of the lists differ by at most 1 item.

```python
>>> iterable = [1, 2, 3, 4, 5, 6, 7]
>>> Iter(iterable).chunked_even(3).to_list()  # List lengths: 3, 2, 2
[[1, 2, 3], [4, 5], [6, 7]]
>>> Iter(iterable).chunked(3).to_list()  # List lengths: 3, 3, 1
[[1, 2, 3], [4, 5, 6], [7]]
```

* **Parameters:**
  **n** (*int*)
* **Return type:**
  [Iter][#pychain.Iter](list[T)]

#### sort(key=None, reverse=False)

Sort the elements of the sequence.
Note: This method must consume the entire iterable to perform the sort.
The result is a new iterable over the sorted sequence.

```python
>>> Iter([3, 1, 2]).sort().to_list()
[1, 2, 3]
>>> data = Iter([{"age": 30}, {"age": 20}])
>>> data.sort(key=lambda x: x["age"]).to_list()
[{'age': 20}, {'age': 30}]
```

* **Parameters:**
  * **self** ([*Iter*](#pychain.Iter))
  * **key** (*Transform* *[**U* *,* *Any* *]*  *|* *None*)
  * **reverse** (*bool*)
* **Return type:**
  [*Iter*](#pychain.Iter)
