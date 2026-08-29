"""校准状态服务 — 轻量 HTTP API + 后台模拟器。

服务器上运行:
  nohup python3 server.py --port 8000 &

API:
  GET  /d              → {"D": 0.322, "n": 42, ...}
  GET  /d/history      → D 值增长历史
  GET  /emotions       → 各情绪校准详情
  GET  /emotions/{code} → 单个情绪 (bias, confidence, rho)
  POST /simulate       → 模拟 N 次处理并返回 D 增长轨迹
  POST /update         → 手动提交一次校准更新

不做 DSP。不需要音频。纯数值计算。
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime

import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

from moodify.calibration.online import CalibrationState, get_state


app = FastAPI(title="Moodify Calibration Engine", version="1.0")

STORAGE_DIR = os.environ.get("MOODIFY_OUTPUT", "/root/moodify/outputs")
HISTORY_PATH = os.path.join(STORAGE_DIR, "d_history.jsonl")


# ═══════════════════════════════════════════════════════════
#  Models
# ═══════════════════════════════════════════════════════════

class SimulateRequest(BaseModel):
    n: int = 50
    seed: int = 42
    emotions: list[str] = ["GA", "DR"]

class UpdateRequest(BaseModel):
    emotion_code: str
    proxy_score: float
    real_eds: float
    strength_vector: dict  # {"spectrum": 0.5, ...}
    ws_before: list[float]  # [E, D, S, T, H]
    ws_after: list[float]

class UpdateResponse(BaseModel):
    d_before: float
    d_after: float
    bias: float
    confidence: float


# ═══════════════════════════════════════════════════════════
#  Helpers
# ═══════════════════════════════════════════════════════════

def _record_d(n: int, d: float) -> None:
    os.makedirs(STORAGE_DIR, exist_ok=True)
    with open(HISTORY_PATH, "a") as f:
        f.write(json.dumps({"n": n, "D": round(d, 4),
                            "timestamp": datetime.now().isoformat()}) + "\n")

def _load_d_history() -> list[dict]:
    if not os.path.exists(HISTORY_PATH):
        return []
    records = []
    with open(HISTORY_PATH) as f:
        for line in f:
            try:
                records.append(json.loads(line))
            except Exception:
                pass
    return records


# ═══════════════════════════════════════════════════════════
#  API
# ═══════════════════════════════════════════════════════════

@app.get("/")
def root():
    return {"service": "Moodify Calibration Engine",
            "version": "1.0", "uptime": time.time() - app.state.start_time}

@app.get("/d")
def get_d():
    state = get_state(STORAGE_DIR)
    summary = state.summary()
    return {
        "D": summary["estimated_D"],
        "total_processed": summary["total_processed"],
        "emotions": summary["emotions"],
        "d_formula": "D = 0.05 + 0.35 * (1 - exp(-n_eff / 20))",
    }

@app.get("/d/history")
def get_d_history():
    return {"history": _load_d_history()}

@app.get("/emotions")
def get_emotions():
    state = get_state(STORAGE_DIR)
    return {"emotions": state.summary()["emotions"]}

@app.get("/emotions/{code}")
def get_emotion(code: str):
    state = get_state(STORAGE_DIR)
    return {
        "code": code,
        "n": state.emotions[code].n if code in state.emotions else 0,
        "mu_bias": round(state.get_bias(code), 3),
        "confidence": round(state.get_confidence(code), 3),
        "rho": state.estimate_rho(code),
        "mu_error_5d": state.get_error_5d(code).tolist() if code in state.emotions else [0]*5,
    }

@app.post("/simulate")
def simulate(req: SimulateRequest):
    """模拟 N 次处理, 返回 D 值增长轨迹。不写入持久化状态。"""
    state = CalibrationState()
    np.random.seed(req.seed)
    trajectory = []

    for i in range(1, req.n + 1):
        emotion = req.emotions[i % len(req.emotions)]
        proxy = 70.0 + np.random.randn() * 3
        real = proxy - 2.0 + np.random.randn() * 1.5

        state.update(
            emotion_code=emotion,
            proxy_score=float(proxy),
            real_eds=float(real),
            strength_vector={"spectrum": 0.5, "dynamic": 0.5, "space": 0.5,
                             "layer": 0.5, "master": 0.5},
            ws_before_5d=np.array([0.4, 0.5, 0.3, 0.5, 0.4]),
            ws_after_5d=np.array([0.5, 0.55, 0.35, 0.52, 0.45]),
        )

        if i in [1, 3, 5, 10, 20, 30, 50, 100] or i == req.n:
            trajectory.append({"n": i, "D": round(state.d_value(), 4)})

    return {"trajectory": trajectory, "final_D": round(state.d_value(), 4)}


@app.post("/update", response_model=UpdateResponse)
def update(req: UpdateRequest):
    """手动提交一次校准更新。本地 moodify process 完成后调用。"""
    state = get_state(STORAGE_DIR)
    d_before = state.d_value()

    state.update(
        emotion_code=req.emotion_code,
        proxy_score=req.proxy_score,
        real_eds=req.real_eds,
        strength_vector=req.strength_vector,
        ws_before_5d=np.array(req.ws_before),
        ws_after_5d=np.array(req.ws_after),
    )
    state.save()
    d_after = state.d_value()

    # 记录 D 变化
    _record_d(state.total_n, d_after)

    return UpdateResponse(
        d_before=round(d_before, 4),
        d_after=round(d_after, 4),
        bias=round(state.get_bias(req.emotion_code), 3),
        confidence=round(state.get_confidence(req.emotion_code), 3),
    )


@app.get("/health")
def health():
    state = get_state(STORAGE_DIR)
    return {
        "status": "ok",
        "storage": STORAGE_DIR,
        "total_processed": state.total_n,
        "estimated_D": round(state.d_value(), 3),
    }


# ═══════════════════════════════════════════════════════════
#  Entry
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Moodify Calibration Server")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--host", default="0.0.0.0")
    args = ap.parse_args()

    app.state.start_time = time.time()
    print(f"Moodify Calibration Server → http://{args.host}:{args.port}")
    print(f"Storage: {STORAGE_DIR}")
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
