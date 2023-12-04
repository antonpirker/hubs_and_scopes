from client import Client, NoopClient
from scope import Scope
import globals


def init(*args, **kwargs):
    client = Client(*args, **kwargs)
    Scope.get_global_scope().set_client(client)


def sentry_is_initialized():
    client = Client.get_client()
    if type(client) == NoopClient:
        return False
    else:
        return True


def get_client():
    return Client.get_client()


def get_current_scope():
    return Scope.get_current_scope()


def get_isolation_scope():
    return Scope.get_isolation_scope()


def get_global_scope():
    return Scope.get_global_scope()


def set_current_scope(scope):
    globals.sentry_current_scope.set(scope)


def set_isolation_scope(isolation_scope):
    globals.sentry_isolation_scope.set(isolation_scope)


def capture_event(event, additional_data=None):
    scope = Scope.get_current_scope()
    return scope.capture_event(event, additional_data)


def set_tag(key, value):
    return Scope.get_isolation_scope().set_tag(key, value)
