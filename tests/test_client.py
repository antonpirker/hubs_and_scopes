import pytest

import sentry_sdk


@pytest.mark.forked
def test_noop_client():
    client = sentry_sdk.get_client()
    assert type(client) == sentry_sdk.NoopClient

    sentry_sdk.init()

    client = sentry_sdk.get_client()
    assert type(client) == sentry_sdk.Client


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
    assert type(global_scope.client) == sentry_sdk.Client

    client = sentry_sdk.get_client()
    assert client is not None
    assert type(client) == sentry_sdk.Client
    

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
    assert type(client) == sentry_sdk.NoopClient


@pytest.mark.forked
def test_set_client_init_current():
    custom_client = sentry_sdk.Client()

    sentry_sdk.init()

    current_scope = sentry_sdk.get_current_scope()
    isolation_scope = sentry_sdk.get_isolation_scope()
    global_scope = sentry_sdk.get_global_scope()

    current_scope.set_client(custom_client)

    assert current_scope.client == custom_client
    assert isolation_scope.client is None
    assert global_scope.client is not None
    assert global_scope.client != custom_client  # the one created in init()

    client = sentry_sdk.get_client()
    assert client == custom_client


@pytest.mark.forked
def test_set_client_init_isolation():
    custom_client = sentry_sdk.Client()

    sentry_sdk.init()

    current_scope = sentry_sdk.get_current_scope()
    isolation_scope = sentry_sdk.get_isolation_scope()
    global_scope = sentry_sdk.get_global_scope()

    isolation_scope.set_client(custom_client)

    assert current_scope.client is None
    assert isolation_scope.client == custom_client
    assert global_scope.client is not None
    assert global_scope.client != custom_client  # the one created in init()

    client = sentry_sdk.get_client()
    assert client == custom_client


@pytest.mark.forked
def test_set_client_init_isolation():
    custom_client = sentry_sdk.Client()

    sentry_sdk.init()

    current_scope = sentry_sdk.get_current_scope()
    isolation_scope = sentry_sdk.get_isolation_scope()
    global_scope = sentry_sdk.get_global_scope()

    global_scope.set_client(custom_client)

    assert current_scope.client is None
    assert isolation_scope.client is None
    assert global_scope.client is not None
    assert global_scope.client == custom_client

    client = sentry_sdk.get_client()
    assert client == custom_client
