"""Learning Query Interface - Access learning data during task execution.

This module provides the critical feedback loop that enables actual learning.
It allows the AI agent to query past execution data when making decisions.

Usage:
    from adw_modules.learning_query import LearningDataAccess

    learning = LearningDataAccess(Path("adw/.tac/learning"))

    # Query similar tasks
    similar = learning.query_similar_tasks(
        task_type="feature",
        complexity_score=5.0
    )

    # Get workflow performance
    perf = learning.get_workflow_performance("adw_sdlc_iso")
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from adw_modules.meta_adw_types import LearningRecord, TaskAnalysis, ExecutionMetrics


logger = logging.getLogger(__name__)


class WorkflowPerformance:
    """Performance statistics for a workflow."""

    def __init__(self, workflow_name: str):
        self.workflow_name = workflow_name
        self.success_count = 0
        self.failure_count = 0
        self.total_count = 0
        self.success_rate = 0.0
        self.avg_duration_minutes = 0.0
        self.avg_token_usage = 0.0
        self.common_errors = []
        self.common_failure_phases = []
        self.task_types = defaultdict(int)
        self.complexity_scores = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for easy access."""
        return {
            "workflow_name": self.workflow_name,
            "success_rate": self.success_rate,
            "total_executions": self.total_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "avg_duration_minutes": self.avg_duration_minutes,
            "avg_token_usage": int(self.avg_token_usage) if self.avg_token_usage else None,
            "common_errors": self.common_errors[:5],  # Top 5
            "common_failure_phases": self.common_failure_phases[:3],  # Top 3
            "task_type_distribution": dict(self.task_types),
            "avg_complexity": sum(self.complexity_scores) / len(self.complexity_scores) if self.complexity_scores else None,
        }


class SimilarTask:
    """Similar past task with similarity score."""

    def __init__(self, learning_record: LearningRecord, similarity_score: float):
        self.record = learning_record
        self.similarity_score = similarity_score
        self.adw_id = learning_record.adw_id
        self.task_type = learning_record.task_analysis.task_type
        self.complexity = learning_record.task_analysis.complexity_score
        self.workflow_used = learning_record.selected_strategy
        self.outcome = learning_record.outcome
        self.duration = learning_record.execution_metrics.actual_duration_minutes

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "adw_id": self.adw_id,
            "task_description": self.record.task_description,
            "task_type": self.task_type,
            "complexity_score": self.complexity,
            "workflow_used": self.workflow_used,
            "outcome": self.outcome,
            "duration_minutes": self.duration,
            "similarity_score": round(self.similarity_score, 2),
            "test_success_rate": self.record.execution_metrics.test_success_rate,
            "errors_count": len(self.record.errors_encountered),
        }


class LearningDataAccess:
    """Provide query interface for learning data during execution.

    This is the critical component that closes the feedback loop.
    """

    def __init__(self, learning_dir: Path):
        """Initialize learning data access.

        Args:
            learning_dir: Path to .tac/learning directory
        """
        self.learning_dir = Path(learning_dir)
        self.execution_logs_dir = self.learning_dir / "execution_logs"
        self.pattern_db_file = self.learning_dir / "pattern_database.json"
        self.decision_weights_file = self.learning_dir / "decision_weights.json"

        # Cache
        self._execution_logs_cache: Optional[List[LearningRecord]] = None
        self._cache_loaded_at: Optional[datetime] = None

    def _load_execution_logs(self, force_reload: bool = False) -> List[LearningRecord]:
        """Load all execution logs with caching.

        Args:
            force_reload: Force reload from disk

        Returns:
            List of LearningRecord objects
        """
        # Use cache if fresh (< 5 minutes old)
        if not force_reload and self._execution_logs_cache is not None:
            if self._cache_loaded_at and (datetime.now() - self._cache_loaded_at).seconds < 300:
                return self._execution_logs_cache

        logs = []

        if not self.execution_logs_dir.exists():
            logger.warning(f"Execution logs directory not found: {self.execution_logs_dir}")
            return logs

        for log_file in self.execution_logs_dir.glob("*.json"):
            try:
                with open(log_file) as f:
                    data = json.load(f)

                # Convert to LearningRecord (handles both old and new schema)
                record = LearningRecord(**data)
                logs.append(record)

            except Exception as e:
                logger.warning(f"Could not load learning record {log_file}: {e}")
                continue

        # Update cache
        self._execution_logs_cache = logs
        self._cache_loaded_at = datetime.now()

        logger.info(f"Loaded {len(logs)} learning records from {self.execution_logs_dir}")
        return logs

    def query_similar_tasks(
        self,
        task_type: Optional[str] = None,
        complexity_score: Optional[float] = None,
        complexity_tolerance: float = 2.0,
        has_ui_changes: Optional[bool] = None,
        requires_e2e_tests: Optional[bool] = None,
        limit: int = 10,
        min_similarity: float = 0.3,
    ) -> List[SimilarTask]:
        """Find similar past tasks.

        Args:
            task_type: Filter by task type (feature/bug/chore)
            complexity_score: Target complexity score
            complexity_tolerance: How much complexity can vary (default: ±2.0)
            has_ui_changes: Filter by UI changes
            requires_e2e_tests: Filter by E2E test requirement
            limit: Maximum number of results
            min_similarity: Minimum similarity score (0-1)

        Returns:
            List of SimilarTask objects sorted by similarity
        """
        logs = self._load_execution_logs()

        if not logs:
            logger.info("No execution logs found to query")
            return []

        similar_tasks = []

        for log in logs:
            # Calculate similarity score
            similarity = self._calculate_similarity(
                log.task_analysis,
                task_type=task_type,
                complexity_score=complexity_score,
                complexity_tolerance=complexity_tolerance,
                has_ui_changes=has_ui_changes,
                requires_e2e_tests=requires_e2e_tests,
            )

            if similarity >= min_similarity:
                similar_tasks.append(SimilarTask(log, similarity))

        # Sort by similarity (highest first)
        similar_tasks.sort(key=lambda x: x.similarity_score, reverse=True)

        # Return top N
        results = similar_tasks[:limit]

        logger.info(f"Found {len(results)} similar tasks (from {len(logs)} total, min similarity: {min_similarity})")

        return results

    def _calculate_similarity(
        self,
        task_analysis: TaskAnalysis,
        task_type: Optional[str],
        complexity_score: Optional[float],
        complexity_tolerance: float,
        has_ui_changes: Optional[bool],
        requires_e2e_tests: Optional[bool],
    ) -> float:
        """Calculate similarity score between tasks.

        Args:
            task_analysis: Task analysis from learning record
            task_type: Target task type
            complexity_score: Target complexity
            complexity_tolerance: Complexity tolerance
            has_ui_changes: Target UI changes flag
            requires_e2e_tests: Target E2E tests flag

        Returns:
            Similarity score (0-1, where 1 is perfect match)
        """
        score = 0.0
        weight_sum = 0.0

        # Task type match (weight: 0.4)
        if task_type is not None:
            weight_sum += 0.4
            if task_analysis.task_type == task_type:
                score += 0.4

        # Complexity match (weight: 0.3)
        if complexity_score is not None:
            weight_sum += 0.3
            complexity_diff = abs(task_analysis.complexity_score - complexity_score)
            if complexity_diff <= complexity_tolerance:
                # Linear decay: perfect match = 1.0, at tolerance = 0.0
                complexity_match = 1.0 - (complexity_diff / complexity_tolerance)
                score += 0.3 * complexity_match

        # UI changes match (weight: 0.15)
        if has_ui_changes is not None:
            weight_sum += 0.15
            if task_analysis.has_ui_changes == has_ui_changes:
                score += 0.15

        # E2E tests match (weight: 0.15)
        if requires_e2e_tests is not None:
            weight_sum += 0.15
            if task_analysis.requires_e2e_tests == requires_e2e_tests:
                score += 0.15

        # Normalize by total weight
        if weight_sum > 0:
            return score / weight_sum
        else:
            # No criteria specified, return 0
            return 0.0

    def get_workflow_performance(
        self,
        workflow_name: str,
        task_type: Optional[str] = None,
        min_complexity: Optional[float] = None,
        max_complexity: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Get performance statistics for a workflow.

        Args:
            workflow_name: Name of workflow (e.g., "adw_sdlc_iso")
            task_type: Filter by task type
            min_complexity: Filter by minimum complexity
            max_complexity: Filter by maximum complexity

        Returns:
            Dict with performance metrics:
            {
                "success_rate": float,
                "total_executions": int,
                "avg_duration_minutes": float,
                "common_errors": List[str],
                ...
            }
        """
        logs = self._load_execution_logs()

        # Filter logs for this workflow
        filtered_logs = [
            log for log in logs
            if log.selected_strategy == workflow_name
        ]

        # Apply additional filters
        if task_type:
            filtered_logs = [
                log for log in filtered_logs
                if log.task_analysis.task_type == task_type
            ]

        if min_complexity is not None:
            filtered_logs = [
                log for log in filtered_logs
                if log.task_analysis.complexity_score >= min_complexity
            ]

        if max_complexity is not None:
            filtered_logs = [
                log for log in filtered_logs
                if log.task_analysis.complexity_score <= max_complexity
            ]

        if not filtered_logs:
            logger.info(f"No execution logs found for workflow {workflow_name} with given filters")
            return {
                "workflow_name": workflow_name,
                "success_rate": 0.0,
                "total_executions": 0,
                "message": "No data available"
            }

        # Calculate statistics
        perf = WorkflowPerformance(workflow_name)
        perf.total_count = len(filtered_logs)

        durations = []
        token_usages = []
        error_types = defaultdict(int)
        failure_phases = defaultdict(int)

        for log in filtered_logs:
            # Outcome
            if log.outcome == "success":
                perf.success_count += 1
            elif log.outcome in ["failure", "partial"]:
                perf.failure_count += 1

            # Duration
            if log.execution_metrics.actual_duration_minutes:
                durations.append(log.execution_metrics.actual_duration_minutes)

            # Token usage
            if log.execution_metrics.total_token_usage:
                token_usages.append(log.execution_metrics.total_token_usage)

            # Errors
            for error in log.errors_encountered:
                error_types[error.error_type] += 1
                failure_phases[error.phase] += 1

            # Task characteristics
            perf.task_types[log.task_analysis.task_type] += 1
            perf.complexity_scores.append(log.task_analysis.complexity_score)

        # Calculate averages
        perf.success_rate = perf.success_count / perf.total_count if perf.total_count > 0 else 0.0
        perf.avg_duration_minutes = sum(durations) / len(durations) if durations else 0.0
        perf.avg_token_usage = sum(token_usages) / len(token_usages) if token_usages else 0.0

        # Top errors and phases
        perf.common_errors = [
            error_type for error_type, _ in
            sorted(error_types.items(), key=lambda x: x[1], reverse=True)
        ]
        perf.common_failure_phases = [
            phase for phase, _ in
            sorted(failure_phases.items(), key=lambda x: x[1], reverse=True)
        ]

        result = perf.to_dict()
        logger.info(
            f"Workflow {workflow_name}: {perf.success_rate:.1%} success rate "
            f"({perf.success_count}/{perf.total_count})"
        )

        return result

    def get_common_failure_modes(
        self,
        workflow_name: Optional[str] = None,
        task_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get most common failure modes.

        Args:
            workflow_name: Filter by workflow
            task_type: Filter by task type
            limit: Maximum number of failure modes to return

        Returns:
            List of failure mode dicts with counts and examples
        """
        logs = self._load_execution_logs()

        # Filter logs
        if workflow_name:
            logs = [log for log in logs if log.selected_strategy == workflow_name]

        if task_type:
            logs = [log for log in logs if log.task_analysis.task_type == task_type]

        # Aggregate failure modes
        failure_modes = defaultdict(lambda: {"count": 0, "examples": []})

        for log in logs:
            for error in log.errors_encountered:
                key = f"{error.phase}:{error.error_type}"
                failure_modes[key]["count"] += 1
                if len(failure_modes[key]["examples"]) < 3:  # Keep up to 3 examples
                    failure_modes[key]["examples"].append({
                        "adw_id": log.adw_id,
                        "error_message": error.error_message[:100],  # Truncate
                        "resolution": error.resolution,
                    })

        # Sort by count
        sorted_failures = sorted(
            failure_modes.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )

        # Format results
        results = []
        for (phase_error, data) in sorted_failures[:limit]:
            phase, error_type = phase_error.split(":", 1)
            results.append({
                "phase": phase,
                "error_type": error_type,
                "occurrence_count": data["count"],
                "examples": data["examples"],
            })

        return results

    def get_average_actual_effort(
        self,
        complexity_score: float,
        task_type: Optional[str] = None,
        complexity_tolerance: float = 1.0,
    ) -> Optional[float]:
        """Get average actual effort for tasks with given complexity.

        Args:
            complexity_score: Target complexity score
            task_type: Filter by task type
            complexity_tolerance: How much complexity can vary

        Returns:
            Average duration in minutes, or None if no data
        """
        logs = self._load_execution_logs()

        # Filter by complexity range
        filtered_logs = [
            log for log in logs
            if abs(log.task_analysis.complexity_score - complexity_score) <= complexity_tolerance
            and log.execution_metrics.actual_duration_minutes is not None
        ]

        # Filter by task type if specified
        if task_type:
            filtered_logs = [
                log for log in filtered_logs
                if log.task_analysis.task_type == task_type
            ]

        if not filtered_logs:
            return None

        durations = [log.execution_metrics.actual_duration_minutes for log in filtered_logs]
        avg = sum(durations) / len(durations)

        logger.info(
            f"Average effort for complexity {complexity_score} (±{complexity_tolerance}): "
            f"{avg:.1f} minutes (from {len(durations)} tasks)"
        )

        return avg

    def get_prediction_accuracy(self) -> Dict[str, float]:
        """Calculate how accurate our predictions have been.

        Returns:
            Dict with accuracy metrics
        """
        logs = self._load_execution_logs()

        if not logs:
            return {"message": "No data available"}

        # Duration prediction accuracy
        duration_errors = []
        for log in logs:
            if (
                log.execution_metrics.actual_duration_minutes
                and log.execution_metrics.estimated_duration_minutes
            ):
                actual = log.execution_metrics.actual_duration_minutes
                estimated = log.execution_metrics.estimated_duration_minutes
                error = abs(actual - estimated) / actual if actual > 0 else 0
                duration_errors.append(error)

        # Outcome prediction accuracy
        correct_predictions = 0
        total_predictions = 0
        for log in logs:
            # Skip manual sessions (no recommended_strategy)
            if log.recommended_strategy is None:
                continue

            total_predictions += 1
            # Consider high confidence (>0.8) recommendations
            if log.recommended_strategy.confidence_score > 0.8:
                if log.outcome == "success":
                    correct_predictions += 1

        return {
            "duration_prediction_avg_error": sum(duration_errors) / len(duration_errors) if duration_errors else None,
            "duration_predictions_count": len(duration_errors),
            "outcome_prediction_accuracy": correct_predictions / total_predictions if total_predictions > 0 else 0.0,
            "high_confidence_predictions": total_predictions,
        }

    def get_learning_stats(self) -> Dict[str, Any]:
        """Get overall learning system statistics.

        Returns:
            Dict with learning system stats
        """
        logs = self._load_execution_logs()

        if not logs:
            return {"message": "No learning data available"}

        total_tasks = len(logs)
        successful_tasks = len([log for log in logs if log.outcome == "success"])
        failed_tasks = len([log for log in logs if log.outcome == "failure"])

        # Workflow usage
        workflow_usage = defaultdict(int)
        for log in logs:
            workflow_usage[log.selected_strategy] += 1

        # Task type distribution
        task_type_dist = defaultdict(int)
        for log in logs:
            task_type_dist[log.task_analysis.task_type] += 1

        return {
            "total_learning_records": total_tasks,
            "overall_success_rate": successful_tasks / total_tasks if total_tasks > 0 else 0.0,
            "successful_executions": successful_tasks,
            "failed_executions": failed_tasks,
            "workflow_usage": dict(workflow_usage),
            "task_type_distribution": dict(task_type_dist),
            "learning_data_age_days": (
                (datetime.now() - min(log.execution_timestamp for log in logs)).days
                if logs else 0
            ),
        }
