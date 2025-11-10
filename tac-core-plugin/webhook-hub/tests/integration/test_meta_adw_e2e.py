"""End-to-end integration tests for Meta-ADW system."""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from meta_strategy import MetaStrategyOrchestrator
from hub_modules.meta_adw_types import TaskAnalysis, StrategyRecommendation
from hub_modules.data_types import GitHubIssue


@pytest.fixture
def temp_repo(tmp_path):
    """Create temporary repository structure."""
    # Create required directories
    tac_dir = tmp_path / ".tac"
    tac_dir.mkdir()
    learning_dir = tac_dir / "learning"
    learning_dir.mkdir()
    (learning_dir / "execution_logs").mkdir()

    # Create template index
    template_index = {
        "v": "1.0",
        "n": 5,
        "t": {
            "feature.md": {"t": 1500, "g": ["feature"], "s": "Plan new features"},
            "bug.md": {"t": 1200, "g": ["bug"], "s": "Fix bugs"},
            "patch.md": {"t": 800, "g": ["patch"], "s": "Quick patches"},
            "chore.md": {"t": 1000, "g": ["chore"], "s": "Maintenance tasks"},
            "test.md": {"t": 900, "g": ["test"], "s": "Testing workflows"},
        },
    }
    with open(tac_dir / "template_index.json", 'w') as f:
        json.dump(template_index, f)

    # Create learning files
    pattern_db = {
        "patterns": [],
        "version": "1.0",
        "last_updated": "2025-11-03T00:00:00Z",
        "total_patterns": 0,
    }
    with open(learning_dir / "pattern_database.json", 'w') as f:
        json.dump(pattern_db, f)

    weights = {
        "version": "1.0",
        "weights": {
            "template_match": 0.4,
            "complexity_match": 0.3,
            "validation_depth": 0.3,
        },
        "thresholds": {
            "use_existing": 0.8,
            "adapt_existing": 0.5,
            "create_custom": 0.0,
        },
        "learning_rate": 0.1,
        "min_executions_for_retraining": 10,
    }
    with open(learning_dir / "decision_weights.json", 'w') as f:
        json.dump(weights, f)

    return tmp_path


@pytest.fixture
def orchestrator(temp_repo):
    """Create MetaStrategyOrchestrator instance."""
    return MetaStrategyOrchestrator(repo_root=temp_repo)


@pytest.fixture
def mock_github_issue():
    """Mock GitHub issue."""
    from hub_modules.data_types import GitHubUser
    return GitHubIssue(
        number=123,
        title="Add user authentication with OAuth",
        body="Implement OAuth 2.0 authentication flow with Google provider",
        state="open",
        url="https://github.com/owner/repo/issues/123",
        author=GitHubUser(login="testuser"),
        labels=[],
        assignees=[],
        comments=[],
        created_at="2025-11-03T00:00:00Z",
        updated_at="2025-11-03T00:00:00Z",
    )


class TestMetaADWEndToEnd:
    """End-to-end integration tests."""

    @patch('meta_strategy.fetch_issue')
    @patch('meta_strategy.get_repo_url')
    @patch('meta_strategy.extract_repo_path')
    def test_fetch_issue(self, mock_extract, mock_get_url, mock_fetch, orchestrator, mock_github_issue):
        """Test fetching GitHub issue."""
        mock_get_url.return_value = "https://github.com/owner/repo"
        mock_extract.return_value = "owner/repo"
        mock_fetch.return_value = mock_github_issue

        issue = orchestrator.fetch_issue(123)

        assert issue.number == 123
        assert issue.title == "Add user authentication with OAuth"
        mock_fetch.assert_called_once_with("123", "owner/repo")

    @patch('meta_strategy.execute_template')
    def test_conduct_interview(self, mock_execute, orchestrator, mock_github_issue):
        """Test conducting user interview."""
        interview_response = json.dumps({
            "task_description": "Add OAuth authentication",
            "task_type": "feature",
            "complexity_level": "complex",
            "user_interaction_layer": "full-stack",
            "testing_requirements": "all",
            "validation_needs": "critical",
            "timeline": "comprehensive",
            "novelty": "novel",
        })
        mock_execute.return_value = interview_response

        interview_data = orchestrator.conduct_interview(mock_github_issue)

        assert interview_data["task_type"] == "feature"
        assert interview_data["complexity_level"] == "complex"
        assert interview_data["validation_needs"] == "critical"

    @patch('meta_strategy.execute_template')
    def test_analyze_task(self, mock_execute, orchestrator):
        """Test task analysis."""
        interview_data = {
            "task_description": "Add OAuth",
            "task_type": "feature",
            "complexity_level": "complex",
            "validation_needs": "critical",
        }

        analysis_response = json.dumps({
            "task_type": "feature",
            "complexity_score": 8.5,
            "complexity_level": "complex",
            "validation_needs": "critical",
            "key_requirements": ["Implement OAuth flow", "Secure endpoints"],
            "estimated_effort_hours": 18.0,
            "risk_factors": ["Security critical"],
            "has_ui_changes": True,
            "requires_e2e_tests": True,
            "external_dependencies": ["OAuth provider"],
            "recommended_model_set": "heavy",
            "analysis_timestamp": "2025-11-03T00:00:00Z",
        })
        mock_execute.return_value = analysis_response

        task_analysis = orchestrator.analyze_task(interview_data)

        assert isinstance(task_analysis, TaskAnalysis)
        assert task_analysis.task_type == "feature"
        assert task_analysis.complexity_score == 8.5
        assert task_analysis.complexity_level == "complex"

    def test_get_recommendation(self, orchestrator):
        """Test getting workflow recommendation."""
        task_analysis = TaskAnalysis(
            task_type="feature",
            complexity_score=8.5,
            complexity_level="complex",
            validation_needs="critical",
            key_requirements=["OAuth flow"],
            estimated_effort_hours=18.0,
            risk_factors=["Security"],
            has_ui_changes=True,
            requires_e2e_tests=True,
            external_dependencies=["OAuth"],
            recommended_model_set="heavy",
        )

        recommendation = orchestrator.get_recommendation(task_analysis)

        assert isinstance(recommendation, StrategyRecommendation)
        assert recommendation.workflow_name in [
            "adw_sdlc_iso",
            "adw_plan_build_test_review_iso",
        ]
        assert 0.0 <= recommendation.confidence_score <= 1.0

    @patch('meta_strategy.execute_template')
    @patch('meta_strategy.fetch_issue')
    @patch('meta_strategy.get_repo_url')
    @patch('meta_strategy.extract_repo_path')
    def test_full_workflow_cancelled(
        self, mock_extract, mock_get_url, mock_fetch, mock_execute, orchestrator, mock_github_issue, monkeypatch
    ):
        """Test full workflow when user cancels."""
        mock_get_url.return_value = "https://github.com/owner/repo"
        mock_extract.return_value = "owner/repo"
        mock_fetch.return_value = mock_github_issue

        # Mock interview
        interview_response = json.dumps({
            "task_description": "Add OAuth",
            "task_type": "feature",
            "complexity_level": "moderate",
            "user_interaction_layer": "backend",
            "testing_requirements": "integration",
            "validation_needs": "thorough",
            "timeline": "normal",
            "novelty": "standard",
        })

        # Mock analysis
        analysis_response = json.dumps({
            "task_type": "feature",
            "complexity_score": 6.0,
            "complexity_level": "moderate",
            "validation_needs": "thorough",
            "key_requirements": ["Add feature"],
            "estimated_effort_hours": 10.0,
            "risk_factors": [],
            "has_ui_changes": False,
            "requires_e2e_tests": False,
            "external_dependencies": [],
            "recommended_model_set": "base",
            "analysis_timestamp": "2025-11-03T00:00:00Z",
        })

        mock_execute.side_effect = [interview_response, analysis_response]

        # Mock user cancelling
        monkeypatch.setattr('builtins.input', lambda _: "0")

        exit_code = orchestrator.run(issue_number=123, model_set="base")

        assert exit_code == 1
        # Check execution log created
        log_files = list((orchestrator.repo_root / ".tac" / "learning" / "execution_logs").glob("*.json"))
        assert len(log_files) > 0

    def test_collect_feedback(self, orchestrator, mock_github_issue):
        """Test collecting execution feedback."""
        from datetime import datetime

        with patch('meta_strategy.fetch_issue') as mock_fetch, \
             patch('meta_strategy.get_repo_url') as mock_get_url, \
             patch('meta_strategy.extract_repo_path') as mock_extract:
            mock_get_url.return_value = "https://github.com/owner/repo"
            mock_extract.return_value = "owner/repo"
            mock_fetch.return_value = mock_github_issue

            start_time = datetime.utcnow()
            feedback = orchestrator.collect_feedback(
                issue_number=123,
                workflow_name="adw_plan_build_test_iso",
                start_time=start_time,
            )

            assert feedback["workflow_name"] == "adw_plan_build_test_iso"
            assert feedback["issue_number"] == 123
            assert "execution_time_minutes" in feedback
            assert feedback["is_false_fix"] == True  # Issue still open

    def test_update_pattern_database(self, orchestrator):
        """Test updating pattern database."""
        task_analysis = TaskAnalysis(
            task_type="feature",
            complexity_score=6.0,
            complexity_level="moderate",
            validation_needs="thorough",
            key_requirements=["Add feature"],
            estimated_effort_hours=10.0,
            risk_factors=[],
            has_ui_changes=True,
            requires_e2e_tests=False,
            external_dependencies=[],
            recommended_model_set="base",
        )

        recommendation = StrategyRecommendation(
            workflow_name="adw_plan_build_test_iso",
            workflow_path="adw/adw_plan_build_test_iso.py",
            template_names=["feature.md"],
            validation_strategy="L5: Closed-loop",
            confidence_score=0.85,
            reasoning="Moderate feature needs plan+build+test",
            alternatives=[],
            estimated_tokens=80000,
            trade_offs=[],
            recommended_phases=["plan", "build", "test"],
        )

        feedback = {
            "execution_time_minutes": 45.0,
            "issue_state": "closed",
            "is_false_fix": False,
        }

        orchestrator.update_pattern_database(
            task_analysis=task_analysis,
            recommendation=recommendation,
            selected_workflow="adw_plan_build_test_iso",
            feedback=feedback,
        )

        # Check pattern database updated
        pattern_db_path = orchestrator.repo_root / ".tac" / "learning" / "pattern_database.json"
        with open(pattern_db_path) as f:
            db = json.load(f)

        assert db["total_patterns"] == 1
        assert len(db["patterns"]) == 1
        pattern = db["patterns"][0]
        assert pattern["task_type"] == "feature"
        assert pattern["selected_workflow"] == "adw_plan_build_test_iso"
        assert pattern["success"] == True

    def test_retrain_weights_insufficient_data(self, orchestrator):
        """Test weight retraining with insufficient data."""
        # With 0 patterns, should skip retraining
        orchestrator.retrain_weights()

        weights_path = orchestrator.repo_root / ".tac" / "learning" / "decision_weights.json"
        with open(weights_path) as f:
            weights = json.load(f)

        # Weights unchanged
        assert weights["weights"]["template_match"] == 0.4
        assert "last_retrained" not in weights

    def test_retrain_weights_with_patterns(self, orchestrator):
        """Test weight retraining with sufficient patterns."""
        # Add 10 patterns with low success rate
        pattern_db_path = orchestrator.repo_root / ".tac" / "learning" / "pattern_database.json"
        patterns = []
        for i in range(10):
            patterns.append({
                "task_type": "feature",
                "complexity_score": 6.0,
                "selected_workflow": "adw_plan_build_test_iso",
                "success": i < 5,  # 50% success rate
            })

        with open(pattern_db_path, 'w') as f:
            json.dump({
                "patterns": patterns,
                "version": "1.0",
                "total_patterns": len(patterns),
                "last_updated": "2025-11-03T00:00:00Z",
            }, f)

        orchestrator.retrain_weights()

        weights_path = orchestrator.repo_root / ".tac" / "learning" / "decision_weights.json"
        with open(weights_path) as f:
            weights = json.load(f)

        # Weights should be adjusted (low success rate < 0.7)
        assert "last_retrained" in weights
        # Template match weight should increase
        assert weights["weights"]["template_match"] > 0.4

    def test_log_execution(self, orchestrator):
        """Test execution logging."""
        task_analysis = TaskAnalysis(
            task_type="bug",
            complexity_score=3.0,
            complexity_level="simple",
            validation_needs="basic",
            key_requirements=["Fix typo"],
            estimated_effort_hours=1.0,
            risk_factors=[],
            has_ui_changes=False,
            requires_e2e_tests=False,
            external_dependencies=[],
            recommended_model_set="base",
        )

        recommendation = StrategyRecommendation(
            workflow_name="adw_patch_iso",
            workflow_path="adw/adw_patch_iso.py",
            template_names=["patch.md"],
            validation_strategy="Basic",
            confidence_score=0.95,
            reasoning="Simple bug fix",
            alternatives=[],
            estimated_tokens=40000,
            trade_offs=[],
            recommended_phases=["patch", "test"],
        )

        log_file = orchestrator.log_execution(
            issue_number=456,
            interview_data={"task_type": "bug"},
            task_analysis=task_analysis,
            recommendation=recommendation,
            selected_workflow="adw_patch_iso",
            outcome="success",
        )

        assert log_file.exists()
        assert "issue-456.json" in str(log_file)

        with open(log_file) as f:
            log_data = json.load(f)

        assert log_data["issue_number"] == 456
        assert log_data["selected_workflow"] == "adw_patch_iso"
        assert log_data["outcome"] == "success"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
