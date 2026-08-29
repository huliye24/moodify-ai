"""QA API routes for Moodify QA.

Main API endpoints for audio quality analysis.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.schemas.report import (
    BatchReportResponse,
    BatchTaskResponse,
    ErrorResponse,
    HealthResponse,
    QAReportResponse,
    TaskResponse,
    TaskStatus,
    VersionResponse,
)
from api.services.analyzer_service import AnalyzerService
from api.storage.database import TaskStorage

# Initialize router
router = APIRouter(prefix="/qa", tags=["QA Analysis"])

# Initialize services
storage = TaskStorage()
analyzer_service = AnalyzerService(storage)


@router.post(
    "/analyze",
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
        413: {"model": ErrorResponse, "description": "File too large"},
    },
)
async def analyze_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Audio file to analyze"),
    webhook_url: Optional[str] = Form(None, description="Optional webhook URL"),
) -> TaskResponse:
    """
    Upload and analyze an audio file.

    - **file**: Audio file (WAV, MP3, FLAC, AIFF, OGG, M4A)
    - **webhook_url**: Optional URL to receive completion notification

    Returns a task ID for tracking the analysis progress.
    """
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )

    # Check file size (100MB limit)
    max_size = 100 * 1024 * 1024  # 100MB
    content = await file.read()
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {max_size / (1024*1024):.0f}MB"
        )

    # Generate task ID
    task_id = analyzer_service.generate_task_id(file.filename)

    # Create task record
    storage.create_task(
        task_id=task_id,
        filename=f"{task_id}.wav",
        original_filename=file.filename,
        file_size=len(content),
        webhook_url=webhook_url,
    )

    # Queue background task
    background_tasks.add_task(
        analyzer_service.process_task,
        task_id=task_id,
        file_content=content,
        original_filename=file.filename,
        webhook_url=webhook_url,
    )

    # Estimate processing time (~1 second per MB)
    estimated_seconds = max(5, len(content) // (1024 * 1024))

    return TaskResponse(
        task_id=task_id,
        status=TaskStatus.PROCESSING,
        created_at=datetime.utcnow(),
        estimated_seconds=estimated_seconds,
        message="Analysis started. Use GET /qa/report/{task_id} to check status.",
    )


@router.get(
    "/report/{task_id}",
    response_model=QAReportResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Task not found"},
        422: {"model": ErrorResponse, "description": "Task not completed"},
    },
)
async def get_report(task_id: str) -> QAReportResponse:
    """
    Get QA report by task ID.

    - **task_id**: Task identifier from /qa/analyze

    Returns the complete QA report including scores, issues, and recommendations.
    """
    task = analyzer_service.get_task_status(task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    # Map database status to API status
    status_map = {
        "pending": TaskStatus.PENDING,
        "processing": TaskStatus.PROCESSING,
        "completed": TaskStatus.COMPLETED,
        "failed": TaskStatus.FAILED,
    }
    task_status = status_map.get(task["status"], TaskStatus.PENDING)

    # If task is not completed, return minimal info
    if task["status"] != "completed":
        return QAReportResponse(
            task_id=task_id,
            status=task_status,
            file={
                "name": task.get("original_filename", "unknown"),
                "duration_seconds": 0.0,
                "sample_rate_hz": 0,
                "channels": 0,
                "size_bytes": task.get("file_size_bytes", 0),
                "sha256": "",
            },
            qa_score=0.0,
            technical_score=0.0,
            musical_score=0.0,
            issues=[],
            recommendations=[],
            breakdown={"technical": {}, "musical": {}},
            created_at=datetime.fromisoformat(task["created_at"]),
        )

    # Build full response
    report = task.get("report", {})
    file_info = {
        "name": task.get("original_filename", "unknown"),
        "duration_seconds": task.get("duration_seconds", 0.0) or 0.0,
        "sample_rate_hz": task.get("sample_rate_hz", 0) or 0,
        "channels": task.get("channels", 0) or 0,
        "bit_depth": task.get("bit_depth"),
        "size_bytes": task.get("file_size_bytes", 0) or 0,
        "sha256": task.get("file_sha256", "") or "",
    }

    return QAReportResponse(
        task_id=task_id,
        status=task_status,
        file=file_info,
        qa_score=task.get("qa_score", 0.0) or 0.0,
        technical_score=task.get("technical_score", 0.0) or 0.0,
        musical_score=task.get("musical_score", 0.0) or 0.0,
        issues=report.get("issues", []),
        recommendations=report.get("recommendations", []),
        breakdown=report.get("breakdown", {"technical": {}, "musical": {}}),
        metrics=task.get("metrics"),
        created_at=datetime.fromisoformat(task["created_at"]),
        completed_at=datetime.fromisoformat(task["completed_at"]) if task.get("completed_at") else None,
    )


@router.post(
    "/batch",
    response_model=BatchTaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
        413: {"model": ErrorResponse, "description": "Files too large"},
    },
)
async def analyze_batch(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(..., description="Audio files to analyze"),
    webhook_url: Optional[str] = Form(None, description="Optional webhook URL"),
) -> BatchTaskResponse:
    """
    Analyze multiple audio files in batch.

    - **files**: List of audio files
    - **webhook_url**: Optional URL to receive completion notification

    Returns a batch ID for tracking the analysis progress.
    """
    # Validate files
    if not files or len(files) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided"
        )

    if len(files) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 50 files per batch"
        )

    # Generate batch ID
    batch_id = analyzer_service.generate_batch_id()

    # Process files
    file_data = []
    task_ids = []

    for file in files:
        if not file.filename:
            continue

        content = await file.read()

        # Check file size (100MB limit per file)
        max_size = 100 * 1024 * 1024
        if len(content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File {file.filename} too large. Maximum size: {max_size / (1024*1024):.0f}MB"
            )

        task_id = analyzer_service.generate_task_id(file.filename)
        task_ids.append(task_id)

        # Create task record
        storage.create_task(
            task_id=task_id,
            filename=f"{task_id}.wav",
            original_filename=file.filename,
            file_size=len(content),
            webhook_url=webhook_url,
            batch_id=batch_id,
        )

        file_data.append((content, file.filename, webhook_url))

    # Create batch record
    storage.create_batch(
        batch_id=batch_id,
        total=len(file_data),
        webhook_url=webhook_url,
    )

    # Queue background task
    background_tasks.add_task(
        analyzer_service.process_batch,
        batch_id=batch_id,
        files=file_data,
    )

    # Estimate processing time
    total_size = sum(len(fd[0]) for fd in file_data)
    estimated_seconds = max(10, total_size // (512 * 1024))  # ~2 seconds per MB

    return BatchTaskResponse(
        batch_id=batch_id,
        task_ids=task_ids,
        total=len(file_data),
        status=TaskStatus.PROCESSING,
        created_at=datetime.utcnow(),
        estimated_seconds=estimated_seconds,
    )


@router.get(
    "/batch/{batch_id}",
    response_model=BatchReportResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Batch not found"},
    },
)
async def get_batch_report(batch_id: str) -> BatchReportResponse:
    """
    Get batch analysis report by batch ID.

    - **batch_id**: Batch identifier from /qa/batch

    Returns the complete batch report including all individual reports.
    """
    batch = analyzer_service.get_batch_status(batch_id)

    if batch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch {batch_id} not found"
        )

    # Map database status to API status
    status_map = {
        "pending": TaskStatus.PENDING,
        "processing": TaskStatus.PROCESSING,
        "completed": TaskStatus.COMPLETED,
        "failed": TaskStatus.FAILED,
    }
    batch_status = status_map.get(batch["status"], TaskStatus.PENDING)

    # Build reports list
    reports = []
    for report_data in batch.get("reports", []):
        if report_data and "file" in report_data:
            reports.append(QAReportResponse(
                task_id=report_data.get("task_id", ""),
                status=TaskStatus.COMPLETED,
                file=report_data.get("file", {}),
                qa_score=report_data.get("qa_score", 0.0),
                technical_score=report_data.get("technical_score", 0.0),
                musical_score=report_data.get("musical_score", 0.0),
                issues=report_data.get("issues", []),
                recommendations=report_data.get("recommendations", []),
                breakdown=report_data.get("breakdown", {"technical": {}, "musical": {}}),
                created_at=datetime.utcnow(),
            ))

    return BatchReportResponse(
        batch_id=batch_id,
        status=batch_status,
        total=batch.get("total", 0),
        completed=batch.get("completed", 0),
        failed=batch.get("failed", 0),
        average_score=batch.get("average_score"),
        reports=reports,
        created_at=datetime.fromisoformat(batch["created_at"]),
        completed_at=datetime.fromisoformat(batch["completed_at"]) if batch.get("completed_at") else None,
    )


@router.get("/tasks", response_model=list[TaskResponse])
async def list_tasks(
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> list[TaskResponse]:
    """
    List analysis tasks.

    - **status**: Filter by status (pending, processing, completed, failed)
    - **limit**: Maximum number of results (default: 100)
    - **offset**: Pagination offset (default: 0)
    """
    tasks = storage.list_tasks(status=status, limit=limit, offset=offset)

    status_map = {
        "pending": TaskStatus.PENDING,
        "processing": TaskStatus.PROCESSING,
        "completed": TaskStatus.COMPLETED,
        "failed": TaskStatus.FAILED,
    }

    return [
        TaskResponse(
            task_id=task["id"],
            status=status_map.get(task["status"], TaskStatus.PENDING),
            created_at=datetime.fromisoformat(task["created_at"]),
            estimated_seconds=30,
        )
        for task in tasks
    ]
