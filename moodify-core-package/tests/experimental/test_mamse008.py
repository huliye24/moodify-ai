"""MAMSE-008 synthetic gates (15 prototype + repo-specific extras).

Nonnegative factors, deterministic NNDSVD, signed rejection, zero
unavailable, NaN mask, beta divergences, rank-3 recovery, rank-3 vs rank-1,
permutation-invariant factor alignment, canonicalization, frozen-basis
out-of-subspace residual, projection shapes, Hoyer sparsity, anonymous
evidence semantics, round-trip; plus repo-specific: mixed-unit signed
matrix rejection, frozen basis reopen, deterministic evidence
serialization, band-ratio matrix fit.
"""

from __future__ import annotations

import json

import numpy as np
import pytest
from scipy.optimize import linear_sum_assignment

from moodify_experimental.mamse008 import (
    NMFConfig,
    NMFUnavailableError,
    activation_sparsity,
    beta_divergence,
    canonicalize_factors,
    component_cosine_similarity,
    evidence_summary,
    fit_nmf,
    load_result,
    project_h,
    save_result,
)

RNG = np.random.default_rng(8)


def synthetic(rank=3, f=64, t=90, noise=0.003):
    x = np.linspace(0, 1, f)
    W = np.stack([
        np.exp(-0.5 * ((x - 0.18) / 0.07) ** 2),
        np.exp(-0.5 * ((x - 0.50) / 0.09) ** 2),
        np.exp(-0.5 * ((x - 0.82) / 0.06) ** 2),
    ], axis=1)[:, :rank]
    tt = np.linspace(0, 1, t)
    H = np.stack([
        0.2 + 0.8 * np.exp(-0.5 * ((tt - 0.22) / 0.10) ** 2),
        0.15 + 0.7 * np.exp(-0.5 * ((tt - 0.55) / 0.14) ** 2),
        0.1 + 0.9 * np.exp(-0.5 * ((tt - 0.80) / 0.08) ** 2),
    ], axis=0)[:rank]
    V = W @ H + noise * RNG.random((f, t))
    return V, W, H


def test_nonnegative_factors():
    V, _, _ = synthetic()
    r = fit_nmf(V, NMFConfig(rank=3, max_iter=300))
    assert np.all(r.W >= 0)
    assert np.all(r.H >= 0)


def test_deterministic_nndsvd_rerun():
    V, _, _ = synthetic()
    cfg = NMFConfig(rank=3, max_iter=250, init="nndsvd")
    a = fit_nmf(V, cfg)
    b = fit_nmf(V, cfg)
    assert a.basis_id == b.basis_id
    assert np.allclose(a.W, b.W, atol=1e-10)
    assert np.allclose(a.H, b.H, atol=1e-10)


def test_negative_input_rejected():
    V, _, _ = synthetic()
    V[0, 0] = -0.1
    with pytest.raises(ValueError):
        fit_nmf(V)


def test_mixed_unit_signed_plane_rejected():
    # canonical-ScalePlane-like mixed matrix (dB + ratios + correlation)
    x = np.random.default_rng(3).standard_normal((30, 40))
    x[:, 0] = np.abs(x[:, 0])
    with pytest.raises(ValueError, match="nonnegative"):
        fit_nmf(x)


def test_zero_input_unavailable():
    with pytest.raises(NMFUnavailableError):
        fit_nmf(np.zeros((10, 20)))


def test_nan_mask_not_physical_zero():
    V, _, _ = synthetic()
    V[4:8, 20:30] = np.nan
    r = fit_nmf(V, NMFConfig(rank=3, max_iter=200))
    assert np.all(r.mask[4:8, 20:30] == 0)
    assert np.isfinite(r.relative_error)


def test_beta_divergences_are_nonnegative_and_zero_on_identity():
    V, _, _ = synthetic()
    for beta in (2.0, 1.0, 0.0):
        assert beta_divergence(V, V, beta) >= -1e-9
        assert beta_divergence(V, V, beta) < 1e-6


def test_rank3_reconstructs_known_rank3_mixture():
    V, _, _ = synthetic(noise=0.001)
    r = fit_nmf(V, NMFConfig(rank=3, max_iter=500, tol=1e-8))
    assert r.relative_error < 0.08


def test_correct_rank_beats_rank1():
    V, _, _ = synthetic(noise=0.001)
    r1 = fit_nmf(V, NMFConfig(rank=1, max_iter=300))
    r3 = fit_nmf(V, NMFConfig(rank=3, max_iter=300))
    assert r3.relative_error < r1.relative_error * 0.75


def test_recovered_components_align_with_true_factors():
    V, Wtrue, _ = synthetic(noise=0.0005)
    r = fit_nmf(V, NMFConfig(rank=3, max_iter=700, tol=1e-9))
    sim = component_cosine_similarity(Wtrue, r.W)
    rows, cols = linear_sum_assignment(-sim)
    assert float(np.mean(sim[rows, cols])) > 0.88


def test_canonicalization_resolves_scale_and_permutation():
    V, _, _ = synthetic()
    r = fit_nmf(V, NMFConfig(rank=3, max_iter=250))
    W = r.W[:, [2, 0, 1]] * np.array([2.0, 0.5, 4.0])[None, :]
    H = r.H[[2, 0, 1], :] / np.array([2.0, 0.5, 4.0])[:, None]
    Wc, Hc, _ = canonicalize_factors(W, H)
    assert np.allclose(Wc @ Hc, r.W @ r.H, atol=1e-8)
    assert np.allclose(np.sum(Wc, axis=0), 1.0, atol=1e-10)


def test_frozen_basis_residual_detects_out_of_subspace_event():
    V, _, _ = synthetic(t=120, noise=0.0005)
    train = V[:, :70]
    basis = fit_nmf(train, NMFConfig(rank=3, max_iter=500)).W
    V2 = V.copy()
    V2[58:63, 88:96] += 0.8
    _, _, residual = project_h(V2, basis, max_iter=400)
    baseline = np.median(residual[10:60])
    anomaly = np.median(residual[88:96])
    assert anomaly > baseline * 4


def test_project_h_shapes():
    V, _, _ = synthetic()
    basis = fit_nmf(V[:, :50], NMFConfig(rank=3, max_iter=200)).W
    H, Y, rr = project_h(V, basis)
    assert H.shape == (3, V.shape[1])
    assert Y.shape == V.shape
    assert rr.shape == (V.shape[1],)


def test_hoyer_sparsity_order():
    sparse = np.array([1, 0, 0, 0, 0], dtype=float)
    dense = np.ones(5)
    assert activation_sparsity(sparse) > activation_sparsity(dense)


def test_evidence_has_no_semantic_source_labels():
    V, _, _ = synthetic()
    r = fit_nmf(V, NMFConfig(rank=3, max_iter=200))
    e = evidence_summary(r)
    assert e["component_semantics"].startswith("anonymous")
    assert all(c["semantic_label"] is None for c in e["components"])


def test_save_result_round_trip(tmp_path):
    V, _, _ = synthetic()
    axis = np.geomspace(50, 16000, V.shape[0])
    times = np.arange(V.shape[1]) * 0.1
    r = fit_nmf(V, NMFConfig(rank=3, max_iter=200), axis=axis)
    save_result(r, tmp_path, axis=axis, frame_times_s=times)
    data = json.loads((tmp_path / "nmf_summary.json").read_text(encoding="utf-8"))
    arr = np.load(tmp_path / "nmf_factors.npz")
    assert data["basis_id"] == r.basis_id
    assert arr["W"].shape == r.W.shape
    assert arr["H"].shape == r.H.shape
    assert (tmp_path / "mamse008_manifest.json").exists()


def test_frozen_basis_reopen_and_project(tmp_path):
    V, _, _ = synthetic()
    train = V[:, :50]
    basis_fit = fit_nmf(train, NMFConfig(rank=3, max_iter=250))
    save_result(basis_fit, tmp_path)
    loaded = load_result(tmp_path)
    assert loaded["summary"]["basis_id"] == basis_fit.basis_id
    H, Y, rr = project_h(V[:, 50:], loaded["W"])
    assert H.shape == (3, V[:, 50:].shape[1])
    assert np.all(rr >= 0)


def test_deterministic_evidence_serialization(tmp_path):
    V, _, _ = synthetic()
    a = fit_nmf(V, NMFConfig(rank=3, max_iter=200))
    save_result(a, tmp_path / "a")
    save_result(a, tmp_path / "b")
    ja = json.loads((tmp_path / "a" / "nmf_summary.json").read_text(encoding="utf-8"))
    jb = json.loads((tmp_path / "b" / "nmf_summary.json").read_text(encoding="utf-8"))
    ja.pop("config")
    jb.pop("config")
    assert ja == jb


def test_band_ratio_matrix_fits():
    # canonical S1 band-ratio style input: rows = 8 bands, cols = frames,
    # nonnegative simplex columns generated from a low-rank (2) mixture
    rng = np.random.default_rng(11)
    w1 = rng.dirichlet(np.ones(8))
    w2 = rng.dirichlet(np.ones(8))
    t = np.linspace(0, 1, 120)
    h1 = 0.4 + 0.6 * np.exp(-0.5 * ((t - 0.3) / 0.15) ** 2)
    h2 = 0.4 + 0.6 * np.exp(-0.5 * ((t - 0.7) / 0.15) ** 2)
    raw = w1[:, None] * h1[None, :] + w2[:, None] * h2[None, :]
    V = raw / raw.sum(axis=0, keepdims=True)  # simplex columns
    r = fit_nmf(V, NMFConfig(rank=2, max_iter=300))
    assert np.all(r.W >= 0) and np.all(r.H >= 0)
    assert r.relative_error < 0.2
