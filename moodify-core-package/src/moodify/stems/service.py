"""Stem separation orchestration (LALAL-STEMS-001)."""

from __future__ import annotations

import math
import os
from datetime import datetime, timezone
from pathlib import Path

from .client import LalalClient
from .constants import DEFAULT_BASE_URL
from .errors import StemError
from .store import StemJob, StemStatus, StemStore

POLL_MIN_SECONDS = 5.0
DOWNLOAD_TTL_HOURS = 23.0


def _store() -> StemStore:
    db = os.environ.get("MOODIFY_STEMS_DB")
    if not db:
        from moodify.node.config import NodeConfig

        db = str(NodeConfig.from_env().state_dir / "stems.sqlite3")
    return StemStore(Path(db))


def _client() -> LalalClient:
    key = os.environ.get("LALAL_LICENSE_KEY", "")
    base = os.environ.get("MOODIFY_LALAL_BASE_URL", DEFAULT_BASE_URL)
    return LalalClient(key, base_url=base)


def _license_present() -> bool:
    return bool(os.environ.get("LALAL_LICENSE_KEY", "").strip())


def uploads_dir() -> Path:
    from moodify.node.config import NodeConfig

    return NodeConfig.from_env().state_dir / "stems" / "uploads"


def estimate_duration(path: Path) -> float | None:
    """Best-effort duration in seconds; None when the file is not decodable."""
    try:
        import soundfile as sf

        return float(sf.info(str(path)).duration)
    except Exception:
        return None


def estimate_pro_minutes(duration_seconds: float | None, stem_count: int) -> float | None:
    if duration_seconds is None:
        return None
    return math.ceil(duration_seconds / 60.0) * stem_count


def _poll_due(job: StemJob) -> bool:
    if job.last_checked_at is None:
        return True
    try:
        last = datetime.fromisoformat(job.last_checked_at)
    except ValueError:
        return True
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - last).total_seconds() >= float(
        os.environ.get("MOODIFY_STEMS_POLL_MIN_SECONDS", str(POLL_MIN_SECONDS))
    )


def _extract_tracks(result) -> list[dict]:
    """Normalize lalal /check/ result payloads into a list of track dicts.

    v1 returns {"tracks": [{"type": "stem"|"back", "label": ..., "url": ...}, ...]};
    a plain list of {"url": ...} is tolerated for older payloads.
    """
    if isinstance(result, dict):
        tracks = result.get("tracks")
        if isinstance(tracks, list):
            return [t for t in tracks if isinstance(t, dict)]
        return []
    if isinstance(result, list):
        return [item for item in result if isinstance(item, dict) and item.get("url")]
    return []


def submit(
    *,
    source_path: Path,
    source_name: str,
    source_bytes: int,
    stems: list[str],
    extraction_level: str,
    splitter: str,
    dereverb_enabled: bool = False,
    multivocal: str | None = None,
) -> StemJob:
    """Create the ledger row, upload to lalal.ai and submit one task per stem."""
    duration = estimate_duration(source_path)
    store = _store()
    job = store.create(
        source_name=source_name,
        source_path=source_path,
        source_bytes=source_bytes,
        stems=stems,
        extraction_level=extraction_level,
        splitter=splitter,
        dereverb_enabled=dereverb_enabled,
        multivocal=multivocal,
        duration_seconds=duration,
        estimated_pro_minutes=estimate_pro_minutes(duration, len(stems)),
    )
    try:
        client = _client()
        source_id = client.upload(source_path, source_name)
        task_ids: dict[str, str] = {}
        for stem in stems:
            presets = {
                "stem": stem,
                "extraction_level": extraction_level,
                "splitter": splitter,
            }
            if dereverb_enabled:
                presets["dereverb_enabled"] = True
            if multivocal and stem == "vocals":
                presets["multivocal"] = multivocal
            task_ids[stem] = client.split(source_id, presets)
        store.update_submitted(job.job_id, source_id, task_ids)
        store.delete_source_file(job.job_id)
        return store.get(job.job_id) or job
    except StemError as exc:
        store.update_status(
            job.job_id,
            status=StemStatus.FAILED,
            last_error=f"{type(exc).__name__}: {exc.message}",
        )
        raise


def refresh(job: StemJob) -> StemJob:
    """Live-poll lalal.ai for a non-terminal job and persist the outcome."""
    if job.is_terminal:
        return job
    client = _client()
    result = client.check(list(job.task_ids.values()))
    by_stem = {stem: result[task_id] for stem, task_id in job.task_ids.items()}
    statuses = [item.get("status") for item in by_stem.values()]
    if any(s == "error" for s in statuses):
        error = next(
            (str(item) for item in by_stem.values() if item.get("status") == "error"),
            "lalal.ai reported an error",
        )
        store = _store()
        store.update_status(
            job.job_id,
            status=StemStatus.FAILED,
            last_error=f"lalal error: {error[:2000]}",
        )
        return store.get(job.job_id) or job
    if any(s == "cancelled" for s in statuses):
        store = _store()
        store.update_status(job.job_id, status=StemStatus.CANCELLED)
        return store.get(job.job_id) or job
    progress = min(int(item.get("progress", 0) or 0) for item in by_stem.values())
    presets = next(
        (item.get("presets") for item in by_stem.values() if item.get("presets")), None
    )
    if all(s == "success" for s in statuses):
        result_urls = {}
        for stem, item in by_stem.items():
            for track in _extract_tracks(item.get("result")):
                if track.get("type") == "back":
                    result_urls[f"{stem}_back"] = track["url"]
                elif track.get("label") == stem:
                    result_urls[stem] = track["url"]
                elif track.get("type") == "stem" and stem not in result_urls:
                    result_urls[stem] = track["url"]
        store = _store()
        store.update_status(
            job.job_id,
            status=StemStatus.SUCCEEDED,
            progress=100,
            result_urls=result_urls,
            presets=presets,
        )
    else:
        store = _store()
        store.update_status(
            job.job_id, status=StemStatus.PROCESSING, progress=progress, presets=presets
        )
    return store.get(job.job_id) or job


def download_expired(job: StemJob) -> bool:
    if job.finished_at is None:
        return False
    try:
        finished = datetime.fromisoformat(job.finished_at)
    except ValueError:
        return True
    if finished.tzinfo is None:
        finished = finished.replace(tzinfo=timezone.utc)
    hours = float(os.environ.get("MOODIFY_STEMS_DOWNLOAD_TTL_HOURS", str(DOWNLOAD_TTL_HOURS)))
    return (datetime.now(timezone.utc) - finished).total_seconds() > hours * 3600


def prune(age_days: int = 7) -> int:
    return _store().prune_old_sources(age_days=age_days)


def get_job(job_id: str) -> StemJob | None:
    return _store().get(job_id)
