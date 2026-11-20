"""Hidden checks for Query.between. Not shown to the agent."""

from tinydb import Query


def test_bounds_are_inclusive_for_numbers_and_strings():
    ages = Query().age.between(18, 65)
    assert ages({"age": 18})
    assert ages({"age": 65})
    assert ages({"age": 40})
    assert not ages({"age": 17})
    assert not ages({"age": 66})
    names = Query().name.between("b", "d")
    assert names({"name": "b"})
    assert names({"name": "c"})
    assert not names({"name": "a"})
    assert not names({"name": "e"})


def test_incomparable_values_are_false_and_do_not_raise():
    query = Query().v.between(1, 3)
    assert query({"v": None}) is False
    assert query({"v": {"a": 1}}) is False
    assert query({"v": [1]}) is False


def test_different_bounds_are_different_queries():
    low = Query().n.between(1, 5)
    high = Query().n.between(1, 9)
    assert low != high
    assert hash(low) != hash(high)
