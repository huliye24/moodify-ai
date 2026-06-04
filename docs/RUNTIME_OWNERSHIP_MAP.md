# Runtime Governance and Ownership Map — MHP-138

**E-Chain**: ECHAIN-MOODIFY-RUNTIME-001

## Module Ownership

| Module | Primary Owner | Reviewers |
|--------|--------------|-----------|
| runner.py | Raphael Davad | Runtime NEM |
| supervisor.py | Runtime NEM | Build NEM |
| runtime_state.py | Runtime NEM | Build NEM |
| runtime_events.py | Runtime NEM | Probe NEM |
| runtime_failures.py | Runtime NEM | Build NEM |
| operator_console.py | Raphael Davad | Studio OS NEM |
| operator_api.py | Raphael Davad | Studio OS NEM |
| cli.py | Raphael Davad | All NEMs |
| config.py | System NEM | All NEMs |

## Change Policy

- **runner.py**: Requires Gate 2 validation (6h run + failure injection)
- **supervisor.py/runtime_state.py**: Changes must pass 7 supervisor tests
- **operator_api.py**: Contract tests must pass before merge
- **config.py**: Must update all runtime profiles (dev + prod)

## Version

Runtime Manifest v0.2.0 — see `docs/RUNTIME_MANIFEST.md`.
