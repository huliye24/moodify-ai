"""CLI smoke tests for session-init and asset-verify commands."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pytest

from tools.studio_session_prep.studio_prep import main as cli_main


@pytest.fixture
def brief_yaml(tmp_path):
    """Create a minimal valid session brief YAML."""
    import yaml
    brief = {
        "project_title": "CLI Test Session",
        "client_name": "Test Client",
        "engineer_name": "Test Engineer",
        "studio_location": "Test Studio",
        "session_date": "2026-08-01",
        "recording_spec": {
            "sample_rate": "48000",
            "bit_depth": "24",
            "target_peak_dbfs": -6.0,
        },
        "backup_targets": [
            {"label": "ssd", "path": "D:/backup/test"},
        ],
    }
    path = tmp_path / "brief.yaml"
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(brief, f)
    return path


class TestSessionInitCLI:
    def test_creates_manifest_and_checklist(self, tmp_path, brief_yaml):
        out = tmp_path / "session_output"
        rc = cli_main(["session-init", "--brief", str(brief_yaml), "--output-dir", str(out)])
        assert rc == 0
        assert (out / "manifest.json").exists()
        assert (out / "RECORDING_DAY_CHECKLIST.md").exists()
        assert (out / "delivery_contract.json").exists()

    def test_manifest_is_valid_json(self, tmp_path, brief_yaml):
        out = tmp_path / "session_output"
        cli_main(["session-init", "--brief", str(brief_yaml), "--output-dir", str(out)])
        with open(out / "manifest.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["schema_version"] == "1.0.0"
        assert "session_id" in data["session_brief"]
        assert data["session_brief"]["project_title"] == "CLI Test Session"

    def test_checklist_contains_key_info(self, tmp_path, brief_yaml):
        out = tmp_path / "session_output"
        cli_main(["session-init", "--brief", str(brief_yaml), "--output-dir", str(out)])
        checklist = (out / "RECORDING_DAY_CHECKLIST.md").read_text(encoding="utf-8")
        assert "CLI Test Session" in checklist
        assert "48000" in checklist
        assert "Test Client" in checklist
        assert "D:/backup/test" in checklist

    def test_rejects_nonexistent_brief(self, tmp_path):
        out = tmp_path / "session_output"
        rc = cli_main(["session-init", "--brief", str(tmp_path / "nope.yaml"), "--output-dir", str(out)])
        assert rc != 0

    def test_rejects_nonempty_output_dir(self, tmp_path, brief_yaml):
        out = tmp_path / "session_output"
        out.mkdir()
        (out / "something.txt").write_text("data")
        rc = cli_main(["session-init", "--brief", str(brief_yaml), "--output-dir", str(out)])
        assert rc != 0

    def test_force_allows_nonempty(self, tmp_path, brief_yaml):
        out = tmp_path / "session_output"
        out.mkdir()
        (out / "something.txt").write_text("data")
        rc = cli_main(["session-init", "--brief", str(brief_yaml), "--output-dir", str(out), "--force"])
        assert rc == 0

    def test_empty_brief_rejected(self, tmp_path):
        out = tmp_path / "session_output"
        empty_yaml = tmp_path / "empty.yaml"
        empty_yaml.write_text("")
        rc = cli_main(["session-init", "--brief", str(empty_yaml), "--output-dir", str(out)])
        assert rc != 0

    def test_manifest_reproducibility(self, tmp_path, brief_yaml):
        """Same brief should produce structurally identical manifest (except IDs/timestamps)."""
        out1 = tmp_path / "out1"
        out2 = tmp_path / "out2"
        cli_main(["session-init", "--brief", str(brief_yaml), "--output-dir", str(out1)])
        cli_main(["session-init", "--brief", str(brief_yaml), "--output-dir", str(out2)])
        m1 = json.loads((out1 / "manifest.json").read_text())
        m2 = json.loads((out2 / "manifest.json").read_text())
        # Fields that should differ
        assert m1["session_brief"]["session_id"] != m2["session_brief"]["session_id"]
        assert m1["created_at"] != m2["created_at"]
        # Fields that should match
        assert m1["session_brief"]["project_title"] == m2["session_brief"]["project_title"]
        assert m1["session_brief"]["client_name"] == m2["session_brief"]["client_name"]
        assert m1["recording_spec"] == m2["recording_spec"]


class TestAssetVerifyCLI:
    def test_verify_synthetic_audio(self, tmp_path, brief_yaml):
        """Create synthetic audio, session-init, then asset-verify it."""
        import soundfile as sf

        # Create synthetic audio
        sr = 48000
        duration = 1.0
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)
        audio = np.column_stack([
            0.5 * np.sin(2 * np.pi * 440 * t),
            0.5 * np.sin(2 * np.pi * 440 * t),
        ])
        audio_path = tmp_path / "test_take.wav"
        sf.write(str(audio_path), audio, sr)

        # Read the brief and add asset reference
        import yaml
        with open(brief_yaml, "r", encoding="utf-8") as f:
            brief_data = yaml.safe_load(f)
        brief_data["assets"] = [{
            "filename": "test_take.wav",
            "role": "source_stem",
            "notes": "Auto-generated test audio",
        }]
        brief2 = tmp_path / "brief2.yaml"
        with open(brief2, "w", encoding="utf-8") as f:
            yaml.dump(brief_data, f)

        # Init session
        session_dir = tmp_path / "session"
        cli_main(["session-init", "--brief", str(brief2), "--output-dir", str(session_dir)])

        # Manually update local_path (simulating user recording the file)
        manifest_path = session_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["assets"][0]["local_path"] = str(audio_path)
        manifest_path.write_text(json.dumps(manifest, indent=2))

        # Verify
        verify_dir = tmp_path / "verify_output"
        rc = cli_main(["asset-verify", "--manifest", str(manifest_path), "--output-dir", str(verify_dir)])
        assert rc == 0

        # Check verified manifest
        verified_path = verify_dir / "manifest_verified.json"
        assert verified_path.exists()
        verified = json.loads(verified_path.read_text())
        asset = verified["assets"][0]
        assert asset["sha256"] is not None
        assert len(asset["sha256"]) == 64
        assert asset["file_size_bytes"] is not None
        assert asset["sample_rate"] == 48000
        assert asset["channels"] == 2
        assert asset["duration_s"] == pytest.approx(1.0, abs=0.1)
        assert asset["decode_error"] is None

    def test_source_hash_unchanged_after_verify(self, tmp_path, brief_yaml):
        """Verify that source audio hash is stable across verification runs."""
        import soundfile as sf

        sr = 48000
        t = np.linspace(0, 0.5, int(sr * 0.5), endpoint=False)
        audio = 0.5 * np.sin(2 * np.pi * 1000 * t)
        audio_path = tmp_path / "source.wav"
        sf.write(str(audio_path), audio, sr)

        # Hash before
        from tools.studio_session_prep.studio_prep import _sha256_file
        hash_before = _sha256_file(audio_path)

        # Create session with this asset
        import yaml
        brief_data = yaml.safe_load(brief_yaml.read_text())
        brief_data["assets"] = [{"filename": "source.wav", "role": "source_stem", "notes": ""}]
        brief2 = tmp_path / "brief2.yaml"
        with open(brief2, "w") as f:
            yaml.dump(brief_data, f)

        session_dir = tmp_path / "session"
        cli_main(["session-init", "--brief", str(brief2), "--output-dir", str(session_dir)])

        manifest_path = session_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["assets"][0]["local_path"] = str(audio_path)
        manifest_path.write_text(json.dumps(manifest, indent=2))

        cli_main(["asset-verify", "--manifest", str(manifest_path), "--output-dir", str(tmp_path / "v1")])
        cli_main(["asset-verify", "--manifest", str(manifest_path), "--output-dir", str(tmp_path / "v2")])

        # Hash after
        hash_after = _sha256_file(audio_path)
        assert hash_before == hash_after

    def test_duplicate_id_different_assets(self, tmp_path, brief_yaml):
        """Two assets with different filenames should get different asset IDs."""
        import yaml
        brief_data = yaml.safe_load(brief_yaml.read_text())
        brief_data["assets"] = [
            {"filename": "take1.wav", "role": "source_stem"},
            {"filename": "take2.wav", "role": "source_stem"},
        ]
        brief2 = tmp_path / "brief2.yaml"
        with open(brief2, "w") as f:
            yaml.dump(brief_data, f)

        session_dir = tmp_path / "session"
        cli_main(["session-init", "--brief", str(brief2), "--output-dir", str(session_dir)])
        manifest = json.loads((session_dir / "manifest.json").read_text())
        ids = [a["asset_id"] for a in manifest["assets"]]
        assert len(ids) == 2
        assert ids[0] != ids[1]

    def test_missing_file_reported(self, tmp_path, brief_yaml):
        """Asset with local_path pointing to missing file should get decode_error."""
        import yaml
        brief_data = yaml.safe_load(brief_yaml.read_text())
        brief_data["assets"] = [{"filename": "ghost.wav", "role": "source_stem"}]
        brief2 = tmp_path / "brief2.yaml"
        with open(brief2, "w") as f:
            yaml.dump(brief_data, f)

        session_dir = tmp_path / "session"
        cli_main(["session-init", "--brief", str(brief2), "--output-dir", str(session_dir)])

        manifest_path = session_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["assets"][0]["local_path"] = str(tmp_path / "ghost.wav")
        manifest_path.write_text(json.dumps(manifest, indent=2))

        rc = cli_main(["asset-verify", "--manifest", str(manifest_path), "--output-dir", str(tmp_path / "v")])
        assert rc != 0  # errors result in non-zero exit

    def test_non_audio_file_probed(self, tmp_path, brief_yaml):
        """A text asset should still get SHA-256 but no audio probe info."""
        text_file = tmp_path / "lyrics.txt"
        text_file.write_text("Verse 1: ...")

        import yaml
        brief_data = yaml.safe_load(brief_yaml.read_text())
        brief_data["assets"] = [{"filename": "lyrics.txt", "role": "lyric_sheet"}]
        brief2 = tmp_path / "brief2.yaml"
        with open(brief2, "w") as f:
            yaml.dump(brief_data, f)

        session_dir = tmp_path / "session"
        cli_main(["session-init", "--brief", str(brief2), "--output-dir", str(session_dir)])

        manifest_path = session_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["assets"][0]["local_path"] = str(text_file)
        manifest_path.write_text(json.dumps(manifest, indent=2))

        verify_dir = tmp_path / "v"
        rc = cli_main(["asset-verify", "--manifest", str(manifest_path), "--output-dir", str(verify_dir)])
        assert rc == 0
        verified = json.loads((verify_dir / "manifest_verified.json").read_text())
        asset = verified["assets"][0]
        assert asset["sha256"] is not None
        # Audio fields should be None for text assets
        assert asset["sample_rate"] is None
