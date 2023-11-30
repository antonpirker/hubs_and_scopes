import pytest

from sentry_sdk import Scope, isolated_scope, new_scope


@pytest.mark.forked
def test_global_scope_data():
    global_scope = Scope.get_global_scope()
    global_scope.set_tag('tag1', 'value1')

    with new_scope() as scope:
        assert scope.get_tags() == {}
        assert scope.get_merged_scope_data() == {'tag1': 'value1'}
        scope.set_tag("tag2", "value2")
    
        assert scope.get_tags() == {'tag2': 'value2'}
        assert scope.get_merged_scope_data() == {'tag1': 'value1', 'tag2': 'value2'}
        assert scope.get_tags() != global_scope.get_tags()

    with isolated_scope() as scope:
        assert scope.get_tags() == {}
        assert scope.get_merged_scope_data() == {'tag1': 'value1'}
        scope.set_tag("tag3", "value3")
    
        assert scope.get_tags() == {'tag3': 'value3'}
        assert scope.get_merged_scope_data() == {'tag1': 'value1', 'tag3': 'value3'}
        assert scope.get_tags() != global_scope.get_tags()

    with new_scope() as scope:
        assert scope.get_tags() == {}
        assert scope.get_merged_scope_data() == {'tag1': 'value1'}
        scope.set_tag("tag1", "valueX")
    
        assert scope.get_tags() == {'tag1': 'valueX'}
        assert global_scope.get_tags() == {'tag1': 'value1'}
        assert scope.get_merged_scope_data() == {'tag1': 'valueX'}


@pytest.mark.forked
def test_global_scope_data_override_current():
    global_scope = Scope.get_global_scope()
    global_scope.set_tag('tag1', 'value_global')

    with new_scope() as current_scope:
        isolation_scope = Scope.get_isolation_scope()
        assert current_scope.get_tags() == {}
        assert current_scope.get_merged_scope_data() == {'tag1': 'value_global'}

        assert isolation_scope.get_tags() == {}
        assert isolation_scope.get_merged_scope_data() == {'tag1': 'value_global'}
        
        current_scope.set_tag("tag1", "value_current_scope")

        assert current_scope.get_tags() == {'tag1': 'value_current_scope'}
        assert isolation_scope.get_tags() == {}
        assert global_scope.get_tags() == {'tag1': 'value_global'}

        # Read operations should be done on current scope, because others return unintuive results
        assert current_scope.get_merged_scope_data() == {'tag1': 'value_current_scope'}
        assert isolation_scope.get_merged_scope_data() == {'tag1': 'value_global'}
        assert global_scope.get_merged_scope_data() == {'tag1': 'value_global'}


@pytest.mark.forked
def test_global_scope_data_override_isolation():
    global_scope = Scope.get_global_scope()
    global_scope.set_tag('tag1', 'value_global')

    with new_scope() as current_scope:
        isolation_scope = Scope.get_isolation_scope()
        assert current_scope.get_tags() == {}
        assert current_scope.get_merged_scope_data() == {'tag1': 'value_global'}

        assert isolation_scope.get_tags() == {}
        assert isolation_scope.get_merged_scope_data() == {'tag1': 'value_global'}
        
        isolation_scope.set_tag("tag1", "value_isolation_scope")   

        assert current_scope.get_tags() == {}
        assert isolation_scope.get_tags() == {'tag1': 'value_isolation_scope'}
        assert global_scope.get_tags() == {'tag1': 'value_global'}

        # Read operations should be done on current scope, because others return unintuive results
        assert current_scope.get_merged_scope_data() == {'tag1': 'value_isolation_scope'}
        assert isolation_scope.get_merged_scope_data() == {'tag1': 'value_isolation_scope'}
        assert global_scope.get_merged_scope_data() == {'tag1': 'value_global'}


@pytest.mark.forked
def test_global_scope_data_override_current_and_isolation():
    global_scope = Scope.get_global_scope()
    global_scope.set_tag('tag1', 'value_global')

    with new_scope() as current_scope:
        isolation_scope = Scope.get_isolation_scope()
        assert current_scope.get_tags() == {}
        assert current_scope.get_merged_scope_data() == {'tag1': 'value_global'}

        assert isolation_scope.get_tags() == {}
        assert isolation_scope.get_merged_scope_data() == {'tag1': 'value_global'}
        
        current_scope.set_tag("tag1", "value_current_scope")
        isolation_scope.set_tag("tag1", "value_isolation_scope")   

        assert current_scope.get_tags() == {'tag1': 'value_current_scope'}
        assert isolation_scope.get_tags() == {'tag1': 'value_isolation_scope'}
        assert global_scope.get_tags() == {'tag1': 'value_global'}

        # Read operations should be done on current scope, because others return unintuive results
        assert current_scope.get_merged_scope_data() == {'tag1': 'value_current_scope'}
        assert isolation_scope.get_merged_scope_data() == {'tag1': 'value_isolation_scope'}
        assert global_scope.get_merged_scope_data() == {'tag1': 'value_global'}


@pytest.mark.forked
@pytest.mark.parametrize("additional_type", [dict, Scope])
def test_global_scope_data_override_current_plus_additional(additional_type):
    global_scope = Scope.get_global_scope()
    global_scope.set_tag('tag1', 'value_global')

    with new_scope() as current_scope:       
        isolation_scope = Scope.get_isolation_scope()

        current_scope.set_tag("tag1", "value_current_scope")

        if additional_type == dict:
            additional_data = {'tag1': 'value_additional'}
        elif additional_type == Scope:
            additional_data = Scope()
            additional_data.set_tag('tag1', 'value_additional')
        else:
            raise Exception("Unknown additional_type")

        assert current_scope.get_merged_scope_data(additional_data=additional_data) == {'tag1': 'value_additional'}
        assert isolation_scope.get_merged_scope_data(additional_data=additional_data) == {'tag1': 'value_additional'}
        assert global_scope.get_merged_scope_data(additional_data=additional_data) == {'tag1': 'value_additional'}


@pytest.mark.forked
@pytest.mark.parametrize("additional_type", [dict, Scope])
def test_global_scope_data_override_isolation_plus_additional(additional_type):
    global_scope = Scope.get_global_scope()
    global_scope.set_tag('tag1', 'value_global')

    with new_scope() as current_scope:       
        isolation_scope = Scope.get_isolation_scope()

        isolation_scope.set_tag("tag1", "value_isolation_scope")

        if additional_type == dict:
            additional_data = {'tag1': 'value_additional'}
        elif additional_type == Scope:
            additional_data = Scope()
            additional_data.set_tag('tag1', 'value_additional')
        else:
            raise Exception("Unknown additional_type")

        assert current_scope.get_merged_scope_data(additional_data=additional_data) == {'tag1': 'value_additional'}
        assert isolation_scope.get_merged_scope_data(additional_data=additional_data) == {'tag1': 'value_additional'}
        assert global_scope.get_merged_scope_data(additional_data=additional_data) == {'tag1': 'value_additional'}


@pytest.mark.forked
@pytest.mark.parametrize("additional_type", [dict, Scope])
def test_global_scope_data_override_global_plus_additional_dict(additional_type):
    global_scope = Scope.get_global_scope()
    global_scope.set_tag('tag1', 'value_global')

    with new_scope() as current_scope:       
        isolation_scope = Scope.get_isolation_scope()

        global_scope.set_tag("tag1", "value_global_scope")

        if additional_type == dict:
            additional_data = {'tag1': 'value_additional'}
        elif additional_type == Scope:
            additional_data = Scope()
            additional_data.set_tag('tag1', 'value_additional')
        else:
            raise Exception("Unknown additional_type")

        assert current_scope.get_merged_scope_data(additional_data=additional_data) == {'tag1': 'value_additional'}
        assert isolation_scope.get_merged_scope_data(additional_data=additional_data) == {'tag1': 'value_additional'}
        assert global_scope.get_merged_scope_data(additional_data=additional_data) == {'tag1': 'value_additional'}
