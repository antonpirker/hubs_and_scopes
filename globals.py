import random

try:
    from contextvars import ContextVar
except ImportError:
    from threading import local

    class ContextVar(object):
        # Super-limited impl of ContextVar

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
            # type: (Any) -> None
            token = str(random.getrandbits(64))
            original_value = self.get()
            setattr(self._original_local, token, original_value)
            setattr(self._local, "value", value)
            return token

        def reset(self, token):
            # type: (Any) -> None
            setattr(self._local, "value", getattr(self._original_local, token))
            setattr(self._original_local, token, None)


# Constant that's True when type checking, but False here.
TYPE_CHECKING = False

# global scope over everything
SENTRY_GLOBAL_SCOPE = None

# created by integrations (where we clone the Hub now)
sentry_isolation_scope = ContextVar("sentry_isolation_scope", default=None)

# cloned for threads/tasks/...
sentry_current_scope = ContextVar("sentry_current_scope", default=None)
