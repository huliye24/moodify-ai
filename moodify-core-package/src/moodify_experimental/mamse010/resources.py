"""MAMSE-010 resource safety: dense memory estimator, tile iterator, guard."""

from __future__ import annotations

import itertools
from typing import Iterable, Iterator

import numpy as np


def estimate_dense_bytes(shape: Iterable[int], dtype=np.float32) -> int:
    n = int(np.prod(tuple(int(x) for x in shape)))
    return n * np.dtype(dtype).itemsize


def iter_tiles(shape: tuple[int, ...], tile_shape: tuple[int, ...]) -> Iterator[tuple[slice, ...]]:
    if len(shape) != len(tile_shape):
        raise ValueError("shape/tile_shape rank mismatch")
    if any(t <= 0 for t in tile_shape):
        raise ValueError("tile sizes must be positive")
    starts_per_axis = [range(0, n, t) for n, t in zip(shape, tile_shape)]
    for starts in itertools.product(*starts_per_axis):
        yield tuple(slice(s, min(s + t, n)) for s, t, n in zip(starts, tile_shape, shape))


class MaterializationGuardError(RuntimeError):
    pass


def guard_materialization(shape: Iterable[int], dtype, max_bytes: int) -> int:
    """Estimate dense bytes and raise if the estimate exceeds max_bytes.

    Returns the byte estimate on success. Default policy: no huge 5D tensor
    is materialized implicitly.
    """
    n = int(np.prod(tuple(int(x) for x in shape)))
    dtype = np.dtype(dtype)
    if dtype.itemsize == 0:
        raise ValueError("cannot estimate bytes for object dtype")
    bytes_ = n * dtype.itemsize
    if bytes_ > max_bytes:
        raise MaterializationGuardError(
            f"dense materialization {bytes_} bytes exceeds guard {max_bytes} bytes"
        )
    return bytes_
