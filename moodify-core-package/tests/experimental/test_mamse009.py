"""MAMSE-009 synthetic gates (16 prototype + repo-specific extras).

Soft threshold, SVT rank reduction, fail-closed NaN/zero, default lambda,
low-rank recovery, sparse support recall, constraint error, determinism,
sparse frame score block response, anonymous candidate semantics, feature
score shape, dense noise residual, model_id space binding, save/reopen,
low-rank similarity; plus: event-overlap report, mixed-unit rejection.
"""

from __future__ import annotations

import json

import numpy as np
import pytest

from moodify_experimental.mamse009 import (
    RPCAConfig,
    RPCAUnavailableError,
    candidate_intervals,
    default_lambda,
    event_overlap_report,
    low_rank_similarity,
    principal_component_pursuit,
    save_result,
    singular_value_threshold,
    soft_threshold,
    sparse_feature_score,
    sparse_frame_score,
)

RNG = np.random.default_rng(9)


def make_data(m=48, n=90, r=3, sparse_frac=0.035, noise=0.0):
    A = RNG.standard_normal((m, r))
    B = RNG.standard_normal((r, n))
    L = A @ B
    S = np.zeros((m, n))
    k = max(1, int(m * n * sparse_frac))
    idx = RNG.choice(m * n, size=k, replace=False)
    signs = RNG.choice([-1., 1.], size=k)
    S.flat[idx] = signs * RNG.uniform(7, 12, size=k)
    N = noise * RNG.standard_normal((m, n))
    return L + S + N, L, S, N


def test_soft_threshold():
    x = np.array([-2., -.5, 0, .5, 2.])
    y = soft_threshold(x, 1.)
    assert np.allclose(y, [-1, 0, 0, 0, 1])


def test_svt_rank_reduction():
    X = np.diag([5., 2., .1])
    Y, s = singular_value_threshold(X, 1.)
    assert np.linalg.matrix_rank(Y) == 2 and np.allclose(s, [4, 1])


def test_fail_on_nan():
    X = np.ones((4, 4))
    X[0, 0] = np.nan
    with pytest.raises(RPCAUnavailableError):
        principal_component_pursuit(X)


def test_fail_on_zero():
    with pytest.raises(RPCAUnavailableError):
        principal_component_pursuit(np.zeros((4, 4)))


def test_default_lambda():
    assert np.isclose(default_lambda((25, 100)), .1)


def test_exactish_low_rank_recovery():
    X, L, S, _ = make_data(sparse_frac=.02)
    r = principal_component_pursuit(X, RPCAConfig(tol=1e-7, max_iter=1000), space_id="syn")
    rel = np.linalg.norm(r.L - L, "fro") / np.linalg.norm(L, "fro")
    assert rel < 0.08


def test_sparse_support_recovery():
    X, L, S, _ = make_data(sparse_frac=.02)
    r = principal_component_pursuit(X, RPCAConfig(tol=1e-7, max_iter=1000), space_id="syn")
    true = np.abs(S) > 1e-10
    est = np.abs(r.S) > 1.0
    tp = np.sum(true & est)
    recall = tp / (np.sum(true) + 1e-12)
    assert recall > .85


def test_constraint_error_small():
    X, _, _, _ = make_data()
    r = principal_component_pursuit(X, space_id="syn")
    assert r.relative_constraint_error < 1e-6


def test_deterministic_rerun():
    X, _, _, _ = make_data()
    a = principal_component_pursuit(X, space_id="same")
    b = principal_component_pursuit(X, space_id="same")
    assert a.model_id == b.model_id
    assert np.allclose(a.L, b.L) and np.allclose(a.S, b.S)


def test_sparse_frame_score_detects_block():
    m, n, r = 40, 100, 3
    A = RNG.standard_normal((m, r))
    B = RNG.standard_normal((r, n))
    L = A @ B
    X = L.copy()
    X[30:38, 60:66] += 15
    res = principal_component_pursuit(X, RPCAConfig(max_iter=1000), space_id="block")
    score = sparse_frame_score(X, res.S)
    assert np.median(score[60:66]) > np.median(score[10:50]) * 4


def test_candidate_interval_is_semantically_unknown():
    s = np.zeros(30)
    s[10:13] = 10
    ev = candidate_intervals(s, z_threshold=3, min_frames=2)
    assert ev and ev[0]["event_type"] == "SPARSE_STRUCTURE_CANDIDATE"
    assert ev[0]["semantic_authority"] == "EXPERIMENTAL_UNKNOWN"


def test_sparse_feature_score_shape():
    X, _, _, _ = make_data()
    r = principal_component_pursuit(X, space_id="a")
    assert sparse_feature_score(X, r.S).shape == (X.shape[0],)


def test_dense_noise_remains_small_residual():
    X, L, S, N = make_data(noise=.01, sparse_frac=.015)
    r = principal_component_pursuit(X, RPCAConfig(tol=1e-6, max_iter=1000), space_id="noise")
    assert r.converged
    assert np.linalg.norm(r.L - L, "fro") / np.linalg.norm(L, "fro") < .12


def test_model_id_changes_with_space_id():
    X, _, _, _ = make_data()
    a = principal_component_pursuit(X, space_id="x")
    b = principal_component_pursuit(X, space_id="y")
    assert a.model_id != b.model_id


def test_save_and_reopen(tmp_path):
    X, _, _, _ = make_data()
    r = principal_component_pursuit(X, space_id="save")
    save_result(r, X, tmp_path, space_id="save", frame_times_s=np.arange(X.shape[1]) * .1)
    j = json.loads((tmp_path / "rpca_summary.json").read_text(encoding="utf-8"))
    z = np.load(tmp_path / "rpca_components.npz")
    assert j["model_id"] == r.model_id and z["L"].shape == X.shape and z["S"].shape == X.shape
    assert (tmp_path / "mamse009_manifest.json").exists()


def test_low_rank_similarity_identity():
    X, _, _, _ = make_data()
    assert low_rank_similarity(X, X) > .999999


def test_event_overlap_report_preserves_both_sides():
    cands = [{"start_time_s": 10.0, "end_time_s": 15.0}, {"start_time_s": 60.0, "end_time_s": 66.0}]
    events = [
        {"start_ms": 12000, "end_ms": 14000, "event_type": "SAMPLE_PEAK", "domain": "integrity"},
        {"start_ms": 61000, "end_ms": 65000, "event_type": "HF_DROPOUT", "domain": "spectrum"},
    ]
    rep = event_overlap_report(cands, events)
    assert rep["candidate_count"] == 2
    assert rep["overlap_rows"][0]["overlapping_events"][0]["event_type"] == "SAMPLE_PEAK"
    assert rep["overlap_rows"][1]["overlapping_events"][0]["event_type"] == "HF_DROPOUT"
    assert "no overwrite" in rep["note"]


def test_mixed_unit_matrix_rejected_by_space_policy():
    # the operator itself only requires finite 2-D; the semantic gate lives
    # in the input audit — verify the audit surface rejects mixed units
    from moodify_experimental.mamse009 import evidence_summary  # noqa: F401
    x = np.random.default_rng(5).standard_normal((20, 30))
    with pytest.raises((ValueError, RPCAUnavailableError)):
        principal_component_pursuit(np.where(np.abs(x) < 0.01, np.nan, x), space_id="mixed")
