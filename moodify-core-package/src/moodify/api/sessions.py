"""
Session-based API — upload, diagnose, match crafts, process, download.
Persists uploaded audio and processing results across requests.
"""

from __future__ import annotations

import os
import uuid
import shutil
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/v1", tags=["sessions"])

ALLOWED_EXTENSIONS = {".wav", ".mp3", ".flac", ".aiff", ".aif", ".m4a"}
MAX_FILE_SIZE = 200 * 1024 * 1024

# ── Storage ──────────────────────────────────────────
BASE_DIR = Path(__file__).parents[4]  # project root
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class Session:
    session_id: str
    filename: str
    file_path: str
    created_at: str
    status: str = "uploaded"
    duration_s: float = 0.0
    sample_rate: int = 0
    channels: int = 0
    diagnosis: dict | None = None
    craft_matches: list[dict] | None = None
    results: list[dict] = field(default_factory=list)


_store: dict[str, Session] = {}
_lock = threading.Lock()


def _lazy_imports():
    """Lazy imports to avoid heavy startup."""
    import sys
    from moodify.diagnosis.engine import DiagnosisEngine
    from moodify.diagnosis.defect_classifier import DefectClassifier
    from moodify.diagnosis.health_scorer import HealthScorer
    from moodify.knowledge.craft_chain_match import CraftChainMatch, generate_craft_cards_from_data
    from moodify.knowledge.emotion_targets import resolve_emotion
    from moodify.orchestration.workflow_engine import WorkflowOrchestrator

# ── Endpoints ────────────────────────────────────────


@router.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower() if file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported format: {ext}")

    raw = await file.read()
    if len(raw) > MAX_FILE_SIZE:
        raise HTTPException(413, "File too large")

    sid = uuid.uuid4().hex[:12]
    session_dir = UPLOAD_DIR / sid
    session_dir.mkdir(parents=True, exist_ok=True)
    file_path = session_dir / file.filename
    file_path.write_bytes(raw)

    # Read header
    import soundfile as sf
    import io
    try:
        info = sf.info(io.BytesIO(raw))
        dur, sr, ch = info.duration, info.samplerate, info.channels
    except Exception:
        dur, sr, ch = 0, 0, 0

    session = Session(
        session_id=sid,
        filename=file.filename,
        file_path=str(file_path.resolve()),
        created_at=datetime.now(timezone.utc).isoformat(),
        duration_s=round(dur, 1),
        sample_rate=sr,
        channels=ch,
    )
    with _lock:
        _store[sid] = session

    return {
        "session_id": sid,
        "filename": file.filename,
        "status": "uploaded",
        "created_at": session.created_at,
        "duration_s": session.duration_s,
        "sample_rate": session.sample_rate,
        "channels": session.channels,
    }


@router.get("/sessions")
async def list_sessions():
    with _lock:
        sessions = [
            {
                "session_id": s.session_id,
                "filename": s.filename,
                "status": s.status,
                "created_at": s.created_at,
            }
            for s in _store.values()
        ]
    return {"sessions": sessions}


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    with _lock:
        s = _store.get(session_id)
    if not s:
        raise HTTPException(404, "Session not found")
    return {
        "session_id": s.session_id,
        "filename": s.filename,
        "status": s.status,
        "created_at": s.created_at,
        "duration_s": s.duration_s,
        "sample_rate": s.sample_rate,
        "channels": s.channels,
        "diagnosis": s.diagnosis,
        "results": s.results,
    }


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    with _lock:
        if session_id not in _store:
            raise HTTPException(404, "Session not found")
        del _store[session_id]
    sd = UPLOAD_DIR / session_id
    if sd.exists():
        shutil.rmtree(sd, ignore_errors=True)
    return {"status": "deleted"}


@router.post("/sessions/{session_id}/diagnose")
async def diagnose_session(session_id: str):
    with _lock:
        s = _store.get(session_id)
    if not s:
        raise HTTPException(404, "Session not found")

    from moodify.diagnosis.engine import DiagnosisEngine
    from moodify.diagnosis.defect_classifier import DefectClassifier
    from moodify.diagnosis.health_scorer import HealthScorer

    t0 = time.perf_counter()
    engine = DiagnosisEngine()
    ws = engine.diagnose_quick(s.file_path)
    classifier = DefectClassifier()
    defects = classifier.classify(ws)
    scorer = HealthScorer()
    whs = scorer.compute_whs(ws, defects)
    elapsed = (time.perf_counter() - t0) * 1000

    diag = {
        "diagnosis_id": f"Dx-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "wave_state": ws.to_dict(),
        "defects": [d.to_dict() for d in defects],
        "health_score": {"whs": whs["WHS"], "level": whs["level"]},
        "duration_ms": round(elapsed, 0),
    }

    with _lock:
        s.diagnosis = diag
        s.status = "diagnosed"

    return diag


@router.get("/sessions/{session_id}/crafts")
async def get_session_crafts(session_id: str):
    with _lock:
        s = _store.get(session_id)
    if not s:
        raise HTTPException(404, "Session not found")
    if not s.diagnosis:
        raise HTTPException(400, "Run diagnosis first")

    from moodify.knowledge.craft_chains import CRAFT_CHAINS_15PARAMS
    from moodify.knowledge.emotion_targets import EMOTION_TARGETS_V2, CODE_TO_KEY

    diag_defects = s.diagnosis.get("defects", [])
    defect_descs = [d.get("description_zh", "") for d in diag_defects]

    # Build craft cards from knowledge base
    crafts = []
    for code, chain in CRAFT_CHAINS_15PARAMS.items():
        emotion_key = CODE_TO_KEY.get(code, "")
        emotion_info = EMOTION_TARGETS_V2.get(emotion_key, {})
        # Score: check common_defects overlap
        common = emotion_info.get("common_defects", [])
        hits = sum(1 for cd in common if any(cd in dd for dd in defect_descs))
        match_score = min(1.0, 0.40 + 0.12 * hits)

        crafts.append({
            "craft_id": f"CC-{code}-001",
            "name_zh": emotion_info.get("name_cn", code),
            "name_en": emotion_info.get("name_en", code),
            "emotion_target": emotion_info.get("primary", code),
            "match_score": round(match_score, 3),
            "sub_scores": {
                "dc": round(min(1.0, hits * 0.25), 2),
                "etf": 0.8,
                "wsc": 0.7,
                "cr": 0.9,
                "rs": 0.1,
            },
            "hard_blocked": False,
            "risk_warnings": chain.get("risk_warnings", [])[:3],
        })

    crafts.sort(key=lambda c: c["match_score"], reverse=True)

    with _lock:
        s.craft_matches = crafts

    return {"crafts": crafts}


@router.post("/sessions/{session_id}/process")
async def process_session(
    session_id: str,
    craft_id: str = Form(...),
    platform: str = Form("spotify"),
):
    with _lock:
        s = _store.get(session_id)
    if not s:
        raise HTTPException(404, "Session not found")

    from moodify.orchestration.workflow_engine import WorkflowOrchestrator
    from moodify.knowledge.emotion_targets import resolve_emotion, CODE_TO_KEY, EMOTION_TARGETS_V2

    # Resolve emotion target from craft ID (e.g., CC-GA-001 -> "GA" -> "gentle_awakening")
    code = craft_id[3:5] if len(craft_id) >= 5 and craft_id.startswith("CC-") else "GA"
    emotion_key = CODE_TO_KEY.get(code, "gentle_awakening")
    emotion_info = EMOTION_TARGETS_V2.get(emotion_key, {})
    emotion = emotion_info.get("name_cn", "温柔觉醒")

    out_dir = str(OUTPUT_DIR / session_id)
    os.makedirs(out_dir, exist_ok=True)

    orchestrator = WorkflowOrchestrator()
    result = orchestrator.process(
        input_path=s.file_path,
        emotion_target=emotion,
        platform=platform,
        mode="auto",
        output_dir=out_dir,
    )

    res = {
        "process_id": result.process_id,
        "success": result.success,
        "emotion_target": result.emotion_target,
        "craft_id": craft_id,
        "wave_state_before": result.wave_state_before,
        "wave_state_after": result.wave_state_after,
        "delta": result.delta,
        "whs_before": result.whs_before,
        "whs_after": result.whs_after,
        "eds": result.eds,
        "total_risk": result.total_risk,
        "risk_level": result.risk_level,
        "total_elapsed_ms": result.total_elapsed_ms,
        "output_file": Path(result.output_path).name if result.output_path else "",
        "download_url": f"/api/v1/download/{session_id}/{Path(result.output_path).name}" if result.output_path else "",
        "phases": [
            {"phase": p.phase, "name": p.name, "status": p.status.value,
             "warnings": p.warnings, "elapsed_ms": p.elapsed_ms}
            for p in result.phases
        ],
    }

    with _lock:
        s.results.append(res)
        s.status = "processed"

    return res


@router.get("/download/{session_id}/{filename}")
async def download_file(session_id: str, filename: str):
    fp = OUTPUT_DIR / session_id / filename
    if not fp.exists():
        raise HTTPException(404, "File not found")
    return FileResponse(str(fp), media_type="audio/wav", filename=filename)
