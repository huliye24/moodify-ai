# Moodify Sound Protocol (MSP) 0.1

**Status:** implemented local CLI contract; not a network protocol or deployed service.

Moodify is a sound-processing protocol and reference runtime for humans, AI systems and agents. An agent writes a declarative JSON job, validates it, then explicitly invokes processing through the shared Moodify Core. The CLI prints one JSON result to stdout; validation and processing errors print JSON to stderr and exit with code 2.

## Job

```json
{
  "protocol": "moodify.sound/0.1",
  "source": "audio/source.wav",
  "preset": "clean_master",
  "output_dir": "outputs"
}
```

Paths are resolved relative to the job file. The four keys are required; unknown keys and unknown presets are rejected. Supported presets are `clean_master`, `warm_vocal`, and `wide_space`. Supported input extensions are WAV, FLAC, MP3, AIFF, and M4A; actual decoding depends on the installed audio libraries. Existing outputs are never intentionally overwritten.

```powershell
moodify protocol validate job.json
moodify protocol process job.json
```

The `process` command calls the existing `v01_pipeline.process_audio`, not a second DSP implementation. It writes a WAV and the Core's adjacent diagnosis report. Stdout returns the source and output SHA-256 hashes, exact preset parameters, diagnosis, and `status: processed_review_required`. This is evidence of *what ran*, not evidence that audio quality, identity preservation, or commercial readiness passed. A human must listen and approve distribution. Agents must not silently treat this status as `verified`.

## Scope and next version

MSP/0.1 exposes explicit preset-based processing only. The richer, editable Mix Graph with bypass/rollback and before/after verification remains a target, not an implemented claim. Future protocol versions should introduce a serializable graph and stronger acoustic verification without changing the shared-Core rule. Version strings are exact; incompatible jobs must fail rather than be guessed into a new format.
