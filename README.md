# pychain

pychain is a project aimed at introducing a more declarative way of using Python, leveraging cytoolz and toolz functions.

## Installation

````None
uv add git+https://github.com/OutSquareCapital/pychain.git
````

## Example

````python
from dataclasses import dataclass

import pychain as pc


@dataclass(slots=True, frozen=True)
class ObjectExample:
    value: int
    foo: str = "bar"

def summed() -> list[float]:
    values_list: list[float] = [
        ObjectExample(value=i, foo="baz").value for i in range(1, 10)
    ]
    result: float = round(number=sum(values_list) / 1000, ndigits=3)
    return [result for _ in range(1, 10)]


def summed_chained():
    return (
        pc.from_range(1, 10)
        .map(lambda i: ObjectExample(value=i, foo="baz").value)
        .agg(sum)
        .into(lambda x: round(number=x / 1000, ndigits=3))
        .into_iter(9)
        .convert_to.list()
    )


def cumsum() -> list[int]:
    values_list: list[int] = [
        ObjectExample(value=i, foo="baz").value for i in range(1, 10)
    ]
    res: int = 0
    new_list: list[int] = []
    for i in values_list:
        res += i
        new_list.append(res)

    return new_list


def cumsum_pychain():
    return (
        pc.from_range(1, 10)
        .map(lambda i: ObjectExample(value=i, foo="baz").value)
        .cumsum()
        .convert_to.list()
    )


def check() -> None:
    assert summed() == summed_chained()
    assert cumsum() == cumsum_pychain()


check()
````
