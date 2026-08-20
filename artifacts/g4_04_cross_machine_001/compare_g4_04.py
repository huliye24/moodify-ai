"""G4-04 cross-machine repeatability analysis.

Compares before-scan metrics for the same byte-identical source
(10_viens_chez_moi.wav, sha256 c3886611...) scanned on:
  - local dev machine (Windows, Python 3.11)
  - Aliyun data node 120.55.191.146 (Ubuntu, Python 3.14)
Both used MFY-WSE-SCAN-PROFILE-001 (hash f0ff177d...).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

LOCAL = Path("E:/moodify/outputs/g4_04_cross_machine/local_scan/metrics.json")
NODE = Path("E:/moodify/outputs/g4_04_cross_machine/node_metrics.json")

# metrics that must match exactly across machines
EXACT = {
    "sample_rate", "channels", "duration", "clipping_sample_count",
    "invalid_sample_count", "finite_sample_ratio",
}

local = json.loads(LOCAL.read_text(encoding="utf-8"))
node = json.loads(NODE.read_text(encoding="utf-8"))

rows = []
for key in sorted(set(local) | set(node)):
    lv = local.get(key)
    nv = node.get(key)
    lv_num = lv.get("value") if isinstance(lv, dict) else lv
    nv_num = nv.get("value") if isinstance(nv, dict) else nv
    if not isinstance(lv_num, (int, float)) or not isinstance(nv_num, (int, float)):
        continue
    abs_diff = nv_num - lv_num
    rel_diff = abs_diff / abs(lv_num) if lv_num else (0.0 if abs_diff == 0 else float("inf"))
    unit = (lv.get("unit") if isinstance(lv, dict) else "") or ""
    rows.append((key, unit, lv_num, nv_num, abs_diff, rel_diff))

rows.sort(key=lambda r: -abs(r[4]))

print(f"{'metric':42} {'unit':8} {'local':>12} {'node':>12} {'abs_diff':>12} {'rel_diff':>10}")
print("-" * 100)
for key, unit, lv, nv, ad, rd in rows:
    print(f"{key:42} {unit:8} {lv:>12.6g} {nv:>12.6g} {ad:>12.6g} {rd:>10.2e}")

worst = rows[0]
exact_fail = [r for r in rows if r[0] in EXACT and r[4] != 0]
print("\n== summary ==")
print(f"metrics compared: {len(rows)}")
print(f"largest abs diff: {worst[0]} ({worst[5]:.2e} rel)")
print(f"exact-match metrics violated: {[r[0] for r in exact_fail] or 'none'}")
