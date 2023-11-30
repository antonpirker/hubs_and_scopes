import threading

import pytest

import sentry_sdk
        

class MyThread(threading.Thread):
    def __init__(self, custom_scope):
        threading.Thread.__init__(self)
        self.custom_scope = custom_scope

    def _run(self):
        print("MyThread, custom_scope: {}".format(self.custom_scope))

        isolation_scope = sentry_sdk.get_isolation_scope()
        print("MyThread, isolation_scope: {}".format(isolation_scope))
        
        global_scope = sentry_sdk.get_global_scope()
        print("MyThread, global_scope: {}".format(global_scope))


        self.custom_scope.set_tag("tag2", "mythread_custom_value")
        event_payload = sentry_sdk.capture_event({"name": "mythread_event"})

        # This does not yet work, for this we need to update TreadingIntegration to propagate the isolation scope to the new thread (or reference it in the current scope).
        assert event_payload["data"]["tags"] == {"tag1": "main_thread_isolated_value", "tag2": "mythread_custom_value"}

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


# @pytest.mark.forked
def test_scope_data_in_threads():
    sentry_sdk.init()

    with sentry_sdk.isolated_scope() as isolated_scope:
        isolated_scope.set_tag("tag1", "main_thread_isolated_value")

        current_scope = sentry_sdk.get_current_scope()
        print("MAIN thread, current_scope: {}".format(current_scope))

        print("MAIN thread, isolation_scope: {}".format(isolated_scope))

        global_scope = sentry_sdk.get_global_scope()
        print("MAIN thread, global_scope: {}".format(global_scope))

        thread = MyThread(current_scope)
        thread.start()
        thread.join()