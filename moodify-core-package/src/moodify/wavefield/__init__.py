"""Moodify Wave Field — local experimental lane (v0).

```text
Waveform → WaveField → Hear → Judge → Choose → Render
```

A waveform is not finished sound; it is the condition that makes sound happen.
This package treats the waveform as a source placed into a *perceptual virtual
acoustic field*, searches a small deterministic space of fields, hears each
result with the existing auditory measurement layer, lets a human choose, and
keeps every chosen result reproducible.

Scope of v0 — deliberately narrow:

* :mod:`~moodify.wavefield.models` — ``FieldSpec`` (versioned, strictly validated)
* :mod:`~moodify.wavefield.renderer` — deterministic algorithmic room field
* :mod:`~moodify.wavefield.hearing` — HearSnapshot + the v0 technical gate
* :mod:`~moodify.wavefield.search` — ``FIELD_SEARCH_POLICY_V0`` (engineering probes)
* :mod:`~moodify.wavefield.record` — case layout, append-only decisions, export

Honest boundary: this is **not** a physical acoustics simulator and does not
claim real room reconstruction or true 3-D acoustic simulation.  A single
mono/stereo file supports a projection only.  See
``docs/canon/WAVEFIELD_CORE_PRINCIPLE.md``.
"""

from moodify.wavefield.hearing import (
    hear_snapshot,
    hear_snapshot_for_file,
    judge_candidate,
    measure_audio,
    summarize,
)
from moodify.wavefield.models import (
    CANDIDATE_IDS,
    CHOICES,
    ENGINE_ALGORITHMIC_ROOM_V0,
    EXPORT_SCHEMA,
    HEAR_SCHEMA,
    RENDER_SCHEMA,
    SEARCH_SCHEMA,
    SESSION_SCHEMA,
    SUPPORTED_ENGINES,
    WAVEFIELD_SCHEMA,
    FieldSpec,
    FieldSpecError,
)
from moodify.wavefield.record import (
    WaveFieldRecordError,
    append_decision,
    decision_for,
    export_chosen,
    inspect,
    read_decisions,
    reproduce_chosen,
    wavefield_dir,
)
from moodify.wavefield.renderer import (
    ENGINE_VERSION,
    RENDERER_ID,
    RenderResult,
    WaveFieldRenderError,
    render_array,
    render_file,
    sha256_file,
)
from moodify.wavefield.search import (
    FIELD_SEARCH_POLICY_V0,
    POLICY_ID,
    policy_document,
    probe_fields,
    run_field_search,
)

__all__ = [
    "CANDIDATE_IDS",
    "CHOICES",
    "ENGINE_ALGORITHMIC_ROOM_V0",
    "ENGINE_VERSION",
    "EXPORT_SCHEMA",
    "FIELD_SEARCH_POLICY_V0",
    "HEAR_SCHEMA",
    "POLICY_ID",
    "RENDERER_ID",
    "RENDER_SCHEMA",
    "SEARCH_SCHEMA",
    "SESSION_SCHEMA",
    "SUPPORTED_ENGINES",
    "WAVEFIELD_SCHEMA",
    "FieldSpec",
    "FieldSpecError",
    "RenderResult",
    "WaveFieldRecordError",
    "WaveFieldRenderError",
    "append_decision",
    "decision_for",
    "export_chosen",
    "hear_snapshot",
    "hear_snapshot_for_file",
    "inspect",
    "judge_candidate",
    "measure_audio",
    "policy_document",
    "probe_fields",
    "read_decisions",
    "render_array",
    "render_file",
    "reproduce_chosen",
    "run_field_search",
    "sha256_file",
    "summarize",
    "wavefield_dir",
]
