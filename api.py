from client import Client, NoopClient
from scope import Scope


def init():
    Scope.get_global_scope().set_client(Client())


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


def capture_event(event, additional_data=None):
    scope = Scope.get_current_scope()
    print(f"Capture event scope: {scope}")
    return scope.capture_event(event, additional_data)