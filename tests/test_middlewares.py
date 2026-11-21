import os

import pytest

from tinydb import TinyDB
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import MemoryStorage, JSONStorage

doc = {'none': [None, None], 'int': 42, 'float': 3.1415899999999999,
       'list': ['LITE', 'RES_ACID', 'SUS_DEXT'],
       'dict': {'hp': 13, 'sp': 5},
       'bool': [True, False, True, False]}


def test_caching(storage):
    # Write contents
    storage.write(doc)

    # Verify contents
    assert doc == storage.read()


def test_caching_read():
    db = TinyDB(storage=CachingMiddleware(MemoryStorage))
    assert db.all() == []


def test_caching_write_many(storage):
    storage.WRITE_CACHE_SIZE = 3
    storage._write_cache_size = 3

    # Storage should be still empty
    assert storage.memory is None

    # Write contents
    for x in range(2):
        storage.write(doc)
        assert storage.memory is None  # Still cached

    storage.write(doc)

    # Verify contents: Cache should be emptied and written to storage
    assert storage.memory


def test_caching_flush(storage):
    # Write contents
    for _ in range(CachingMiddleware.WRITE_CACHE_SIZE - 1):
        storage.write(doc)

    # Not yet flushed...
    assert storage.memory is None

    storage.write(doc)

    # Verify contents: Cache should be emptied and written to storage
    assert storage.memory


def test_caching_flush_manually(storage):
    # Write contents
    storage.write(doc)

    storage.flush()

    # Verify contents: Cache should be emptied and written to storage
    assert storage.memory


def test_caching_write(storage):
    # Write contents
    storage.write(doc)

    storage.close()

    # Verify contents: Cache should be emptied and written to storage
    assert storage.storage.memory


def test_nested():
    storage = CachingMiddleware(MemoryStorage)
    storage()  # Initialization

    # Write contents
    storage.write(doc)

    # Verify contents
    assert doc == storage.read()


def test_caching_json_write(tmpdir):
    path = str(tmpdir.join('test.db'))

    with TinyDB(path, storage=CachingMiddleware(JSONStorage)) as db:
        db.insert({'key': 'value'})

    # Verify database filesize
    statinfo = os.stat(path)
    assert statinfo.st_size != 0

    # Assert JSON file has been closed
    assert db._storage._handle.closed

    del db

    # Reopen database
    with TinyDB(path, storage=CachingMiddleware(JSONStorage)) as db:
        assert db.all() == [{'key': 'value'}]


def test_caching_rejects_use_after_close(tmpdir):
    path = str(tmpdir.join('closed.db'))
    db = TinyDB(path, storage=CachingMiddleware(JSONStorage))
    db.insert({'key': 'value'})
    db.close()

    with pytest.raises(ValueError, match='closed'):
        db.insert({'key': 'again'})

    with pytest.raises(ValueError, match='closed'):
        db.all()

    with TinyDB(path, storage=CachingMiddleware(JSONStorage)) as reopened:
        assert reopened.all() == [{'key': 'value'}]


# ---------------------------------------------------------------------------
# New tests for configurable cache_size (AC-1 … AC-7)
# ---------------------------------------------------------------------------

class _TrackingStorage:
    """Minimal in-memory storage that records every write call."""

    def __init__(self):
        self.memory = None
        self.write_count = 0

    def read(self):
        return self.memory

    def write(self, data):
        self.memory = data
        self.write_count += 1

    def close(self):
        pass


def _make_tracking_caching(cache_size=None):
    """Return (CachingMiddleware_instance, underlying_TrackingStorage_instance)."""
    inner = _TrackingStorage()

    if cache_size is None:
        mw = CachingMiddleware(_TrackingStorage)
    else:
        mw = CachingMiddleware(_TrackingStorage, cache_size=cache_size)

    # Manually wire the inner storage so we can inspect it.
    mw.storage = inner
    return mw, inner


# AC-1: default cache_size=1000; a single write must NOT reach the wrapped storage.
def test_caching_middleware_default_cache_size():
    mw, inner = _make_tracking_caching()

    mw.write({'_default': {}})

    assert inner.write_count == 0, "write should be cached, not forwarded yet"
    assert CachingMiddleware.WRITE_CACHE_SIZE == 1000


# AC-2: cache_size=1; a single write IS passed through immediately.
def test_caching_middleware_cache_size_one():
    mw, inner = _make_tracking_caching(cache_size=1)

    mw.write({'_default': {}})

    assert inner.write_count == 1, "write should be forwarded immediately with cache_size=1"


# AC-3: cache_size=2; first write cached, second write flushes both.
def test_caching_middleware_cache_size_two():
    mw, inner = _make_tracking_caching(cache_size=2)

    mw.write({'_default': {'1': {'x': 1}}})
    assert inner.write_count == 0, "first write should still be cached"

    mw.write({'_default': {'1': {'x': 1}, '2': {'x': 2}}})
    assert inner.write_count == 1, "second write should flush to storage"


# AC-4: cache_size=1; each of three writes forwarded immediately; close() leaves nothing pending.
def test_caching_middleware_cache_size_one_close():
    mw, inner = _make_tracking_caching(cache_size=1)

    for i in range(3):
        mw.write({'_default': {str(i): {'v': i}}})

    assert inner.write_count == 3, "each write should be forwarded immediately"

    mw.close()
    # After close, no extra spurious write should have been issued
    assert inner.write_count == 3


# AC-5: two independent instances; one with cache_size=1, one default; they don't interfere.
def test_caching_middleware_independent_instances():
    mw_a, inner_a = _make_tracking_caching(cache_size=1)
    mw_b, inner_b = _make_tracking_caching()  # default=1000

    mw_a.write({'_default': {}})
    assert inner_a.write_count == 1, "instance A (cache_size=1) should forward immediately"

    mw_b.write({'_default': {}})
    assert inner_b.write_count == 0, "instance B (default cache) should not forward yet"

    assert CachingMiddleware.WRITE_CACHE_SIZE == 1000


# AC-6: cache_size=0 raises ValueError.
def test_caching_middleware_cache_size_zero():
    with pytest.raises(ValueError):
        CachingMiddleware(MemoryStorage, cache_size=0)


# AC-7: cache_size=-5 raises ValueError.
def test_caching_middleware_cache_size_negative():
    with pytest.raises(ValueError):
        CachingMiddleware(MemoryStorage, cache_size=-5)
