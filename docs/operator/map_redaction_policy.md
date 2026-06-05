# MAP Report Redaction Policy v0.2

**MHP**: MHP-888
**Effective**: 2026-06-05

## Redaction Levels

| Level | Audience | Artifacts Included | Artifacts Excluded |
|-------|----------|-------------------|-------------------|
| **Full** | Operator, Engineer | All 10 artifacts | Nothing |
| **Standard** | Artist, Producer | WAV, PDF report, before/after spectrum PNGs | JSON report, manifest.json, metadata.json, environment.txt, validation_report.json, MAP_CHAIN_VERSION |
| **Public** | Listener, Distribution | Processed WAV only | All reports, charts, metadata, validation |

## Level Decision Matrix

| Use Case | Recommended Level |
|----------|-------------------|
| Internal engineering review | Full |
| Nightly automated processing | Full |
| Delivering to artist for approval | Standard |
| Sending to mastering engineer | Standard |
| Publishing to streaming platform | Public |
| Sharing on social media | Public |

## What Each Level Hides

### Standard hides:
- MRS scores (proprietary scoring)
- Damage loss metrics (internal quality metric)
- Git hash and platform (infrastructure detail)
- Dependency versions (security surface)
- SHA256 hashes (unnecessary for artists)

### Public hides:
- All of the above
- Before/after comparison charts
- PDF analysis report

## Implementation

Redaction is currently manual. The operator selects which files to share based on the audience. Automated redaction (script that copies only allowed files) is deferred to MAP v0.3.

## Example: Manual Redaction for Artist Delivery

```bash
mkdir -p delivery/artist_track/
cp outputs/track_clean_master.wav delivery/artist_track/
cp outputs/track_clean_master_report.pdf delivery/artist_track/
cp outputs/track_before_spectrum.png delivery/artist_track/
cp outputs/track_clean_master_after_spectrum.png delivery/artist_track/
# Artist receives: 1 WAV + 1 PDF + 2 PNGs = 4 files
```
