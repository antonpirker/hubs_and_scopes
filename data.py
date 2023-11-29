from contextvars import ContextVar

# global scope over everything
GLOBAL_SCOPE = None

# created by integrations (where we clone the Hub now)
sentry_isolation_scope = ContextVar("sentry_isolation_scope", default=None)

# cloned for threads/tasks/...
sentry_current_scope = ContextVar("sentry_current_scope", default=None)
