from moodify.node.resources import safe_to_start, snapshot


def test_resource_snapshot_has_disk(tmp_path):
    snap = snapshot(tmp_path)
    assert snap.free_disk_gb > 0
    assert snap.available_memory_mb >= 0


def test_resource_guard_rejects_impossible_disk_requirement(tmp_path):
    allowed, _, _ = safe_to_start(tmp_path, 0, 10**9)
    assert allowed is False
