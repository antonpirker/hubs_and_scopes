
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

    with sentry_sdk.isolated_scope() as isolated_scope:
        isolated_scope.set_tag("itag1", "i1")
        assert isolated_scope.get_tags() == {"itag1": "i1"}
        assert sentry_sdk.Scope.get_current_scope().get_merged_scope_data() == {"itag1": "i1"}  # this is what sentry_sdk.capure_event() sends.
        sentry_sdk.capture_event({"name": "ievent1"})

        scope = sentry_sdk.get_current_scope()
        scope.set_tag("tag1", "1")
        assert scope.get_tags() == {"tag1": "1"}
        assert sentry_sdk.Scope.get_current_scope().get_merged_scope_data() == {"itag1": "i1", "tag1": "1"}  # this is what sentry_sdk.capure_event() sends.
        sentry_sdk.capture_event({"name": "event1"})

        with sentry_sdk.isolated_scope() as isolated_scope:
            isolated_scope.set_tag("itag2", "i2")
            # QUESTION: the rfc states that "withIsolationScope" also forks the current scope, this is why we have `tag1` in here. Is this correct?
            assert isolated_scope.get_tags() == {"itag2": "i2", "tag1": "1"}
            assert sentry_sdk.Scope.get_current_scope().get_merged_scope_data() == {"itag2": "i2", "tag1": "1"}  # this is what sentry_sdk.capure_event() sends.
            sentry_sdk.capture_event({"name": "ievent2"}) 

            with sentry_sdk.new_scope() as scope:  # did not call it "withScope" this sounds more natural
                scope.set_tag("tag4", "4")
                assert scope.get_tags() == {"tag1": "1", "tag4": "4"}
                assert sentry_sdk.Scope.get_current_scope().get_merged_scope_data() == {"itag2": "i2", "tag1": "1", "tag4": "4"}  # this is what sentry_sdk.capure_event() sends.
                sentry_sdk.capture_event({"name": "event2"}) 

        with sentry_sdk.new_scope() as scope:  # did not call it "withScope" this sounds more natural
            scope.set_tag("tag2", "2")
            assert scope.get_tags() == {"tag1": "1", "tag2": "2"}
            assert sentry_sdk.Scope.get_current_scope().get_merged_scope_data() == {"itag1": "i1", "tag1": "1", "tag2": "2"}  # this is what sentry_sdk.capure_event() sends.
            sentry_sdk.capture_event({"name": "event2"}) 

        scope = sentry_sdk.get_current_scope()
        scope.set_tag("tag3", "3")
        assert scope.get_tags() == {"tag1": "1", "tag3": "3"}
        assert sentry_sdk.Scope.get_current_scope().get_merged_scope_data() == {"itag1": "i1", "tag1": "1", "tag3": "3"}  # this is what sentry_sdk.capure_event() sends.
        sentry_sdk.capture_event({"name": "event3"})

    scope = sentry_sdk.get_current_scope()
    scope.set_tag("tagx", "x")
    assert scope.get_tags() == {"tagx": "x"}
    assert sentry_sdk.Scope.get_current_scope().get_merged_scope_data() == {"tagx": "x"}  # this is what sentry_sdk.capure_event() sends.
    sentry_sdk.capture_event({"name": "eventx"})


if __name__ == '__main__':
    main()