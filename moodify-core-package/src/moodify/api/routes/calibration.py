"""Calibration Status API — D 值实时查询."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/calibration", tags=["calibration"])


class DStatusResponse(BaseModel):
    d_value: float
    total_n: int
    d_max: float
    lambda_param: float
    emotions: dict


@router.get("/status", response_model=DStatusResponse)
async def get_calibration_status():
    """返回当前 D 值和各情绪的校准统计."""
    from moodify.calibration.online import CalibrationState

    try:
        state = CalibrationState.load()
        summary = state.summary()
        return DStatusResponse(
            d_value=summary.get("estimated_D", 0.05),
            total_n=summary.get("total_processed", 0),
            d_max=0.40,
            lambda_param=20.0,
            emotions=summary.get("emotions", {}),
        )
    except Exception:
        return DStatusResponse(
            d_value=0.05,
            total_n=0,
            d_max=0.40,
            lambda_param=20.0,
            emotions={},
        )
