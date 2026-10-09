# Cross-Lane Requests

Per `MOODIFY_THINKPAD_HEAVY_LANE_001` §24: changes to mainline-owned surfaces are
**not** made from the heavy lane; they are recorded here for the mainline machine.

---

## CLR-001 — CLI help text still says "The Ear of AI"

```text
file:     moodify-core-package/src/moodify/release_cli.py (argparse description)
need:     update the CLI program description to the current canonical identity.
reason:   `moodify --help` prints "Moodify — The Ear of AI". That public identity was
          superseded by Canon v2.1 (2026-09-23); Ear is internal-only. Found while
          walking the real CLI surface for the PROCESS pipeline verification.
status:   NON_BLOCKING
suggest:  one-line string change, but it is product-narrative language — a mainline
          decision. No behavior effect.
```

## CLR-002 — `docs/development/README.md` is stale

```text
file:     docs/development/README.md
need:     refresh or archive. It still describes apps/web/ as an active system and
          "Cloud Production 001" as the next step (2026-08-24 boundaries), all
          superseded by the 2026-10-03 restructure and Canon v3.
reason:   discovered while adding the heavy-lane documents to docs/development/.
status:   NON_BLOCKING
suggest:  mainline rewrites it as the dev-entry index; the heavy-lane docs added here
          (THINKPAD_*) are self-contained.
```

## CLR-003 — `preview_separation` declaration names the wrong venv (and a stale lib)

```text
file:     moodify-core-package/src/moodify/capabilities/builtin.py
          (moodify.preview_separation runtime_requirements)
need:     align the declaration with the desktop's current runtime layout.
reason:   the declaration says "external venv .venv-basic-pitch" + "librosa", but the
          desktop shell now launches dsp_separate.py on resolveRuntime('audio')
          = .venv-audio (moodify-desktop/src/main.js:1187; requirements-audio.txt
          exists for exactly this runtime). dsp_separate.py imports
          numpy/soundfile/scipy only — requirements-audio.txt drops librosa
          deliberately (librosa→sklearn→pandas C-ABI chain), so the declared
          "librosa" is stale too. Measured on the ThinkPad 2026-10-09:
          .venv-audio does not exist, so the shell's quick-separation path would
          raise DEPENDENCY_MISSING, while the probe (declaration-faithful,
          .venv-basic-pitch) reports all requirements SATISFIED. Found by
          THINKPAD 003.
status:   NON_BLOCKING (probe is declaration-faithful; drift is documentation truth)
suggest:  either update the declaration to "external venv .venv-audio" +
          "numpy"/"soundfile"/"scipy", or change runtime.js back; a mainline call
          between Core declarations and desktop runtime layout. Do not auto-fix.
```

## CLR-004 — `music21.local` declares `.venv-score`, desktop resolves `.venv-basic-pitch`

```text
file:     moodify-core-package/src/moodify/capabilities/builtin.py
          (music21.local runtime_requirements) and/or moodify-desktop/src/runtime.js
need:     one canonical location for music21, declared and implemented alike.
reason:   builtin.py declares "external venv .venv-score"; runtime.js aliases the
          score runtime to .venv-basic-pitch (dir: '.venv-basic-pitch') and
          requirements-transcribe.txt installs music21 into .venv-basic-pitch.
          Measured ThinkPad 2026-10-09: .venv-basic-pitch has NO music21
          (ModuleNotFoundError) while .venv-score has music21 9.9.2.
          Probe demonstration (THINKPAD 003 evidence doc): music21.local probed
          against the declared .venv-score = AVAILABLE; probed against the
          desktop-resolved .venv-basic-pitch = UNAVAILABLE (import fails) — i.e.
          the shell's score:run fails on this machine today.
status:   NON_BLOCKING for the probe (declaration-faithful), BLOCKING-equivalent
          for the desktop score path on this machine.
suggest:  decide the canonical venv (likely: install music21 into .venv-basic-pitch
          per requirements-transcribe.txt and update the builtin.py declaration),
          then machine venvs are rebuilt to match. Product-adjacent call — mainline.
```

## CLR-005 — AGENTS.md §6 still describes the V3 pipeline (②⑤ exist there, V4 deleted them)

```text
file:     AGENTS.md (§6 生产流程段落; authority file — mainline-owned)
need:     sync the pipeline wording with STUDIO_PRODUCTION_PIPELINE_V4.md.
reason:   AGENTS.md §6 still says the Creator flow is 检测 → 问题 → 分轨 → 结构 → 方案 → 成品,
          with "⑤ 方案在 分轨 + MIDI 齐备前保持锁定" and a finish-mode rule that unlocks ⑤.
          V4 (2026-10-04, implemented in moodify-desktop/src/pipeline.js:60) deleted ②问题
          and ⑤方案 outright: stages are IMPORTED/ANALYZED/SEPARATED/STRUCTURED/TUNED/
          COMPOSED/RECHECKED/CHOSEN/EXPORTED, findings live inside ①, and quick mode never
          unlocks any plan stage. Found while characterizing the pipeline for THINKPAD 004
          (docs/development/THINKPAD_PRODUCTION_GRAPH_PARITY.md §10.4).
status:   NON_BLOCKING for THINKPAD 004 (code is V4; the graph ports code semantics), but a
          reader following AGENTS.md alone would build the V3 model.
suggest:  mainline updates AGENTS.md §6 to the V4 vocabulary (and its "参见 V3" pointer),
          keeping whatever product principles remain true (Understand first / no black box /
          quick is explicit-only).
