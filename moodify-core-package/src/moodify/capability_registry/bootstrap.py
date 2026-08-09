"""Bootstrap the first capability set from real environment facts.

Registers only capabilities backed by detected tools or Moodify's own
implemented modules. Missing tools are registered as known_missing. Every
provider carries known_failure_modes (negative knowledge) sourced from real
failure ledgers; an empty registry is not allowed.
"""

from __future__ import annotations

import datetime
from pathlib import Path

from moodify.capability_registry.detect import DetectionResult, detect_all
from moodify.capability_registry.model import (
    SCHEMA_VERSION,
    CapabilityContract,
    CapabilityRegistry,
    ProviderRecord,
)

REGISTRY_PATH = Path(__file__).resolve().parents[3] / "capability_registry.json"


def _utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _capability(
    capability_id: str,
    purpose: str,
    inputs: tuple[str, ...],
    outputs: tuple[str, ...],
    quality: dict | None = None,
    execution: dict | None = None,
    validation: tuple[str, ...] = (),
    evidence: tuple[str, ...] = (),
) -> CapabilityContract:
    return CapabilityContract(
        capability_id=capability_id,
        contract_version="1.0",
        purpose=purpose,
        inputs=inputs,
        outputs=outputs,
        quality_policy=quality or {},
        execution=execution or {},
        validation=validation,
        evidence=evidence,
    )


def _provider(
    provider_id: str,
    capability_id: str,
    license_class: str,
    license_label: str,
    detection: DetectionResult,
) -> ProviderRecord:
    status = "active" if detection.found else "known_missing"
    return ProviderRecord(
        provider_id=provider_id,
        capability_id=capability_id,
        adapter_version="0.0",
        license_class=license_class,
        license_label=license_label,
        status=status,
        version=detection.version,
        binary_path=detection.binary_path,
        detected_at=_utc_now(),
        known_failure_modes=detection.known_failure_modes,
        health={"found": detection.found},
        notes=detection.notes,
    )


def build_registry() -> CapabilityRegistry:
    det = detect_all()
    utc = _utc_now()

    capabilities = (
        _capability(
            "media.transcode",
            "Decode, transcode and repackage media files between formats.",
            ("wav", "flac", "mp3", "m4a", "ogg"),
            ("wav", "flac", "mp3", "m4a", "ogg"),
            quality={"clipping_allowed": False},
            execution={"requires_approved_envelope": False, "network_access": False},
            validation=("output_exists", "nonzero_size", "source_hash_linked"),
            evidence=("provider_version", "command_manifest", "input_hashes", "output_hashes", "execution_log"),
        ),
        _capability(
            "media.probe",
            "Read media metadata, streams and duration without transcoding.",
            ("audio_files", "video_files"),
            ("json_metadata",),
            validation=("output_exists", "parseable"),
            evidence=("provider_version", "command_manifest", "execution_log"),
        ),
        _capability(
            "notation.render",
            "Render an approved symbolic score into publication artifacts.",
            ("musicxml", "midi"),
            ("pdf", "svg", "normalized_musicxml"),
            quality={"page_count_nonzero": True},
            execution={"requires_approved_envelope": False, "network_access": False},
            validation=("output_exists", "page_count_nonzero", "no_missing_glyphs", "source_hash_linked"),
            evidence=("provider_version", "command_manifest", "input_hashes", "output_hashes", "execution_log"),
        ),
        _capability(
            "audio.time_stretch",
            "Change tempo and/or pitch of audio without resampling artifacts.",
            ("wav", "flac"),
            ("wav", "flac"),
            quality={"clipping_allowed": False},
            execution={"network_access": False},
            validation=("output_exists", "nonzero_size", "no_nan", "duration_alignment"),
            evidence=("provider_version", "command_manifest", "parameter_manifest", "output_hashes", "execution_log"),
        ),
        _capability(
            "audio.measure_loudness",
            "Measure integrated loudness, peak and dynamics statistics.",
            ("wav", "flac", "mp3"),
            ("json_statistics",),
            validation=("output_exists", "parseable"),
            evidence=("provider_version", "command_manifest", "execution_log"),
        ),
        _capability(
            "audio.separate_manifest",
            "Transcribe audio into stem-aware MIDI with per-stem profiles.",
            ("wav", "stems"),
            ("midi", "json_manifest"),
            execution={"requires_approved_envelope": False, "network_access": False},
            validation=("output_exists", "source_hash_linked"),
            evidence=("provider_version", "model_version", "parameter_manifest", "output_hashes", "execution_log"),
        ),
        _capability(
            "waveform.region_edit",
            "Edit waveform regions under controlled human direction.",
            ("wav", "project"),
            ("wav",),
            execution={"human_handoff_required": True},
            validation=("output_exists", "source_hash_linked"),
            evidence=("provider_version", "command_manifest", "output_hashes", "execution_log"),
        ),
        _capability(
            "lyric.align",
            "Align authoritative lyric text to final audio, producing line/word timelines with quality gates.",
            ("wav", "mp3", "flac", "m4a", "aac", "lyrics_text", "translation_text"),
            ("alignment_json", "lrc", "enhanced_lrc", "srt", "ass", "qc_report", "evidence_manifest"),
            quality={"min_coverage": 0.92, "max_unaligned_token_ratio": 0.05,
                     "min_mean_word_confidence": 0.72, "min_line_confidence": 0.55,
                     "max_rerun_delta_ms": 80.0, "heuristic_always_draft_only": True},
            execution={"network_access": False, "requires_approved_envelope": False},
            validation=("line_monotonicity", "word_monotonicity", "coverage",
                        "unaligned_token_ratio", "rerun_delta", "boundary_jump"),
            evidence=("audio_sha256", "lyrics_sha256", "translation_sha256",
                      "alignment_sha256", "backend_sha256", "backend_raw_sha256",
                      "config_sha256", "qc_report"),
        ),
        _capability(
            "auditory.ocean_listen",
            "Raw auditory sensor evidence from Ocean Listen (hearing layer only).",
            ("wav", "mp3", "flac", "m4a"),
            ("raw_ocean_report", "auditory_observation_v1", "ocean_quality_gate", "ocean_run_manifest"),
            quality={
                "sensor_output_only": True,
                "may_approve_artistic_decision": False,
                "may_transition_to_technically_validated": False,
                "heuristic_always_draft_only": True,
            },
            execution={"requires_approved_envelope": False, "network_access": False},
            validation=("source_hash_linked", "commit_pin_linked", "no_non_finite", "evidence_registry_written"),
            evidence=("source_sha256", "configuration_hash", "upstream_commit", "artifact_sha256", "qc_report"),
        ),
    )

    providers = (
        _provider("ffmpeg.cli", "media.transcode", "external_process", "GPLv3/LGPL (external process)", det["ffmpeg"]),
        _provider("ffprobe.cli", "media.probe", "external_process", "GPLv3/LGPL (external process)", det["ffprobe"]),
        _provider("musescore.cli", "notation.render", "external_process", "GPLv3 (external process)", det["musescore"]),
        _provider("rubberband.cli", "audio.time_stretch", "external_process", "GPLv2 (external process)", det["rubberband"]),
        _provider("sox.cli", "audio.measure_loudness", "external_process", "LGPL (external process)", det["sox"]),
        _provider("basic_pitch.moodify", "audio.separate_manifest", "reviewed", "Apache-2.0 (internal)", det["basic_pitch"]),
        _provider("audacity.cli", "waveform.region_edit", "external_process", "GPLv2 (external process)", det["audacity"]),
        _provider("lyric_align.core", "lyric.align", "internal", "GPL-3.0-only (internal)", det["moodify_self"]),
        _provider("ocean_listen.git", "auditory.ocean_listen", "external_process", "MIT (external sensor; bridge code proprietary)", det["ocean_listen"]),
    )

    return CapabilityRegistry(
        schema_version=SCHEMA_VERSION,
        capabilities=capabilities,
        providers=providers,
        generated_at=utc,
    )


def write_registry(registry: CapabilityRegistry, path: Path = REGISTRY_PATH) -> Path:
    from moodify.capability_registry.model import registry_dumps

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(registry_dumps(registry), encoding="utf-8")
    return path


def load_registry(path: Path = REGISTRY_PATH) -> CapabilityRegistry:
    from moodify.capability_registry.model import registry_loads

    return registry_loads(path.read_text(encoding="utf-8"))
