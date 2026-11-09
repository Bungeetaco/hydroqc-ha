"""Custon cache module."""

import functools
from collections.abc import Callable
from typing import ParamSpec, TypeVar, cast

from aiocache import Cache, cached  # type: ignore

T = TypeVar("T")
P = ParamSpec("P")


class CCached(cached):  # type: ignore[misc]
    """Custom cache class based on aiocache.

    This decorator respects the enable_cache attribute on the instance
    (self) if it exists, allowing caching to be toggled at runtime.
    """

    def __init__(self, ttl: int) -> None:
        """Initialize custom cache decorator.

        Args:
            ttl: Time to live for cached values in seconds.

        """
        cached.__init__(self, ttl=ttl, cache=Cache.MEMORY)
        self.ttl = ttl

    def __call__(self, func: Callable[P, T]) -> Callable[P, T]:
        """Call custom cache decorator."""
        self.cache = self._cache()

        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Check if the first argument (self) has enable_cache attribute
            # If caching is disabled, call the function directly
            if args and hasattr(args[0], "enable_cache") and not args[0].enable_cache:
                result = func(*args, **kwargs)
                # func is async, so we need to await it
                if hasattr(result, "__await__"):
                    return await result  # type: ignore[no-any-return]
                return result  # pragma: no cover

            # Otherwise use the cached decorator
            value = await self.decorator(func, *args, **kwargs)
            return cast(T, value)

        wrapper.cache = self.cache  # type: ignore[attr-defined]
        return cast(Callable[P, T], wrapper)
