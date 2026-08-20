"""Reopen and verify the golden Production Case.

Run:  python examples/golden_case/reopen_golden.py
Exits non-zero on any integrity or schema failure.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "moodify-core-package" / "src"))

from moodify.data_factory.dataset_builder import build_case_dataset

CASE = Path(__file__).parent


def main() -> None:
    record = build_case_dataset(CASE)
    rows = len(record["pairwise_preferences"])
    assert record["case_id"] == "case_00000000000000000000000000000001", record["case_id"]
    assert rows == 6, f"expected 6 pairwise rows, got {rows}"
    assert set(record["candidates"]) == {"A", "B", "C"}
    print(f"GOLDEN CASE OK: {rows} pairwise rows, {len(record['candidates'])} candidates")


if __name__ == "__main__":
    main()
