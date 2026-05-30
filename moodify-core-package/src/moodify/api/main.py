"""Moodify API — single endpoint. Upload audio + emotion → processed result.

Design: stateless, no sessions. Processing history IS the state (memory/history.py).
         C is minimized — every line serves T_audio or E_exec directly.
"""

import os, uuid, tempfile, time
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Moodify", version="0.3.0")

# CORS: 允许 Web 前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册新增路由 (SPEC-014 T-A)
from moodify.api.routes import sessions, calibration

app.include_router(sessions.router)
app.include_router(calibration.router)
MAX_SIZE = 50 * 1024 * 1024  # 50 MB

_orchestrator = None


def _get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        from moodify.orchestration.workflow_engine import WorkflowOrchestrator
        _orchestrator = WorkflowOrchestrator()
    return _orchestrator


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.2.0"}


@app.post("/process")
async def process(
    audio: UploadFile = File(...),
    emotion: str = Form(..., description="Target emotion (温柔觉醒/黑暗浪漫/...)"),
    platform: str = Form("spotify"),
):
    """Process audio through the full pipeline: diagnose → search → DSP → output."""
    ext = Path(audio.filename).suffix or ".wav"
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tf:
        content = await audio.read()
        if len(content) > MAX_SIZE:
            raise HTTPException(413, f"File too large. Max {MAX_SIZE // 1024**2} MB")
        tf.write(content)
        tmp_path = tf.name

    t0 = time.perf_counter()
    try:
        result = _get_orchestrator().process(
            input_path=tmp_path, emotion_target=emotion, platform=platform)
        elapsed = (time.perf_counter() - t0) * 1000
        response = {
            "success": result.success,
            "emotion_target": result.emotion_target,
            "whs_before": result.whs_before, "whs_after": result.whs_after,
            "eds": result.eds, "risk_level": result.risk_level,
            "total_elapsed_ms": elapsed,
            "phases": [{"phase": p.phase, "name": p.name, "status": p.status.value,
                        "warnings": p.warnings, "elapsed_ms": p.elapsed_ms}
                       for p in result.phases],
        }
        if result.success and result.output_path:
            return FileResponse(
                result.output_path, media_type="audio/wav",
                filename=Path(result.output_path).name,
                headers={"X-Process-Result": str(response).replace("\n", " ")[:500]},
            )
        return response
    except Exception as e:
        raise HTTPException(500, detail=str(e))
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
