# in real sentry: 
#from sentry_sdk.utils import ContextVar
# in here it is this: 
from contextvars import ContextVar

# useless. can be just in the sentry_global_scope context var
sentry_global_client = ContextVar("sentry_global_client")

sentry_current_scope = ContextVar("sentry_current_scope")
sentry_isolation_scope = ContextVar("sentry_isolation_scope")
sentry_global_scope = ContextVar("sentry_global_scope")