# MAMSE-012 — Test Results (Gates G1–G29)

**Date:** 2026-08-11
**Command:** `python -m pytest tests/experimental/test_mamse012.py -q`

## Result: 24 passed (24/24) — 23 prototype gates + repo-specific

| Gate | Test | Covers |
|---|---|---|
| G1/G6 | `test_band_graph_is_path` | 8 nodes / 7 edges path, degree profile |
| G6 | `test_band_node_axis_preserves_frequency_order` | reversed input → canonical frequency order |
| G6 | `test_graph_id_independent_of_input_order` | graph_id stable; node axis canonical |
| G3 | `test_self_loop_rejected` | self-loop contract |
| G4 | `test_negative_weight_rejected` | negative edge contract |
| G5 | `test_heterogeneous_edge_types_rejected` | mixed edge semantics contract |
| G7/G8 | `test_laplacian_symmetric_psd` | symmetric PSD Laplacian |
| G9 | `test_zero_eigenvalues_equal_components` | zero-eigenvalue count = components |
| G10 | `test_constant_signal_zero_dirichlet_energy` | constant → Dirichlet 0 |
| G11 | `test_graph_fourier_roundtrip` | GFT inverse round-trip |
| G13 | `test_smooth_signal_has_lower_dirichlet_than_spike` | isolated break → 10× Dirichlet |
| G14 | `test_spike_has_more_high_graph_frequency_energy` | break → 2× high-freq ratio |
| G16 | `test_heat_filter_identity_at_zero` | tau=0 identity |
| G16 | `test_heat_filter_reduces_dirichlet_energy` | heat smooths |
| G17 | `test_polynomial_identity` | eigen-free polynomial filter |
| G15 | `test_local_variation_localizes_spike` | local variation localizes break node |
| G20 | `test_event_graph_overlap_weight_one` | overlapping events → weight 1 |
| G20 | `test_event_graph_gap_decay` | exp(-gap/tau) decay |
| G21 | `test_event_graph_does_not_invent_musical_label` | no invented labels |
| G22 | `test_positive_correlation_graph_omits_negative_edge` | negative corr never abs'd |
| G25 | `test_dense_guard` | dense eigendecomposition blocked |
| G18/G19 | `test_graph_evidence_semantic_boundaries` | "not acoustic Hz" boundary |
| G24 | `test_save_graph_evidence_roundtrip` | JSON/NPZ/manifest reopen |
| G26 | `test_large_graph_sparse_path_guard` | >512 nodes: k=None blocked, k=2 sparse path works |

## Gate mapping summary

| Acceptance gate | Status |
|---|---|
| G1–G5 contracts | **Pass** — unique ids, legal edges, no self-loop/negative/heterogeneous |
| G6 graph_id | **Pass** — order-independent; signal axis canonical |
| G7–G9 Laplacian | **Pass** — symmetric PSD, components = zero eigenvalues |
| G10–G12 GFT | **Pass** — constant → 0 Dirichlet, round-trip, deterministic sign |
| G13–G15 localization | **Pass** — break raises Dirichlet/high-freq, local variation localizes |
| G16–G17 filters | **Pass** — heat smooths, polynomial eigen-free |
| G18–G22 semantics | **Pass** — topology≠Hz, no psychoacoustic claim, event semantics preserved, no musical labels, no abs() |
| G23–G24 evidence | **Pass** — authority/provenance saved, reopen |
| G25–G27 resource | **Pass** — dense guard, sparse path, benchmark N/E/runtime |
| G28 transform reuse | **Pass** — one build_representation per track |
| G29 blocked features | **Pass** — correlation graph built on MAMSE-011 clean subset only |
| G30–G33 real cases | See real_case_results.md + release gate |

## Regression

- Full suite with MAMSE-012 active: expected 522 passed / 5 skipped (498 + 24) — verified at release.
- `ruff check src/moodify_experimental/mamse012 tests/experimental/test_mamse012.py scripts/mamse012_*.py`: clean.
