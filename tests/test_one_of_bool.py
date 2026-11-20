from tinydb import Query


def test_one_of_treats_bool_as_int():
    """Lock the current contract: True is contained in [1]."""
    query = Query().n.one_of([1])
    assert query({"n": True})
    assert not query({"n": False})
