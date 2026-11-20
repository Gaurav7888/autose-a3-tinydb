"""Hidden checks for type-sensitive one_of. Not shown to the agent."""

from tinydb import Query


def test_bool_and_int_are_distinct():
    ints = Query().n.one_of([1, 2])
    assert ints({"n": 1})
    assert not ints({"n": True})
    assert not ints({"n": 0})
    flags = Query().n.one_of([True])
    assert flags({"n": True})
    assert not flags({"n": 1})


def test_string_and_float_are_distinct_from_int():
    query = Query().n.one_of([1])
    assert query({"n": 1})
    assert not query({"n": "1"})
    assert not query({"n": 1.0})
    floats = Query().n.one_of([1.0])
    assert floats({"n": 1.0})
    assert not floats({"n": 1})


def test_strings_still_match():
    query = Query().n.one_of(["a", "b"])
    assert query({"n": "a"})
    assert not query({"n": "c"})
    assert not query({"n": "A"})
