from __future__ import annotations

from ._aggregations import BaseAgg
from ._booleans import BaseBool
from ._filters import BaseFilter
from ._lists import BaseList
from ._maps import BaseMap
from ._process import BaseProcess
from ._rolling import BaseRolling
from ._tuples import BaseTuples


class Executor[T](
    BaseAgg[T],
    BaseBool[T],
    BaseFilter[T],
    BaseProcess[T],
    BaseMap[T],
    BaseRolling[T],
    BaseList[T],
    BaseTuples[T],
):
    pass
