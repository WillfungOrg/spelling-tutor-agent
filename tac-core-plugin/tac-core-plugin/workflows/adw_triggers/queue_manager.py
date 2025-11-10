"""Queue management system for ADW workflows.

Handles queueing of issues when rate limits are hit and automatic processing
when quota becomes available. Supports up to 15 concurrent workflows.
"""

import sqlite3
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from enum import Enum


class QueueStatus(str, Enum):
    """Status of a queued item."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"


class QueueManager:
    """Manages queued ADW workflow requests."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize queue manager.

        Args:
            db_path: Path to SQLite database. Defaults to ~/.adw/queue.db
        """
        if db_path is None:
            adw_dir = Path.home() / ".adw"
            adw_dir.mkdir(exist_ok=True)
            db_path = str(adw_dir / "queue.db")

        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    issue_number INTEGER NOT NULL,
                    workflow TEXT NOT NULL,
                    label TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT,
                    error_message TEXT,
                    retry_count INTEGER DEFAULT 0,
                    adw_id TEXT
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_status
                ON queue(status)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_issue_number
                ON queue(issue_number)
            """)

    def enqueue(
        self,
        issue_number: int,
        workflow: str,
        label: str
    ) -> int:
        """Add an issue to the queue.

        Args:
            issue_number: GitHub issue number
            workflow: Workflow script name (e.g., "adw_sdlc_iso.py")
            label: Label that triggered workflow (e.g., "auto-sdlc")

        Returns:
            Queue item ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO queue (issue_number, workflow, label, status, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (issue_number, workflow, label, QueueStatus.PENDING, datetime.utcnow().isoformat()))
            return cursor.lastrowid

    def get_pending_items(self, limit: int = 15) -> List[Dict]:
        """Get pending items ready for processing.

        Args:
            limit: Maximum number of items to return (default: 15 for parallel limit)

        Returns:
            List of pending queue items
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM queue
                WHERE status = ?
                ORDER BY created_at ASC
                LIMIT ?
            """, (QueueStatus.PENDING, limit))
            return [dict(row) for row in cursor.fetchall()]

    def mark_processing(self, item_id: int, adw_id: str) -> None:
        """Mark item as processing.

        Args:
            item_id: Queue item ID
            adw_id: ADW ID assigned to this workflow
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE queue
                SET status = ?, started_at = ?, adw_id = ?
                WHERE id = ?
            """, (QueueStatus.PROCESSING, datetime.utcnow().isoformat(), adw_id, item_id))

    def mark_completed(self, item_id: int) -> None:
        """Mark item as completed.

        Args:
            item_id: Queue item ID
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE queue
                SET status = ?, completed_at = ?
                WHERE id = ?
            """, (QueueStatus.COMPLETED, datetime.utcnow().isoformat(), item_id))

    def mark_failed(self, item_id: int, error_message: str) -> None:
        """Mark item as failed.

        Args:
            item_id: Queue item ID
            error_message: Error description
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE queue
                SET status = ?, error_message = ?, completed_at = ?
                WHERE id = ?
            """, (QueueStatus.FAILED, error_message, datetime.utcnow().isoformat(), item_id))

    def mark_rate_limited(self, item_id: int) -> None:
        """Mark item as rate limited and increment retry count.

        Args:
            item_id: Queue item ID
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE queue
                SET status = ?, retry_count = retry_count + 1
                WHERE id = ?
            """, (QueueStatus.RATE_LIMITED, item_id))

    def reset_rate_limited_to_pending(self) -> int:
        """Reset rate limited items back to pending status.

        Called when quota is available again.

        Returns:
            Number of items reset
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                UPDATE queue
                SET status = ?
                WHERE status = ?
            """, (QueueStatus.PENDING, QueueStatus.RATE_LIMITED))
            return cursor.rowcount

    def get_processing_count(self) -> int:
        """Get count of currently processing items.

        Returns:
            Number of items in processing status
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) FROM queue
                WHERE status = ?
            """, (QueueStatus.PROCESSING,))
            return cursor.fetchone()[0]

    def get_queue_stats(self) -> Dict[str, int]:
        """Get queue statistics.

        Returns:
            Dictionary with counts for each status
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT status, COUNT(*) as count
                FROM queue
                GROUP BY status
            """)
            stats = {row[0]: row[1] for row in cursor.fetchall()}
            stats.setdefault("pending", 0)
            stats.setdefault("processing", 0)
            stats.setdefault("rate_limited", 0)
            return stats

    def cleanup_old_items(self, days: int = 7) -> int:
        """Clean up completed/failed items older than specified days.

        Args:
            days: Number of days to keep (default: 7)

        Returns:
            Number of items deleted
        """
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                DELETE FROM queue
                WHERE status IN (?, ?)
                AND completed_at < ?
            """, (QueueStatus.COMPLETED, QueueStatus.FAILED, cutoff))
            return cursor.rowcount

    def get_item_by_issue(self, issue_number: int) -> Optional[Dict]:
        """Get most recent queue item for an issue.

        Args:
            issue_number: GitHub issue number

        Returns:
            Queue item dict or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM queue
                WHERE issue_number = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (issue_number,))
            row = cursor.fetchone()
            return dict(row) if row else None
