
import sentry_sdk


def main():
    # noop client
    client = sentry_sdk.get_client()
    assert type(client) == sentry_sdk.NoopClient
    assert not sentry_sdk.sentry_is_initialized()
    
    # sentry init
    sentry_sdk.init()
    assert sentry_sdk.sentry_is_initialized()

    client = sentry_sdk.get_client()
    assert type(client) == sentry_sdk.Client
    assert client == sentry_sdk.get_global_scope().client

    # new scope
    scope = sentry_sdk.get_current_scope()
    scope.set_tag("tag1", "1")
    assert scope.get_tags() == {"tag1": "1"}
    sentry_sdk.capture_event({"name": "event1"})

    with sentry_sdk.new_scope() as scope:  # did not call it "withScope" this sounds more natural
        scope.set_tag("tag2", "2")
        assert scope.get_tags() == {"tag1": "1", "tag2": "2"}
        sentry_sdk.capture_event({"name": "event2"}) 

    scope = sentry_sdk.get_current_scope()
    scope.set_tag("tag3", "3")
    assert scope.get_tags() == {"tag1": "1", "tag3": "3"}
    sentry_sdk.capture_event({"name": "event3"})


if __name__ == '__main__':
    main()