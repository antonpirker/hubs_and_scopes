import pytest

import sentry_sdk


@pytest.mark.forked
def test_noop_client():
    import sentry_sdk

    client = sentry_sdk.get_client()
    assert client.__class__ == sentry_sdk.NoopClient

    sentry_sdk.init()

    client = sentry_sdk.get_client()
    assert client.__class__ == sentry_sdk.Client


@pytest.mark.forked
def test_init():
    assert not sentry_sdk.sentry_is_initialized()

    sentry_sdk.init()

    assert sentry_sdk.sentry_is_initialized()


@pytest.mark.forked
def test_client_on_scope_init():
    sentry_sdk.init()

    current_scope = sentry_sdk.get_current_scope()
    isolation_scope = sentry_sdk.get_isolation_scope()
    global_scope = sentry_sdk.get_global_scope()

    assert current_scope.client is None
    assert isolation_scope.client is None
    assert global_scope.client is not None
    assert global_scope.client.__class__ == sentry_sdk.Client

    client = sentry_sdk.get_client()
    assert client is not None
    assert client.__class__ == sentry_sdk.Client


@pytest.mark.forked
def test_client_on_scope_without_init():
    current_scope = sentry_sdk.get_current_scope()
    isolation_scope = sentry_sdk.get_isolation_scope()
    global_scope = sentry_sdk.get_global_scope()

    assert current_scope.client is None
    assert isolation_scope.client is None
    assert global_scope.client is None

    client = sentry_sdk.get_client()
    assert client is not None
    assert client.__class__ == sentry_sdk.NoopClient


@pytest.mark.forked
def test_set_client_init_current():
    sentry_sdk.init()
    initial_client = sentry_sdk.get_client()

    current_scope = sentry_sdk.get_current_scope()
    isolation_scope = sentry_sdk.get_isolation_scope()
    global_scope = sentry_sdk.get_global_scope()

    custom_client = sentry_sdk.Client()
    current_scope.set_client(custom_client)

    assert current_scope.client == custom_client

    assert isolation_scope.client is None

    assert global_scope.client is not None
    assert global_scope.client != custom_client
    assert global_scope.client == initial_client

    client = sentry_sdk.get_client()
    assert client == custom_client


@pytest.mark.forked
def test_set_client_init_isolation():
    sentry_sdk.init()
    initial_client = sentry_sdk.get_client()

    current_scope = sentry_sdk.get_current_scope()
    isolation_scope = sentry_sdk.get_isolation_scope()
    global_scope = sentry_sdk.get_global_scope()

    custom_client = sentry_sdk.Client()
    isolation_scope.set_client(custom_client)

    assert current_scope.client is None

    assert isolation_scope.client == custom_client

    assert global_scope.client is not None
    assert global_scope.client != custom_client
    assert global_scope.client == initial_client

    client = sentry_sdk.get_client()
    assert client == custom_client


@pytest.mark.forked
def test_set_client_init_global():
    sentry_sdk.init()
    initial_client = sentry_sdk.get_client()

    current_scope = sentry_sdk.get_current_scope()
    isolation_scope = sentry_sdk.get_isolation_scope()
    global_scope = sentry_sdk.get_global_scope()

    custom_client = sentry_sdk.Client()
    global_scope.set_client(custom_client)

    assert current_scope.client is None

    assert isolation_scope.client is None

    assert global_scope.client is not None
    assert global_scope.client == custom_client
    assert global_scope.client != initial_client

    client = sentry_sdk.get_client()
    assert client == custom_client
    assert client != initial_client


@pytest.mark.forked
def test_set_multiple_clients():
    sentry_sdk.init()
    initial_client = sentry_sdk.get_client()

    current_client = sentry_sdk.Client()
    isolation_client = sentry_sdk.Client()
    global_client = sentry_sdk.Client()

    current_scope = sentry_sdk.get_current_scope()
    isolation_scope = sentry_sdk.get_isolation_scope()
    global_scope = sentry_sdk.get_global_scope()

    current_scope.set_client(current_client)
    isolation_scope.set_client(isolation_client)
    global_scope.set_client(global_client)

    assert current_scope.client == current_client
    assert current_scope.client != initial_client

    assert isolation_scope.client == isolation_client
    assert isolation_scope.client != initial_client

    assert global_scope.client == global_client
    assert global_scope.client != initial_client

    client = sentry_sdk.get_client()
    assert client == current_client
    assert client != initial_client
