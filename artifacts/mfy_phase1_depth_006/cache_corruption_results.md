# Cache Corruption Results

The feature payload was modified after caching. Content-hash verification detected
the mismatch, removed only the corrupt node, recomputed it, incremented corruption
and invalidation counters, and preserved the expected result. The run did not trust
or report completion from corrupt content.
