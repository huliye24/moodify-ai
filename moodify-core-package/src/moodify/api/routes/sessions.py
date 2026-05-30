"""Sessions API — 历史记录浏览 + 反馈提交."""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import json

router = APIRouter(prefix="/sessions", tags=["sessions"])


class FeedbackRequest(BaseModel):
    session_id: str
    rating: int  # 1-5
    notes: Optional[str] = ""
    preferred_version: Optional[str] = None


class SessionResponse(BaseModel):
    session_id: str
    filename: str
    emotion_code: str
    emotion_name: str
    whs_before: float
    whs_after: float
    eds: float
    proxy_score: float
    real_eds: Optional[float]
    ai_score: Optional[float]
    user_rating: Optional[int]
    timestamp: str


@router.get("", response_model=list[SessionResponse])
async def list_sessions(limit: int = 50, offset: int = 0):
    """列出最近的处理记录."""
    from moodify.memory.history import ProcessingHistory

    history = ProcessingHistory()
    if not history._path.exists():
        return []

    with open(history._path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    records = []
    for line in reversed(lines[offset:offset + limit]):
        try:
            rec = json.loads(line.strip())
            records.append(SessionResponse(
                session_id=rec.get("timestamp", ""),
                filename=rec.get("filename", "unknown"),
                emotion_code=rec.get("emotion_code", "?"),
                emotion_name=rec.get("emotion_name", ""),
                whs_before=rec.get("whs_before", 0.0),
                whs_after=rec.get("whs_after", 0.0),
                eds=rec.get("eds", 0.0),
                proxy_score=rec.get("proxy_score", 0.0),
                real_eds=rec.get("eds"),
                ai_score=rec.get("eds", 0.0) * 2 + 50 if rec.get("eds") else None,
                user_rating=int(rec.get("satisfied", 0) * 5) if rec.get("satisfied") is not None else None,
                timestamp=rec.get("timestamp", ""),
            ))
        except Exception:
            continue
    return records


@router.post("/feedback")
async def submit_feedback(req: FeedbackRequest):
    """提交用户反馈，更新校准状态."""
    from moodify.memory.history import ProcessingHistory

    history = ProcessingHistory()
    if history._path.exists():
        with open(history._path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        updated = False
        new_lines = []
        for line in reversed(lines):
            try:
                rec = json.loads(line.strip())
                if req.session_id in rec.get("timestamp", ""):
                    rec["satisfied"] = req.rating / 5.0
                    rec["user_feedback"] = req.notes
                    updated = True
                new_lines.insert(0, json.dumps(rec, ensure_ascii=False) + "\n")
            except Exception:
                new_lines.insert(0, line)

        if updated:
            with open(history._path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

    return {"success": True, "message": f"Rating {req.rating}/5 recorded"}
