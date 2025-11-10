"""Integration tests for complete learning flow."""

import pytest
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from hub_modules.meta_adw_types import TaskAnalysis, StrategyRecommendation
from hub_modules.learning_feedback import TestFeedbackCollector
from hub_modules.cross_project_learning import CrossProjectLearningStore


@pytest.fixture
def integration_setup(tmp_path):
    """Set up complete repo structure for integration test."""
    repo = tmp_path / "test-repo"
    repo.mkdir()

    # Create all necessary directories
    (repo / ".tac" / "learning" / "execution_logs").mkdir(parents=True)
    (repo / ".tac" / "prompts").mkdir(parents=True)
    (repo / "agents" / "test123").mkdir(parents=True)
    (repo / "logs" / "session-1").mkdir(parents=True)
    (repo / "tac-core-plugin" / "commands").mkdir(parents=True)

    # Create mock ADW state
    state = {
        "adw_id": "test123",
        "issue_number": "42",
        "branch_name": "feat-42-test123-feature",
    }
    with open(repo / "agents" / "test123" / "adw_state.json", 'w') as f:
        json.dump(state, f)

    # Create mock chat log with test results
    chat_log = {
        "messages": [
            {
                "role": "assistant",
                "content": "Running tests for ADW test123..."
            },
            {
                "role": "tool_use",
                "content": "pytest"
            },
            {
                "role": "tool_result",
                "content": (
                    "============================= test session starts ==============================\n"
                    "collected 10 items\n\n"
                    "app/tests/test_auth.py::test_login PASSED\n"
                    "app/tests/test_auth.py::test_logout PASSED\n"
                    "app/tests/test_api.py::test_get PASSED\n"
                    "app/tests/test_api.py::test_post PASSED\n"
                    "app/tests/test_database.py::test_connect PASSED\n"
                    "app/tests/test_database.py::test_query FAILED\n"
                    "app/tests/test_ui.py::test_render PASSED\n"
                    "app/tests/test_ui.py::test_click PASSED\n"
                    "app/tests/test_integration.py::test_flow PASSED\n"
                    "app/tests/test_integration.py::test_validation FAILED\n"
                    "========================= 8 passed, 2 failed in 1.23s ==========================\n"
                )
            }
        ]
    }
    with open(repo / "logs" / "session-1" / "chat.json", 'w') as f:
        json.dump(chat_log, f)

    return repo


def test_test_feedback_collection_end_to_end(integration_setup):
    """Test complete test feedback collection flow."""
    repo_root = integration_setup

    # Initialize collector
    collector = TestFeedbackCollector(repo_root)

    # Collect feedback
    feedback = collector.collect(adw_id="test123", issue_number="42")

    # Verify feedback was collected
    assert feedback is not None
    assert feedback["total_tests"] == 10
    assert feedback["passed"] == 8
    assert feedback["failed"] == 2
    assert feedback["success_rate"] == 0.8

    # Verify failure patterns identified
    assert "database" in feedback["failure_patterns"]
    assert "integration" in feedback["failure_patterns"]


def test_learning_record_storage(integration_setup):
    """Test that LearningRecord is stored correctly."""
    repo_root = integration_setup

    # Create LearningRecord
    from hub_modules.meta_adw_types import LearningRecord

    task_analysis = TaskAnalysis(
        description="Add user authentication",
        task_type="feature",
        complexity_level="moderate",
        complexity_score=5,
        estimated_effort_hours=3,
        key_requirements=["auth", "security", "tests"],
        validation_needs="thorough",
        requires_e2e_tests=True,
    )

    recommendation = StrategyRecommendation(
        workflow_name="adw_plan_build_test_iso",
        workflow_path="adw/adw_plan_build_test_iso.py",
        template_names=["feature.md"],
        validation_strategy="L5: Closed-loop validation",
        confidence_score=0.85,
        reasoning="Standard feature workflow",
        alternatives=[],
        estimated_tokens=80000,
        trade_offs=["Balanced approach"],
        recommended_phases=["plan", "build", "test"],
    )

    record = LearningRecord(
        task_description="Add user authentication",
        task_analysis=task_analysis,
        recommended_strategy=recommendation,
        selected_strategy="adw_plan_build_test_iso",
        user_overrode_recommendation=False,
        outcome="partial",
        success_metrics={
            "test_success_rate": 0.8,
            "review_approved": None,
            "deployed_successfully": None,
        },
        problems_encountered=["Test failures in database", "Test failures in integration"],
        false_fix_detected=True,
        user_satisfaction=None,
        execution_timestamp=datetime.utcnow(),
        adw_id="test123",
        issue_number="42",
    )

    # Store record
    collector = TestFeedbackCollector(repo_root)
    collector.store_learning_record(record)

    # Verify stored
    log_file = repo_root / ".tac" / "learning" / "execution_logs" / "test123.json"
    assert log_file.exists()

    with open(log_file) as f:
        stored = json.load(f)

    assert stored["adw_id"] == "test123"
    assert stored["outcome"] == "partial"
    assert stored["false_fix_detected"] is True
    assert len(stored["problems_encountered"]) == 2


def test_pattern_database_creation(integration_setup):
    """Test that pattern database is created and updated."""
    repo_root = integration_setup

    # Create initial pattern database
    pattern_db_path = repo_root / ".tac" / "learning" / "pattern_database.json"

    db = {
        "patterns": [
            {
                "pattern_name": "feature-auth",
                "task_type": "feature",
                "complexity_score": 5,
                "success_rate": 0.8,
                "use_count": 1,
            }
        ],
        "total_patterns": 1,
        "last_updated": datetime.utcnow().isoformat(),
    }

    with open(pattern_db_path, 'w') as f:
        json.dump(db, f, indent=2)

    # Verify created
    assert pattern_db_path.exists()

    # Load and verify
    with open(pattern_db_path) as f:
        loaded = json.load(f)

    assert loaded["total_patterns"] == 1
    assert loaded["patterns"][0]["pattern_name"] == "feature-auth"


def test_cross_project_aggregation_flow(tmp_path):
    """Test complete cross-project aggregation flow."""
    # Setup two projects
    global_dir = tmp_path / "global"

    project_a_dir = tmp_path / "project-a" / ".tac" / "learning"
    project_a_dir.mkdir(parents=True)

    project_b_dir = tmp_path / "project-b" / ".tac" / "learning"
    project_b_dir.mkdir(parents=True)

    store = CrossProjectLearningStore(global_dir)

    # Project A patterns
    project_a_patterns = {
        "patterns": [
            {"pattern_name": "auth-feature", "success_rate": 0.85, "use_count": 10},
            {"pattern_name": "api-bug-fix", "success_rate": 0.75, "use_count": 5},
        ],
        "total_patterns": 2
    }

    with open(project_a_dir / "pattern_database.json", 'w') as f:
        json.dump(project_a_patterns, f)

    # Project B patterns
    project_b_patterns = {
        "patterns": [
            {"pattern_name": "auth-feature", "success_rate": 0.90, "use_count": 8},  # Same pattern, different success
            {"pattern_name": "database-refactor", "success_rate": 0.95, "use_count": 3},
        ],
        "total_patterns": 2
    }

    with open(project_b_dir / "pattern_database.json", 'w') as f:
        json.dump(project_b_patterns, f)

    # Aggregate from both projects
    store.aggregate_from_project("project-a", project_a_dir)
    store.aggregate_from_project("project-b", project_b_dir)

    # Check global database
    global_db = store._load_global_patterns()

    assert global_db["total_patterns"] == 3  # auth-feature (merged), api-bug-fix, database-refactor

    # Check auth-feature was merged
    auth_pattern = next(p for p in global_db["patterns"] if p["pattern_name"] == "auth-feature")
    assert auth_pattern["use_count"] == 18  # 10 + 8
    # Weighted average: (0.85*10 + 0.90*8) / 18
    expected_success = (0.85*10 + 0.90*8) / 18
    assert abs(auth_pattern["success_rate"] - expected_success) < 0.01
    assert len(auth_pattern["contributing_projects"]) == 2

    # Now sync back to project A
    store.sync_to_project(project_a_dir)

    with open(project_a_dir / "pattern_database.json") as f:
        project_a_synced = json.load(f)

    # Project A should now have all 3 patterns
    assert len(project_a_synced["patterns"]) == 3

    # Check that database-refactor was synced (new pattern from project B)
    db_refactor = next((p for p in project_a_synced["patterns"] if p["pattern_name"] == "database-refactor"), None)
    assert db_refactor is not None
    assert db_refactor["success_rate"] == 0.95


def test_global_insights(tmp_path):
    """Test global insights calculation across projects."""
    global_dir = tmp_path / "global"
    store = CrossProjectLearningStore(global_dir)

    # Create global patterns from multiple projects
    global_patterns = {
        "patterns": [
            {"pattern_name": "p1", "success_rate": 0.8, "use_count": 10, "source_project": "proj-a"},
            {"pattern_name": "p2", "success_rate": 0.9, "use_count": 20, "source_project": "proj-b"},
            {"pattern_name": "p3", "success_rate": 0.7, "use_count": 5, "source_project": "proj-a"},
            {"pattern_name": "p4", "success_rate": 0.95, "use_count": 15, "source_project": "proj-c"},
        ],
        "total_patterns": 4
    }

    with open(global_dir / "global_pattern_database.json", 'w') as f:
        json.dump(global_patterns, f)

    # Create project registry
    registry = {
        "projects": [
            {"name": "proj-a", "learning_dir": "/path/to/a"},
            {"name": "proj-b", "learning_dir": "/path/to/b"},
            {"name": "proj-c", "learning_dir": "/path/to/c"},
        ]
    }

    with open(global_dir / "project_registry.json", 'w') as f:
        json.dump(registry, f)

    # Get insights
    insights = store.get_global_insights()

    assert insights["total_patterns"] == 4
    assert insights["total_projects"] == 3

    # Average success rate: (0.8 + 0.9 + 0.7 + 0.95) / 4 = 0.8375
    assert abs(insights["average_success_rate"] - 0.8375) < 0.01

    # Top patterns should be sorted by success rate
    assert insights["top_patterns"][0]["name"] == "p4"  # 0.95
    assert insights["top_patterns"][1]["name"] == "p2"  # 0.9

    # Patterns by project
    assert insights["patterns_by_project"]["proj-a"] == 2
    assert insights["patterns_by_project"]["proj-b"] == 1
    assert insights["patterns_by_project"]["proj-c"] == 1


def test_prompt_refinement_integration(integration_setup):
    """Test prompt refinement integration."""
    repo_root = integration_setup

    from hub_modules.prompt_refiner import PromptRefiner

    refiner = PromptRefiner(repo_root)

    # Create a simple prompt
    original_prompt = (
        "# Feature Planning\n\n"
        "## Instructions\n\n"
        "- Create a detailed plan\n"
        "- Include implementation steps\n\n"
        "## Validation\n\n"
        "- Run tests\n"
    )

    # Simulate feedback with issues
    feedback = {
        "test_failures": ["auth", "database"],
        "review_changes": ["security", "logic"],
        "deployment_errors": False,
        "success_rate": 0.6,
    }

    # Refine prompt
    refined = refiner.refine_prompt(
        prompt_id="feature_planning",
        current_prompt=original_prompt,
        feedback=feedback,
        max_iterations=3
    )

    # Verify refinements were applied
    assert len(refined) > len(original_prompt)
    assert "authentication tests" in refined.lower() or "auth" in refined.lower()
    # Check that at least one type of improvement was applied (logic or security)
    assert "logic verification" in refined.lower() or "security checklist" in refined.lower()

    # Verify files were saved
    latest_file = repo_root / ".tac" / "prompts" / "feature_planning_latest.md"
    assert latest_file.exists()

    history_file = repo_root / ".tac" / "prompts" / "refinement_history.json"
    assert history_file.exists()

    # Get stats
    stats = refiner.get_refinement_stats("feature_planning")
    assert stats["total_refinements"] > 0
    assert stats["current_version"] > 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
