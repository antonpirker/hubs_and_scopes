import pytest

from sentry_sdk import Scope, isolated_scope, new_scope

@pytest.mark.forked
def test_get_global_scope():
    global_scope1 = Scope.get_global_scope()
    global_scope2 = Scope.get_global_scope()
    assert global_scope1 == global_scope2
    assert global_scope1.client is None
    assert global_scope2.client is None

    global_scope1.set_tag('tag1', 'value')
    tags_scope1 = global_scope1.get_tags()
    tags_scope2 = global_scope2.get_tags()
    assert tags_scope1 == tags_scope2
    assert global_scope1.client is None
    assert global_scope2.client is None


@pytest.mark.forked
def test_get_global_with_new_scope():
    original_global_scope = Scope.get_global_scope()

    with new_scope() as scope:
        in_with_global_scope = Scope.get_global_scope()

        assert scope is not in_with_global_scope
        assert in_with_global_scope is original_global_scope

    after_with_global_scope = Scope.get_global_scope()
    assert after_with_global_scope is original_global_scope


@pytest.mark.forked
def test_get_global_with_isolated_scope():
    original_global_scope = Scope.get_global_scope()

    with isolated_scope() as scope:
        in_with_global_scope = Scope.get_global_scope()

        assert scope is not in_with_global_scope
        assert in_with_global_scope is original_global_scope

    after_with_global_scope = Scope.get_global_scope()
    assert after_with_global_scope is original_global_scope

