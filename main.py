import sentry_sdk
import globals


def main():
    # noop client
    client = sentry_sdk.get_client()
    assert isinstance(client, sentry_sdk.NoopClient)
    assert not sentry_sdk.sentry_is_initialized()

    # sentry init
    sentry_sdk.init()
    assert sentry_sdk.sentry_is_initialized()

    client = sentry_sdk.get_client()
    assert isinstance(client, sentry_sdk.Client)
    assert client == sentry_sdk.get_global_scope().client

    global_scope = sentry_sdk.get_global_scope()
    global_scope.set_tag("gtag1", "g1")
    assert global_scope.get_tags() == {"gtag1": "g1"}
    assert sentry_sdk.Scope.get_current_scope().get_merged_scope_data() == {
        "gtag1": "g1"
    }  # this is what sentry_sdk.capure_event() sends.
    sentry_sdk.capture_event({"name": "gevent1"})

    current_scope = globals.sentry_current_scope.get()
    isolation_scope = globals.sentry_isolation_scope.get()
    print(f"before with Current: {current_scope}/{isolation_scope}")
    print("--------")

    with sentry_sdk.isolated_scope() as isolated_scope:
        current_scope = globals.sentry_current_scope.get()
        isolation_scope = globals.sentry_isolation_scope.get()
        print(f"in with Current: {current_scope}/{isolation_scope}")
        print("--------")
        isolated_scope.set_tag("itag2", "i1")
        assert isolated_scope.get_tags() == {"itag2": "i1"}
        assert sentry_sdk.Scope.get_current_scope().get_merged_scope_data() == {
            "gtag1": "g1",
            "itag2": "i1",
        }  # this is what sentry_sdk.capure_event() sends.
        sentry_sdk.capture_event({"name": "ievent1"})

        scope = sentry_sdk.get_current_scope()
        scope.set_tag("tag2", "1")
        assert scope.get_tags() == {"tag2": "1"}
        assert sentry_sdk.Scope.get_current_scope().get_merged_scope_data() == {
            "gtag1": "g1",
            "itag2": "i1",
            "tag2": "1",
        }  # this is what sentry_sdk.capure_event() sends.
        sentry_sdk.capture_event({"name": "event1"})

        with sentry_sdk.isolated_scope() as isolated_scope:
            isolated_scope.set_tag("itag2", "i2")
            assert isolated_scope.get_tags() == {"itag2": "i2", "tag2": "1"}
            assert sentry_sdk.Scope.get_current_scope().get_merged_scope_data() == {
                "gtag1": "g1",
                "itag2": "i2",
                "tag2": "1",
            }  # this is what sentry_sdk.capure_event() sends.
            sentry_sdk.capture_event({"name": "ievent2"})

            with sentry_sdk.new_scope() as scope:  # did not call it "withScope" this sounds more natural
                scope.set_tag("tag4", "4")
                assert scope.get_tags() == {"tag2": "1", "tag4": "4"}
                assert sentry_sdk.Scope.get_current_scope().get_merged_scope_data() == {
                    "gtag1": "g1",
                    "itag2": "i2",
                    "tag2": "1",
                    "tag4": "4",
                }  # this is what sentry_sdk.capure_event() sends.
                sentry_sdk.capture_event({"name": "event2"})

                global_scope = sentry_sdk.get_global_scope()
                global_scope.set_tag("gtag2", "g2")
                assert global_scope.get_tags() == {"gtag1": "g1", "gtag2": "g2"}
                assert sentry_sdk.Scope.get_current_scope().get_merged_scope_data() == {
                    "gtag1": "g1",
                    "gtag2": "g2",
                    "itag2": "i2",
                    "tag2": "1",
                    "tag4": "4",
                }  # this is what sentry_sdk.capure_event() sends.
                sentry_sdk.capture_event({"name": "gevent1"})

        with sentry_sdk.new_scope() as scope:  # did not call it "withScope" this sounds more natural
            scope.set_tag("tag2", "2")
            assert scope.get_tags() == {"tag2": "1", "tag2": "2"}
            assert sentry_sdk.Scope.get_current_scope().get_merged_scope_data() == {
                "gtag1": "g1",
                "gtag2": "g2",
                "itag2": "i1",
                "tag2": "1",
                "tag2": "2",
            }  # this is what sentry_sdk.capure_event() sends.
            sentry_sdk.capture_event({"name": "event2"})

        scope = sentry_sdk.get_current_scope()
        scope.set_tag("tag3", "3")
        assert scope.get_tags() == {"tag2": "1", "tag3": "3"}
        assert sentry_sdk.Scope.get_current_scope().get_merged_scope_data() == {
            "gtag1": "g1",
            "gtag2": "g2",
            "itag2": "i1",
            "tag2": "1",
            "tag3": "3",
        }  # this is what sentry_sdk.capure_event() sends.
        sentry_sdk.capture_event({"name": "event3"})

    scope = sentry_sdk.get_current_scope()
    scope.set_tag("tagx", "x")
    assert scope.get_tags() == {"tagx": "x"}
    assert sentry_sdk.Scope.get_current_scope().get_merged_scope_data() == {
        "gtag1": "g1",
        "gtag2": "g2",
        "tagx": "x",
    }  # this is what sentry_sdk.capure_event() sends.
    sentry_sdk.capture_event({"name": "eventx"})


if __name__ == "__main__":
    main()
