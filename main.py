
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
    print(f"Current scope before: {scope} / tags: {scope.get_tags()} ({id(scope._tags)})")
    assert scope.get_tags() == {"tag1": "1"}

    with sentry_sdk.new_scope() as scope:
        scope.set_tag("tag2", "2")
        print(f"New scope: {scope} / tags: {scope.get_tags()} ({id(scope._tags)})")
        assert scope.get_tags() == {"tag1": "1", "tag2": "2"}

    scope = sentry_sdk.get_current_scope()
    scope.set_tag("tag3", "3")
    print(f"Current scope after: {scope} / tags: {scope.get_tags()} ({id(scope._tags)})")
    assert scope.get_tags() == {"tag1": "1", "tag3": "3"}


if __name__ == '__main__':
    main()