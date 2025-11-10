"""
Shared learning system integration for ADW workflows.

This module provides a single function that all ADW workflows can call
to trigger learning system feedback collection and improvement.
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional


def trigger_learning_system(
    adw_id: str,
    issue_number: str,
    workflow_name: str,
    start_time: datetime,
    workflow_type: str = "complete",  # "complete", "phase", or "patch"
    phase_timings: dict = None,  # Optional: phase-by-phase timings
    error_records: list = None,  # Optional: detailed error records
):
    """
    Trigger learning system to collect feedback and improve.

    This is called after workflow completion to:
    1. Collect test, review, and deployment feedback
    2. Update pattern database
    3. Sync cross-project learnings
    4. Refine prompts based on outcomes

    Args:
        adw_id: The ADW ID for this execution
        issue_number: GitHub issue number
        workflow_name: Name of the workflow that completed
        start_time: When the workflow started
        workflow_type: Type of workflow - "complete", "phase", or "patch"
    """
    # Check if learning was already collected in this execution chain
    if os.getenv("ADW_LEARNING_COLLECTED") == "true":
        print("\n[Learning] Skipped (already collected by parent workflow)")
        return

    # Check feature flag
    enable_learning = os.getenv("ENABLE_ADW_LEARNING", "true").lower() == "true"
    if not enable_learning:
        print("\n[Learning] Skipped (ENABLE_ADW_LEARNING=false)")
        return

    # Mark that we're collecting learning to prevent duplicates
    os.environ["ADW_LEARNING_COLLECTED"] = "true"

    try:
        print("\n=== LEARNING SYSTEM ===")
        print(f"Collecting feedback for {workflow_name}...")

        # Import learning modules
        from adw_modules.learning_feedback import (
            TestFeedbackCollector,
            ReviewFeedbackCollector,
            DeploymentFeedbackCollector,
        )
        from adw_modules.cross_project_learning import CrossProjectLearningStore
        from adw_modules.prompt_refiner import PromptRefiner
        from adw_modules.meta_adw_types import LearningRecord, TaskAnalysis, StrategyRecommendation

        # Get repo root
        repo_root = Path.cwd()

        # Load ADW state to get workflow details (optional - may not exist yet)
        try:
            from adw_modules.state import ADWState
            state = ADWState.load(adw_id)
        except:
            state = None  # State may not exist during first run

        # Collect feedback from all sources
        test_collector = TestFeedbackCollector(repo_root)
        review_collector = ReviewFeedbackCollector(repo_root)
        deployment_collector = DeploymentFeedbackCollector(repo_root)

        test_feedback = test_collector.collect(adw_id, issue_number)
        review_feedback = review_collector.collect(adw_id, issue_number)
        deployment_feedback = deployment_collector.collect(adw_id, issue_number)

        # Create task analysis based on workflow type
        if workflow_type == "patch":
            task_analysis = TaskAnalysis(
                description=f"Patch for Issue #{issue_number}",
                task_type="patch",
                complexity_level="simple",
                complexity_score=3,
                estimated_effort_hours=1,
                key_requirements=[],
                validation_needs="basic",
                requires_e2e_tests=False,
            )
            validation_strategy = "L3: Basic validation"
            estimated_tokens = 30000
            phases = ["patch", "commit"]
        elif workflow_type == "phase":
            task_analysis = TaskAnalysis(
                description=f"Phase execution for Issue #{issue_number}",
                task_type="feature",
                complexity_level="moderate",
                complexity_score=4,
                estimated_effort_hours=1,
                key_requirements=[],
                validation_needs="thorough",
                requires_e2e_tests=False,
            )
            validation_strategy = "L4: Phase validation"
            estimated_tokens = 40000
            phases = [workflow_name.replace("adw_", "").replace("_iso", "")]
        else:  # complete workflow
            task_analysis = TaskAnalysis(
                description=f"Issue #{issue_number}",
                task_type="feature",
                complexity_level="moderate",
                complexity_score=5,
                estimated_effort_hours=2,
                key_requirements=[],
                validation_needs="thorough",
                requires_e2e_tests=False,
            )
            validation_strategy = "L5: Closed-loop validation"
            estimated_tokens = 50000
            phases = ["plan", "build", "test"]

        # Create recommendation
        recommendation = StrategyRecommendation(
            workflow_name=workflow_name,
            workflow_path=f"adw/{workflow_name}.py",
            template_names=[],
            validation_strategy=validation_strategy,
            confidence_score=0.8,
            reasoning=f"Executed {workflow_name}",
            alternatives=[],
            estimated_tokens=estimated_tokens,
            trade_offs=[],
            recommended_phases=phases,
        )

        # Determine outcome
        outcome = "success"
        if test_feedback and test_feedback.get("success_rate", 1.0) < 1.0:
            outcome = "partial"
        if review_feedback and review_feedback.get("human_commits_after_ai"):
            outcome = "partial"

        # Detect false fixes
        false_fix = False
        if test_feedback and test_feedback.get("success_rate", 1.0) < 0.7:
            false_fix = True

        # Calculate execution duration
        end_time = datetime.utcnow()
        actual_duration = (end_time - start_time).total_seconds() / 60.0  # minutes

        # Import ExecutionMetrics and ErrorRecord
        from adw_modules.meta_adw_types import ExecutionMetrics, ErrorRecord

        # Create execution metrics
        execution_metrics = ExecutionMetrics(
            actual_duration_minutes=actual_duration,
            estimated_duration_minutes=task_analysis.estimated_effort_hours * 60 if task_analysis.estimated_effort_hours else None,
            duration_accuracy_ratio=None,  # Will be calculated if both exist
            phase_timings=phase_timings or {},
            retry_count=0,  # TODO: Track retries
            error_count=len(error_records) if error_records else 0,
            tests_passed=test_feedback.get("passed") if test_feedback else None,
            tests_failed=test_feedback.get("failed") if test_feedback else None,
            test_success_rate=test_feedback.get("success_rate") if test_feedback else None,
            review_approved=review_feedback.get("review_status") == "approved" if review_feedback else None,
            deployed_successfully=deployment_feedback.get("deployed") if deployment_feedback else None,
        )

        # Calculate duration accuracy if we have both values
        if execution_metrics.actual_duration_minutes and execution_metrics.estimated_duration_minutes:
            execution_metrics.duration_accuracy_ratio = (
                execution_metrics.actual_duration_minutes / execution_metrics.estimated_duration_minutes
            )

        # Convert error records if provided
        errors_encountered = []
        if error_records:
            for err in error_records:
                if isinstance(err, ErrorRecord):
                    errors_encountered.append(err)
                elif isinstance(err, dict):
                    errors_encountered.append(ErrorRecord(**err))

        # Create learning record with new structure
        record = LearningRecord(
            task_description=f"Issue #{issue_number}",
            task_analysis=task_analysis,
            recommended_strategy=recommendation,
            selected_strategy=workflow_name,
            user_overrode_recommendation=False,
            outcome=outcome,
            execution_metrics=execution_metrics,
            # Keep legacy for backward compatibility
            success_metrics={
                "test_success_rate": test_feedback.get("success_rate") if test_feedback else None,
                "review_approved": review_feedback.get("review_status") == "approved" if review_feedback else None,
                "deployed_successfully": deployment_feedback.get("deployed") if deployment_feedback else None,
            },
            errors_encountered=errors_encountered,
            problems_encountered=[],  # Deprecated, use errors_encountered
            false_fix_detected=false_fix,
            user_satisfaction=None,
            execution_timestamp=end_time,
            execution_start_time=start_time,
            execution_end_time=end_time,
            adw_id=adw_id,
            issue_number=issue_number,
        )

        # Store learning record
        test_collector.store_learning_record(record)
        print(f"✓ Learning record stored: {adw_id}")

        # Sync cross-project learning
        global_learning_dir = Path.home() / "agentic-coding-library" / ".tac" / "learning" / "global"
        local_learning_dir = repo_root / ".tac" / "learning"

        if global_learning_dir.exists():
            store = CrossProjectLearningStore(global_learning_dir)
            project_name = repo_root.name
            store.aggregate_from_project(project_name, local_learning_dir)
            store.sync_to_project(local_learning_dir)
            print(f"✓ Cross-project learning synced")

        # Refine prompts if there were issues
        if outcome == "partial" or false_fix:
            refiner = PromptRefiner(repo_root)
            feedback_data = {
                "test_failures": test_feedback.get("failure_patterns", []) if test_feedback else [],
                "review_changes": review_feedback.get("change_categories", []) if review_feedback else [],
                "deployment_errors": deployment_feedback.get("failed", False) if deployment_feedback else False,
                "success_rate": test_feedback.get("success_rate", 1.0) if test_feedback else 1.0,
            }

            # Refine relevant prompts based on workflow
            prompt_ids = ["feature_planning", "implementation", "testing"]
            for prompt_id in prompt_ids:
                prompt_file = repo_root / ".claude" / "commands" / f"{prompt_id}.md"
                if prompt_file.exists():
                    current_prompt = prompt_file.read_text()
                    refined = refiner.refine_prompt(prompt_id, current_prompt, feedback_data, max_iterations=2)
                    print(f"✓ Refined prompt: {prompt_id}")

        print(f"✓ Learning completed for {workflow_name}")

    except Exception as e:
        print(f"\n[Learning] Warning: Failed to collect feedback: {e}")
        print("[Learning] This is non-critical, workflow completed successfully.")
    finally:
        # Clear the flag for next execution
        if "ADW_LEARNING_COLLECTED" in os.environ:
            del os.environ["ADW_LEARNING_COLLECTED"]
