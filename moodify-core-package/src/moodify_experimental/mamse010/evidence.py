"""MAMSE-010 evidence contract: bundle JSON + NPZ + manifest."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import scipy

from .contracts import AuditoryTensorBundle, SCHEMA_VERSION

MANIFEST_SCHEMA_VERSION = "mamse-010-manifest-v1"


def _git_commit() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5)
        return out.stdout.strip() if out.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def save_bundle(bundle: AuditoryTensorBundle, out_dir: str | Path) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    meta = bundle.to_meta()
    (out / "tensor_bundle.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
    )
    arrays: dict[str, np.ndarray] = {}
    for name, field in sorted(bundle.fields.items()):
        arrays[f"{name}__data"] = field.data
        arrays[f"{name}__valid_mask"] = field.valid_mask.astype(np.uint8)
    np.savez_compressed(out / "tensor_bundle.npz", **arrays)
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "operator_id": "MAMSE-010",
        "schema_version_tensor": SCHEMA_VERSION,
        "tensor_id": bundle.tensor_id,
        "source_sha256": bundle.source_sha256,
        "profile_ids": bundle.profile_ids,
        "git_commit": _git_commit(),
        "runtime": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    (out / "mamse010_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def load_bundle(out_dir: str | Path) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    out = Path(out_dir)
    meta = json.loads((out / "tensor_bundle.json").read_text(encoding="utf-8"))
    z = np.load(out / "tensor_bundle.npz")
    return meta, {k: z[k] for k in z.files}
