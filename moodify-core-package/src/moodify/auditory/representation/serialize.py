"""Representation serialization (MFY-PHASE1-DEPTH-003).

Inspectable JSON metadata plus compact dense NPZ arrays. JSON keeps NaN
as null so missing values survive round trips without semantic loss;
the NPZ companion stores the raw float planes.
"""

from __future__ import annotations

import json
from pathlib import Path
import numpy as np

from moodify.auditory.representation.models import AuditoryRepresentation


def save_representation(representation: AuditoryRepresentation, json_path: Path,
                        npz_path: Path | None = None) -> None:
    json_path = Path(json_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    payload = representation.to_dict()
    payload["_arrays"] = {sid: f"{json_path.stem}.{sid}.npy" for sid in representation.planes}
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=True), encoding="utf-8"
    )
    if npz_path is not None:
        npz_path = Path(npz_path)
        np.savez_compressed(
            npz_path,
            **{f"{sid}_values": plane.values for sid, plane in representation.planes.items()},
        )


def load_representation(json_path: Path) -> AuditoryRepresentation:
    json_path = Path(json_path)
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    payload.pop("_arrays", None)
    return AuditoryRepresentation.from_dict(payload)
