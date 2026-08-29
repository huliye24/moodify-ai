# Delivery Invariants

## DLV-INV-01 — READY Only
Formal playback entry is issued only for READY tracks.

## DLV-INV-02 — No Long-Lived Cloud Secret
Mobile clients hold no long-lived OSS/DB credential.

## DLV-INV-03 — URI Is Replaceable
A signed/proxy playback URI is not Track identity.

## DLV-INV-04 — Track Identity Is Stable
Track ID survives URL expiry, delivery provider change and session refresh.

## DLV-INV-05 — Authorization Before Delivery
Access is checked before issuing a playable entry.

## DLV-INV-06 — Expiry Is Recoverable
Expired delivery credentials can refresh without reprocessing.

## DLV-INV-07 — Seekable Delivery
Production format/delivery supports reasonable range/seek semantics.

## DLV-INV-08 — Internal Complexity Hidden
Client does not depend on stem/analysis/judgment/intervention internals.

## DLV-INV-09 — Playback Failure Is Not Production Failure
Playback problems do not mutate READY compute state.

## DLV-INV-10 — Delivery Evidence Is Separate
Playback evidence does not overwrite production evidence.

## DLV-INV-11 — Render Traceability
Playback sessions can be traced to render object/version.

## DLV-INV-12 — No Accidental Internal Asset Exposure
Source, stems and internal evidence are not exposed by default.
