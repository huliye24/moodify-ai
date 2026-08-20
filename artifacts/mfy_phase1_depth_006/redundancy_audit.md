# Redundancy Audit

## Resolved

- One persistent decoded PCM node supplies all downstream nodes.
- Cold run decodes once; identical warm run decodes zero times.
- Measurements, representation, events, judgment and evidence are cached independently.
- Rule-only changes reuse decode, measurements and representation.
- Representation S3 consumes the already-computed global measurement node instead of calling `compute_metrics` again.

## Transform audit

Temporal spectrum uses 1000/250 ms windows, while representation spectra use
400/100 and 2000/500 ms windows. These are semantically different transforms and
must not be conflated. No identical parameterized spectral transform remains in the
canonical execution graph.
