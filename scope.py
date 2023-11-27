from copy import copy
from functools import wraps

import data
from data import sentry_current_scope, sentry_isolation_scope


# TODO: check otel impl
def copy_on_write(property_name):
    """
    Decorator that implements copy on write on a property of a class.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self = args[0]
            current_scope = sentry_current_scope.get(None)

            same_property_different_scope = (
                id(self) != id(current_scope) and 
                id(getattr(self, property_name)) == id(getattr(current_scope, property_name))
            )
            if same_property_different_scope:
                # TODO: need to check if shallow copy is ok here. (Check all writable attributes in Scope class)
                setattr(self, property_name, copy(getattr(self, property_name)))

            return func(*args, **kwargs)

        return wrapper

    return decorator


class Scope:
    def __init__(self, ty, client=None):
        self._ty = ty  # this is just for debugging, not used in actual implementation
        self._tags = {}
        self.set_client(client or data.GLOBAL_SCOPE and data.GLOBAL_SCOPE.client or None)

    def __repr__(self):
        return f"<{self.__class__.__name__} id={id(self)} ty={self._ty}>"
    
    def set_client(self, client):
        self.client = client

    @copy_on_write("_tags")
    def set_tag(self, key, value):
        self._tags[key] = value

    def fork(self):
        return copy(self)

    def capture_event(self, event, aditional_data=None):
        data = Scope.get_global_scope().get_scope_data()
        data.update(Scope.get_isolation_scope.get_scope_data())
        data.update(Scope.get_current_scope().get_scope_data())
        data.update(aditional_data or {})
        
        print(f"Captured {event} / data: {data}")
 
    def get_tags(self):
        return self._tags

    def get_scope_data(self):
        return self._tags

    @classmethod    
    def get_current_scope(cls):
        scope = sentry_current_scope.get(None)
        if scope is None:
            scope = Scope(ty='current')
            sentry_current_scope.set(scope)

        return scope

    @classmethod    
    def get_isolation_scope(cls):
        scope = sentry_isolation_scope.get(None)
        if scope is None:
            scope = Scope(ty='isolation')
            sentry_isolation_scope.set(scope)

        return scope

    @classmethod    
    def get_global_scope(cls):
        scope = data.GLOBAL_SCOPE
        if scope is None:
            scope = Scope(ty='global')
            data.GLOBAL_SCOPE = scope

        return scope


class new_scope:
    def __enter__(self):
        current_scope = Scope.get_current_scope()
        forked_scope = current_scope.fork()

        return forked_scope

    def __exit__(self, exc_type, exc_value, tb):
        ...