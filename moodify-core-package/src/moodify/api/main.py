"""Moodify API -- v0.1.0 mainline.

v0.1.0 API contract:
    GET  /health
    GET  /presets
    POST /process

Mainline:
    upload audio -> v01_pipeline.process_audio() -> WAV output

Important:
    The legacy WorkflowOrchestrator is intentionally NOT used here.
    It is preserved in moodify.orchestration.workflow_engine for future v1.x.
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from moodify.v01_pipeline import process_audio
from moodify.v01_presets import PRESETS, list_presets
from moodify.api.routes.lyric_align import router as lyric_align_router
from moodify.api.routes.pairwise_judge import router as pairwise_judge_router
from moodify.api.routes.ntrack_ranking import router as ntrack_ranking_router
from moodify.api.routes.access import router as access_router
from moodify.api.routes.workspace_projects import router as workspace_projects_router
from moodify.api.routes.v1 import router as mobile_v1_router
from moodify_runtime.config import load_config
from moodify_runtime.operator_console import (
    attach_run_report_to_job,
    create_operator_job,
    get_operator_job_detail,
    list_operator_jobs,
)


APP_VERSION = "0.1.0"
API_MODE = "v01"
MAX_SIZE = 50 * 1024 * 1024  # 50 MB
DEFAULT_OUTPUT_DIR = "outputs"
DEFAULT_PRESET = "clean_master"


class OperatorJobCreateRequest(BaseModel):
    source_audio: str
    processing_depth: str = "quick_scan"
    project_label: str = ""
    customer_label: str = ""
    target_notes: str = ""
    priority: int = 5
    delivery_mode: str = "report_bundle"


class OperatorAttachRunRequest(BaseModel):
    run_id: str
    run_dir: Optional[str] = None
    report_path: Optional[str] = None
    required_mrs_delta: float = 0.0




app = FastAPI(
    title="Moodify",
    version=APP_VERSION,
    description="Moodify v0.1.0 -- AI music post-processing engine",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(workspace_projects_router)
app.include_router(mobile_v1_router)
app.include_router(lyric_align_router)
app.include_router(pairwise_judge_router)
app.include_router(ntrack_ranking_router)
app.include_router(access_router)


# Legacy emotion compatibility.
# v0.1.0 canonical API uses `preset`.
# `emotion` is accepted only to avoid breaking old frontend/API calls.
EMOTION_TO_PRESET = {
    "gentle_awakening": "warm_vocal",
    "温柔觉醒": "warm_vocal",
    "sacred_ethereal": "warm_vocal",
    "神圣空灵": "warm_vocal",
    "warm": "warm_vocal",
    "vocal": "warm_vocal",

    "dark_romance": "wide_space",
    "黑暗浪漫": "wide_space",
    "cinematic": "wide_space",
    "电影感": "wide_space",
    "space": "wide_space",
    "wide": "wide_space",

    "clean": "clean_master",
    "master": "clean_master",
    "default": "clean_master",
    "clean_master": "clean_master",
}


def _resolve_preset(preset: Optional[str], emotion: Optional[str]) -> tuple[str, str]:
    """Resolve API input to one v0.1.0 preset.

    Priority:
        1. preset
        2. emotion -> preset compatibility mapping
        3. clean_master fallback

    Returns:
        (resolved_preset, source)
    """
    valid_presets = {"auto", *list_presets()}

    if preset:
        key = preset.strip()
        if key not in valid_presets:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": f"Unknown preset: {key}",
                    "valid_presets": sorted(valid_presets),
                },
            )
        return key, "preset"

    if emotion:
        key = emotion.strip()
        mapped = EMOTION_TO_PRESET.get(key)

        # Also allow users to pass a preset in the old emotion field.
        if key in valid_presets:
            return key, "emotion_as_preset"

        if mapped:
            return mapped, "emotion_mapping"

        return DEFAULT_PRESET, "emotion_fallback"

    return DEFAULT_PRESET, "default"


def _result_header(result, elapsed_ms: float, preset_source: str) -> str:
    """Compact JSON metadata for response header."""
    payload = {
        "success": result.success,
        "preset": result.preset,
        "preset_source": preset_source,
        "elapsed_ms": round(elapsed_ms, 1),
        "output": Path(result.output_path).name if result.output_path else "",
        "health": result.diagnosis.overall_health if result.diagnosis else "",
        "issues": result.diagnosis.issues[:3] if result.diagnosis else [],
    }
    return json.dumps(payload, ensure_ascii=True)[:1000]



def _runtime_cfg():
    return load_config(os.environ.get("MOODIFY_RUNTIME_CONFIG"))


def _operator_error(exc: Exception) -> HTTPException:
    if isinstance(exc, KeyError):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, (ValueError, FileNotFoundError)):
        return HTTPException(status_code=400, detail=str(exc))
    return HTTPException(status_code=500, detail=f"{type(exc).__name__}: {exc}")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": APP_VERSION,
        "mode": API_MODE,
        "mainline": "v01_pipeline",
    }


@app.get("/presets")
async def presets():
    """List v0.1.0 processing presets."""
    return {
        "version": APP_VERSION,
        "mode": API_MODE,
        "default": DEFAULT_PRESET,
        "presets": [
            {
                "key": key,
                "name": value["name"],
                "name_zh": value["name_zh"],
                "description": value["description"],
            }
            for key, value in PRESETS.items()
        ],
    }



@app.post("/operator/jobs")
async def operator_create_job(request: OperatorJobCreateRequest):
    try:
        return create_operator_job(
            _runtime_cfg(),
            source_audio=request.source_audio,
            processing_depth=request.processing_depth,
            project_label=request.project_label,
            customer_label=request.customer_label,
            target_notes=request.target_notes,
            priority=request.priority,
            delivery_mode=request.delivery_mode,
        )
    except Exception as exc:
        raise _operator_error(exc) from exc


@app.get("/operator/jobs")
async def operator_list_jobs(status: Optional[str] = None):
    try:
        return {"jobs": list_operator_jobs(_runtime_cfg(), status=status)}
    except Exception as exc:
        raise _operator_error(exc) from exc


@app.get("/operator/jobs/{job_id}")
async def operator_job_detail(job_id: str):
    try:
        return get_operator_job_detail(_runtime_cfg(), job_id=job_id)
    except Exception as exc:
        raise _operator_error(exc) from exc


@app.post("/operator/jobs/{job_id}/attach-run")
async def operator_attach_run(job_id: str, request: OperatorAttachRunRequest):
    try:
        return attach_run_report_to_job(
            _runtime_cfg(),
            job_id=job_id,
            run_id=request.run_id,
            run_dir=request.run_dir,
            report_path=request.report_path,
            required_mrs_delta=request.required_mrs_delta,
        )
    except Exception as exc:
        raise _operator_error(exc) from exc

@app.post("/process")
async def process(
    audio: UploadFile = File(...),
    preset: Optional[str] = Form(
        None,
        description="v0.1.0 preset: auto / warm_vocal / clean_master / wide_space",
    ),
    emotion: Optional[str] = Form(
        None,
        description="Legacy emotion parameter. Accepted for compatibility only.",
    ),
    platform: str = Form(
        "spotify",
        description="Legacy field. Accepted but ignored in v0.1.0.",
    ),
    output_dir: str = Form(
        DEFAULT_OUTPUT_DIR,
        description="Output directory for processed audio and report.",
    ),
    return_json: bool = Form(
        False,
        description="If true, return JSON metadata instead of WAV file.",
    ),
):
    """Process one audio file through the v0.1.0 pipeline.

    v0.1.0 flow:
        upload -> scan -> analyze -> diagnose -> smart process -> report -> export WAV

    Success default:
        returns audio/wav FileResponse

    Optional:
        return_json=true returns metadata JSON instead of file.
    """
    resolved_preset, preset_source = _resolve_preset(preset, emotion)

    ext = Path(audio.filename or "upload.wav").suffix or ".wav"

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tf:
        content = await audio.read()

        if len(content) > MAX_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max {MAX_SIZE // 1024**2} MB",
            )

        tf.write(content)
        tmp_path = tf.name

    t0 = time.perf_counter()

    try:
        result = process_audio(
            input_path=tmp_path,
            preset=resolved_preset,
            output_dir=output_dir,
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000

        if not result.success:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "version": APP_VERSION,
                    "mode": API_MODE,
                    "preset": resolved_preset,
                    "preset_source": preset_source,
                    "error": result.error,
                    "elapsed_ms": round(elapsed_ms, 1),
                },
            )

        diagnosis = result.diagnosis.to_dict() if result.diagnosis else {}
        metrics = (
            result.metrics_before.to_dict()
            if result.metrics_before
            else {}
        )

        response_payload = {
            "success": True,
            "version": APP_VERSION,
            "mode": API_MODE,
            "requested_preset": result.requested_preset,
            "preset": result.preset,
            "preset_source": preset_source,
            "legacy_platform_ignored": platform,
            "output_path": result.output_path,
            "report_path": result.report_path,
            "elapsed_ms": round(elapsed_ms, 1),
            "diagnosis": diagnosis,
            "metrics_before": metrics,
            "metrics_after": result.metrics_after.to_dict(),
            "quality_gate": result.quality_gate.to_dict(),
            "delivery": result.delivery.to_dict(),
        }

        if return_json:
            return response_payload

        if not result.output_path or not Path(result.output_path).exists():
            raise HTTPException(
                status_code=500,
                detail="Processing succeeded but output file was not found.",
            )

        return FileResponse(
            result.output_path,
            media_type="audio/wav",
            filename=Path(result.output_path).name,
            headers={
                "X-Moodify-Version": APP_VERSION,
                "X-Moodify-Mode": API_MODE,
                "X-Moodify-Preset": result.preset,
                "X-Moodify-Preset-Source": preset_source,
                "X-Process-Result": _result_header(
                    result=result,
                    elapsed_ms=elapsed_ms,
                    preset_source=preset_source,
                ),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
