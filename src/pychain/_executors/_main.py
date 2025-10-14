from ._filters import BaseFilter
from ._process import BaseProcess


class BaseExecutor[T](BaseFilter[T], BaseProcess[T]):
    pass
