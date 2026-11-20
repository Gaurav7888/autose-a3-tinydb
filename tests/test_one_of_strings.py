from tinydb import Query


def test_one_of_matches_strings():
    query = Query().color.one_of(["red", "blue"])
    assert query({"color": "red"})
    assert not query({"color": "green"})
