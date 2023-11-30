import copy
from contextlib import contextmanager
from contextvars import copy_context  # This does not exist in Python 2.7
from functools import wraps

import globals
from globals import sentry_current_scope, sentry_isolation_scope


# TODO: check otel impl
def copy_on_write(property_name):
    """
    Decorator that implements copy on write on a property of a class.
    """
    # Stuff that write on scope right now:
    # - Hub.configure_scope writes the propagation context to the scope (if not existing on scope)
    # - Hub.start_session writes the session to the scope 
    # - Hub.end_session changes data on the scope
    # - Hub.stop_auto_session_tracking changes data on the scope
    # - Hub.resume_auto_session_tracking changes data on the scope
    #
    # - Scope.set_new_propagation_context set self._propagation_context  # type: Optional[Dict[str, Any]]
    # - Scope.generate_propagation_context set self._propagation_context  # type: Optional[Dict[str, Any]]
    # - Scope.get_dynamic_sampling_context set self._dynamic_sampling_context  # type: Optional[Dict[str, Any]]
    # - Scope.clear reset all local vars
    # - Scope.level (_attr_setter) sets self._level  # type: int
    # - Scope.set_level sets self._level  # type: int
    # - Scope.fingerprint (_attr_setter) sets self._fingerprint  # type: Optional[List[str]]
    #( - Scope.transaction sets self._span.containing_transaction  # type: Optional[Span]) because changes span, not scope per se
    # - Scope.set_transaction_name sets self._transaction  # type: Optional[str] and self._span.containing_transaction.name (and self._span.containing_transaction.source)
    # - Scope.user (_attr_setter) sets self._user  # type: Optional[User]
    # - Scope.set_user sets self._user  # type: Optional[User] and updates self._session
    # - Scope.span (@span.setter) sets self._span  # type: Optional[Span]
    # - Scope.profile (@profile.setter) sets self._profile  # type: Optional[Profile]
    # - Scope.set_tag sets self._tags  # type: Dict[str, str]
    # - Scope.remove_tag pops from self._tags  # type: Dict[str, str]
    # - Scope.set_context sets self._contexts  # type: Dict[str, Any]
    # - Scope.remove_context pops from self._contexts  # type: Dict[str, Any]
    # - Scope.set_extra sets self._extra  # type: Dict[str, Any]
    # - Scope.remove_extra pops from self._extra  # type: Dict[str, Any]
    # - Scope.clear_breadcrumbs sets self._breadcrumbs  # type: Deque[Breadcrumb]
    # - Scope.add_attachment appends to self._attachments  # type: List[Attachment]
    # - Scope.add_event_processor appends to self._event_processors  # type: List[EventProcessor]
    # - Scope.add_error_processor appends to self._error_processors  # type: List[ErrorProcessor]
    # - Scope.update_from_scope updates local vars from other given scope
    # - Scope.update_from_kwargs updates local vars from given kwargs

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self = args[0]

            same_property_different_scope = (
                self.is_forked and
                id(getattr(self, property_name)) == id(getattr(self.original_scope, property_name))
            )
            if same_property_different_scope:
                setattr(self, property_name, copy.deepcopy(getattr(self.original_scope, property_name)))

            return func(*args, **kwargs)

        return wrapper

    return decorator


class Scope:
    def __init__(self, ty=None, client=None):
        self._ty = ty  # this is just for debugging, not used in actual implementation
        self._tags = {}
        self.original_scope = None

        self.set_client(client)

    def __repr__(self):
        return "<{} id={} ty={}>".format(self.__class__.__name__, id(self), self._ty)
    
    @classmethod    
    def get_current_scope(cls):
        scope = sentry_current_scope.get()
        if scope is None:
            scope = Scope(ty='current')
            sentry_current_scope.set(scope)

        return scope

    @classmethod    
    def get_isolation_scope(cls):
        scope = sentry_isolation_scope.get()
        if scope is None:
            scope = Scope(ty='isolation')
            sentry_isolation_scope.set(scope)

        return scope

    @classmethod    
    def get_global_scope(cls):
        scope = globals.SENTRY_GLOBAL_SCOPE
        if scope is None:
            scope = Scope(ty='global')
            globals.SENTRY_GLOBAL_SCOPE = scope

        return scope
        
    @property
    def is_forked(self):
        return self.original_scope is not None
    
    def fork(self):
        self.original_scope = self
        return copy.copy(self)
    
    def isolate(self):
        # fork isolation scope
        isolation_scope = Scope.get_isolation_scope()
        forked_isolation_scope = isolation_scope.fork()
        sentry_isolation_scope.set(forked_isolation_scope)

    def set_client(self, client):
        self.client = client

    @copy_on_write("_tags")
    def set_tag(self, key, value):
        self._tags[key] = value
  
    def get_tags(self):
        return self._tags

    def get_scope_data(self):
        scope_data = {}

        if self._tags:
            scope_data["tags"] = self._tags

        return scope_data

    def merge_scope_data(self, data, additional_data=None):
        """Merges `additional_data` into `data`."""
        if additional_data is None:
            return data
        
        for key, val in additional_data.items(): 
            if key in data:
                data[key].update(val)
            else:
                data[key] = val
    
    def get_merged_scope_data(self, additional_data=None):
        """
        Merge all scope data into a single dict.
        
        Note: This should always be called from the current scope. 
        When calling this from isolation or global scope, 
        the values from the current scope will not be used.
        """
        data = copy.deepcopy(Scope.get_global_scope().get_scope_data())
        self.merge_scope_data(data, Scope.get_isolation_scope().get_scope_data())
        self.merge_scope_data(data, self.get_scope_data())

        if isinstance(additional_data, Scope):
            self.merge_scope_data(data, additional_data.get_scope_data())
        elif isinstance(additional_data, dict):
            self.merge_scope_data(data, additional_data)

        return data

    def capture_event(self, event, aditional_data=None):
        data = self.get_merged_scope_data(additional_data=aditional_data)

        event_payload = event
        event_payload.update(data)

        print("Captured event {}".format(event_payload))

        return event_payload
 

def with_new_scope(*args, **kwargs):
    # fork current scope
    current_scope = Scope.get_current_scope()
    forked_scope = current_scope.fork()
    token = sentry_current_scope.set(forked_scope)

    try:
        yield forked_scope
    
    finally:
        # restore original scope
        sentry_current_scope.reset(token)       


@contextmanager
def new_scope(*args, **kwargs):
    ctx = copy_context()  # This does not exist in Python 2.7
    return ctx.run(with_new_scope, *args, **kwargs)


def with_isolated_scope(*args, **kwargs):
    # fork current scope
    current_scope = Scope.get_current_scope()
    forked_current_scope = current_scope.fork()
    current_token = sentry_current_scope.set(forked_current_scope)

    # fork isolation scope
    isolation_scope = Scope.get_isolation_scope()
    forked_isolation_scope = isolation_scope.fork()
    isolation_token = sentry_isolation_scope.set(forked_isolation_scope)

    try:
        yield forked_isolation_scope
    
    finally:
        # restore original scopes
        sentry_current_scope.reset(current_token)
        sentry_isolation_scope.reset(isolation_token)       


@contextmanager
def isolated_scope(*args, **kwargs):
    ctx = copy_context()
    return ctx.run(with_isolated_scope, *args, **kwargs)
