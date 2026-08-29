"""Analyzer service for Moodify QA API.

Background task processing for audio analysis.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import httpx

# Import core modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.analyzer import AudioAnalyzer
from core.scoring import QAScorer
from core.report import QAReport

from api.storage.database import TaskStorage


class AnalyzerService:
    """Service for running audio analysis tasks."""

    def __init__(
        self,
        storage: TaskStorage,
        upload_dir: str = "./uploads",
    ):
        self.storage = storage
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def generate_task_id(self, filename: str) -> str:
        """Generate unique task ID."""
        timestamp = datetime.utcnow().isoformat()
        random_bytes = os.urandom(8).hex()
        hash_input = f"{filename}{timestamp}{random_bytes}"
        return f"qa_{hashlib.sha256(hash_input.encode()).hexdigest()[:12]}"

    def generate_batch_id(self) -> str:
        """Generate unique batch ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        random_bytes = os.urandom(8).hex()
        return f"batch_{timestamp}_{random_bytes}"

    async def process_task(
        self,
        task_id: str,
        file_content: bytes,
        original_filename: str,
        webhook_url: Optional[str] = None,
    ) -> dict[str, Any]:
        """Process a single analysis task."""
        temp_path = None

        try:
            # Update status to processing
            self.storage.update_task_status(task_id, "processing")

            # Save uploaded file to temp location
            file_ext = Path(original_filename).suffix or ".wav"
            temp_path = self.upload_dir / f"{task_id}{file_ext}"
            temp_path.write_bytes(file_content)

            # Run analysis
            analyzer = AudioAnalyzer()
            analysis = analyzer.analyze(temp_path)

            # Calculate scores
            scorer = QAScorer()
            scoring = scorer.score(analysis)

            # Generate report
            report = QAReport.from_scoring_result(scoring, analysis)

            # Prepare results
            results = {
                "task_id": task_id,
                "status": "completed",
                "file": {
                    "name": original_filename,
                    "duration_seconds": analysis.duration_seconds,
                    "sample_rate_hz": analysis.sample_rate,
                    "channels": analysis.channels,
                    "bit_depth": analysis.bit_depth,
                    "size_bytes": analysis.file_size_bytes,
                    "sha256": analysis.sha256,
                },
                "qa_score": scoring.qa_score,
                "technical_score": scoring.technical_score,
                "musical_score": scoring.musical_score,
                "issues": [i.to_dict() for i in scoring.issues],
                "recommendations": [r.to_dict() for r in scoring.recommendations],
                "breakdown": scoring.breakdown.to_dict(),
                "metrics": analysis.raw_metrics,
                "created_at": report.generated_at,
            }

            # Save to database
            self.storage.save_task_results(
                task_id=task_id,
                qa_score=scoring.qa_score,
                technical_score=scoring.technical_score,
                musical_score=scoring.musical_score,
                report={
                    "issues": results["issues"],
                    "recommendations": results["recommendations"],
                    "breakdown": results["breakdown"],
                },
                metrics=analysis.raw_metrics,
                file_info=results["file"],
            )

            # Send webhook if configured
            if webhook_url:
                await self._send_webhook(
                    webhook_url,
                    {
                        "task_id": task_id,
                        "status": "completed",
                        "qa_score": scoring.qa_score,
                        "message": "Analysis completed successfully",
                        "completed_at": datetime.utcnow().isoformat(),
                    }
                )

            return results

        except Exception as e:
            # Update status to failed
            self.storage.update_task_status(task_id, "failed", str(e))

            # Send webhook for failure
            if webhook_url:
                await self._send_webhook(
                    webhook_url,
                    {
                        "task_id": task_id,
                        "status": "failed",
                        "message": str(e),
                        "completed_at": datetime.utcnow().isoformat(),
                    }
                )

            raise

        finally:
            # Cleanup temp file
            if temp_path and temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass

    async def process_batch(
        self,
        batch_id: str,
        files: list[tuple[bytes, str, Optional[str]]],
    ) -> dict[str, Any]:
        """Process a batch of files."""
        # Tasks are already created by the route handler
        # Just process them here

        # Get all task IDs for this batch
        tasks = self.storage.get_batch_tasks(batch_id)
        task_id_map = {t["original_filename"]: t["id"] for t in tasks}

        # Process all files
        results = []
        errors = []

        for file_content, original_filename, webhook_url in files:
            task_id = task_id_map.get(original_filename)
            if not task_id:
                # Generate new task ID if not found
                task_id = self.generate_task_id(original_filename)
                self.storage.create_task(
                    task_id=task_id,
                    filename=f"{task_id}.wav",
                    original_filename=original_filename,
                    file_size=len(file_content),
                    webhook_url=webhook_url,
                    batch_id=batch_id,
                )

            try:
                result = await self.process_task(
                    task_id=task_id,
                    file_content=file_content,
                    original_filename=original_filename,
                    webhook_url=webhook_url,
                )
                results.append(result)
            except Exception as e:
                errors.append({
                    "task_id": task_id,
                    "filename": original_filename,
                    "error": str(e),
                })

        # Update batch status
        self.storage.update_batch_status(batch_id)

        # Get final batch status
        batch = self.storage.get_batch(batch_id)

        return {
            "batch_id": batch_id,
            "status": batch["status"],
            "total": len(files),
            "completed": len(results),
            "failed": len(errors),
            "average_score": batch.get("average_score"),
            "reports": results,
            "errors": errors if errors else None,
        }

    async def _send_webhook(
        self,
        webhook_url: str,
        payload: dict[str, Any],
    ) -> None:
        """Send webhook notification."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                await client.post(
                    webhook_url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": "Moodify-QA/0.2.0",
                    },
                )
        except Exception:
            # Webhook failures should not affect task processing
            pass

    def get_task_status(self, task_id: str) -> Optional[dict[str, Any]]:
        """Get task status and results."""
        task = self.storage.get_task(task_id)
        if task is None:
            return None

        # Parse JSON fields
        result = dict(task)

        if task.get("report_json"):
            try:
                result["report"] = json.loads(task["report_json"])
            except json.JSONDecodeError:
                result["report"] = None

        if task.get("metrics_json"):
            try:
                result["metrics"] = json.loads(task["metrics_json"])
            except json.JSONDecodeError:
                result["metrics"] = None

        return result

    def get_batch_status(self, batch_id: str) -> Optional[dict[str, Any]]:
        """Get batch status and results."""
        batch = self.storage.get_batch(batch_id)
        if batch is None:
            return None

        # Get all tasks in batch
        tasks = self.storage.get_batch_tasks(batch_id)

        # Parse task reports
        reports = []
        for task in tasks:
            if task.get("report_json"):
                try:
                    report = json.loads(task["report_json"])
                    report["task_id"] = task["id"]
                    report["status"] = task["status"]
                    reports.append(report)
                except json.JSONDecodeError:
                    pass

        result = dict(batch)
        result["reports"] = reports

        return result
