from __future__ import annotations

from ._filters import BaseFilter
from ._lists import BaseList
from ._maps import BaseMap
from ._process import BaseProcess
from ._rolling import BaseRolling


class BaseExecutor[T](
    BaseFilter[T], BaseProcess[T], BaseMap[T], BaseRolling[T], BaseList[T]
):
    pass
