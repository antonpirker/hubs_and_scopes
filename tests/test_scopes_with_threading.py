import threading

import pytest

import sentry_sdk


class MyThread(threading.Thread):
    def __init__(
        self,
        custom_current_scope=None,
        custom_isolation_scope=None,
        set_current_scope=None,
    ):
        threading.Thread.__init__(self)
        self.custom_current_scope = custom_current_scope
        self.custom_isolation_scope = custom_isolation_scope
        self.set_current_scope = set_current_scope

    def _run(self):
        if self.set_current_scope:
            if self.custom_current_scope is not None:
                sentry_sdk.set_current_scope(self.custom_current_scope)

            if self.custom_isolation_scope is not None:
                sentry_sdk.set_isolation_scope(self.custom_isolation_scope)

        self.custom_current_scope.set_tag("tag2", "mythread_custom_value")
        event_payload = sentry_sdk.capture_event({"name": "mythread_event"})

        if self.set_current_scope:
            if (
                self.custom_current_scope is not None
                and self.custom_isolation_scope is None
            ):
                assert event_payload["tags"] == {"tag2": "mythread_custom_value"}
            elif (
                self.custom_current_scope is not None
                and self.custom_isolation_scope is not None
            ):
                assert event_payload["tags"] == {
                    "tag1": "main_thread_isolated_value",
                    "tag2": "mythread_custom_value",
                }
        else:
            # The `custom_scope` is not the current scope, so the tags on it will not be captured
            # The tags from the isolation scope are also not present, because we also do not know about it.
            assert "tags" not in event_payload

    def run(self):
        self.exc = None
        try:
            self._run()
        except BaseException as e:
            self.exc = e

    def join(self):
        super(MyThread, self).join()
        if self.exc:
            raise self.exc


@pytest.mark.forked
@pytest.mark.parametrize("set_current_scope", [True, False])
def test_scope_data_in_threads_current(set_current_scope):
    sentry_sdk.init()
    sentry_sdk.set_tag("tag1", "main_thread_isolated_value")

    current_scope = sentry_sdk.get_current_scope()

    thread = MyThread(
        custom_current_scope=current_scope, set_current_scope=set_current_scope
    )
    thread.start()
    thread.join()


@pytest.mark.forked
@pytest.mark.parametrize("set_current_scope", [True, False])
def test_scope_data_in_threads_current_plus_isolation(set_current_scope):
    sentry_sdk.init()
    sentry_sdk.set_tag("tag1", "main_thread_isolated_value")

    current_scope = sentry_sdk.get_current_scope()
    isolation_scope = sentry_sdk.get_isolation_scope()

    thread = MyThread(
        custom_current_scope=current_scope,
        custom_isolation_scope=isolation_scope,
        set_current_scope=set_current_scope,
    )
    thread.start()
    thread.join()
