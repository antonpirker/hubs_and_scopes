import pytest

from sentry_sdk import Scope, new_scope


@pytest.mark.forked
def test_get_current_scope():
    scope1 = Scope.get_current_scope()
    scope2 = Scope.get_current_scope()
    assert id(scope1) == id(scope2)
    assert scope1.client is None
    assert scope2.client is None

    scope1.set_tag("tag1", "value")
    tags_scope1 = scope1.get_tags()
    tags_scope2 = scope2.get_tags()
    assert tags_scope1 == tags_scope2
    assert scope1.client is None
    assert scope2.client is None


@pytest.mark.forked
def test_with_new_scope():
    original_current_scope = Scope.get_current_scope()
    original_isolation_scope = Scope.get_isolation_scope()

    with new_scope() as scope:
        in_with_current_scope = Scope.get_current_scope()
        in_with_isolation_scope = Scope.get_isolation_scope()

        assert scope is in_with_current_scope
        assert in_with_current_scope is not original_current_scope
        assert in_with_isolation_scope is original_isolation_scope

    after_with_current_scope = Scope.get_current_scope()
    after_with_isolation_scope = Scope.get_isolation_scope()
    assert after_with_current_scope is original_current_scope
    assert after_with_isolation_scope is original_isolation_scope
