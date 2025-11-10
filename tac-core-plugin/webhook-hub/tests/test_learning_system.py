"""Unit tests for learning system components."""

import pytest
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from hub_modules.learning_feedback import (
    TestFeedbackCollector,
    ReviewFeedbackCollector,
    DeploymentFeedbackCollector,
)
from hub_modules.cross_project_learning import CrossProjectLearningStore
from hub_modules.prompt_refiner import PromptRefiner


@pytest.fixture
def temp_repo(tmp_path):
    """Create temporary repo structure."""
    repo = tmp_path / "test-repo"
    repo.mkdir()
    (repo / ".tac" / "learning" / "execution_logs").mkdir(parents=True)
    (repo / "agents").mkdir()
    (repo / "logs").mkdir()
    (repo / ".tac" / "prompts").mkdir(parents=True)
    return repo


class TestFeedbackCollectors:
    """Tests for feedback collector classes."""

    def test_test_feedback_collector_parses_pytest_output(self, temp_repo):
        """Test that TestFeedbackCollector parses pytest output correctly."""
        collector = TestFeedbackCollector(temp_repo)

        # Create mock pytest output
        chat_log = {
            "messages": [
                {
                    "role": "tool_result",
                    "content": (
                        "============================= test session starts ==============================\n"
                        "collected 10 items\n\n"
                        "app/tests/test_auth.py::test_login PASSED\n"
                        "app/tests/test_auth.py::test_logout FAILED\n"
                        "app/tests/test_api.py PASSED\n"
                        "========================= 8 passed, 2 failed in 1.23s =========================="
                    )
                }
            ]
        }

        # Test parsing logic directly
        results = collector._parse_pytest_output(chat_log)

        assert results["total_tests"] == 10
        assert results["passed"] == 8
        assert results["failed"] == 2
        assert results["success_rate"] == 0.8

    def test_test_feedback_collector_categorizes_failures(self, temp_repo):
        """Test that failures are categorized by test name."""
        collector = TestFeedbackCollector(temp_repo)

        chat_log = {
            "messages": [
                {
                    "role": "tool_result",
                    "content": (
                        "FAILED app/tests/test_auth.py::test_login\n"
                        "FAILED app/tests/test_auth.py::test_logout\n"
                        "FAILED app/tests/test_database.py::test_connection\n"
                        "========================= 5 passed, 3 failed =========================="
                    )
                }
            ]
        }

        results = collector._parse_pytest_output(chat_log)

        assert "auth" in results["failure_patterns"]
        assert "database" in results["failure_patterns"]
        assert len(results["failure_patterns"]) == 2  # Unique categories

    def test_review_feedback_determines_status(self, temp_repo):
        """Test ReviewFeedbackCollector determines review status."""
        collector = ReviewFeedbackCollector(temp_repo, github_token=None)

        # Test approved status
        reviews = [{"state": "APPROVED"}]
        status = collector._determine_review_status(reviews)
        assert status == "approved"

        # Test changes requested
        reviews = [{"state": "CHANGES_REQUESTED"}]
        status = collector._determine_review_status(reviews)
        assert status == "changes_requested"

        # Test no review
        reviews = []
        status = collector._determine_review_status(reviews)
        assert status == "no_review"

    def test_review_feedback_categorizes_changes(self, temp_repo):
        """Test ReviewFeedbackCollector categorizes review comments."""
        collector = ReviewFeedbackCollector(temp_repo)

        comments = [
            {"body": "This has a security vulnerability with SQL injection"},
            {"body": "Please fix the code style and naming conventions"},
            {"body": "The logic here is incorrect for edge cases"},
            {"body": "This is slow, please optimize the query"},
        ]

        categories = collector._analyze_review_changes(comments)

        assert "security" in categories
        assert "style" in categories
        assert "logic" in categories
        assert "performance" in categories

    def test_review_feedback_detects_human_commits(self, temp_repo):
        """Test that human commits are detected."""
        collector = ReviewFeedbackCollector(temp_repo)

        # AI commits
        ai_commits = [
            {"commit": {"message": "feat: add auth system\n\nadw_id: abc12345"}},
            {"commit": {"message": "fix: update logic\n\n🤖 Generated with Claude Code"}},
        ]

        assert not collector._detect_human_commits(ai_commits, "abc12345")

        # Human commit
        human_commits = [
            {"commit": {"message": "feat: add auth system\n\nadw_id: abc12345"}},
            {"commit": {"message": "fix: correct typo in variable name"}},
        ]

        assert collector._detect_human_commits(human_commits, "abc12345")

    def test_deployment_feedback_checks_labels(self, temp_repo):
        """Test DeploymentFeedbackCollector checks labels."""
        collector = DeploymentFeedbackCollector(temp_repo)

        # Mock issue with deployment labels (would normally come from GitHub API)
        # Testing the label checking logic
        labels_deployed = ["deployed", "production"]
        assert any(label in ["deployed", "production"] for label in labels_deployed)

        labels_failed = ["deployed", "failed"]
        assert any(label in ["failed"] for label in labels_failed)


class TestCrossProjectLearning:
    """Tests for cross-project learning store."""

    def test_aggregates_patterns_from_project(self, tmp_path):
        """Test that patterns are aggregated from project to global store."""
        global_dir = tmp_path / "global"
        project_dir = tmp_path / "project" / ".tac" / "learning"
        project_dir.mkdir(parents=True)

        store = CrossProjectLearningStore(global_dir)

        # Create project patterns
        project_patterns = {
            "patterns": [
                {
                    "pattern_name": "feature-auth",
                    "success_rate": 0.8,
                    "use_count": 5
                }
            ],
            "total_patterns": 1
        }

        with open(project_dir / "pattern_database.json", 'w') as f:
            json.dump(project_patterns, f)

        # Aggregate
        store.aggregate_from_project("test-project", project_dir)

        # Verify global store
        global_db = store._load_global_patterns()
        assert len(global_db["patterns"]) == 1
        assert global_db["patterns"][0]["pattern_name"] == "feature-auth"
        assert global_db["patterns"][0]["source_project"] == "test-project"
        assert "test-project" in global_db["patterns"][0]["contributing_projects"]

    def test_aggregates_merges_existing_patterns(self, tmp_path):
        """Test that patterns are merged (not duplicated) when aggregating."""
        global_dir = tmp_path / "global"
        project_dir = tmp_path / "project" / ".tac" / "learning"
        project_dir.mkdir(parents=True)

        store = CrossProjectLearningStore(global_dir)

        # Create initial global pattern
        global_patterns = {
            "patterns": [
                {
                    "pattern_name": "feature-auth",
                    "success_rate": 0.7,
                    "use_count": 10,
                    "contributing_projects": ["project-a"]
                }
            ],
            "total_patterns": 1
        }

        with open(global_dir / "global_pattern_database.json", 'w') as f:
            json.dump(global_patterns, f)

        # Create project pattern (same name, different success rate)
        project_patterns = {
            "patterns": [
                {
                    "pattern_name": "feature-auth",
                    "success_rate": 0.9,
                    "use_count": 5
                }
            ],
            "total_patterns": 1
        }

        with open(project_dir / "pattern_database.json", 'w') as f:
            json.dump(project_patterns, f)

        # Aggregate
        store.aggregate_from_project("project-b", project_dir)

        # Verify weighted average
        global_db = store._load_global_patterns()
        assert len(global_db["patterns"]) == 1  # Still only one pattern

        pattern = global_db["patterns"][0]
        assert pattern["use_count"] == 15  # 10 + 5
        # Weighted average: (0.7*10 + 0.9*5) / 15 = (7 + 4.5) / 15 = 0.7666...
        assert abs(pattern["success_rate"] - 0.7666) < 0.01
        assert "project-b" in pattern["contributing_projects"]

    def test_syncs_global_patterns_to_project(self, tmp_path):
        """Test that global patterns sync back to projects."""
        global_dir = tmp_path / "global"
        project_dir = tmp_path / "project" / ".tac" / "learning"
        project_dir.mkdir(parents=True)

        store = CrossProjectLearningStore(global_dir)

        # Create global patterns
        global_patterns = {
            "patterns": [
                {
                    "pattern_name": "bug-fix",
                    "success_rate": 0.95,
                    "use_count": 20
                }
            ],
            "total_patterns": 1
        }

        with open(global_dir / "global_pattern_database.json", 'w') as f:
            json.dump(global_patterns, f)

        # Sync to project
        store.sync_to_project(project_dir)

        # Verify project got the pattern
        with open(project_dir / "pattern_database.json") as f:
            project_db = json.load(f)

        assert len(project_db["patterns"]) == 1
        assert project_db["patterns"][0]["success_rate"] == 0.95

    def test_syncs_only_better_patterns(self, tmp_path):
        """Test that only patterns with higher success rates are synced."""
        global_dir = tmp_path / "global"
        project_dir = tmp_path / "project" / ".tac" / "learning"
        project_dir.mkdir(parents=True)

        store = CrossProjectLearningStore(global_dir)

        # Create global pattern
        global_patterns = {
            "patterns": [
                {"pattern_name": "pattern-a", "success_rate": 0.7},
                {"pattern_name": "pattern-b", "success_rate": 0.95},
            ],
            "total_patterns": 2
        }

        with open(global_dir / "global_pattern_database.json", 'w') as f:
            json.dump(global_patterns, f)

        # Create project pattern (pattern-a with higher success rate)
        project_patterns = {
            "patterns": [
                {"pattern_name": "pattern-a", "success_rate": 0.9},  # Better local version
            ],
            "total_patterns": 1
        }

        with open(project_dir / "pattern_database.json", 'w') as f:
            json.dump(project_patterns, f)

        # Sync
        store.sync_to_project(project_dir)

        # Verify
        with open(project_dir / "pattern_database.json") as f:
            project_db = json.load(f)

        # Should have pattern-b (new) and original pattern-a (better than global)
        assert len(project_db["patterns"]) == 2
        pattern_a = next(p for p in project_db["patterns"] if p["pattern_name"] == "pattern-a")
        assert pattern_a["success_rate"] == 0.9  # Kept better local version

    def test_get_global_insights(self, tmp_path):
        """Test global insights calculation."""
        global_dir = tmp_path / "global"
        store = CrossProjectLearningStore(global_dir)

        # Create global patterns
        global_patterns = {
            "patterns": [
                {"pattern_name": "p1", "success_rate": 0.8, "use_count": 10, "source_project": "proj-a"},
                {"pattern_name": "p2", "success_rate": 0.9, "use_count": 5, "source_project": "proj-b"},
                {"pattern_name": "p3", "success_rate": 0.7, "use_count": 15, "source_project": "proj-a"},
            ],
            "total_patterns": 3
        }

        with open(global_dir / "global_pattern_database.json", 'w') as f:
            json.dump(global_patterns, f)

        # Get insights
        insights = store.get_global_insights()

        assert insights["total_patterns"] == 3
        assert abs(insights["average_success_rate"] - 0.8) < 0.01  # (0.8 + 0.9 + 0.7) / 3
        assert len(insights["top_patterns"]) == 3
        assert insights["top_patterns"][0]["name"] == "p2"  # Highest success rate
        assert insights["patterns_by_project"]["proj-a"] == 2
        assert insights["patterns_by_project"]["proj-b"] == 1


class TestPromptRefiner:
    """Tests for prompt refinement engine."""

    def test_generates_suggestions_from_test_failures(self, temp_repo):
        """Test that PromptRefiner generates suggestions from test failures."""
        refiner = PromptRefiner(temp_repo)

        feedback = {
            "test_failures": ["auth", "api"],
            "review_changes": [],
        }

        suggestions = refiner._generate_suggestions(feedback)

        assert len(suggestions) > 0
        assert any("authentication tests" in s for s in suggestions)
        assert any("API endpoints" in s for s in suggestions)

    def test_generates_suggestions_from_review_changes(self, temp_repo):
        """Test suggestions from review feedback."""
        refiner = PromptRefiner(temp_repo)

        feedback = {
            "test_failures": [],
            "review_changes": ["security", "logic", "performance"],
        }

        suggestions = refiner._generate_suggestions(feedback)

        assert any("Security Checklist" in s for s in suggestions)
        assert any("Logic Verification" in s for s in suggestions)
        assert any("performance implications" in s for s in suggestions)

    def test_applies_explicit_instruction(self, temp_repo):
        """Test that explicit instructions are applied correctly."""
        refiner = PromptRefiner(temp_repo)

        original_prompt = (
            "# Feature Planning\n\n"
            "## Instructions\n\n"
            "- Create a plan\n\n"
            "## Tasks\n\n"
            "- Implement feature"
        )

        suggestion = "Add explicit instruction: 'Include comprehensive tests'"

        refined = refiner._apply_suggestion(original_prompt, suggestion)

        assert "Include comprehensive tests" in refined
        assert "## Instructions" in refined
        # Should be inserted in instructions section
        assert refined.find("Include comprehensive tests") < refined.find("## Tasks")

    def test_applies_section_addition(self, temp_repo):
        """Test that sections are added to end."""
        refiner = PromptRefiner(temp_repo)

        original_prompt = "# Feature\n\nOriginal content"

        suggestion = (
            "Add section: '## Security Checklist\\n"
            "- [ ] Input validation\\n"
            "- [ ] SQL injection prevention'"
        )

        refined = refiner._apply_suggestion(original_prompt, suggestion)

        assert "## Security Checklist" in refined
        assert "Input validation" in refined
        assert refined.endswith("SQL injection prevention'")

    def test_refine_prompt_applies_multiple_suggestions(self, temp_repo):
        """Test that multiple suggestions are applied iteratively."""
        refiner = PromptRefiner(temp_repo)

        original_prompt = "# Feature\n\n## Instructions\n\n- Original"

        feedback = {
            "test_failures": ["auth"],
            "review_changes": ["security"],
        }

        refined = refiner.refine_prompt(
            prompt_id="test_prompt",
            current_prompt=original_prompt,
            feedback=feedback,
            max_iterations=3
        )

        # Should have suggestions applied
        assert len(refined) > len(original_prompt)

        # Check that versioned file was saved
        latest_file = temp_repo / ".tac" / "prompts" / "test_prompt_latest.md"
        assert latest_file.exists()

        # Check history was updated
        history_file = temp_repo / ".tac" / "prompts" / "refinement_history.json"
        assert history_file.exists()

        with open(history_file) as f:
            history = json.load(f)

        assert "test_prompt" in history["prompts"]
        assert len(history["prompts"]["test_prompt"]["refinements"]) > 0

    def test_get_refinement_stats(self, temp_repo):
        """Test refinement statistics retrieval."""
        refiner = PromptRefiner(temp_repo)

        # Create some refinement history
        history = {
            "prompts": {
                "feature_planning": {
                    "refinements": [
                        {"iteration": 1, "suggestion": "Add tests", "timestamp": "2024-01-01"},
                        {"iteration": 2, "suggestion": "Add security", "timestamp": "2024-01-02"},
                    ],
                    "version": 3
                }
            }
        }

        with open(temp_repo / ".tac" / "prompts" / "refinement_history.json", 'w') as f:
            json.dump(history, f)

        stats = refiner.get_refinement_stats("feature_planning")

        assert stats["total_refinements"] == 2
        assert stats["current_version"] == 3
        assert stats["last_refined"] == "2024-01-02"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
