# Basic Pitch and MuseScore LA Deployment Evidence

- Date: 2026-08-16
- Host role: Moodify production LA origin/worker node
- Host address: `103.144.246.242`
- Operating system: Ubuntu 22.04.2 LTS, x86_64
- Capacity observed before deployment: 4 vCPU, 7.7 GiB RAM, 82 GiB free disk
- Change classification: canonical cloud capability runtime; no new queue or
  product state machine

## Installed capabilities

### Basic Pitch

- Isolated runtime: `/opt/moodify/capabilities/basic-pitch/venv`
- Runner: `/opt/moodify/capabilities/bin/moodify-basic-pitch`
- Runtime versions: Basic Pitch 0.4.0, TFLite Runtime 2.14.0, NumPy 1.26.4,
  Setuptools 80.9.0
- Isolation reason: TFLite Runtime 2.14 uses the NumPy 1.x ABI, while the
  canonical Moodify environment uses NumPy 2.x.
- Dependency check: `pip check` reported no broken requirements.

### MuseScore

- Package: Ubuntu `musescore3` 3.2.3+dfsg2-11
- Runner: `/opt/moodify/capabilities/bin/moodify-musescore-export`
- Execution mode: Qt `offscreen`, no synthesizer, no MIDI device, bounded
  300-second timeout
- Writable state: `/var/lib/moodify/capabilities/musescore`

## Reproducibility

The deployed runner and pin-file hashes match the repository copies:

| File | SHA-256 |
|---|---|
| `moodify-basic-pitch` | `7e5a7648743ae7d26db6cf8a2efe35660d002581520453b374104ffe876001c8` |
| `moodify-musescore-export` | `15df942424dd6ebbfcce4fb55043f27afe1907aa2033ff0a8a1649e8d48044fd` |
| `requirements.txt` | `d0f7de0417ea51dbdbf03815fee36a7eefe936c2377dad04aa6ea745fc0d8a0a` |

## End-to-end smoke test

The server generated a synthetic 3-second C5 sine-wave input and executed:

```text
WAV -> Basic Pitch -> MIDI + note-event CSV -> MuseScore -> PDF
```

- Total runner time: 4 seconds
- WAV: 264,678 bytes,
  `9cdfd0c94b5e735500118e20dd73ed2caa27ea4b08993122e92c9a1fcad9b2c9`
- MIDI: 831 bytes,
  `2ce1fd6855f92ab499672d5242a78dab2c7609c462113d625c5f2a16f1563b6c`
- Note-event CSV: 612 bytes
- PDF: 19,745 bytes,
  `7acfda714ddc7e71411e556098a75729b9bfa86f2462ef33ca1ea7e00a087cc8`

Smoke artifacts are retained under
`/var/lib/moodify/capabilities/smoke-20260816-runner` for operator inspection.

## Production verification and failure behavior

- `moodify-api`, `moodify-worker`, `moodify-music`, and `nginx` remained active.
- Ear API `/api/v1/health` returned `status=ok`.
- Music BFF `/health` returned `status=ok`.
- Runner input absence returns a typed non-zero process result.
- MuseScore execution is bounded to five minutes.
- Capability output is not yet wired into the public API or canonical queue;
  this deployment proves runtime readiness only.

## Operator follow-up

The host already reports `/var/run/reboot-required` for libc, systemd, and a
new kernel. No reboot was performed because that would interrupt production
services and requires an explicit maintenance window.
