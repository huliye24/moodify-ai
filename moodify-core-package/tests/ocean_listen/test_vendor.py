from pathlib import Path

from moodify.adapters.auditory.ocean_listen.vendor import vendor_snapshot


def test_vendor_preserves_license_and_notice(tmp_path: Path):
    source = tmp_path / "ocean"
    (source / "modules").mkdir(parents=True)
    (source / "LICENSE").write_text("MIT", encoding="utf-8")
    (source / "NOTICES").write_text("notices", encoding="utf-8")
    (source / "README.md").write_text("readme", encoding="utf-8")
    (source / "ocean.py").write_text("print('x')", encoding="utf-8")
    (source / "modules" / "classifier.py").write_text("X = 1", encoding="utf-8")

    target = tmp_path / "vendor"
    result = vendor_snapshot(source, target)

    assert (target / "LICENSE").read_text(encoding="utf-8") == "MIT"
    assert (target / "NOTICES").read_text(encoding="utf-8") == "notices"
    assert (target / "MOODIFY_VENDOR_MANIFEST.json").is_file()
    assert "LICENSE" in result["copied_paths"]
