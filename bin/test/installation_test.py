import yaml
from nose.tools import assert_equals

from lib.installation import targets_from


def parse_targets(string_config, enabled=None):
    enabled = enabled if enabled else set()
    return list(targets_from(yaml.load(string_config, Loader=yaml.BaseLoader), enabled))


def test_targets_from_simple_cases():
    assert list(targets_from({}, set())) == []
    assert parse_targets("") == []

    assert_equals(
        parse_targets("""
weasel:
    type: foo
    targets:
    - moo
    """), [
            {'type': 'foo', 'name': 'moo', 'context': ['weasel']}
        ])


def test_targets_from_carries_hierarchy_config():
    assert_equals(
        parse_targets("""
weasel:
    base_config: "weasel"
    weasel_config: "weasel"
    baboon:
        type: foo
        base_config: "baboon" # overrides weasel
        targets:
        - ook
    """), [
            {'type': 'foo', 'base_config': 'baboon', 'weasel_config': 'weasel',
             'context': ['weasel', 'baboon'], 'name': 'ook'}
        ])


def test_multiple_targets_with_overrides():
    assert_equals(
        parse_targets("""
compilers:
    clang:
    - type: type_a
      value: type_a_base
      targets:
      - one
      - two
      - name: three
        value: type_three_override
    - type: type_b
      targets:
      - four
      - five
    - type: type_c
      targets:
      - six
    """), [
            {'type': 'type_a', 'value': 'type_a_base', 'name': 'one', 'context': ['compilers', 'clang']},
            {'type': 'type_a', 'value': 'type_a_base', 'name': 'two', 'context': ['compilers', 'clang']},
            {'type': 'type_a', 'value': 'type_three_override', 'name': 'three', 'context': ['compilers', 'clang']},
            {'type': 'type_b', 'name': 'four', 'context': ['compilers', 'clang']},
            {'type': 'type_b', 'name': 'five', 'context': ['compilers', 'clang']},
            {'type': 'type_c', 'name': 'six', 'context': ['compilers', 'clang']}
        ])


def test_targets_with_string_interpolation():
    assert_equals(
        parse_targets("""
root:
    var: The first var
    child:
        type: tip
        var2: the second var
        targets:
        - name: bob
          value: "{var}-{var2}"
    """), [
            {'type': 'tip', 'name': 'bob', 'context': ['root', 'child'], 'var': 'The first var',
             'var2': 'the second var',
             'value': 'The first var-the second var'}
        ])


def test_targets_enabled():
    assert_equals(
        parse_targets("""
weasel:
    if: weasels_allowed
    type: foo
    targets:
    - moo
    """), [])
    assert_equals(
        parse_targets("""
weasel:
    if: weasels_allowed
    type: foo
    targets:
    - moo
    """, ['weasels_allowed']), [
            {'if': 'weasels_allowed', 'type': 'foo', 'context': ['weasel'], 'name': 'moo'}
        ])
