# Moodify Technology Stack

**Document status:** Repository-backed technology inventory

**Verification note:** Inclusion means the technology is present in repository code, declared dependencies, or referenced operational tooling. It does not by itself mean a component is deployed or production-validated.

## Language and Runtime

- **Python 3.10+** — core analysis, processing, API, and workflow implementation.
- **Node.js** — queue and worker components documented in the repository’s verified runtime status.

## Audio I/O and Processing

- **FFmpeg / FFprobe** — decode, probing, transcoding, and spectrogram-related paths; external system dependency.
- **SoundFile** — native audio loading for supported formats.
- **librosa** — fallback loading, time-frequency analysis, feature extraction, resampling, onset analysis, and spectral utilities.
- **Pedalboard** — rule-based DSP processing chain.

## Analysis and Measurement

- **pyloudnorm** — LUFS measurement where available, with documented fallbacks in selected code paths.
- **NumPy** and **SciPy** — numerical arrays, signal-processing operations, and analysis support.
- **Matplotlib** — spectrum and evidence visualizations.
- Implemented measures include loudness-related values, band energy, dynamic range, and stereo correlation.

## APIs and Data Contracts

- **FastAPI** and **Uvicorn** — Python REST API services and local serving paths.
- **Pydantic** — validated Python data models and contracts.
- JSON and schema files under `schemas/` — structured records for canonical assets and evidence-oriented workflows.

## Infrastructure Status

The repository contains cloud-operation, queue/worker, API, and data-factory components. Verified runtime evidence records two VPS environments and a running Node queue/worker; the full Ear processing chain has no verified production traffic. Object storage and cloud AI inference must not be assumed available.

Accordingly, “cloud deployment ready” is not used as a capability claim. Deployment readiness is a per-component operational question requiring environment-specific verification.

## Explicit Non-Claims

This stack does not establish the existence of:

- a trained audio foundation model;
- a production reward or preference model;
- a public enterprise API offering;
- universally valid audio-quality scoring;
- verified cloud AI inference.
