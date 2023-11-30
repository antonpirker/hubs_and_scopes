import threading

import pytest

import sentry_sdk
        

class MyThread(threading.Thread):
    def __init__(self, custom_scope, set_current_scope=None):
        threading.Thread.__init__(self)
        self.custom_scope = custom_scope
        self.set_current_scope = set_current_scope

    def _run(self):
        if self.set_current_scope:
            sentry_sdk.set_current_scope(self.custom_scope)

        self.custom_scope.set_tag("tag2", "mythread_custom_value")
        event_payload = sentry_sdk.capture_event({"name": "mythread_event"})

        if self.set_current_scope:
            assert event_payload["tags"] == {"tag2": "mythread_custom_value"}
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
def test_scope_data_in_threads(set_current_scope):
    sentry_sdk.init()

    with sentry_sdk.isolated_scope() as isolated_scope:
        isolated_scope.set_tag("tag1", "main_thread_isolated_value")

        current_scope = sentry_sdk.get_current_scope()
        thread = MyThread(custom_scope=current_scope, set_current_scope=set_current_scope)
        thread.start()
        thread.join()