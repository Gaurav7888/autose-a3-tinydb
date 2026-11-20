"""Hidden checks for the missing-field update. Not shown to the agent."""

import pytest
from tinydb import TinyDB
from tinydb.operations import add, decrement, delete, increment
from tinydb.storages import MemoryStorage


def _db():
    return TinyDB(storage=MemoryStorage)


def test_delete_missing_does_not_abort_the_batch():
    db = _db()
    db.insert({"name": "a", "nickname": "ann"})
    db.insert({"name": "b"})
    db.update(delete("nickname"))
    rows = {row["name"]: row for row in db.all()}
    assert "nickname" not in rows["a"]
    assert rows["a"]["name"] == "a"
    assert rows["b"] == {"name": "b"}


def test_increment_missing_becomes_one_and_existing_grows():
    db = _db()
    db.insert({"name": "a"})
    db.insert({"name": "b", "n": 3})
    db.update(increment("n"))
    rows = {row["name"]: row for row in db.all()}
    assert rows["a"]["n"] == 1
    assert rows["b"]["n"] == 4


def test_decrement_missing_becomes_minus_one():
    db = _db()
    db.insert({"name": "a", "n": 2})
    db.insert({"name": "b"})
    db.update(decrement("n"))
    rows = {row["name"]: row for row in db.all()}
    assert rows["a"]["n"] == 1
    assert rows["b"]["n"] == -1


def test_add_missing_still_raises():
    db = _db()
    db.insert({"name": "a"})
    with pytest.raises(KeyError):
        db.update(add("name_extra", 1))
