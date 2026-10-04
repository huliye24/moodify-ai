"""The canonical built-in capability registry (``moodify.capabilities/0.1``).

Declarations are **static and explicit**. Nothing here is discovered by
scanning the filesystem or inspecting imports — module existence is not
capability existence. A capability is part of Moodify because Moodify declares
it here and contracts it, not because a file with a promising name exists.

Every ``status`` is justified from repository evidence on this branch, and the
justification is carried in ``notes`` so a reader can re-check it rather than
trust it. Where the honest answer is "nothing implements this", the status says
``ABSENT`` and the entry still exists — an absent capability is information.
"""

from __future__ import annotations

from functools import lru_cache

from .failures import FailureCode
from .models import (
    Capability,
    CapabilityStatus,
    CommercialUse,
    Determinism,
    ExecutionMode,
    IOType,
    Locality,
    Provider,
    ProviderStatus,
    ProviderType,
    Redistribution,
    StrategicPosture,
)
from .registry import CapabilityRegistry

# Failure codes every capability can return.
_BASE = (FailureCode.INVALID_INPUT, FailureCode.EXECUTION_FAILED)
# Plus the codes that apply when an external engine backs the capability.
_DELEGATED = _BASE + (
    FailureCode.DEPENDENCY_MISSING,
    FailureCode.PROVIDER_UNAVAILABLE,
    FailureCode.UNSUPPORTED_FORMAT,
)
# Plus the codes that apply when a remote service backs it.
_REMOTE = _DELEGATED + (FailureCode.AUTH_REQUIRED, FailureCode.RATE_LIMITED)
# For declared-but-unimplemented capabilities.
_UNBUILT = _BASE + (FailureCode.NOT_IMPLEMENTED,)
# For work whose output needs human authority before being treated as final.
_REVIEWABLE = _BASE + (FailureCode.QUALITY_GATE_FAILED, FailureCode.REVIEW_REQUIRED)

_MOODIFY_CODE_LICENSE = "GPL-3.0-only"


_PROVIDERS: tuple[Provider, ...] = (
    Provider(
        provider_id="moodify.auditory",
        name="Moodify Core auditory measurement",
        provider_type=ProviderType.LIBRARY,
        capability_ids=("audio.analyze", "audio.verify"),
        execution_mode=ExecutionMode.LOCAL,
        status=ProviderStatus.ACTIVE,
        code_license=_MOODIFY_CODE_LICENSE,
        commercial_use=CommercialUse.ALLOWED,
        redistribution=Redistribution.ALLOWED,
        runtime_requirements=("python>=3.10", "numpy", "scipy", "librosa", "soundfile"),
        notes="auditory/metrics.py, loudness.py, true_peak.py, evidence/. Standards-backed; "
        "loudness and true peak are oracle-verified against pyloudnorm and ffmpeg ebur128.",
    ),
    Provider(
        provider_id="moodify.intervention",
        name="Moodify Core intervention primitives",
        provider_type=ProviderType.LIBRARY,
        capability_ids=("clipping.repair",),
        execution_mode=ExecutionMode.LOCAL,
        status=ProviderStatus.ACTIVE,
        code_license=_MOODIFY_CODE_LICENSE,
        commercial_use=CommercialUse.ALLOWED,
        redistribution=Redistribution.ALLOWED,
        runtime_requirements=("python>=3.10", "numpy"),
        notes="intervention/primitives.py. Primitives are pre-registered with scope, max "
        "strength and identity risk. Peak repair only — not true declipping.",
    ),
    Provider(
        provider_id="moodify.mix_graph",
        name="Moodify Mix Graph",
        provider_type=ProviderType.LIBRARY,
        capability_ids=("master.render", "mix.render"),
        execution_mode=ExecutionMode.LOCAL,
        status=ProviderStatus.EXPERIMENTAL,
        code_license=_MOODIFY_CODE_LICENSE,
        commercial_use=CommercialUse.ALLOWED,
        redistribution=Redistribution.ALLOWED,
        runtime_requirements=("python>=3.10", "pedalboard", "numpy", "scipy"),
        notes="mix_graph/. Self-declared EXPERIMENTAL in its own serialization. Node types "
        "are rendered by exactly one provider and must be deterministic.",
    ),
    Provider(
        provider_id="moodify.release",
        name="Moodify Core release path",
        provider_type=ProviderType.LIBRARY,
        capability_ids=("delivery.export",),
        execution_mode=ExecutionMode.LOCAL,
        status=ProviderStatus.ACTIVE,
        code_license=_MOODIFY_CODE_LICENSE,
        commercial_use=CommercialUse.ALLOWED,
        redistribution=Redistribution.ALLOWED,
        runtime_requirements=("python>=3.10", "soundfile"),
        notes="v01_exporter.py (16-bit PCM WAV, peak clamped) and data_plane/delivery.py "
        "(authorized delivery contract). Only WAV encoding exists.",
    ),
    Provider(
        provider_id="moodify.preview_separation",
        name="Moodify preview separation (DSP)",
        provider_type=ProviderType.CLI,
        capability_ids=("stem.separate",),
        execution_mode=ExecutionMode.LOCAL,
        status=ProviderStatus.EXPERIMENTAL,
        code_license=_MOODIFY_CODE_LICENSE,
        commercial_use=CommercialUse.ALLOWED,
        redistribution=Redistribution.ALLOWED,
        runtime_requirements=("python>=3.10", "librosa", "soundfile", "external venv .venv-basic-pitch"),
        notes="moodify-desktop/scripts/dsp_separate.py — centre-channel estimate + HPSS, "
        "second-scale, NOT a neural separator. Its own docstring states it does not constitute "
        "mastering-grade stems. The venv it needs is not shipped in released builds.",
    ),
    Provider(
        provider_id="ffmpeg.system",
        name="FFmpeg / FFprobe (system binary)",
        provider_type=ProviderType.BINARY,
        capability_ids=("audio.convert", "audio.decode", "metadata.read"),
        execution_mode=ExecutionMode.LOCAL,
        status=ProviderStatus.ACTIVE,
        code_license="build-dependent: LGPL-2.1-or-later or GPL-3.0-or-later",
        weights_license=None,
        commercial_use=CommercialUse.ALLOWED,
        redistribution=Redistribution.UNKNOWN,
        runtime_requirements=("ffmpeg", "ffprobe"),
        notes="Redistribution rights depend on how the user's ffmpeg build was configured; "
        "Moodify consumes the system binary and does not ship one, so this is recorded as "
        "UNKNOWN rather than guessed.",
    ),
    Provider(
        provider_id="lalal.cloud",
        name="LALAL.AI stem separation service",
        provider_type=ProviderType.API,
        capability_ids=("stem.separate",),
        execution_mode=ExecutionMode.CLOUD,
        status=ProviderStatus.CONNECTED_UNTESTED,
        code_license="GPL-3.0-only (Moodify client adapter); the service itself is commercial",
        weights_license=None,
        commercial_use=CommercialUse.RESTRICTED,
        redistribution=Redistribution.RESTRICTED,
        runtime_requirements=("network", "LALAL.AI API key"),
        notes="stems/client.py exposes a 10-stem catalog and four splitters; Canon records it "
        "as CONNECTED_UNTESTED. Currently the only cloud separation provider — "
        "SINGLE_SOURCE_ACCEPTED, which is a named risk rather than a neutral fact.",
    ),
    Provider(
        provider_id="basic_pitch.local",
        name="Spotify Basic Pitch (local)",
        provider_type=ProviderType.MODEL,
        capability_ids=("midi.transcribe",),
        execution_mode=ExecutionMode.LOCAL,
        status=ProviderStatus.CONNECTED_UNTESTED,
        code_license="Apache-2.0",
        weights_license="Apache-2.0",
        commercial_use=CommercialUse.ALLOWED,
        redistribution=Redistribution.UNKNOWN,
        runtime_requirements=("python>=3.10", "basic-pitch==0.4.0", "external venv .venv-basic-pitch"),
        notes="Invoked as a CLI from the desktop shell; Core contains no import. Canon records "
        "it as IMPLEMENTED_NOT_MERGED, and released builds do not ship the venv it needs.",
    ),
    Provider(
        provider_id="music21.local",
        name="music21 (local)",
        provider_type=ProviderType.LIBRARY,
        capability_ids=("score.generate",),
        execution_mode=ExecutionMode.LOCAL,
        status=ProviderStatus.CONNECTED_UNTESTED,
        code_license="BSD-3-Clause",
        weights_license=None,
        commercial_use=CommercialUse.ALLOWED,
        redistribution=Redistribution.ALLOWED,
        runtime_requirements=("python>=3.10", "music21", "external venv .venv-score"),
        notes="Used only by moodify-desktop/scripts/midi_to_musicxml.py. Not declared in any "
        "pyproject — an undeclared runtime dependency.",
    ),
)


_CAPABILITIES: tuple[Capability, ...] = (
    # ── INGEST ────────────────────────────────────────────────────────────
    Capability(
        capability_id="audio.decode",
        title="Decode audio to samples",
        description="Probe a container and decode it to samples without altering the source.",
        domain="audio",
        status=CapabilityStatus.CANONICAL,
        strategic_posture=StrategicPosture.BUILD,
        input_types=(IOType.AUDIO,),
        output_types=(IOType.AUDIO, IOType.METADATA),
        failure_codes=_DELEGATED,
        provider_ids=("ffmpeg.system",),
        locality=Locality.LOCAL,
        determinism=Determinism.DETERMINISTIC,
        notes="auditory/decode.py. Subprocess argument arrays only, never shell command strings.",
    ),
    Capability(
        capability_id="audio.convert",
        title="Transcode audio",
        description="Convert between audio container/codec formats.",
        domain="audio",
        status=CapabilityStatus.PARTIAL,
        strategic_posture=StrategicPosture.INTEGRATE,
        input_types=(IOType.AUDIO,),
        output_types=(IOType.AUDIO,),
        failure_codes=_DELEGATED,
        provider_ids=("ffmpeg.system",),
        locality=Locality.LOCAL,
        determinism=Determinism.DETERMINISTIC,
        notes="Only WAV transcode exists (reconstruction_job/audio_util.transcode_to_wav). "
        "No lame/opus/aac encoder is referenced anywhere in Core.",
    ),
    Capability(
        capability_id="metadata.read",
        title="Read audio metadata",
        description="Read container and stream metadata from an audio file.",
        domain="metadata",
        status=CapabilityStatus.PARTIAL,
        strategic_posture=StrategicPosture.INTEGRATE,
        input_types=(IOType.AUDIO,),
        output_types=(IOType.METADATA,),
        failure_codes=_DELEGATED,
        provider_ids=("ffmpeg.system",),
        locality=Locality.LOCAL,
        determinism=Determinism.DETERMINISTIC,
        notes="ffprobe container/stream facts only. No ID3/Vorbis/MP4 tag reader exists in Core.",
    ),
    # ── UNDERSTAND ────────────────────────────────────────────────────────
    Capability(
        capability_id="audio.analyze",
        title="Auditory analysis",
        description="Measure a recording against the standards-backed auditory metric set.",
        domain="audio",
        status=CapabilityStatus.CANONICAL,
        strategic_posture=StrategicPosture.BUILD,
        input_types=(IOType.AUDIO,),
        output_types=(IOType.REPORT, IOType.EVIDENCE, IOType.METADATA),
        failure_codes=_REVIEWABLE,
        provider_ids=("moodify.auditory",),
        locality=Locality.LOCAL,
        determinism=Determinism.DETERMINISTIC,
        requires_human_review=True,
        notes="auditory/metrics.py — 31 registered metrics across 5 authority classes. Analysis "
        "persists authority_state=HUMAN_REQUIRED: machine measurement never becomes a human "
        "verdict. HOTFIX 000 corrected stereo loudness aggregation and channel-domain peak/RMS.",
    ),
    Capability(
        capability_id="audio.verify",
        title="Verify a result",
        description="Compare before/after audio and produce machine evidence with invariance checks.",
        domain="audio",
        status=CapabilityStatus.CANONICAL,
        strategic_posture=StrategicPosture.BUILD,
        input_types=(IOType.AUDIO,),
        output_types=(IOType.EVIDENCE, IOType.REPORT),
        failure_codes=_BASE + (FailureCode.QUALITY_GATE_FAILED, FailureCode.INTEGRITY_ERROR),
        provider_ids=("moodify.auditory",),
        locality=Locality.LOCAL,
        determinism=Determinism.DETERMINISTIC,
        notes="mix_graph/verify.py plus auditory/evidence/ (7 modules incl. conflicts, "
        "epistemic, completeness). Machine evidence only — no listening-quality claims.",
    ),
    Capability(
        capability_id="rhythm.analyze",
        title="Rhythm and tempo analysis",
        description="Estimate tempo, beats and downbeats.",
        domain="rhythm",
        status=CapabilityStatus.PARTIAL,
        strategic_posture=StrategicPosture.INTEGRATE,
        input_types=(IOType.AUDIO,),
        output_types=(IOType.METADATA, IOType.REPORT),
        failure_codes=_DELEGATED + (FailureCode.QUALITY_GATE_FAILED,),
        provider_ids=(),
        locality=Locality.LOCAL,
        determinism=Determinism.UNKNOWN,
        notes="tempo_bpm is declared (structure.py:41) and serialized (:75); the only "
        "construction site in the tree is a test fixture. grep for beat_track/librosa.beat "
        "returns zero hits. A type with no producer is not a capability.",
    ),
    Capability(
        capability_id="structure.analyze",
        title="Song structure analysis",
        description="Segment a song into labelled sections with boundaries.",
        domain="structure",
        status=CapabilityStatus.PARTIAL,
        strategic_posture=StrategicPosture.INTEGRATE,
        input_types=(IOType.AUDIO,),
        output_types=(IOType.REPORT, IOType.METADATA),
        failure_codes=_DELEGATED + (FailureCode.RESOURCE_LIMIT, FailureCode.QUALITY_GATE_FAILED),
        provider_ids=(),
        locality=Locality.LOCAL,
        determinism=Determinism.UNKNOWN,
        notes="StructureContext is defined and consumed as an optional parameter, but has "
        "0 construction sites in production code — nothing ever builds one.",
    ),
    Capability(
        capability_id="harmony.analyze",
        title="Harmony and chord analysis",
        description="Estimate key and chord progression.",
        domain="harmony",
        status=CapabilityStatus.ABSENT,
        strategic_posture=StrategicPosture.INTEGRATE,
        input_types=(IOType.AUDIO,),
        output_types=(IOType.METADATA, IOType.REPORT),
        failure_codes=_UNBUILT,
        provider_ids=(),
        locality=Locality.LOCAL,
        determinism=Determinism.UNKNOWN,
        notes="No chord or key detection in Core (0 hits). Experimental chroma in "
        "moodify_experimental/mamse002 explicitly disclaims being harmony understanding.",
    ),
    Capability(
        capability_id="instrument.identify",
        title="Instrument identification",
        description="Identify instruments present in a recording.",
        domain="instrument",
        status=CapabilityStatus.ABSENT,
        strategic_posture=StrategicPosture.INTEGRATE,
        input_types=(IOType.AUDIO,),
        output_types=(IOType.METADATA,),
        failure_codes=_UNBUILT,
        provider_ids=(),
        locality=Locality.LOCAL,
        determinism=Determinism.UNKNOWN,
        notes="0 hits for instrument recognition / PANNs / YAMNet. The only 'instrumental' "
        "concept in the repo is a stem label from the LALAL catalog.",
    ),
    Capability(
        capability_id="pitch.analyze",
        title="Pitch analysis",
        description="Estimate fundamental frequency and tuning.",
        domain="pitch",
        status=CapabilityStatus.EXPERIMENTAL,
        strategic_posture=StrategicPosture.INTEGRATE,
        input_types=(IOType.AUDIO,),
        output_types=(IOType.METADATA,),
        failure_codes=_DELEGATED + (FailureCode.QUALITY_GATE_FAILED,),
        provider_ids=(),
        locality=Locality.LOCAL,
        determinism=Determinism.UNKNOWN,
        notes="moodify_experimental/mamse002 (log-frequency CQT, dominant MIDI, tuning cents). "
        "Its own evidence file states dominant_midi is an estimator, not perceived pitch. "
        "No provider is declared because nothing on the shipping path produces this.",
    ),
    # ── TRANSCRIBE ────────────────────────────────────────────────────────
    Capability(
        capability_id="midi.transcribe",
        title="Audio to MIDI",
        description="Convert audio to MIDI note events with pitch bend.",
        domain="midi",
        status=CapabilityStatus.IMPLEMENTED_NOT_CANONICAL,
        strategic_posture=StrategicPosture.INTEGRATE,
        input_types=(IOType.AUDIO, IOType.STEM),
        output_types=(IOType.MIDI,),
        failure_codes=_DELEGATED,
        provider_ids=("basic_pitch.local",),
        locality=Locality.LOCAL,
        determinism=Determinism.CONDITIONALLY_DETERMINISTIC,
        notes="Invoked as an external CLI from the desktop shell (pipeline.js); Core contains "
        "no basic_pitch import. Canon records Basic Pitch as IMPLEMENTED_NOT_MERGED.",
    ),
    Capability(
        capability_id="score.generate",
        title="MIDI to score",
        description="Convert MIDI to MusicXML for notation rendering.",
        domain="score",
        status=CapabilityStatus.IMPLEMENTED_NOT_CANONICAL,
        strategic_posture=StrategicPosture.INTEGRATE,
        input_types=(IOType.MIDI,),
        output_types=(IOType.MUSICXML, IOType.SCORE),
        failure_codes=_DELEGATED,
        provider_ids=("music21.local",),
        locality=Locality.LOCAL,
        determinism=Determinism.DETERMINISTIC,
        notes="moodify-desktop/scripts/midi_to_musicxml.py calls music21 makeNotation then "
        "writes MusicXML. music21 is not declared in any pyproject.",
    ),
    Capability(
        capability_id="lyrics.align",
        title="Lyrics alignment",
        description="Align known lyrics to a recording with timestamps.",
        domain="lyrics",
        status=CapabilityStatus.ABSENT,
        strategic_posture=StrategicPosture.INTEGRATE,
        input_types=(IOType.AUDIO, IOType.LYRICS),
        output_types=(IOType.LYRICS, IOType.METADATA),
        failure_codes=_UNBUILT,
        provider_ids=(),
        locality=Locality.LOCAL,
        determinism=Determinism.UNKNOWN,
        notes="0 hits for lyric/whisper/forced-align in Core or the desktop shell.",
    ),
    # ── SEPARATE ──────────────────────────────────────────────────────────
    Capability(
        capability_id="stem.separate",
        title="Stem separation",
        description="Split a mixed recording into named stems.",
        domain="stem",
        status=CapabilityStatus.EXPERIMENTAL,
        strategic_posture=StrategicPosture.INTEGRATE,
        input_types=(IOType.AUDIO,),
        output_types=(IOType.STEM, IOType.EVIDENCE),
        failure_codes=_REMOTE + (FailureCode.RESOURCE_LIMIT, FailureCode.QUALITY_GATE_FAILED),
        provider_ids=("moodify.preview_separation", "lalal.cloud"),
        locality=Locality.HYBRID,
        determinism=Determinism.CONDITIONALLY_DETERMINISTIC,
        notes="Three disjoint paths and no unifying contract: a LALAL cloud client "
        "(CONNECTED_UNTESTED), a self-declared preview-grade local DSP script, and a Demucs "
        "extra that is declared in pyproject with no code behind it.",
    ),
    # ── REPAIR ────────────────────────────────────────────────────────────
    Capability(
        capability_id="clipping.repair",
        title="Clipping repair",
        description="Detect and repair clipped segments.",
        domain="clipping",
        status=CapabilityStatus.IMPLEMENTED_NOT_CANONICAL,
        strategic_posture=StrategicPosture.INTEGRATE,
        input_types=(IOType.AUDIO,),
        output_types=(IOType.AUDIO, IOType.EVIDENCE),
        failure_codes=_BASE + (FailureCode.QUALITY_GATE_FAILED, FailureCode.REVIEW_REQUIRED),
        provider_ids=("moodify.intervention",),
        locality=Locality.LOCAL,
        determinism=Determinism.DETERMINISTIC,
        notes="intervention/primitives.py (detect_clip_segments, apply_clip_peak_repair). "
        "Peak repair rather than reconstruction. Identity-gated: a legitimate clip repair can "
        "trip the flat-segment detector.",
    ),
    Capability(
        capability_id="noise.reduce",
        title="Noise reduction",
        description="Reduce persistent noise in a recording.",
        domain="noise",
        status=CapabilityStatus.ABSENT,
        strategic_posture=StrategicPosture.INTEGRATE,
        input_types=(IOType.AUDIO,),
        output_types=(IOType.AUDIO,),
        failure_codes=_UNBUILT,
        provider_ids=(),
        locality=Locality.LOCAL,
        determinism=Determinism.UNKNOWN,
        notes="Explicitly unsupported rather than missing: the reconstruction objective routes "
        "ED_02_PERSISTENT_NOISE to NOISE_REDUCTION and returns INTERVENTION_NOT_SUPPORTED_V0_1.",
    ),
    Capability(
        capability_id="timing.correct",
        title="Timing correction",
        description="Correct timing or quantise performance to a grid.",
        domain="timing",
        status=CapabilityStatus.ABSENT,
        strategic_posture=StrategicPosture.DEFER,
        input_types=(IOType.AUDIO, IOType.MIDI),
        output_types=(IOType.AUDIO, IOType.MIDI),
        failure_codes=_UNBUILT,
        provider_ids=(),
        locality=Locality.LOCAL,
        determinism=Determinism.UNKNOWN,
        notes="0 hits for time_stretch/quantize/warp. Deferred by posture, not merely unbuilt: "
        "it would also require rhythm.analyze, which is itself PARTIAL.",
    ),
    # ── ARRANGE / MIX / MASTER ────────────────────────────────────────────
    Capability(
        capability_id="pitch.correct",
        title="Pitch correction",
        description="Correct intonation of a performance.",
        domain="pitch",
        status=CapabilityStatus.ABSENT,
        strategic_posture=StrategicPosture.INTEGRATE,
        input_types=(IOType.AUDIO,),
        output_types=(IOType.AUDIO,),
        failure_codes=_UNBUILT,
        provider_ids=(),
        locality=Locality.LOCAL,
        determinism=Determinism.UNKNOWN,
        notes="0 hits for pitch_shift/autotune/psola anywhere in src/ or moodify_experimental/.",
    ),
    Capability(
        capability_id="mix.render",
        title="Render a mix",
        description="Render a mix session to audio and verify the result.",
        domain="mix",
        status=CapabilityStatus.EXPERIMENTAL,
        strategic_posture=StrategicPosture.BUILD,
        input_types=(IOType.MIX_SESSION, IOType.AUDIO),
        output_types=(IOType.AUDIO, IOType.EVIDENCE),
        failure_codes=_REVIEWABLE + (FailureCode.INTEGRITY_ERROR,),
        provider_ids=("moodify.mix_graph",),
        locality=Locality.LOCAL,
        determinism=Determinism.DETERMINISTIC,
        requires_human_review=True,
        notes="mix_graph serializes its own status as EXPERIMENTAL. Rendering is deterministic "
        "per node type by contract. Human authority decides what counts as better.",
    ),
    Capability(
        capability_id="master.render",
        title="Render a master",
        description="Render a finished master and verify the result.",
        domain="master",
        status=CapabilityStatus.EXPERIMENTAL,
        strategic_posture=StrategicPosture.BUILD,
        input_types=(IOType.AUDIO, IOType.MIX_SESSION),
        output_types=(IOType.MASTER, IOType.AUDIO, IOType.EVIDENCE),
        failure_codes=_REVIEWABLE + (FailureCode.INTEGRITY_ERROR,),
        provider_ids=("moodify.mix_graph",),
        locality=Locality.LOCAL,
        determinism=Determinism.DETERMINISTIC,
        requires_human_review=True,
        notes="Mix Graph finishing (EXPERIMENTAL). Note that the desktop shell currently routes "
        "through the LEGACY v01 preset pipeline, so the shipping path is not the forward path.",
    ),
    # ── DELIVER ───────────────────────────────────────────────────────────
    Capability(
        capability_id="delivery.export",
        title="Export a deliverable",
        description="Export a finished result as a deliverable file.",
        domain="delivery",
        status=CapabilityStatus.IMPLEMENTED_NOT_CANONICAL,
        strategic_posture=StrategicPosture.BUILD,
        input_types=(IOType.AUDIO, IOType.MASTER),
        output_types=(IOType.AUDIO, IOType.METADATA),
        failure_codes=_BASE + (FailureCode.INTEGRITY_ERROR,),
        provider_ids=("moodify.release",),
        locality=Locality.LOCAL,
        determinism=Determinism.DETERMINISTIC,
        notes="v01_exporter.py writes 16-bit PCM WAV with the peak clamped to 0.999. The "
        "delivery contract (data_plane) is canonical; encoding is WAV-only.",
    ),
)


@lru_cache(maxsize=1)
def builtin_registry() -> CapabilityRegistry:
    """The canonical built-in registry.

    Built once and validated at construction: duplicates, dangling references
    and asymmetric capability/provider claims raise ``RegistryValidationError``
    rather than being silently repaired.
    """
    return CapabilityRegistry(_CAPABILITIES, _PROVIDERS)
