import pytest
from tinydb import where, TinyDB
from tinydb.storages import MemoryStorage
from tinydb.operations import delete, increment, decrement, add, subtract, set


def test_delete(db):
    db.update(delete('int'), where('char') == 'a')
    assert 'int' not in db.get(where('char') == 'a')


def test_add_int(db):
    db.update(add('int', 5), where('char') == 'a')
    assert db.get(where('char') == 'a')['int'] == 6


def test_add_str(db):
    db.update(add('char', 'xyz'), where('char') == 'a')
    assert db.get(where('char') == 'axyz')['int'] == 1


def test_subtract(db):
    db.update(subtract('int', 5), where('char') == 'a')
    assert db.get(where('char') == 'a')['int'] == -4


def test_set(db):
    db.update(set('char', 'xyz'), where('char') == 'a')
    assert db.get(where('char') == 'xyz')['int'] == 1


def test_increment(db):
    db.update(increment('int'), where('char') == 'a')
    assert db.get(where('char') == 'a')['int'] == 2


def test_decrement(db):
    db.update(decrement('int'), where('char') == 'a')
    assert db.get(where('char') == 'a')['int'] == 0


# --- AC-1: delete on missing field leaves document unchanged ---
def test_delete_missing_field():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'nickname': 'Alice'})
    db.insert({'name': 'Bob'})
    # Must not raise; document without 'nickname' stays unchanged
    db.update(delete('nickname'))
    assert db.get(where('nickname') == 'Alice') is None  # field removed from A
    bob = db.get(where('name') == 'Bob')
    assert bob is not None
    assert 'nickname' not in bob  # B still has no 'nickname'


# --- AC-2: increment on missing field sets field to 1 ---
def test_increment_missing_field():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'name': 'Bob'})
    db.update(increment('counter'))
    doc = db.get(where('name') == 'Bob')
    assert doc['counter'] == 1


# --- AC-3: decrement on missing field sets field to -1 ---
def test_decrement_missing_field():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'name': 'Bob'})
    db.update(decrement('counter'))
    doc = db.get(where('name') == 'Bob')
    assert doc['counter'] == -1


# --- AC-4: add on missing field raises KeyError ---
def test_add_missing_field_raises():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'name': 'Bob'})
    with pytest.raises(KeyError):
        db.update(add('tags', 'new_tag'))
    # Document must remain unchanged
    doc = db.get(where('name') == 'Bob')
    assert 'tags' not in doc


# --- AC-5: subtract on missing field raises KeyError ---
def test_subtract_missing_field_raises():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'name': 'Bob'})
    with pytest.raises(KeyError):
        db.update(subtract('balance', 5))
    doc = db.get(where('name') == 'Bob')
    assert 'balance' not in doc


# --- AC-6: delete across multiple documents, some with field, some without ---
def test_delete_multiple_documents():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'email': 'a@example.com', 'idx': 1})
    db.insert({'email': 'b@example.com', 'idx': 2})
    db.insert({'idx': 3})
    # Must not raise; docs 1 and 2 lose 'email', doc 3 unchanged
    db.update(delete('email'))
    assert db.get(where('idx') == 1) is not None
    assert 'email' not in db.get(where('idx') == 1)
    assert db.get(where('idx') == 2) is not None
    assert 'email' not in db.get(where('idx') == 2)
    doc3 = db.get(where('idx') == 3)
    assert doc3 is not None
    assert 'email' not in doc3
