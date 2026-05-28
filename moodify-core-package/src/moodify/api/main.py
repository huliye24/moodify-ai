"""
Moodify Core Engine REST API (SPEC §18)
========================================
Endpoints:
  POST /api/v1/analyze    — 上传音频 → 诊断报告
  POST /api/v1/process    — 上传音频 → 一键处理 → 输出
  GET  /api/v1/craft_cards — 浏览工艺库
  GET  /health            — 健康检查
"""

import os
import uuid
import tempfile
import time
from datetime import datetime
from typing import Optional
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB

app = FastAPI(
    title="Moodify Core Engine API",
    description="情绪波场显影器 API — 诊断、处理、评估 AI 生成的音乐",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register session-based API router
from moodify.api.sessions import router as sessions_router
app.include_router(sessions_router)

# 延迟加载 (避免启动时的重导入)
_engine = None
_orchestrator = None


def _get_engine():
    global _engine
    if _engine is None:
        import sys
        from moodify.diagnosis.engine import DiagnosisEngine
        _engine = DiagnosisEngine()
    return _engine


def _get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        import sys
        from moodify.orchestration.workflow_engine import WorkflowOrchestrator
        _orchestrator = WorkflowOrchestrator()
    return _orchestrator


# ============================================================
#  Models
# ============================================================

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"


class DiagnosisResponse(BaseModel):
    diagnosis_id: str
    wave_state: dict
    defects: list[dict]
    health_score: dict
    recommendations: dict
    duration_ms: float


class ProcessResponse(BaseModel):
    process_id: str
    success: bool
    output_path: str
    emotion_target: str
    wave_state_before: dict
    wave_state_after: dict
    delta: dict
    whs_before: float
    whs_after: float
    eds: float
    total_risk: float
    risk_level: str
    total_elapsed_ms: float
    phases: list[dict]


# ============================================================
#  Routes
# ============================================================

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse()


@app.post("/api/v1/analyze")
async def analyze(
    audio_file: UploadFile = File(...),
    mode: str = Form("quick"),
    detect_emotion: bool = Form(False),
):
    """
    分析 AI 生成的音频 → 完整诊断报告 (SPEC §18.2)

    - **mode**: "quick" (最小测量集 14 自动参数) | "full" (全量 18 参数)
    - **detect_emotion**: 是否自动检测情绪方向
    """
    # 保存上传文件
    temp_dir = tempfile.mkdtemp()
    ext = Path(audio_file.filename).suffix or ".wav"
    temp_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}{ext}")

    content = await audio_file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large. Max {MAX_UPLOAD_SIZE // (1024*1024)} MB")
    with open(temp_path, "wb") as f:
        f.write(content)

    t0 = time.perf_counter()

    try:
        engine = _get_engine()
        from moodify.diagnosis.defect_classifier import DefectClassifier
        from moodify.diagnosis.health_scorer import HealthScorer

        ws = engine.diagnose_quick(temp_path)
        classifier = DefectClassifier()
        defects = classifier.classify(ws)
        scorer = HealthScorer()
        whs = scorer.compute_whs(ws, defects)

        elapsed = (time.perf_counter() - t0) * 1000
        diag_id = f"Dx-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        return DiagnosisResponse(
            diagnosis_id=diag_id,
            wave_state=ws.to_dict(),
            defects=[d.to_dict() for d in defects],
            health_score={"whs": whs["WHS"], "level": whs["level"]},
            recommendations={"suggested_emotions": _suggest_emotions(defects, ws)},
            duration_ms=round(elapsed, 0),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            os.remove(temp_path)
            os.rmdir(temp_dir)
        except Exception:
            pass


@app.post("/api/v1/process")
async def process(
    audio_file: UploadFile = File(...),
    emotion_target: str = Form(..., description="目标情绪 (温柔觉醒/神圣空灵/...)"),
    mode: str = Form("auto"),
    craft_card_id: Optional[str] = Form(None),
    platform: str = Form("spotify"),
):
    """
    一键处理: 自动诊断 → 工艺匹配 → DSP → 母带 → 输出 (SPEC §18.2)

    - **emotion_target**: 8 种标准情绪之一
    - **mode**: "auto" (全自动) | "expert" (手动指定工艺卡)
    - **platform**: spotify / youtube / apple_music
    """
    temp_dir = tempfile.mkdtemp()
    ext = Path(audio_file.filename).suffix or ".wav"
    temp_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}{ext}")
    with open(temp_path, "wb") as f:
        f.write(await audio_file.read())

    try:
        orchestrator = _get_orchestrator()
        result = orchestrator.process(
            input_path=temp_path,
            emotion_target=emotion_target,
            platform=platform,
            mode=mode,
            craft_card_id=craft_card_id,
        )

        return ProcessResponse(
            process_id=result.process_id,
            success=result.success,
            output_path=result.output_path,
            emotion_target=result.emotion_target,
            wave_state_before=result.wave_state_before,
            wave_state_after=result.wave_state_after,
            delta=result.delta,
            whs_before=result.whs_before,
            whs_after=result.whs_after,
            eds=result.eds,
            total_risk=result.total_risk,
            risk_level=result.risk_level,
            total_elapsed_ms=result.total_elapsed_ms,
            phases=[{
                "phase": p.phase,
                "name": p.name,
                "status": p.status.value,
                "warnings": p.warnings,
                "elapsed_ms": p.elapsed_ms,
            } for p in result.phases],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            os.remove(temp_path)
            os.rmdir(temp_dir)
        except Exception:
            pass


@app.get("/api/v1/craft_cards")
async def list_craft_cards(emotion: Optional[str] = None):
    """浏览工艺库"""
    try:
        from moodify.knowledge.craft_chain_match import generate_craft_cards_from_data
        cards = generate_craft_cards_from_data()

        if emotion:
            filtered = []
            for c in cards:
                if emotion in c.target_emotion.primary or emotion in c.name_zh:
                    filtered.append(c.to_dict())
            return {"crafts": filtered, "total": len(filtered)}
        return {"crafts": [c.to_dict() for c in cards], "total": len(cards)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/emotions")
async def list_emotions():
    """列出所有可用情绪"""
    from moodify.knowledge.emotion_targets import EMOTION_TARGETS_V2
    return {
        "emotions": [
            {"key": k, "code": v["code"], "name_zh": v["name_cn"],
             "name_en": v["name_en"], "primary": v["primary"]}
            for k, v in EMOTION_TARGETS_V2.items()
        ]
    }


def _suggest_emotions(defects, ws) -> list[str]:
    """根据诊断结果推荐情绪方向"""
    suggestions = []
    s = ws.Spectrum
    d = ws.Dynamics

    if s.S4_AirBand < -4 and d.D1_LRA < 6:
        suggestions.extend(["都市危险", "废土机械"])
    elif s.S4_AirBand > 2 and d.D1_LRA > 8:
        suggestions.extend(["神圣空灵", "电影感"])
    elif s.S2_BassWarmth > -1 and s.S3_MidClarity > 0.5:
        suggestions.extend(["温柔觉醒", "治愈温暖"])
    elif s.S3_MidClarity < 0.4:
        suggestions.extend(["黑暗浪漫", "孤独留白"])

    if not suggestions:
        suggestions = ["温柔觉醒", "治愈温暖"]
    return suggestions[:3]
