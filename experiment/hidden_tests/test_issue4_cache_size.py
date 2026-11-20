"""Hidden checks for a per-instance cache size. Not shown to the agent."""

import pytest
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import MemoryStorage


def test_default_stays_1000_for_the_class_and_a_later_instance():
    CachingMiddleware(MemoryStorage, cache_size=1)
    assert CachingMiddleware.WRITE_CACHE_SIZE == 1000
    other = CachingMiddleware(MemoryStorage)()
    assert other.WRITE_CACHE_SIZE == 1000


def test_size_one_writes_through_and_size_two_waits():
    immediate = CachingMiddleware(MemoryStorage, cache_size=1)()
    immediate.write({"a": 1})
    assert immediate.storage.memory == {"a": 1}
    deferred = CachingMiddleware(MemoryStorage, cache_size=2)()
    deferred.write({"a": 1})
    assert deferred.storage.memory is None
    deferred.write({"a": 2})
    assert deferred.storage.memory == {"a": 2}


def test_size_below_one_raises():
    with pytest.raises(ValueError):
        CachingMiddleware(MemoryStorage, cache_size=0)


def test_close_flushes_a_large_cache():
    storage = CachingMiddleware(MemoryStorage, cache_size=1000)()
    storage.write({"a": 1})
    assert storage.storage.memory is None
    storage.close()
    assert storage.storage.memory == {"a": 1}
