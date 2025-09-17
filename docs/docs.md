# PyChain Documentation

<a id="module-pychain"></a>

## *class* pychain.Dict(data)

Wrapper for Python dictionaries with chainable methods.

* **Parameters:**
  **data** (*T*)

### copy()

Return a shallow copy of the dict.

* **Return type:**
  *Self*

### drop(\*keys)

Return a new Dict with given keys removed.

New dict has d[key] deleted for each supplied key.

```python
>>> Dict({"x": 1, "y": 2}).drop("y")
{'x': 1}
>>> Dict({"x": 1, "y": 2}).drop("y", "x")
{}
>>> Dict({"x": 1}).drop("y")  # Ignores missing keys
{'x': 1}
>>> Dict({1: 2, 3: 4}).drop(1)
{3: 4}
```

* **Parameters:**
  **keys** (*K*)
* **Return type:**
  Self

### filter_items(predicate)

Filter items by predicate applied to (key, value) tuples.

```python
>>> Dict({1: 2, 3: 4}).filter_items(lambda it: it[1] > 2)
{3: 4}
```

* **Parameters:**
  **predicate** (*Callable* *[* *[**tuple* *[**K* *,* *V* *]* *]* *,* *bool* *]*)
* **Return type:**
  Self

### filter_keys(predicate)

Return a new Dict containing keys that satisfy predicate.

```python
>>> d = {1: 2, 2: 3, 3: 4, 4: 5}
>>> Dict(d).filter_keys(lambda x: x % 2 == 0)
{2: 3, 4: 5}
```

* **Parameters:**
  **predicate** (*Callable* *[* *[**K* *]* *,* *bool* *]*)
* **Return type:**
  Self

### filter_kv(predicate)

Filter items by predicate applied to (key, value) tuples.

```python
>>> Dict({1: 2, 3: 4}).filter_kv(lambda k, v: v > 2)
{3: 4}
```

* **Parameters:**
  **predicate** (*Callable* *[* *[**K* *,* *V* *]* *,* *bool* *]*)
* **Return type:**
  Self

### filter_values(predicate)

Return a new Dict containing items whose values satisfy predicate.

```python
>>> d = {1: 2, 2: 3, 3: 4, 4: 5}
>>> Dict(d).filter_values(lambda x: x % 2 == 0)
{1: 2, 3: 4}
```

* **Parameters:**
  **predicate** (*Callable* *[* *[**V* *]* *,* *bool* *]*)
* **Return type:**
  Self

### *classmethod* from_zipped(keys, values)

Create a Dict from two iterables of keys and values.

Syntactic sugar for Dict(dict(zip(keys, values))).

```python
>>> Dict.from_zipped([1, 2], ["a", "b"])
{1: 'a', 2: 'b'}
```

* **Parameters:**
  * **keys** (*Iterable*)
  * **values** (*Iterable*)
* **Return type:**
  [*Dict*](#pychain.Dict)

### get_value(key, default=None)

Get the value for a key, returning default if not found.

* **Parameters:**
  * **key** (*K*)
  * **default** (*V* *|* *None*)
* **Return type:**
  V | None

### iter_items()

Return a Iter of the dict’s items.

```python
>>> Dict({1: 2}).iter_items().to_list()
[(1, 2)]
```

* **Return type:**
  [Iter](#pychain.Iter)[tuple[K, V]]

### iter_keys()

Return a Iter of the dict’s keys.

```python
>>> Dict({1: 2}).iter_keys().to_list()
[1]
```

* **Return type:**
  [Iter](#pychain.Iter)[K]

### iter_values()

Return a Iter of the dict’s values.

```python
>>> Dict({1: 2}).iter_values().to_list()
[2]
```

* **Return type:**
  [Iter](#pychain.Iter)[V]

### map_items(func)

Transform (key, value) pairs using a function that takes a (key, value) tuple.

```python
>>> Dict({"Alice": 10, "Bob": 20}).map_items(reversed)
{10: 'Alice', 20: 'Bob'}
```

* **Parameters:**
  **func** (*Callable* *[* *[**tuple* *[**K* *,* *V* *]* *]* *,* *tuple* *[**KR* *,* *VR* *]* *]*)
* **Return type:**
  [Dict](#pychain.Dict)[KR, VR]

### map_keys(func)

Return a Dict with keys transformed by func.

```python
>>> Dict({"Alice": [20, 15, 30], "Bob": [10, 35]}).map_keys(str.lower)
{'alice': [20, 15, 30], 'bob': [10, 35]}
>>>
>>> Dict({1: "a"}).map_keys(str)
{'1': 'a'}
```

* **Parameters:**
  **func** (*Callable* *[* *[**K* *]* *,* *T* *]*)
* **Return type:**
  [Dict](#pychain.Dict)[T, V]

### map_kv(func)

Transform (key, value) pairs using a function that takes key and value as separate arguments.

```python
>>> Dict({1: 2}).map_kv(lambda k, v: (k + 1, v * 10))
{2: 20}
```

* **Parameters:**
  **func** (*Callable* *[* *[**K* *,* *V* *]* *,* *tuple* *[**KR* *,* *VR* *]* *]*)
* **Return type:**
  [Dict](#pychain.Dict)[KR, VR]

### map_values(func)

Return a Dict with values transformed by func.

```python
>>> Dict({"Alice": [20, 15, 30], "Bob": [10, 35]}).map_values(sum)
{'Alice': 65, 'Bob': 45}
>>>
>>> Dict({1: 1}).map_values(lambda v: v + 1)
{1: 2}
```

* **Parameters:**
  **func** (*Callable* *[* *[**V* *]* *,* *T* *]*)
* **Return type:**
  [Dict](#pychain.Dict)[K, T]

### merge(\*others)

Merge other dicts into this one and return a new Dict.

```python
>>> Dict({1: "one"}).merge({2: "two"})
{1: 'one', 2: 'two'}
```

Later dictionaries have precedence

```python
>>> Dict({1: 2, 3: 4}).merge({3: 3, 4: 4})
{1: 2, 3: 3, 4: 4}
```

* **Parameters:**
  **others** (*dict* *[**K* *,* *V* *]*)
* **Return type:**
  Self

### merge_with(\*others, func)

Merge dicts using a function to combine values for duplicate keys.

A key may occur in more than one dict, and all values mapped from the key will be passed to the function as a list, such as func([val1, val2, …]).

```python
>>> Dict({1: 1, 2: 2}).merge_with({1: 10, 2: 20}, func=sum)
{1: 11, 2: 22}
>>> Dict({1: 1, 2: 2}).merge_with({2: 20, 3: 30}, func=max)
{1: 1, 2: 20, 3: 30}
```

* **Parameters:**
  * **others** (*dict* *[**K* *,* *V* *]*)
  * **func** (*Callable* *[* *[**Iterable* *[**V* *]* *]* *,* *V* *]*)
* **Return type:**
  Self

### pipe_into(func, \*args, \*\*kwargs)

Pipe the underlying data into a function, then wrap the result in the same wrapper type.

Each pychain class implement this method to allow chaining of functions that transform the
underlying data and return a new wrapped instance of the same subclass.

```python
>>> from pychain import Dict
>>> Dict({1: 2}).pipe_into(lambda d: {k: v + 1 for k, v in d.items()})
{1: 3}
```

Use this to keep the chainable API after applying a transformation to the data.

* **Parameters:**
  * **func** (*Callable* *[**Concatenate* *[**dict* *[**K* *,* *V* *]* *,* *P* *]* *,* *dict* *[**KU* *,* *VU* *]* *]*)
  * **args** (*P.args*)
  * **kwargs** (*P.kwargs*)
* **Return type:**
  [Dict](#pychain.Dict)[KU, VU]

### set_value(key, value)

Set the value for a key and return self for convenience.

**Warning** ⚠️

This modifies the dict in place.

```python
>>> Dict({}).set_value("x", 1)
{'x': 1}
```

* **Parameters:**
  * **key** (*K*)
  * **value** (*V*)
* **Return type:**
  Self

### update(\*others)

Update the dict with other(s) dict(s) and return self for convenience.

**Warning** ⚠️

This modifies the dict in place.

```python
>>> Dict({1: 2}).update({3: 4})
{1: 2, 3: 4}
```

* **Parameters:**
  **others** (*dict* *[**K* *,* *V* *]*)
* **Return type:**
  Self

### update_in(keys, func, default=None)

Update value in a (potentially) nested dictionary

inputs: d - dictionary on which to operate keys - list or tuple giving the location of the value to be changed in d func - function to operate on that value

If keys == [k0,..,kX] and d[k0]..[kX] == v, update_in returns a copy of the original dictionary with v replaced by func(v), but does not mutate the original dictionary.

If k0 is not a key in d, update_in creates nested dictionaries to the depth specified by the keys, with the innermost value set to func(default).

```python
>>> inc = lambda x: x + 1
>>> Dict({"a": 0}).update_in(["a"], func=inc)
{'a': 1}
>>> transaction = {
...     "name": "Alice",
...     "purchase": {"items": ["Apple", "Orange"], "costs": [0.50, 1.25]},
...     "credit card": "5555-1234-1234-1234",
... }
>>> Dict(transaction).update_in(["purchase", "costs"], func=sum)
{'name': 'Alice', 'purchase': {'items': ['Apple', 'Orange'], 'costs': 1.75}, 'credit card': '5555-1234-1234-1234'}
>>> # updating a value when k0 is not in d
>>> Dict({}).update_in([1, 2, 3], func=str, default="bar")
{1: {2: {3: 'bar'}}}
>>> Dict({1: "foo"}).update_in([2, 3, 4], func=inc, default=0)
{1: 'foo', 2: {3: {4: 1}}}
```

* **Parameters:**
  * **keys** (*Iterable* *[**K* *]*)
  * **func** (*Callable* *[* *[**V* *]* *,* *V* *]*)
  * **default** (*V* *|* *None*)
* **Return type:**
  Self

### with_key(key, value)

Return a new Dict with key set to value.

```python
>>> Dict({"x": 1}).with_key("x", 2)
{'x': 2}
>>> Dict({"x": 1}).with_key("y", 3)
{'x': 1, 'y': 3}
>>> Dict({}).with_key("x", 1)
{'x': 1}
```

* **Parameters:**
  * **key** (*K*)
  * **value** (*V*)
* **Return type:**
  Self

### with_nested_key(keys, value)

Set a nested key path and return a new Dict with new, potentially nested, key value pair

```python
>>> purchase = {
...     "name": "Alice",
...     "order": {"items": ["Apple", "Orange"], "costs": [0.50, 1.25]},
...     "credit card": "5555-1234-1234-1234",
... }
>>> Dict(purchase).with_nested_key(["order", "costs"], [0.25, 1.00])
{'name': 'Alice', 'order': {'items': ['Apple', 'Orange'], 'costs': [0.25, 1.0]}, 'credit card': '5555-1234-1234-1234'}
```

* **Parameters:**
  * **keys** (*Iterable* *[**K* *]*  *|* *K*)
  * **value** (*V*)
* **Return type:**
  Self

## *class* pychain.Iter(data)

A wrapper around Python’s built-in iterable types, providing a rich set of functional programming tools.

It supports lazy evaluation, allowing for efficient processing of large datasets.

It is not a collection itself, but a wrapper that provides additional methods for working with iterables.

It can be constructed from any iterable, including lists, tuples, sets, and generators.

* **Parameters:**
  **data** (*T*)

### adjacent(predicate, distance=1)

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
  * **predicate** (*Callable* *[* *[**T* *]* *,* *bool* *]*)
  * **distance** (*int*)
* **Return type:**
  [Iter](#pychain.Iter)[tuple[bool, T]]

### batch(n)

Batch elements into tuples of length n and return a new Iter.

```python
>>> Iter("ABCDEFG").batch(3).to_list()
[('A', 'B', 'C'), ('D', 'E', 'F'), ('G',)]
```

* **Parameters:**
  **n** (*int*)
* **Return type:**
  [Iter](#pychain.Iter)[tuple[T, …]]

### chunked(n, strict=False)

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
  [Iter](#pychain.Iter)[list[T]]

### chunked_even(n)

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
  [Iter](#pychain.Iter)[list[T]]

### combinations(r)

Return all combinations of length r.

```python
>>> Iter([1, 2, 3]).combinations(2).to_list()
[(1, 2), (1, 3), (2, 3)]
```

* **Parameters:**
  **r** (*int*)
* **Return type:**
  [Iter](#pychain.Iter)[tuple[T, …]]

### combinations_with_replacement(r)

Return all combinations with replacement of length r.

```python
>>> Iter([1, 2, 3]).combinations_with_replacement(2).to_list()
[(1, 1), (1, 2), (1, 3), (2, 2), (2, 3), (3, 3)]
```

* **Parameters:**
  **r** (*int*)
* **Return type:**
  [Iter](#pychain.Iter)[tuple[T, …]]

### diff(\*others, key=None)

Yield differences between sequences.

```python
>>> Iter([1, 2, 3]).diff([1, 2, 10]).to_list()
[(3, 10)]
```

* **Parameters:**
  * **others** (*Iterable* *[**T* *]*)
  * **key** (*Callable* *[* *[**T* *]* *,* *T* *]*  *|* *None*)
* **Return type:**
  [Iter](#pychain.Iter)[tuple[T, …]]

### elements()

Iterator over elements repeating each as many times as its count.

```python
>>> Iter("ABCABC").elements().sort()
['A', 'A', 'B', 'B', 'C', 'C']
```

Knuth’s example for prime factors of 1836:  2\*\*2 \* 3\*\*3 \* 17\*\*1

```python
>>> import math
>>> Iter({2: 2, 3: 3, 17: 1}).elements().pipe_into(math.prod)
1836
```

Note, if an element’s count has been set to zero or is a negative
number, elements() will ignore it.

* **Return type:**
  [Iter](#pychain.Iter)[T]

### enumerate()

Return a Iter of (index, value) pairs.

```python
>>> Iter(["a", "b"]).enumerate().to_list()
[(0, 'a'), (1, 'b')]
```

* **Return type:**
  [Iter](#pychain.Iter)[tuple[int, T]]

### flatten()

Flatten one level of nesting and return a new Iterable wrapper.

```python
>>> Iter([[1, 2], [3]]).flatten().to_list()
[1, 2, 3]
```

* **Parameters:**
  **self** ([*Iter*](#pychain.Iter) *[**Iterable* *]*)
* **Return type:**
  [*Iter*](#pychain.Iter)

### frequencies()

Return a Dict of value frequencies.

```python
>>> from pychain import Iter
>>> Iter([1, 1, 2]).frequencies()
{1: 2, 2: 1}
```

* **Return type:**
  [Dict](#pychain.Dict)[T, int]

### group_by(on)

Group elements by key function and return a Dict result.

```python
>>> from pychain import Iter
>>> Iter(["a", "bb"]).group_by(len)
{1: ['a'], 2: ['bb']}
```

* **Parameters:**
  **on** (*Callable* *[* *[**T* *]* *,* *K* *]*)
* **Return type:**
  [Dict](#pychain.Dict)[K, list[T]]

### join(other, left_on, right_on, left_default=None, right_default=None)

Perform a relational join with another iterable.

```python
>>> colors = Iter(["blue", "red"])
>>> sizes = ["S", "M"]
>>> colors.join(sizes, left_on=lambda c: c, right_on=lambda s: s).to_list()
[(None, 'S'), (None, 'M'), ('blue', None), ('red', None)]
```

* **Parameters:**
  * **other** (*Iterable* *[**R* *]*)
  * **left_on** (*Callable* *[* *[**T* *]* *,* *K* *]*)
  * **right_on** (*Callable* *[* *[**R* *]* *,* *K* *]*)
  * **left_default** (*T* *|* *None*)
  * **right_default** (*R* *|* *None*)
* **Return type:**
  [Iter](#pychain.Iter)[tuple[T, R]]

### map(func, \*args, \*\*kwargs)

Map each element through func and return a Iter of results.

```python
>>> Iter([1, 2]).map(lambda x: x + 1).to_list()
[2, 3]
```

* **Parameters:**
  * **func** (*Callable* *[**Concatenate* *[**T* *,* *P* *]* *,* *R* *]*)
  * **args** (*P.args*)
  * **kwargs** (*P.kwargs*)
* **Return type:**
  [Iter](#pychain.Iter)[R]

### map_except(func, \*exceptions)

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
  * **func** (*Callable* *[* *[**T* *]* *,* *R* *]*)
  * **exceptions** (*type* *[**BaseException* *]*)
* **Return type:**
  [Iter](#pychain.Iter)[R]

### map_filter(func)

Apply func to every element of iterable, yielding only those which are not None.

```python
>>> elems = ["1", "a", "2", "b", "3"]
>>> Iter(elems).map_filter(
...     lambda s: int(s) if s.isnumeric() else None
... ).to_list()
[1, 2, 3]
```

* **Parameters:**
  **func** (*Callable* *[* *[**T* *]* *,* *R* *]*)
* **Return type:**
  [Iter](#pychain.Iter)[R]

### map_flat(func, \*args, \*\*kwargs)

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
  * **func** (*Callable* *[**Concatenate* *[**T* *,* *P* *]* *,* *Iterable* *[**R* *]* *]*)
  * **args** (*P.args*)
  * **kwargs** (*P.kwargs*)
* **Return type:**
  [Iter](#pychain.Iter)[R]

### map_if(predicate, func, func_else=None)

Evaluate each item from iterable using pred. If the result is equivalent to True, transform the item with func and yield it.

Otherwise, transform the item with func_else and yield it.
Predicate, func, and func_else should each be functions that accept one argument.

By default, func_else is the identity function.

```python
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
  * **predicate** (*Callable* *[* *[**T* *]* *,* *bool* *]*)
  * **func** (*Callable* *[* *[**T* *]* *,* *R* *]*)
  * **func_else** (*Callable* *[* *[**T* *]* *,* *R* *]*  *|* *None*)
* **Return type:**
  [Iter](#pychain.Iter)[R]

### map_join(func, \*others)

Equivalent to flat_map, but allow to join other iterables.

However, it don’t take additional arguments for the function.

```python
>>> Iter(["a", "b"]).map_join(
...     lambda s: [c.upper() for c in s], ["c", "d", "e"]
... ).to_list()
['A', 'B', 'C', 'D', 'E']
```

* **Parameters:**
  * **func** (*Callable* *[* *[**Iterable* *[**T* *]* *]* *,* *Iterable* *[**R* *]* *]*)
  * **others** (*Iterable* *[**T* *]*)
* **Return type:**
  [Iter](#pychain.Iter)[R]

### map_juxt(\*funcs)

Apply several functions to each item.
Returns a new Iter where each item is a tuple of the results of applying each function to the original item.

```python
>>> Iter([1, -2, 3]).map_juxt(
...     lambda n: n % 2 == 0, lambda n: n > 0
... ).to_list()
[(False, True), (True, False), (False, True)]
```

* **Parameters:**
  **funcs** (*Callable* *[* *[**T* *]* *,* *object* *]*)
* **Return type:**
  [Iter](#pychain.Iter)[tuple[object, …]]

### map_star(func)

Applies a function to each element, where each element is an iterable.

Unlike .map(), which passes each element as a single argument, .starmap() unpacks each element into positional arguments for the function.

In short, for each element in the sequence, it computes func(\*element).

**Tip**: It is the perfect tool to process pairs generated by .product() or .zip_with().

```python
>>> def make_sku(color, size):
...     return f"{color}-{size}"
>>> Iter(["blue", "red"]).product(["S", "M"]).map_star(make_sku).to_list()
['blue-S', 'blue-M', 'red-S', 'red-M']
```

* **Parameters:**
  * **self** ([*Iter*](#pychain.Iter))
  * **func** (*Callable* *[* *[* *...* *]* *,* *R* *]*)
* **Return type:**
  [*Iter*](#pychain.Iter)

### most_common(n=None)

Return an iterable over the n most common elements and their counts from the most common to the least.
If n is None, then all elements are returned.

```python
>>> Iter([1, 1, 2, 3, 3, 3]).most_common(2).to_list()
[(3, 3), (1, 2)]
```

* **Parameters:**
  **n** (*int* *|* *None*)
* **Return type:**
  [Iter](#pychain.Iter)[tuple[T, int]]

### pairwise()

Return an iterator over pairs of consecutive elements.

```python
>>> Iter([1, 2, 3]).pairwise().to_list()
[(1, 2), (2, 3)]
```

* **Return type:**
  [Iter](#pychain.Iter)[tuple[T, T]]

### partition(n, pad=None)

Partition into tuples of length n, optionally padded.

```python
>>> Iter([1, 2, 3, 4]).partition(2).to_list()
[(1, 2), (3, 4)]
```

* **Parameters:**
  * **n** (*int*)
  * **pad** (*T* *|* *None*)
* **Return type:**
  [Iter](#pychain.Iter)[tuple[T, …]]

### partition_all(n)

Partition into tuples of length at most n.

```python
>>> Iter([1, 2, 3]).partition_all(2).to_list()
[(1, 2), (3,)]
```

* **Parameters:**
  **n** (*int*)
* **Return type:**
  [Iter](#pychain.Iter)[tuple[T, …]]

### permutations(r=None)

Return all permutations of length r.

```python
>>> Iter([1, 2, 3]).permutations(2).to_list()
[(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)]
```

* **Parameters:**
  **r** (*int* *|* *None*)
* **Return type:**
  [Iter](#pychain.Iter)[tuple[T, …]]

### pipe_into(func, \*args, \*\*kwargs)

Pipe the underlying data into a function, then wrap the result in the same wrapper type.

Each pychain class implement this method to allow chaining of functions that transform the
underlying data and return a new wrapped instance of the same subclass.

```python
>>> from pychain import Dict
>>> Dict({1: 2}).pipe_into(lambda d: {k: v + 1 for k, v in d.items()})
{1: 3}
```

Use this to keep the chainable API after applying a transformation to the data.

* **Parameters:**
  * **func** (*Callable* *[**Concatenate* *[**Iterable* *[**T* *]* *,* *P* *]* *,* *Iterable* *[**U* *]* *]*)
  * **args** (*P.args*)
  * **kwargs** (*P.kwargs*)
* **Return type:**
  [Iter](#pychain.Iter)[U]

### pluck(key)

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

### product(other)

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
  **other** (*Iterable* *[**U* *]*)
* **Return type:**
  [Iter](#pychain.Iter)[tuple[T, U]]

### reduce_by(key, binop)

Perform a simultaneous groupby and reduction
on the elements of the sequence.

```python
>>> Iter([1, 2, 3, 4]).reduce_by(
...     key=lambda x: x % 2, binop=lambda a, b: a + b
... ).to_list()
[1, 0]
```

* **Parameters:**
  * **key** (*Callable* *[* *[**T* *]* *,* *K* *]*)
  * **binop** (*Callable* *[* *[**T* *,* *T* *]* *,* *T* *]*)
* **Return type:**
  [Iter](#pychain.Iter)[K]

### repeat(n)

Repeat the entire iterable n times (as elements) and return Iter.

```python
>>> Iter([1, 2]).repeat(2).to_list()
[[1, 2], [1, 2]]
```

* **Parameters:**
  **n** (*int*)
* **Return type:**
  [Iter](#pychain.Iter)[Iterable[T]]

### repeat_last(default=None)

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
  [Iter](#pychain.Iter)[T | U]

### rolling(length)

A sequence of overlapping subsequences

```python
>>> Iter([1, 2, 3, 4]).rolling(2).to_list()
[(1, 2), (2, 3), (3, 4)]
```

This function creates a sliding window suitable for transformations like sliding means / smoothing

```python
>>> mean = lambda seq: float(sum(seq)) / len(seq)
>>> Iter([1, 2, 3, 4]).rolling(2).map(mean).to_list()
[1.5, 2.5, 3.5]
```

* **Parameters:**
  **length** (*int*)
* **Return type:**
  [Iter](#pychain.Iter)[tuple[T, …]]

### sort(key=None, reverse=False)

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
  * **key** (*Callable* *[* *[**U* *]* *,* *Any* *]*  *|* *None*)
  * **reverse** (*bool*)
* **Return type:**
  [*Iter*](#pychain.Iter)

### split_after(predicate, max_split=-1)

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
  * **predicate** (*Callable* *[* *[**T* *]* *,* *bool* *]*)
  * **max_split** (*int*)
* **Return type:**
  [Iter](#pychain.Iter)[list[T]]

### zip(\*others, strict=False)

Zip with other iterables, optionally strict, wrapped in Iter.

```python
>>> Iter([1, 2]).zip([10, 20]).to_list()
[(1, 10), (2, 20)]
```

* **Parameters:**
  * **others** (*Iterable* *[**Any* *]*)
  * **strict** (*bool*)
* **Return type:**
  [*Iter*](#pychain.Iter)[tuple[*Any*, …]]

### zip_broadcast(\*others, scalar_types=(<class 'str'>, <class 'bytes'>), strict=False)

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
  * **others** (*Iterable* *[**T* *]*)
  * **scalar_types** (*tuple* *[**type* *,* *type* *]*  *|* *None*)
  * **strict** (*bool*)
* **Return type:**
  [Iter](#pychain.Iter)[tuple[T, …]]

### zip_equal(\*others)

* **Parameters:**
  **others** (*Iterable* *[**Any* *]*)

### zip_longest(\*others, fill_value=None)

Zip with other iterables, filling missing values.

```python
>>> Iter([1, 2]).zip_longest([10], fill_value=0).to_list()
[(1, 10), (2, 0)]
```

* **Parameters:**
  * **others** (*Iterable* *[**T* *]*)
  * **fill_value** (*U*)
* **Return type:**
  [Iter](#pychain.Iter)[tuple[U | T, …]]

### zip_offset(\*others, offsets, longest=False, fillvalue=None)

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
  * **others** (*Iterable* *[**T* *]*)
  * **offsets** (*list* *[**int* *]*)
  * **longest** (*bool*)
  * **fillvalue** (*U*)
* **Return type:**
  [Iter](#pychain.Iter)[tuple[T | U, …]]

## *class* pychain.Array(data)

Wrapper for numpy arrays and similar objects.
This is a simple class but that allows to use the same API as the other wrappers.
It is mainly useful to chain operations on numpy arrays.

* **Parameters:**
  **data** (*T*)

### pipe_into(func, \*args, \*\*kwargs)

Pipe the underlying data into a function, then wrap the result in the same wrapper type.

Each pychain class implement this method to allow chaining of functions that transform the
underlying data and return a new wrapped instance of the same subclass.

```python
>>> from pychain import Dict
>>> Dict({1: 2}).pipe_into(lambda d: {k: v + 1 for k, v in d.items()})
{1: 3}
```

Use this to keep the chainable API after applying a transformation to the data.

* **Parameters:**
  * **func** (*Callable* *[* *[**Concatenate* *[**T* *,* *P* *]* *]* *,* *U* *]*)
  * **args** (*P*)
  * **kwargs** (*P*)
* **Return type:**
  [*Array*](#pychain.Array)

### to_iter()

Convert the wrapped array to an Iter wrapper.

```python
>>> import numpy as np
>>> import pychain as pc
>>>
>>> data = np.array([1, 2, 3])
>>>
>>> pc.Array(data).to_iter().to_list()
[np.int64(1), np.int64(2), np.int64(3)]
```

* **Return type:**
  [Iter](#pychain.Iter)[T]

## pychain.iter_count(start=0, step=1)

Create an infinite iterator of evenly spaced values.

**Warning** ⚠️

This creates an infinite iterator.

Be sure to use Iter.head() or Iter.slice() to limit the number of items taken.

```python
>>> iter_count(10, 2).head(3).to_list()
[10, 12, 14]
```

* **Parameters:**
  * **start** (*int*)
  * **step** (*int*)
* **Return type:**
  [*Iter*](#pychain.Iter)[int]

## pychain.iter_func(func, x)

Create an infinite iterator by repeatedly applying a function into an original input x.

**Warning** ⚠️

This creates an infinite iterator.

Be sure to use Iter.head() or Iter.slice() to limit the number of items taken.

```python
>>> iter_func(lambda x: x + 1, 0).head(3).to_list()
[0, 1, 2]
```

* **Parameters:**
  * **func** (*Callable* *[* *[**T* *]* *,* *T* *]*)
  * **x** (*T*)
* **Return type:**
  [*Iter*](#pychain.Iter)

## pychain.iter_range(start, stop, step=1)

Create an iterator from a range.

Syntactic sugar for Iter(range(start, stop, step)).

```python
>>> iter_range(1, 5).to_list()
[1, 2, 3, 4]
```

* **Parameters:**
  * **start** (*int*)
  * **stop** (*int*)
  * **step** (*int*)
* **Return type:**
  [*Iter*](#pychain.Iter)[int]
