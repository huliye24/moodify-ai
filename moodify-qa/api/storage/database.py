"""Database storage for Moodify QA API.

SQLite/PostgreSQL compatible task storage.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


class TaskStorage:
    """SQLite-based task storage.

    Compatible with PostgreSQL for production deployment.
    """

    _local = threading.local()

    def __init__(self, db_path: str = "./qa_storage.db"):
        self.db_path = Path(db_path)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection."""
        if not hasattr(self._local, "connection"):
            self._local.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0,
            )
            self._local.connection.row_factory = sqlite3.Row
        return self._local.connection

    def _init_db(self) -> None:
        """Initialize database schema."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Analysis tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_tasks (
                id TEXT PRIMARY KEY,
                batch_id TEXT,
                filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_size_bytes INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                webhook_url TEXT,

                -- Timestamps
                created_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,

                -- Results (JSON)
                qa_score REAL,
                technical_score REAL,
                musical_score REAL,
                report_json TEXT,
                metrics_json TEXT,

                -- Error info
                error_message TEXT,

                -- File info
                duration_seconds REAL,
                sample_rate_hz INTEGER,
                channels INTEGER,
                bit_depth INTEGER,
                file_sha256 TEXT
            )
        """)

        # Batch tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batch_tasks (
                id TEXT PRIMARY KEY,
                total INTEGER NOT NULL DEFAULT 0,
                completed INTEGER NOT NULL DEFAULT 0,
                failed INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'pending',
                webhook_url TEXT,
                created_at TEXT NOT NULL,
                completed_at TEXT,
                average_score REAL
            )
        """)

        # Indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_status ON analysis_tasks(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_batch ON analysis_tasks(batch_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_created ON analysis_tasks(created_at)
        """)

        conn.commit()

    def create_task(
        self,
        task_id: str,
        filename: str,
        original_filename: str,
        file_size: int,
        webhook_url: Optional[str] = None,
        batch_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a new analysis task."""
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.utcnow().isoformat()

        cursor.execute("""
            INSERT INTO analysis_tasks (
                id, batch_id, filename, original_filename, file_size_bytes,
                status, webhook_url, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task_id, batch_id, filename, original_filename, file_size,
            "pending", webhook_url, now
        ))

        conn.commit()

        return {
            "task_id": task_id,
            "status": "pending",
            "created_at": now,
        }

    def create_batch(
        self,
        batch_id: str,
        total: int,
        webhook_url: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a new batch task."""
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.utcnow().isoformat()

        cursor.execute("""
            INSERT INTO batch_tasks (
                id, total, status, webhook_url, created_at
            ) VALUES (?, ?, ?, ?, ?)
        """, (batch_id, total, "pending", webhook_url, now))

        conn.commit()

        return {
            "batch_id": batch_id,
            "status": "pending",
            "total": total,
            "created_at": now,
        }

    def get_task(self, task_id: str) -> Optional[dict[str, Any]]:
        """Get task by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM analysis_tasks WHERE id = ?
        """, (task_id,))

        row = cursor.fetchone()
        if row is None:
            return None

        return dict(row)

    def get_batch(self, batch_id: str) -> Optional[dict[str, Any]]:
        """Get batch by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM batch_tasks WHERE id = ?
        """, (batch_id,))

        row = cursor.fetchone()
        if row is None:
            return None

        return dict(row)

    def get_batch_tasks(self, batch_id: str) -> list[dict[str, Any]]:
        """Get all tasks in a batch."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM analysis_tasks WHERE batch_id = ?
        """, (batch_id,))

        return [dict(row) for row in cursor.fetchall()]

    def update_task_status(
        self,
        task_id: str,
        status: str,
        error_message: Optional[str] = None,
    ) -> None:
        """Update task status."""
        conn = self._get_connection()
        cursor = conn.cursor()

        if status == "processing":
            cursor.execute("""
                UPDATE analysis_tasks
                SET status = ?, started_at = ?
                WHERE id = ?
            """, (status, datetime.utcnow().isoformat(), task_id))
        elif status in ("completed", "failed"):
            cursor.execute("""
                UPDATE analysis_tasks
                SET status = ?, completed_at = ?, error_message = ?
                WHERE id = ?
            """, (status, datetime.utcnow().isoformat(), error_message, task_id))
        else:
            cursor.execute("""
                UPDATE analysis_tasks SET status = ? WHERE id = ?
            """, (status, task_id))

        conn.commit()

    def save_task_results(
        self,
        task_id: str,
        qa_score: float,
        technical_score: float,
        musical_score: float,
        report: dict[str, Any],
        metrics: Optional[dict[str, Any]] = None,
        file_info: Optional[dict[str, Any]] = None,
    ) -> None:
        """Save task analysis results."""
        conn = self._get_connection()
        cursor = conn.cursor()

        update_fields = [
            "qa_score = ?",
            "technical_score = ?",
            "musical_score = ?",
            "report_json = ?",
            "status = ?",
            "completed_at = ?",
        ]
        params = [
            qa_score,
            technical_score,
            musical_score,
            json.dumps(report),
            "completed",
            datetime.utcnow().isoformat(),
        ]

        if metrics:
            update_fields.append("metrics_json = ?")
            params.append(json.dumps(metrics))

        if file_info:
            update_fields.append("duration_seconds = ?")
            update_fields.append("sample_rate_hz = ?")
            update_fields.append("channels = ?")
            update_fields.append("bit_depth = ?")
            update_fields.append("file_sha256 = ?")
            params.extend([
                file_info.get("duration_seconds"),
                file_info.get("sample_rate_hz"),
                file_info.get("channels"),
                file_info.get("bit_depth"),
                file_info.get("sha256"),
            ])

        params.append(task_id)

        query = f"""
            UPDATE analysis_tasks
            SET {', '.join(update_fields)}
            WHERE id = ?
        """

        cursor.execute(query, params)
        conn.commit()

    def update_batch_status(self, batch_id: str) -> None:
        """Update batch status based on task statuses."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Get all tasks in batch
        tasks = self.get_batch_tasks(batch_id)

        total = len(tasks)
        completed = sum(1 for t in tasks if t["status"] == "completed")
        failed = sum(1 for t in tasks if t["status"] == "failed")

        # Calculate average score
        scores = [
            t["qa_score"] for t in tasks
            if t["status"] == "completed" and t["qa_score"] is not None
        ]
        avg_score = sum(scores) / len(scores) if scores else None

        # Determine status
        if completed + failed == total:
            status = "completed"
            completed_at = datetime.utcnow().isoformat()
        elif any(t["status"] == "processing" for t in tasks):
            status = "processing"
            completed_at = None
        else:
            status = "pending"
            completed_at = None

        cursor.execute("""
            UPDATE batch_tasks
            SET status = ?, completed = ?, failed = ?, average_score = ?, completed_at = ?
            WHERE id = ?
        """, (status, completed, failed, avg_score, completed_at, batch_id))

        conn.commit()

    def list_tasks(
        self,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """List tasks with optional filtering."""
        conn = self._get_connection()
        cursor = conn.cursor()

        if status:
            cursor.execute("""
                SELECT * FROM analysis_tasks
                WHERE status = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (status, limit, offset))
        else:
            cursor.execute("""
                SELECT * FROM analysis_tasks
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))

        return [dict(row) for row in cursor.fetchall()]

    def delete_old_tasks(self, days: int = 30) -> int:
        """Delete tasks older than specified days."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM analysis_tasks
            WHERE created_at < datetime('now', '-{} days')
        """.format(days))

        deleted = cursor.rowcount
        conn.commit()
        return deleted

    def get_stats(self) -> dict[str, Any]:
        """Get storage statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Task counts by status
        cursor.execute("""
            SELECT status, COUNT(*) FROM analysis_tasks GROUP BY status
        """)
        status_counts = {row[0]: row[1] for row in cursor.fetchall()}

        # Total tasks
        cursor.execute("SELECT COUNT(*) FROM analysis_tasks")
        total = cursor.fetchone()[0]

        # Average scores
        cursor.execute("""
            SELECT AVG(qa_score), AVG(technical_score), AVG(musical_score)
            FROM analysis_tasks
            WHERE status = 'completed' AND qa_score IS NOT NULL
        """)
        row = cursor.fetchone()
        averages = {
            "qa_score": row[0],
            "technical_score": row[1],
            "musical_score": row[2],
        } if row[0] else None

        return {
            "total_tasks": total,
            "status_counts": status_counts,
            "average_scores": averages,
        }
