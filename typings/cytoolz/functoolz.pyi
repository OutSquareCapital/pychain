"""
functoolz
========

- apply : Applies a function and returns the results
- complement : Convert a predicate function to its logical complement.
- compose : Compose functions to operate in series.
- compose_left : Compose functions to operate in series.
- curry : Curry a callable function
- do : Runs func on x, returns x
- excepts : A wrapper around a function to catch exceptions and dispatch to a handler.
- flip : Call the function call with the arguments flipped
- identity : Identity function.
- juxt : Creates a function that calls several functions with the same arguments
- memoize : Cache a function's result for speedy future evaluation
- pipe : Pipe a value through a sequence of functions
- thread_first : Thread value through a sequence of functions/forms
- thread_last : Thread value through a sequence of functions/forms
"""

from typing import Any
from collections.abc import Callable, MutableMapping

def apply[T](func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """Applies a function and returns the results

    >>> def double(x):
    ...     return 2 * x
    >>> def inc(x):
    ...     return x + 1
    >>> apply(double, 5)
    10

    >>> tuple(map(apply, [double, inc, double], [10, 500, 8000]))
    (20, 501, 16000)
    """
    ...

def complement(func: Callable[..., bool]) -> Callable[..., bool]:
    """Convert a predicate function to its logical complement.

    In other words, return a function that, for inputs that normally
    yield True, yields False, and vice-versa.

    >>> def iseven(n):
    ...     return n % 2 == 0
    >>> isodd = complement(iseven)
    >>> iseven(2)
    True
    >>> isodd(2)
    False
    """
    ...

def compose(*funcs: Callable[..., Any]) -> Callable[..., Any]:
    """Compose functions to operate in series.

    Returns a function that applies other functions in sequence.

    Functions are applied from right to left so that
    ``compose(f, g, h)(x, y)`` is the same as ``f(g(h(x, y)))``.

    If no arguments are provided, the identity function (f(x) = x) is returned.

    >>> inc = lambda i: i + 1
    >>> compose(str, inc)(3)
    '4'

    See Also:
        compose_left
        pipe
    """
    ...

def compose_left(*funcs: Callable[..., Any]) -> Callable[..., Any]:
    """Compose functions to operate in series.

    Returns a function that applies other functions in sequence.

    Functions are applied from left to right so that
    ``compose_left(f, g, h)(x, y)`` is the same as ``h(g(f(x, y)))``.

    If no arguments are provided, the identity function (f(x) = x) is returned.

    >>> inc = lambda i: i + 1
    >>> compose_left(inc, str)(3)
    '4'

    See Also:
        compose
        pipe
    """
    ...

class curry:
    """Curry a callable function

    Enables partial application of arguments through calling a function with an
    incomplete set of arguments.

    >>> def mul(x, y):
    ...     return x * y
    >>> mul = curry(mul)

    >>> double = mul(2)
    >>> double(10)
    20

    Also supports keyword arguments

    >>> @curry  # Can use curry as a decorator
    ... def f(x, y, a=10):
    ...     return a * (x + y)

    >>> add = f(a=1)
    >>> add(2, 3)
    5

    See Also:
        toolz.curried - namespace of curried functions
                        https://toolz.readthedocs.io/en/latest/curry.html
    """
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...

def do[T](func: Callable[[T], Any], x: T) -> T:
    """Runs ``func`` on ``x``, returns ``x``

    Because the results of ``func`` are not returned, only the side
    effects of ``func`` are relevant.

    Logging functions can be made by composing ``do`` with a storage function
    like ``list.append`` or ``file.write``

    >>> from toolz import compose
    >>> from toolz.curried import do

    >>> log = []
    >>> inc = lambda x: x + 1
    >>> inc = compose(inc, do(log.append))
    >>> inc(1)
    2
    >>> inc(11)
    12
    >>> log
    [1, 11]
    """
    ...

class excepts(Exception):
    """A wrapper around a function to catch exceptions and
    dispatch to a handler.

    This is like a functional try/except block, in the same way that
    ifexprs are functional if/else blocks.

    Examples
    --------
    >>> excepting = excepts(
    ...     ValueError,
    ...     lambda a: [1, 2].index(a),
    ...     lambda _: -1,
    ... )
    >>> excepting(1)
    0
    >>> excepting(3)
    -1

    Multiple exceptions and default except clause.

    >>> excepting = excepts((IndexError, KeyError), lambda a: a[0])
    >>> excepting([])
    >>> excepting([1])
    1
    >>> excepting({})
    >>> excepting({0: 1})
    1
    """
    def __init__(
        self,
        exc: type | tuple[type, ...],
        func: Callable[..., Any],
        handler: Callable[[Exception], Any] = ...,
    ) -> None: ...

def flip[T](func: Callable[..., T], a: Any, b: Any) -> T:
    """Call the function call with the arguments flipped

    This function is curried.

    >>> def div(a, b):
    ...     return a // b
    >>> flip(div, 2, 6)
    3
    >>> div_by_two = flip(div, 2)
    >>> div_by_two(4)
    2

    This is particularly useful for built in functions and functions defined
    in C extensions that accept positional only arguments. For example:
    isinstance, issubclass.

    >>> data = [1, "a", "b", 2, 1.5, object(), 3]
    >>> only_ints = list(filter(flip(isinstance, int), data))
    >>> only_ints
    [1, 2, 3]
    """
    ...

def identity[T](x: T) -> T:
    """
    Identity function. Return x

    >>> identity(3)
    3
    """
    ...

class juxt:
    """Creates a function that calls several functions with the same arguments

    Takes several functions and returns a function that applies its arguments
    to each of those functions then returns a tuple of the results.

    Name comes from juxtaposition: the fact of two things being seen or placed
    close together with contrasting effect.

    >>> inc = lambda x: x + 1
    >>> double = lambda x: x * 2
    >>> juxt(inc, double)(10)
    (11, 20)
    >>> juxt([inc, double])(10)
    (11, 20)
    """
    def __init__(self, *funcs: Callable[..., Any]) -> None: ...
    def __call__(self, *args: Any, **kwargs: Any) -> tuple[Any, ...]: ...

def memoize[T](
    func: Callable[..., T],
    cache: MutableMapping[Any, Any] | None = ...,
    key: Callable[..., Any] | None = ...,
) -> Callable[..., T]:
    """Cache a function's result for speedy future evaluation

    Considerations:
        Trades memory for speed.
        Only use on pure functions.

    >>> def add(x, y):
    ...     return x + y
    >>> add = memoize(add)

    Or use as a decorator

    >>> @memoize
    ... def add(x, y):
    ...     return x + y

    Use the ``cache`` keyword to provide a dict-like object as an initial cache

    >>> @memoize(cache={(1, 2): 3})
    ... def add(x, y):
    ...     return x + y

    Note that the above works as a decorator because ``memoize`` is curried.

    It is also possible to provide a ``key(args, kwargs)`` function that
    calculates keys used for the cache, which receives an ``args`` tuple and
    ``kwargs`` dict as input, and must return a hashable value.  However,
    the default key function should be sufficient most of the time.

    >>> # Use key function that ignores extraneous keyword arguments
    >>> @memoize(key=lambda args, kwargs: args)
    ... def add(x, y, verbose=False):
    ...     if verbose:
    ...         print("Calculating %s + %s" % (x, y))
    ...     return x + y
    """
    ...

def pipe(data: Any, *funcs: Callable[..., Any]) -> Any:
    """Pipe a value through a sequence of functions

    I.e. ``pipe(data, f, g, h)`` is equivalent to ``h(g(f(data)))``

    We think of the value as progressing through a pipe of several
    transformations, much like pipes in UNIX

    ``$ cat data | f | g | h``

    >>> double = lambda i: 2 * i
    >>> pipe(3, double, str)
    '6'

    See Also:
        compose
        compose_left
        thread_first
        thread_last
    """
    ...

def thread_first[T, T1](
    val: T, *forms: Callable[[T], T1] | tuple[Callable[..., T1], Any]
) -> T1:
    """Thread value through a sequence of functions/forms

    >>> def double(x):
    ...     return 2 * x
    >>> def inc(x):
    ...     return x + 1
    >>> thread_first(1, inc, double)
    4

    If the function expects more than one input you can specify those inputs
    in a tuple.  The value is used as the first input.

    >>> def add(x, y):
    ...     return x + y
    >>> def pow(x, y):
    ...     return x**y
    >>> thread_first(1, (add, 4), (pow, 2))  # pow(add(1, 4), 2)
    25

    So in general
        thread_first(x, f, (g, y, z))
    expands to
        g(f(x), y, z)

    See Also:
        thread_last
    """
    ...

def thread_last[T, T1](
    val: T, *forms: Callable[[T], T1] | tuple[Callable[..., T1], Any]
) -> T1:
    """Thread value through a sequence of functions/forms

    >>> def double(x):
    ...     return 2 * x
    >>> def inc(x):
    ...     return x + 1
    >>> thread_last(1, inc, double)
    4

    If the function expects more than one input you can specify those inputs
    in a tuple.  The value is used as the last input.

    >>> def add(x, y):
    ...     return x + y
    >>> def pow(x, y):
    ...     return x**y
    >>> thread_last(1, (add, 4), (pow, 2))  # pow(2, add(4, 1))
    32

    So in general
        thread_last(x, f, (g, y, z))
    expands to
        g(y, z, f(x))

    >>> def iseven(x):
    ...     return x % 2 == 0
    >>> list(thread_last([1, 2, 3], (map, inc), (filter, iseven)))
    [2, 4]

    See Also:
        thread_first
    """
    ...
