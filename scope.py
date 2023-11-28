import copy
from functools import wraps

import data
from data import sentry_current_scope, sentry_isolation_scope


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
            current_scope = sentry_current_scope.get()

            print(f"copy on write decorator: {self} / {current_scope}")
            same_property_different_scope = (
                id(self) != id(current_scope) and 
                id(getattr(self, property_name)) == id(getattr(current_scope, property_name))
            )
            if same_property_different_scope:
                # Probably a deep copy is better, because some attributes reference non-primitive types. (Breadcrumbs, Attachments, EventProcessor, ErrorProcessor)
                # see big comment above.
                setattr(self, property_name, copy.deepcopy(getattr(current_scope, property_name)))

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
        return copy.copy(self)

    def capture_event(self, event, aditional_data=None):
        data = {}
        data.update(Scope.get_global_scope().get_scope_data())
        data.update(Scope.get_isolation_scope().get_scope_data())
        data.update(self.get_scope_data())
        data.update(aditional_data or {})
        
        print(f"Captured event {event} / data: {data}")
 
    def get_tags(self):
        return self._tags

    def get_scope_data(self):
        return self._tags

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
        scope = data.GLOBAL_SCOPE
        if scope is None:
            scope = Scope(ty='global')
            data.GLOBAL_SCOPE = scope

        return scope


class new_scope:
    def __enter__(self):
        current_scope = Scope.get_current_scope()
        forked_scope = current_scope.fork()

        self.token = sentry_current_scope.set(forked_scope)

        return forked_scope

    def __exit__(self, exc_type, exc_value, tb):
        sentry_current_scope.reset(self.token)


class isolated_scope:
    def __enter__(self):
        current_isolation_scope = Scope.get_isolation_scope()
        forked_isolation_scope = current_isolation_scope.fork()

        self.token = sentry_isolation_scope.set(forked_isolation_scope)

        return forked_isolation_scope

    def __exit__(self, exc_type, exc_value, tb):
        sentry_isolation_scope.reset(self.token)
