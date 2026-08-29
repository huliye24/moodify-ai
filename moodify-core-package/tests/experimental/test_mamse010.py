"""MAMSE-010 synthetic gates (17 prototype + repo-specific extras).

Axis/shape contract, duplicate axis rejection, missing-mask vs zero,
deterministic tensor_id, grid coverage, overlap alignment, heterogeneous
feature missing-mask, unfold/fold round-trip, n-mode product, exact HOSVD,
deterministic model_id, frozen-tucker residual localization, mode singular
values, dense bytes, tile coverage, save/load; plus: materialization guard,
channel-spectral view shapes, cross-scale alignment on canonical planes.
"""

from __future__ import annotations

import numpy as np
import pytest

from moodify_experimental.mamse010 import (
    AuditoryTensorBundle,
    AxisSpec,
    MaterializationGuardError,
    TensorContractError,
    TensorField,
    build_channel_spectral_tensor,
    build_scale_feature_tensor,
    estimate_dense_bytes,
    fold,
    guard_materialization,
    hosvd,
    interval_overlap_weighted,
    iter_tiles,
    load_bundle,
    mode_dot,
    mode_singular_values,
    project_tucker,
    regular_time_grid,
    relative_residual_by_time,
    save_bundle,
    unfold,
)

SR = 48000


def test_axis_shape_contract():
    a = AxisSpec("time", (0, 1, 2))
    with pytest.raises(TensorContractError):
        TensorField("x", np.zeros((2,)), (a,))


def test_duplicate_axis_names_rejected():
    a = AxisSpec("time", (0, 1))
    with pytest.raises(TensorContractError):
        TensorField("x", np.zeros((2, 2)), (a, a))


def test_missing_mask_not_physical_zero():
    a = AxisSpec("time", (0, 1, 2))
    f = TensorField("x", np.array([1.0, np.nan, 0.0]), (a,))
    assert f.valid_mask.tolist() == [True, False, True]


def test_bundle_id_deterministic():
    a = AxisSpec("time", (0, 1, 2))
    f1 = TensorField("x", np.array([1., 2., 3.]), (a,), unit="dB")
    f2 = TensorField("x", np.array([1., 2., 3.]), (a,), unit="dB")
    b1 = AuditoryTensorBundle("abc", {"x": f1}, {"temporal": "v1"})
    b2 = AuditoryTensorBundle("abc", {"x": f2}, {"temporal": "v1"})
    assert b1.tensor_id == b2.tensor_id


def test_regular_grid_covers_duration():
    s, e = regular_time_grid(1050, 100)
    assert s[0] == 0
    assert e[-1] == 1050
    assert np.all(e > s)


def test_overlap_alignment_constant():
    v = np.array([3., 3., 3.])
    s = np.array([0, 100, 200])
    e = np.array([100, 200, 300])
    ds = np.array([0, 150])
    de = np.array([150, 300])
    out, mask = interval_overlap_weighted(v, s, e, ds, de)
    assert np.all(mask)
    assert np.allclose(out, 3.0)


def test_overlap_alignment_transition():
    v = np.array([0., 10.])
    s = np.array([0, 100])
    e = np.array([100, 200])
    out, mask = interval_overlap_weighted(v, s, e, np.array([50]), np.array([150]))
    assert mask[0]
    assert np.isclose(out[0], 5.0)


def test_heterogeneous_feature_tensor_keeps_missing_as_mask():
    planes = {
        "S0": {
            "values": np.array([[1., 2.], [3., 4.]]),
            "feature_names": ["rms", "clip"],
            "window_starts_ms": [0, 100],
            "window_ends_ms": [100, 200],
        },
        "S1": {
            "values": np.array([[5.], [6.]]),
            "feature_names": ["rms"],
            "window_starts_ms": [0, 100],
            "window_ends_ms": [100, 200],
        },
    }
    f = build_scale_feature_tensor(planes, feature_names=["rms", "clip"], duration_ms=200, grid_hop_ms=100)
    assert np.isnan(f.data[:, 1, 1]).all()
    assert not f.valid_mask[:, 1, 1].any()


def test_unfold_fold_roundtrip():
    x = np.arange(2 * 3 * 4).reshape(2, 3, 4)
    for mode in range(3):
        assert np.array_equal(fold(unfold(x, mode), mode, x.shape), x)


def test_mode_dot_shape():
    x = np.zeros((4, 3, 2))
    M = np.ones((5, 3))
    y = mode_dot(x, M, 1)
    assert y.shape == (4, 5, 2)


def test_hosvd_exact_low_multilinear_rank():
    rng = np.random.default_rng(10)
    core = rng.normal(size=(2, 2, 2))
    U0, _ = np.linalg.qr(rng.normal(size=(8, 2)))
    U1, _ = np.linalg.qr(rng.normal(size=(7, 2)))
    U2, _ = np.linalg.qr(rng.normal(size=(5, 2)))
    x = core
    for mode, U in enumerate((U0, U1, U2)):
        x = mode_dot(x, U, mode)
    model = hosvd(x, (2, 2, 2))
    rec = model.reconstruct()
    assert np.linalg.norm(x - rec) / np.linalg.norm(x) < 1e-10


def test_hosvd_model_id_deterministic():
    rng = np.random.default_rng(1)
    x = rng.normal(size=(10, 8, 3))
    a = hosvd(x, (3, 3, 2))
    b = hosvd(x, (3, 3, 2))
    assert a.model_id == b.model_id
    assert np.allclose(a.core, b.core)


def test_frozen_tucker_residual_detects_new_structure():
    rng = np.random.default_rng(11)
    T, F = 80, 24
    t = np.linspace(0, 1, T)
    f = np.linspace(0, 1, F)
    base = (
        (1 + 0.2 * np.sin(2 * np.pi * t))[:, None, None, None]
        * (np.exp(-((f - 0.3) / 0.18) ** 2)[None, :, None, None])
        * np.array([1.0, 0.85])[None, None, :, None]
        * np.array([1.0, 0.7, 0.45])[None, None, None, :]
    )
    base += 0.005 * rng.normal(size=base.shape)
    model = hosvd(base[:50], (4, 4, 2, 2))
    factors = (np.eye(T), model.factors[1], model.factors[2], model.factors[3])
    x = base.copy()
    x[62:68, 19:23, 1, 2] += 1.2
    rec, res = project_tucker(x, factors)
    rr = relative_residual_by_time(x, res)
    assert np.median(rr[62:68]) > np.median(rr[10:40]) * 5


def test_mode_singular_values_descend():
    rng = np.random.default_rng(3)
    s = mode_singular_values(rng.normal(size=(6, 5, 4)), 1)
    assert np.all(s[:-1] >= s[1:])


def test_dense_bytes():
    assert estimate_dense_bytes((10, 20, 3), np.float32) == 10 * 20 * 3 * 4


def test_tiles_cover_each_element_once():
    shape = (7, 5, 3)
    count = np.zeros(shape, dtype=int)
    for sl in iter_tiles(shape, (3, 2, 2)):
        count[sl] += 1
    assert np.all(count == 1)


def test_save_load_bundle(tmp_path):
    a = AxisSpec("time", (0, 1, 2), unit="ms")
    f = TensorField("x", np.array([1., np.nan, 3.]), (a,), unit="ratio")
    b = AuditoryTensorBundle("sha", {"x": f})
    save_bundle(b, tmp_path)
    meta, arrays = load_bundle(tmp_path)
    assert meta["tensor_id"] == b.tensor_id
    assert np.isnan(arrays["x__data"][1])
    assert arrays["x__valid_mask"].tolist() == [1, 0, 1]
    assert (tmp_path / "mamse010_manifest.json").exists()


def test_materialization_guard_raises():
    with pytest.raises(MaterializationGuardError):
        guard_materialization((100000, 100000, 5), np.float64, max_bytes=1 << 30)
    assert guard_materialization((10, 20, 3), np.float32, max_bytes=1 << 30) == 2400


def test_channel_spectral_view_shapes():
    rng = np.random.default_rng(4)
    x = rng.standard_normal((int(3.0 * SR), 2)) * 0.1
    f = build_channel_spectral_tensor(x, SR)
    assert f.data.ndim == 3
    assert f.data.shape[2] == 2
    assert np.all(f.valid_mask)
    assert f.axes[1].unit == "hz"


def test_cross_scale_alignment_on_canonical_planes():
    # two scales with different windowing but overlapping time coverage
    planes = {
        "S1": {
            "values": np.array([[1.0], [2.0], [3.0]]),
            "feature_names": ["rms_db"],
            "window_starts_ms": [0, 500, 1000],
            "window_ends_ms": [500, 1000, 1500],
        },
        "S2": {
            "values": np.array([[10.0]]),
            "feature_names": ["rms_db"],
            "window_starts_ms": [0],
            "window_ends_ms": [1500],
        },
    }
    f = build_scale_feature_tensor(planes, feature_names=["rms_db"], duration_ms=1500, grid_hop_ms=250)
    assert f.data.shape[0] == 6  # time grid
    assert f.data.shape[1] == 2  # scales
    s1col = f.data[:, 0, 0]
    s2col = f.data[:, 1, 0]
    assert np.isclose(s1col[0], 1.0) and np.isclose(s1col[-1], 3.0)
    assert np.all(np.isclose(s2col, 10.0))
    assert np.all(f.valid_mask)
