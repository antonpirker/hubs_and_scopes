import random

# Constant that's True when type checking, but False here.
TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Any, Optional, Tuple
    import sentry_sdk


def _get_contextvars():
    # type: () -> Tuple[Any, Any]
    """
    If context vars are available, use them. Otherwise, fall back to our own implementation.
    """
    try:
        from contextvars import ContextVar  # This does not exist in Python 2.7
        from contextvars import copy_context  # This does not exist in Python 2.7

        return ContextVar, copy_context

    except ImportError:
        from threading import local

        class ContextVar(object):
            # Super-limited implementation of ContextVar

            def __init__(self, name, default=None):
                # type: (str, Any) -> None
                self._name = name
                self._default = default
                self._local = local()
                self._original_local = local()

            def get(self, default=None):
                # type: (Any) -> Any
                return getattr(self._local, "value", default or self._default)

            def set(self, value):
                # type: (Any) -> Any
                token = str(random.getrandbits(64))
                original_value = self.get()
                setattr(self._original_local, token, original_value)
                setattr(self._local, "value", value)
                return token

            def reset(self, token):
                # type: (Any) -> None
                setattr(self._local, "value", getattr(self._original_local, token))
                setattr(self._original_local, token, None)

        class NoOpContext:
            def run(self, func, *args, **kwargs):
                return func(*args, **kwargs)

        def copy_context():
            # type: () -> NoOpContext
            return NoOpContext()

        return ContextVar, copy_context


ContextVar, copy_context = _get_contextvars()

# global scope over everything
SENTRY_GLOBAL_SCOPE = None  # type: Optional[sentry_sdk.Scope]

# created by integrations (where we clone the Hub now)
sentry_isolation_scope = ContextVar("sentry_isolation_scope", default=None)

# cloned for threads/tasks/...
sentry_current_scope = ContextVar("sentry_current_scope", default=None)
