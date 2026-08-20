from __future__ import annotations

import importlib.util
import sqlite3
import tarfile
from pathlib import Path


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


MODULE = load_module(
    Path(__file__).parents[3] / "ops" / "data_node" / "metadata_backup.py",
    "metadata_backup",
)


def test_sqlite_backup_and_metadata_filter(tmp_path: Path):
    srcdb = tmp_path / "a.sqlite3"
    con = sqlite3.connect(srcdb)
    con.execute("CREATE TABLE t(x INTEGER)")
    con.execute("INSERT INTO t VALUES(1)")
    con.commit()
    con.close()

    dstdb = tmp_path / "b.sqlite3"
    assert MODULE.sqlite_backup(srcdb, dstdb)
    con = sqlite3.connect(dstdb)
    assert con.execute("SELECT x FROM t").fetchone()[0] == 1
    con.close()

    cases = tmp_path / "cases"
    cases.mkdir()
    (cases / "metrics.json").write_text("{}", encoding="utf-8")
    (cases / "audio.wav").write_bytes(b"heavy")
    archive = tmp_path / "meta.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        n = MODULE.add_metadata_tree(tar, cases, "cases")
    assert n == 1
    with tarfile.open(archive, "r:gz") as tar:
        names = tar.getnames()
    assert "cases/metrics.json" in names
    assert "cases/audio.wav" not in names
