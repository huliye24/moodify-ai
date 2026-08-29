"""MAMSE-007 synthetic gates (14 reference + 2 semantic preflight).

Rank-3 recovery, reconstruction monotonicity, unit scaling, deterministic
sign, missing imputation evidence, high-missing drop, constant drop, frozen
projection without refit, feature order fail-closed, out-of-subspace
residual, variance validity, deterministic basis id, serialization,
CASE_LOCAL non-comparability, S1/S2 semantic conflict exclusion.
"""

from __future__ import annotations

import json

import numpy as np
import pytest

from moodify_experimental.mamse007 import (
    PCAConfig,
    basis_eligible_feature_names,
    fit_pca,
    latent_auditory_matrix,
    load_basis,
    preflight_features,
    project_with_basis,
    save_result,
)

FEATURES = (
    "rms_db", "peak_db", "spectral_centroid_hz", "band_bass_ratio",
    "band_presence_ratio", "band_air_ratio", "stereo_correlation",
    "crest_db", "hf_ratio", "phase_risk_proxy",
)


def test_rank3_latent_structure_explained():
    x, _ = latent_auditory_matrix(600)
    r = fit_pca(x, FEATURES, PCAConfig(n_components=3))
    assert sum(r.basis.explained_variance_ratio) > 0.90


def test_reconstruction_error_decreases_with_more_components():
    x, _ = latent_auditory_matrix(500)
    r1 = fit_pca(x, FEATURES, PCAConfig(n_components=1))
    r3 = fit_pca(x, FEATURES, PCAConfig(n_components=3))
    assert r3.residual_norm.mean() < r1.residual_norm.mean()


def test_robust_scaling_prevents_hz_unit_domination():
    x, _ = latent_auditory_matrix(500)
    r = fit_pca(x, FEATURES, PCAConfig(n_components=3, scaling="robust"))
    centroid_idx = r.basis.retained_feature_names.index("spectral_centroid_hz")
    assert abs(r.basis.components[0, centroid_idx]) < 0.95


def test_sign_canonicalization_is_deterministic():
    x, _ = latent_auditory_matrix(420)
    a = fit_pca(x, FEATURES, PCAConfig(n_components=3))
    b = fit_pca(x, FEATURES, PCAConfig(n_components=3))
    assert np.allclose(a.basis.components, b.basis.components)
    for comp in a.basis.components:
        assert comp[np.argmax(np.abs(comp))] >= 0


def test_missing_cells_are_explicitly_imputed():
    x, _ = latent_auditory_matrix(300)
    x[10:20, 1] = np.nan
    r = fit_pca(x, FEATURES, PCAConfig(n_components=3, max_missing_fraction=.20))
    assert r.imputation_mask[:, r.basis.retained_feature_names.index("peak_db")].sum() == 10
    assert r.evidence["imputed_cells"] == 10


def test_excessively_missing_feature_is_dropped():
    x, _ = latent_auditory_matrix(300)
    x[:100, 1] = np.nan
    r = fit_pca(x, FEATURES, PCAConfig(n_components=3, max_missing_fraction=.20))
    assert "peak_db" not in r.basis.retained_feature_names
    assert any(d["feature"] == "peak_db" and d["reason"] == "TOO_MISSING" for d in r.basis.dropped_features)


def test_constant_feature_is_dropped():
    x, _ = latent_auditory_matrix(300)
    x[:, 0] = -18.0
    r = fit_pca(x, FEATURES, PCAConfig(n_components=3))
    assert "rms_db" not in r.basis.retained_feature_names


def test_frozen_basis_projection_does_not_refit():
    train, _ = latent_auditory_matrix(500, seed=1)
    test, _ = latent_auditory_matrix(120, seed=2)
    fitted = fit_pca(train, FEATURES, PCAConfig(n_components=3, mode="CORPUS_FROZEN"))
    proj = project_with_basis(test, FEATURES, fitted.basis)
    assert proj.basis.basis_id == fitted.basis.basis_id
    assert proj.evidence["mode"] == "PROJECTION_ONLY"


def test_feature_schema_mismatch_fails_closed():
    train, _ = latent_auditory_matrix(300)
    fitted = fit_pca(train, FEATURES, PCAConfig(n_components=3, mode="CORPUS_FROZEN"))
    with pytest.raises(ValueError, match="FEATURE_SCHEMA_MISMATCH"):
        project_with_basis(train[:, ::-1], tuple(reversed(FEATURES)), fitted.basis)


def test_out_of_subspace_segment_has_larger_residual():
    train, _ = latent_auditory_matrix(600, seed=3)
    test, _ = latent_auditory_matrix(220, seed=4, anomaly=(90, 120))
    fitted = fit_pca(train, FEATURES, PCAConfig(n_components=3, mode="CORPUS_FROZEN"))
    proj = project_with_basis(test, FEATURES, fitted.basis)
    baseline = np.r_[proj.residual_norm[:80], proj.residual_norm[140:]]
    anomalous = proj.residual_norm[90:120]
    assert np.median(anomalous) > np.median(baseline) * 2.0


def test_explained_variance_ratios_are_valid():
    x, _ = latent_auditory_matrix(350)
    r = fit_pca(x, FEATURES, PCAConfig(n_components=5))
    assert np.all(r.basis.explained_variance_ratio >= 0)
    assert r.basis.explained_variance_ratio.sum() <= 1.0 + 1e-12
    assert np.all(np.diff(r.basis.singular_values) <= 1e-12)


def test_basis_id_is_deterministic():
    x, _ = latent_auditory_matrix(360)
    a = fit_pca(x, FEATURES, PCAConfig(n_components=3, mode="CORPUS_FROZEN"))
    b = fit_pca(x.copy(), FEATURES, PCAConfig(n_components=3, mode="CORPUS_FROZEN"))
    assert a.basis.basis_id == b.basis.basis_id


def test_serialization_round_trip(tmp_path):
    x, _ = latent_auditory_matrix(300)
    r = fit_pca(x, FEATURES, PCAConfig(n_components=3, mode="CORPUS_FROZEN"))
    save_result(r, tmp_path)
    b = load_basis(tmp_path / "pca_evidence.json")
    assert b.basis_id == r.basis.basis_id
    assert np.allclose(b.components, r.basis.components)
    raw = json.loads((tmp_path / "pca_evidence.json").read_text(encoding="utf-8"))
    assert raw["evidence"]["operator"] == "MAMSE-007"
    assert (tmp_path / "mamse007_manifest.json").exists()


def test_case_local_basis_is_explicitly_marked_non_comparable():
    x, _ = latent_auditory_matrix(300)
    r = fit_pca(x, FEATURES, PCAConfig(n_components=3, mode="CASE_LOCAL"))
    assert r.basis.mode == "CASE_LOCAL"
    assert any("not cross-case comparable" in s for s in r.evidence["interpretation_limits"])


def test_preflight_s1_mid_side_conflict_excluded():
    records = preflight_features(("mid_energy", "side_energy", "rms_db"))
    assert [r.status for r in records] == ["SEMANTIC_CONFLICT", "SEMANTIC_CONFLICT", "UNRESOLVED"]
    retained, dropped = basis_eligible_feature_names(records)
    assert "mid_energy" not in retained and "side_energy" not in retained
    assert any(d["reason"] == "IMPL_IS_LINEAR_ENERGY_NOT_RATIO" for d in dropped)


def test_preflight_s2_short_term_lufs_conflict_excluded():
    records = preflight_features(("short_term_lufs", "crest_db"))
    assert records[0].status == "SEMANTIC_CONFLICT"
    assert records[0].reason == "IMPL_IS_RMS_PROXY_NOT_LUFS"
    retained, dropped = basis_eligible_feature_names(records)
    assert "short_term_lufs" not in retained
    assert any(d["feature"] == "short_term_lufs" for d in dropped)
