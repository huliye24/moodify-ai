"""Contract and security tests for the optional lyrics intent evidence layer."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from moodify_bridge import services
from moodify_bridge.hashing import sha256_file
from moodify_bridge.schemas import LyricsRef, OnePointSpec, OnePointStatus


def _lyrics_ref(path: Path, **overrides: object) -> LyricsRef:
    values: dict[str, object] = {
        "path": str(path),
        "language": "en",
        "version": "authorized-draft",
        "rights_basis": "owner-provided",
        "declared_intent": "A restrained movement toward release.",
    }
    values.update(overrides)
    return LyricsRef(**values)


def _spec(project: Path, lyrics: LyricsRef | None) -> OnePointSpec:
    return OnePointSpec(
        source=str(project / "demo/case.yaml"),
        essence="A quiet study in distance.",
        must_preserve=("dynamic identity",),
        desired_change="verify the evidence package",
        must_avoid=("distortion",),
        human_owner="Codex Validator",
        lyrics=lyrics,
    )


@pytest.mark.parametrize("language", ["", "english", "en_US", "e", "zh-$$$$"])
def test_invalid_lyrics_language_rejected(language: str, tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        _lyrics_ref(tmp_path / "lyrics.txt", language=language)


def test_mixed_language_is_explicitly_allowed(tmp_path: Path) -> None:
    assert _lyrics_ref(tmp_path / "lyrics.txt", language="mixed").language == "mixed"


def test_non_utf8_encoding_declaration_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        _lyrics_ref(tmp_path / "lyrics.txt", encoding="utf-16")


def test_blank_declared_intent_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        _lyrics_ref(tmp_path / "lyrics.txt", declared_intent="   ")


def test_missing_rights_basis_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        LyricsRef(
            path=str(tmp_path / "lyrics.txt"),
            language="en",
            version="authorized-draft",
        )


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        (b"\xff\xfe\xfa", "valid UTF-8"),
        (b"line\x00line", "NUL"),
        (b" \r\n\t", "empty or whitespace-only"),
    ],
)
def test_unsafe_lyrics_content_rejected(
    tmp_path: Path, payload: bytes, message: str,
) -> None:
    path = tmp_path / "lyrics.txt"
    path.write_bytes(payload)
    with pytest.raises(ValueError, match=message):
        services._load_lyrics_safe(path)


def test_oversize_lyrics_rejected(tmp_path: Path) -> None:
    path = tmp_path / "lyrics.txt"
    path.write_bytes(b"a" * (services.LYRICS_MAX_BYTES + 1))
    with pytest.raises(ValueError, match="size limit"):
        services._load_lyrics_safe(path)


def test_path_outside_authorized_workspace_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("not authorized", encoding="utf-8")
    monkeypatch.setattr(services, "LYRICS_ALLOWED_ROOT", allowed)
    with pytest.raises(ValueError, match="outside the authorized workspace"):
        services._validate_lyrics_path(str(outside))


def test_parent_traversal_rejected() -> None:
    with pytest.raises(ValueError, match="traversal"):
        services._validate_lyrics_path("../lyrics.txt")


def test_structure_analysis_is_deterministic_and_text_free() -> None:
    body = "[Verse 1]\nA private marker line\n\n[Chorus]\nA private marker line\n"
    first = services._analyze_lyrics_structure(body)
    second = services._analyze_lyrics_structure(body)
    assert first == second
    assert first.normalized_repetition_count == 1
    assert len(first.sections) == 2
    serialized = first.model_dump_json()
    assert "A private marker line" not in serialized


def test_valid_lyrics_are_hashed_and_do_not_leak(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Path(__file__).parents[1]
    lyrics = tmp_path / "lyrics.txt"
    secret_line = "ORCHID-CLOCK-PRIVATE-LYRIC"
    lyrics.write_text(f"[Verse]\n{secret_line}\n\n[Chorus]\n{secret_line}\n", encoding="utf-8")
    monkeypatch.setattr(services, "LYRICS_ALLOWED_ROOT", tmp_path)
    monkeypatch.chdir(project)

    out = tmp_path / "run"
    result = services.refine_prepare(_spec(project, _lyrics_ref(lyrics)), out)

    assert result.status == OnePointStatus.READY_FOR_REVIEW
    lyrics_dir = out / "evidence/lyrics"
    assert (lyrics_dir / "original.txt").read_bytes() == lyrics.read_bytes()
    evidence = json.loads((lyrics_dir / "lyrics_evidence.json").read_text(encoding="utf-8"))
    assert evidence["source_facts"]["sha256"] == sha256_file(lyrics)
    package = json.loads((out / "evidence/package_manifest.json").read_text(encoding="utf-8"))
    for relative in (
        "evidence/lyrics/original.txt",
        "evidence/lyrics/original.txt.sha256",
        "evidence/lyrics/lyrics_evidence.json",
    ):
        assert package["artifacts"][relative] == sha256_file(out / relative)
    for relative in ("result.json", "summary.md", "summary.html"):
        assert secret_line not in (out / relative).read_text(encoding="utf-8")


def test_unknown_rights_never_reads_or_copies_body(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Path(__file__).parents[1]
    forbidden = tmp_path / "does-not-need-to-exist.txt"
    ref = _lyrics_ref(forbidden, rights_basis="unknown")
    monkeypatch.setattr(services, "LYRICS_ALLOWED_ROOT", tmp_path)
    monkeypatch.chdir(project)

    out = tmp_path / "unknown-rights"
    result = services.refine_prepare(_spec(project, ref), out)

    assert result.status == OnePointStatus.NEEDS_EVIDENCE
    assert not (out / "evidence/lyrics").exists()
    assert "not collected" in result.action


def test_declared_intent_conflict_is_entrusted_to_owner(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Path(__file__).parents[1]
    lyrics = tmp_path / "lyrics.txt"
    lyrics.write_text("[Verse]\nA harmless line\n", encoding="utf-8")
    ref = _lyrics_ref(lyrics, declared_intent="Explore distortion as a narrative device.")
    monkeypatch.setattr(services, "LYRICS_ALLOWED_ROOT", tmp_path)
    monkeypatch.chdir(project)

    result = services.refine_prepare(_spec(project, ref), tmp_path / "conflict")

    assert result.status == OnePointStatus.NEEDS_EVIDENCE
    assert "owner should review" in result.entrust.lower()


def test_lyrics_change_spec_identity(tmp_path: Path) -> None:
    project = Path(__file__).parents[1]
    first = _spec(project, _lyrics_ref(tmp_path / "a.txt"))
    second = _spec(project, _lyrics_ref(tmp_path / "b.txt"))
    fields = lambda spec: {
        "schema_version": spec.schema_version,
        "source": spec.source,
        "essence": spec.essence,
        "must_preserve": list(spec.must_preserve),
        "desired_change": spec.desired_change,
        "must_avoid": list(spec.must_avoid),
        "human_owner": spec.human_owner,
        "lyrics": json.loads(spec.lyrics.model_dump_json()) if spec.lyrics else None,
    }
    from moodify_bridge.hashing import sha256_bytes

    digest = lambda spec: sha256_bytes(
        json.dumps(fields(spec), sort_keys=True, separators=(",", ":")).encode()
    )
    assert digest(first) != digest(second)


def test_hard_lyrics_rejection_leaves_no_partial_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Path(__file__).parents[1]
    bad = tmp_path / "bad.txt"
    bad.write_bytes(b"\xff\xfe")
    monkeypatch.setattr(services, "LYRICS_ALLOWED_ROOT", tmp_path)
    out = tmp_path / "rejected"
    with pytest.raises(ValueError, match="LYRICS_LOAD_FAILED"):
        services.refine_prepare(_spec(project, _lyrics_ref(bad)), out)
    assert not out.exists()
