# HOTFIX 000 — Measurement Correctness

Correctness note for the four defects found during local desktop acceptance
(`MOODIFY_DESKTOP_LOCAL_ACCEPTANCE_001`, 2026-10-04).

> This note records what was wrong, why it mattered, and what is still
> deliberately unresolved. It is not a strategy document.

---

## Why this was release-blocking

The intended Agent control loop reads machine measurements and then chooses an
intervention:

```text
Analyze → read measurements → Diagnose → Plan → Process → Verify
```

A measurement tool that returns a *plausible but wrong* number is more
dangerous than one that fails loudly: the error is invisible and propagates
into every downstream decision. `Measurement Correctness > Feature Expansion`
for this stage.

---

## F1 — Stereo integrated loudness was 3.01 dB low

**Root cause.** In `auditory/loudness.py` the per-channel K-weighted energies
were aggregated as a *mean over channels*:

```python
combined = np.sum(energies, axis=0) / sum(weights)   # wrong
```

BS.1770 aggregates by **summing** the channel-weighted powers
(`L_K = -0.691 + 10·log10(Σ_i G_i · z_i)`). Dividing by `Σ weights` biases
every stereo measurement by `-10·log10(2) = -3.0103 dB`. For mono the divisor
is 1, so the bug was invisible on mono material.

**Fix.** Removed the division; the weighted energies are summed.

## F2 — `sample_peak_dbfs` and `rms_dbfs` measured a mono downmix

**Root cause.** In `auditory/metrics.py`, `true_peak_dbfs` was measured per
channel, but peak and RMS were taken from `mono = samples.mean(axis=1)`. One
report therefore mixed two signal domains: an asymmetric mix under-reported its
own sample peak (a +0.50/−0.01 stereo pair reported −12.03 dBFS instead of
−6.02 dBFS) and disagreed with its own true peak.

**Fix.** Both now span every channel. RMS is *total energy over total sample
count*, which is the definition `execution/chunking.py::chunked_peak_rms`
already used, and what the registry calls "full-signal RMS".

## F3 — Defect-induced `CREST_FACTOR_COLLAPSE` false positive

**Not an independent bug.** `crest_factor_db = sample_peak_dbfs - rms_dbfs`, so
the F2 downmix error manufactured ~3 dB of crest factor the signal did not
have and tripped the 4.0 dB floor.

**Outcome: A** — correcting the measurements removes the false positive. No
threshold change was made. See "Still unresolved" below for the remaining
calibration question, which is a *different* issue.

## F4 — Silent external-runtime fallback

**Root cause.** `moodify-desktop/src/main.js` resolved dedicated venvs relative
to its packaged location and silently substituted system Python when they were
absent:

```js
return fs.existsSync(exe) ? exe : PYTHON;   // removed
```

System Python cannot run that chain (`librosa → sklearn → pandas` ABI
mismatch), so a missing dependency surfaced as a deep `numpy.dtype size
changed` traceback.

**Fix.** A dedicated resolver (`moodify-desktop/src/runtime.js`) returns the
dedicated interpreter or raises `RuntimeMissingError`
(`code: "DEPENDENCY_MISSING"`). No fallback path exists; a failed resolution
returns before any process is spawned.

---

## Corrected measurement semantics

| Metric | Domain | Definition |
| --- | --- | --- |
| `integrated_lufs` | all channels, power-summed | BS.1770-5 / EBU 3341, K-weighted, 400 ms blocks, −70 LUFS absolute + −10 LU relative gates |
| `sample_peak_dbfs` | all samples, all channels | `20·log10(max|x|)` |
| `rms_dbfs` | all samples, all channels | `20·log10(sqrt(mean(x²)))` — total energy / total sample count |
| `crest_factor_db` | derived, one domain | `sample_peak_dbfs − rms_dbfs` |
| `true_peak_dbfs` | per channel, 4x oversampled | unchanged (was already correct) |

The canonical registry (`configs/measurement_registry_v1.yaml`) already
declared `max(|x|) -> 20*log10`, `sqrt(mean(x^2)) -> 20*log10` and
"full-signal RMS" — **the implementation was violating its own documented
authority**, so no registry or provenance change was required.

## Why it shipped: the oracle suite was mono-only

Every loudness oracle test used a single-channel fixture. For mono,
`Σ weights == 1` makes the division a no-op and the downmix is the signal, so
both defects were mathematically invisible. Worse, one test asserted
stereo-twin `==` mono, encoding the bug as a "stereo identity".

`tests/auditory/test_measurement_channel_domain.py` closes that gap: stereo
probes are compared against `pyloudnorm`, the old error is asserted to be far
outside tolerance, and peak/RMS are asserted to span all channels.

## Reference oracles

Three-way agreement at 48 kHz (exact K-weighting coefficients):

```text
Probe A: Mine -11.950 | pyloudnorm -11.992 | ffmpeg ebur128 -12.0 LUFS
Probe B: Mine  -9.712 | pyloudnorm  -9.754 | ffmpeg ebur128  -9.7 LUFS
```

At 44.1 kHz the implementation reuses the 48 kHz coefficients — a
**pre-existing, documented approximation** unrelated to this hotfix:

| Sample rate | K-weighting coefficients | Current oracle validation | Test tolerance |
| --- | --- | --- | --- |
| 48 kHz | standard exact | **≤ 0.05 LU** (vs pyloudnorm and ffmpeg ebur128) | 0.1 LU |
| 44.1 kHz | reuses the 48 kHz set | **up to ~0.15 LU** on the deterministic probes | **0.2 LU** |

The 44.1 kHz tolerance is wider *at that rate only*, and for that documented
reason. The aggregation defect was 3 dB, far outside either tolerance.

---

## Still unresolved (deliberately not fixed here)

This hotfix is scoped to the four named defects. The following are recorded so
they are not mistaken for fixed:

1. **Crest floor is an uncalibrated engineering default.** `min_crest_db: 4.0`
   has no standard basis and no experiment behind it — its own provenance says
   so. A pure sine has a 3.01 dB crest factor *by definition*, so steady
   harmonic material at unity level still trips it. This is a **rule
   calibration question, not a measurement bug**; retuning it without evidence
   would be exactly the kind of guess this note exists to prevent.

2. **`loudness_range_lu` measures a mono downmix** (`channel_policy: mono
   downmix for short-term loudness` in the registry). That is *declared*
   policy, not an accidental defect, and LRA is a spread so a constant offset
   cancels. Whether the policy is conformant is a separate question.

3. **`timeline.py` windowed `sample_peak_dbfs` / `rms_dbfs` are still
   mono-domain**, in the same `scan/timeline_metrics.jsonl` evidence as the
   corrected metrics. Same defect class as F2, different file.

4. **`mix_graph/verify.py` RMS uses a mono downmix** while its peak spans all
   channels — the same F2 shape, in the finishing path.

5. **`clipping_sample_count` / silence analysis use the mono downmix**, so a
   clipped channel can be missed when the other channel is quiet.

Items 3–5 are the same class of defect as F2 and are **not fixed here** to keep
the change set reviewable. They need their own task and their own oracle.

6. **Runtime validation checks executable presence only.** It does not probe
   `import basic_pitch` / `import music21`, so a venv that exists but is broken
   still resolves. Deferred deliberately: probing costs startup time on every
   resolution.

## Out of scope — packaging

The shipped installed and portable builds still do not contain `.venv-*` at
the paths the resolver looks for. This hotfix makes that failure **explicit**
rather than silent; supplying the runtimes is a release-packaging task.
