from tinydb import Query


def test_between_is_inclusive_for_numbers_and_strings():
    ages = Query().age.between(18, 65)
    assert ages({"age": 18})
    assert ages({"age": 40})
    assert ages({"age": 65})
    assert not ages({"age": 17})
    assert not ages({"age": 66})
    names = Query().name.between("b", "d")
    assert names({"name": "b"})
    assert names({"name": "c"})
    assert not names({"name": "a"})


def test_between_incomparable_is_false():
    query = Query().v.between(1, 3)
    assert query({"v": None}) is False
    assert query({"v": {"a": 1}}) is False


def test_between_bounds_are_part_of_the_hash():
    assert Query().n.between(1, 5) != Query().n.between(1, 9)
    assert hash(Query().n.between(1, 5)) != hash(Query().n.between(1, 9))
