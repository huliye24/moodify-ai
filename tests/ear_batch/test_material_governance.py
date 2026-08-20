import importlib.util
import json
from pathlib import Path


MODULE_PATH = Path(__file__).parents[2] / "ops" / "ear_batch" / "material_governance.py"
SPEC = importlib.util.spec_from_file_location("material_governance", MODULE_PATH)
material = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(material)


def test_sha256(tmp_path):
    path = tmp_path / "value.txt"
    path.write_bytes(b"abc")
    assert material.sha256(path) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_write_json_preserves_unicode(tmp_path):
    path = tmp_path / "value.json"
    material.write_json(path, {"name": "听见"})
    assert json.loads(path.read_text(encoding="utf-8"))["name"] == "听见"
