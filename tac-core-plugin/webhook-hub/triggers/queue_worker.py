#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic", "requests", "claude-agent-sdk"]
# ///

"""
Queue Worker - Automatically processes queued ADW workflows

Features:
- Monitors queue every 30 seconds
- Processes pending items when capacity available (up to 15 concurrent)
- Automatically retries rate-limited items when quota resets
- Self-healing (continues running despite errors)

Usage: uv run queue_worker.py

Runs indefinitely until stopped with Ctrl+C.
"""

import os
import subprocess
import sys
import time
import logging
from pathlib import Path
from typing import Optional, Tuple
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from queue_manager import QueueManager
from hub_modules.github import make_issue_comment
from hub_modules.utils import make_adw_id, get_safe_subprocess_env

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("queue_worker")

# Initialize queue manager
queue = QueueManager()

# Worker configuration
CHECK_INTERVAL = 30  # Check queue every 30 seconds
MAX_CONCURRENT = 15  # Maximum concurrent workflows


def spawn_workflow(
    issue_number: int,
    workflow: str,
    adw_id: str
) -> Tuple[bool, Optional[str]]:
    """Spawn ADW workflow process.

    Args:
        issue_number: GitHub issue number
        workflow: Workflow script name
        adw_id: ADW ID for this workflow

    Returns:
        Tuple of (success, error_message)
    """
    try:
        script_path = Path(__file__).parent.parent / workflow
        cmd = ["uv", "run", str(script_path), str(issue_number), adw_id]

        logger.info(f"Spawning {workflow} for issue #{issue_number} (ADW: {adw_id})")

        # Spawn in background
        process = subprocess.Popen(
            cmd,
            cwd=script_path.parent.parent,
            env=get_safe_subprocess_env(),
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )

        # Wait briefly to catch immediate failures
        try:
            exit_code = process.wait(timeout=2)
            if exit_code != 0:
                stderr = process.stderr.read().decode() if process.stderr else ""
                return False, f"Workflow failed: {stderr}"
        except subprocess.TimeoutExpired:
            # Still running - expected
            pass

        logger.info(f"Workflow started (PID: {process.pid})")
        return True, None

    except Exception as e:
        logger.error(f"Error spawning workflow: {e}")
        return False, str(e)


def process_queue_batch():
    """Process a batch of queued items if capacity is available."""
    try:
        # Check current processing count
        processing_count = queue.get_processing_count()
        available_slots = MAX_CONCURRENT - processing_count

        if available_slots <= 0:
            logger.debug(f"Queue full ({processing_count}/{MAX_CONCURRENT}), waiting...")
            return

        logger.info(f"Available slots: {available_slots}/{MAX_CONCURRENT}")

        # Get pending items
        pending_items = queue.get_pending_items(limit=available_slots)

        if not pending_items:
            logger.debug("No pending items in queue")
            return

        logger.info(f"Processing {len(pending_items)} queued items")

        for item in pending_items:
            item_id = item["id"]
            issue_number = item["issue_number"]
            workflow = item["workflow"]
            label = item["label"]

            # Generate ADW ID
            adw_id = make_adw_id()

            # Mark as processing
            queue.mark_processing(item_id, adw_id)

            # Spawn workflow
            success, error_msg = spawn_workflow(issue_number, workflow, adw_id)

            if success:
                # Post notification comment
                try:
                    make_issue_comment(
                        str(issue_number),
                        f"🤖 **ADW Workflow Started (from queue)**\n\n"
                        f"Label: `{label}`\n"
                        f"Workflow: `{workflow}`\n"
                        f"ADW ID: `{adw_id}`\n\n"
                        f"Your queued issue is now being processed. "
                        f"You'll receive a notification when the PR is ready for review.\n\n"
                        f"Logs: `agents/{adw_id}/`"
                    )
                except Exception as e:
                    logger.warning(f"Failed to post queue start comment: {e}")

                logger.info(f"Successfully started queued item #{item_id} (issue #{issue_number})")

            else:
                # Check if rate limit error
                if error_msg and ("rate limit" in error_msg.lower() or "quota" in error_msg.lower()):
                    # Mark as rate limited
                    queue.mark_rate_limited(item_id)
                    logger.warning(f"Item #{item_id} hit rate limit, will retry later")

                    # Post rate limit comment if first time
                    if item["retry_count"] == 0:
                        try:
                            make_issue_comment(
                                str(issue_number),
                                f"🤖 **ADW Workflow Delayed (Rate Limit)**\n\n"
                                f"Claude Code rate limit reached while processing your queued issue. "
                                f"Will automatically retry when quota resets (typically within 5 hours).\n\n"
                                f"No action needed - the system will process this automatically."
                            )
                        except Exception as e:
                            logger.warning(f"Failed to post rate limit comment: {e}")
                else:
                    # Other error - mark as failed
                    queue.mark_failed(item_id, error_msg)
                    logger.error(f"Item #{item_id} failed: {error_msg}")

                    # Post error comment
                    try:
                        make_issue_comment(
                            str(issue_number),
                            f"❌ **ADW Workflow Failed (from queue)**\n\n"
                            f"Error: {error_msg}\n\n"
                            f"The queued workflow could not be started. "
                            f"Please check the webhook server logs or try manually.\n\n"
                            f"Logs: `/tmp/webhook_server.log`"
                        )
                    except Exception as e:
                        logger.warning(f"Failed to post error comment: {e}")

    except Exception as e:
        logger.error(f"Error processing queue batch: {e}")


def reset_rate_limited_items():
    """Reset rate-limited items back to pending if quota might be available."""
    try:
        # Check if there are rate-limited items
        stats = queue.get_queue_stats()
        rate_limited_count = stats.get("rate_limited", 0)

        if rate_limited_count > 0:
            # Reset them to pending
            reset_count = queue.reset_rate_limited_to_pending()
            if reset_count > 0:
                logger.info(f"Reset {reset_count} rate-limited items to pending")
    except Exception as e:
        logger.error(f"Error resetting rate-limited items: {e}")


def cleanup_old_items():
    """Clean up old completed/failed items."""
    try:
        deleted_count = queue.cleanup_old_items(days=7)
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old queue items")
    except Exception as e:
        logger.error(f"Error cleaning up old items: {e}")


def main():
    """Main worker loop."""
    logger.info("Queue worker starting...")
    logger.info(f"Check interval: {CHECK_INTERVAL} seconds")
    logger.info(f"Max concurrent: {MAX_CONCURRENT} workflows")

    cycle_count = 0

    try:
        while True:
            cycle_count += 1

            # Process queue batch
            process_queue_batch()

            # Every 10 cycles (~5 minutes), try to reset rate-limited items
            if cycle_count % 10 == 0:
                reset_rate_limited_items()

            # Every 120 cycles (~1 hour), cleanup old items
            if cycle_count % 120 == 0:
                cleanup_old_items()
                cycle_count = 0  # Reset counter

            # Wait before next check
            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        logger.info("Queue worker stopped by user")
    except Exception as e:
        logger.error(f"Queue worker crashed: {e}")
        raise


if __name__ == "__main__":
    main()
