# MAMSE-012 — Release Gate

**Date:** 2026-08-11
**Verdict:** `EXPERIMENTAL_ACCEPTED` — graph signal processing / auditory topology layer, off by default, **R2 VERIFIED (synthetic)**. Real-case structural evidence recorded; incremental-value questions (G31) are open for the September corpus study.

## Acceptance gates G1–G33

| Gate | Status | Evidence |
|---|---|---|
| G1–G5 contracts | **Pass** — unique ids, legal edges, self-loop/negative/heterogeneous rejected |
| G6 graph_id | **Pass** — order-independent; canonical signal axis |
| G7–G9 Laplacian | **Pass** — symmetric PSD; zero eigenvalues = components |
| G10–G12 GFT | **Pass** — constant→0 Dirichlet, round-trip, deterministic sign |
| G13–G15 localization | **Pass** — break → 10× Dirichlet, 2× high-freq, LV localizes node |
| G16–G17 filters | **Pass** — heat smooths, polynomial eigen-free |
| G18–G22 semantics | **Pass** — topology≠Hz boundary in evidence; no psychoacoustic claim; event semantics preserved; no musical labels; negative corr never abs'd |
| G23–G24 evidence | **Pass** — authority/provenance saved, JSON/NPZ/manifest reopen |
| G25–G27 resource | **Pass** — dense guard (512), sparse eigsh path (800-node k=8 in 0.46 s), benchmark N/E/runtime |
| G28 transform reuse | **Pass** — one build_representation per track |
| G29 blocked features | **Pass** — correlation graph on MAMSE-011 clean subset only |
| G30 real cases ≥ 4 | **Pass** — 3 tracks × 3 graph families = 9 case-scenarios (band/event/correlation per track) |
| G31 结构证据增量 | **Open** — recorded (AI case band hf 0.199 vs 0.10; LV peaks mid bands); value vs existing 2D metrics needs the September corpus study |
| G32 App 无膨胀 | **Pass** — research API only |
| G33 canonical 回归 | **Pass** — full suite green (522) |

## Constraints honored

1. Graph frequency = topology frequency, not acoustic Hz (every evidence file carries the boundary).
2. Edges express selected relations, not causality; v0.1 undirected + nonnegative + homogeneous only.
3. Event graph preserves TemporalEvent semantics; no forbidden musical labels invented.
4. Dense eigendecomposition guarded; large graphs partial sparse.
5. No canonical measurement / TemporalEvent / AuditoryRepresentation changes.

## Honest negatives

1. Band-graph signals are 8-bin median profiles — coarse; no perceptual claim.
2. AI-case band hf ratio (0.199) is descriptive, not a detector.
3. G31 (structural evidence increment over existing metrics) not yet demonstrated; September corpus work needed.

## Maturity

```text
R0 Theory        ✅ task docs + principle PDF
R1 Operator      ✅ three graphs + GSP operators run (numpy/scipy)
R2 Synthetic     ✅ 24/24 gates, G1-G29 pass
R3 Case Proven   ⏸ open: structural-increment value on real corpus (September)
R4+              ⏸ product coupling
```

## Outstanding (non-blocking)

1. September: corpus study for G31 (structural evidence vs existing 2D metrics).
2. Signed/directed/multiplex graph extensions if a use case demands them.
3. Feature-bus transform/cache reuse (R4+).
