import threading

import pytest

import sentry_sdk
        

class MyThread(threading.Thread):
    def __init__(self, custom_scope):
        threading.Thread.__init__(self)
        self.custom_scope = custom_scope

    def _run(self):
        isolation_scope = sentry_sdk.get_isolation_scope()
        global_scope = sentry_sdk.get_global_scope()

        print("MyThread, custom_scope (passed in current scope): {}".format(self.custom_scope))
        print("MyThread, isolation_scope: {}".format(isolation_scope))
        print("MyThread, global_scope: {}".format(global_scope))

        self.custom_scope.set_tag("tag2", "mythread_custom_value")
        event_payload = sentry_sdk.capture_event({"name": "mythread_event"})

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
def test_scope_data_in_threads():
    sentry_sdk.init()

    with sentry_sdk.isolated_scope() as isolated_scope:
        current_scope = sentry_sdk.get_current_scope()
        global_scope = sentry_sdk.get_global_scope()

        print("MAIN thread, current_scope: {}".format(current_scope))
        print("MAIN thread, isolation_scope: {}".format(isolated_scope))
        print("MAIN thread, global_scope: {}".format(global_scope))

        isolated_scope.set_tag("tag1", "main_thread_isolated_value")

        thread = MyThread(current_scope)
        thread.start()
        thread.join()