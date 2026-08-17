# MFY-CR-P02 — Unresolved

Items that affect P03+ planning. None blocks P02 completion.

## 1. Reconstruction Cloud vs Listening Environment service boundaries

The constitution defines conceptual boundaries. Concrete API/module ownership
(Layer 2 vs Layer 3) is not yet assigned to code paths — must be decided before
P08 (Cloud Reconstruction Job) so no new module layout is invented later.

## 2. Existing system reclassification mechanics

Reclassification is documented; nothing enforces it yet (no labels in code).
A future governance pass could add a machine-readable mapping (e.g. in
`docs/` metadata or a registry) — deferred, not required by P02.

## 3. Human artistic authority operational model

The constitution preserves human authority but does not define the review
workflow for reconstruction decisions (who reviews, when, with what tooling).
P03+ must not invent a second Human Review system — reuse the existing
`MFY-HUMAN-REVIEW-001` machinery.

## 4. README/AGENTS identity wording drift

`docs/REPOSITORY_STATUS.md` and older snapshots still carry the pre-reconstruction
identity wording. Kept as dated records; if they are ever republished they
should reference the Constitution.

## 5. Carried over from P01

- Android dual line decision (apps/android vs apps/music-android).
- Gradle wrapper strategy for music-android.
- Large evidence bundles offline storage.
- PR #21 close decision; push strategy for the baseline branch.
