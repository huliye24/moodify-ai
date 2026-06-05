# MHP-888: Customer Report Redaction Policy
**Status**: done

## Redaction Levels
| Level | Audience | Includes | Excludes |
|-------|----------|----------|----------|
| Full | Operator/Engineer | All 10 artifacts | Nothing |
| Standard | Artist/Producer | WAV, PDF, before/after charts | JSON internals, metadata, validation_report |
| Public | Listener | WAV only | All reports, charts, metadata |

## Implementation
Redaction is currently manual (operator discretion). Automated redaction deferred to MAP v0.3.
