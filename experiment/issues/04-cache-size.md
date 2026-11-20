# Let each CachingMiddleware choose its own write cache size

`CachingMiddleware.WRITE_CACHE_SIZE` is a class attribute set to 1000. I have two databases in one process. One of them should hit the disk on every write. The other should keep the default.

Please let me pass the size in the constructor:

    CachingMiddleware(JSONStorage, cache_size=1)

When I do not pass it, the default stays 1000. That includes the class attribute, because existing code reads `CachingMiddleware.WRITE_CACHE_SIZE`.

`cache_size` below 1 should raise ValueError.

A middleware built with `cache_size=1` should write through to the wrapped storage on every write. `cache_size=2` should write on the second write, not the first. `close()` should still flush whatever is pending. Building one middleware with `cache_size=1` must not change the size of another middleware I build afterwards with the default.
