import inspect
import abc
from typing import Any, Callable

from functools import wraps

class Decorator(object):
    func: Callable

    def __call__(self, func) -> callable:
        self.__dict__["func"] = func

        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def awrap(*args, **kwargs):
                return await self.awrapper(*args, **kwargs)
            return awrap
        else:
            @wraps(func)
            def wrap(*args, **kwargs):
                return self.wrapper(*args, **kwargs)
            return wrap

    @abc.abstractmethod
    def wrapper(self, *args, **kwargs):
        raise NotImplementedError()

    @abc.abstractmethod
    def awrapper(self, *args, **kwargs):
        raise NotImplementedError()