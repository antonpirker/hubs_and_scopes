from scope import Scope
from globals import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Optional


class NoopClient:
    def __repr__(self):
        return "<{} id={}>".format(self.__class__.__name__, id(self))

    def get_integration(name_or_class):
        return None

    def should_send_default_pii():
        return False

    def __init__(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        return None

    def __getstate__(self, *args, **kwargs):
        # type: (*Any, **Any) -> Any
        return {"options": {}}

    def __setstate__(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        pass

    def _setup_instrumentation(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        return None

    def _init_impl(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        return None

    @property
    def dsn(self):
        # type: () -> Optional[str]
        """Returns the configured DSN as string."""
        return None

    def _prepare_event(self, *args, **kwargs):
        # type: (*Any, **Any) -> Optional[Any]
        return None

    def _is_ignored_error(self, *args, **kwargs):
        # type: (*Any, **Any) -> bool
        return True

    def _should_capture(self, *args, **kwargs):
        # type: (*Any, **Any) -> bool
        return False

    def _should_sample_error(self, *args, **kwargs):
        # type: (*Any, **Any) -> bool
        return False

    def _update_session_from_event(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        return False

    def capture_event(self, *args, **kwargs):
        # type: (*Any, **Any) -> Optional[str]
        return None

    def capture_session(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        return None

    def get_integration(self, *args, **kwargs):
        # type: (*Any, **Any) -> Any
        return None

    def close(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        return None

    def flush(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        return None

    def __enter__(self):
        # type: () -> NoopClient
        return self

    def __exit__(self, exc_type, exc_value, tb):
        # type: (Any, Any, Any) -> None
        return None


class Client(NoopClient):
    def __repr__(self):
        return "<{} id={}>".format(self.__class__.__name__, id(self))

    @classmethod
    def get_client(cls):
        client = Scope.get_current_scope().client
        if client is not None:
            return client

        client = Scope.get_isolation_scope().client
        if client is not None:
            return client

        client = Scope.get_global_scope().client
        if client is not None:
            return client

        return NoopClient()
