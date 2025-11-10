"""Unit tests for Meta-ADW Pydantic data models."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from hub_modules.meta_adw_types import (
    TaskAnalysis,
    StrategyRecommendation,
    LearningRecord,
    TemplateIndexEntry,
    PatternMatch,
    TemplateIndex,
    PatternDatabaseEntry,
    PatternDatabase,
    DecisionWeights,
)


class TestTaskAnalysis:
    """Tests for TaskAnalysis model."""

    def test_valid_task_analysis(self):
        """Test creating a valid TaskAnalysis."""
        analysis = TaskAnalysis(
            task_type="feature",
            complexity_score=7.5,
            complexity_level="complex",
            validation_needs="thorough",
            key_requirements=["user authentication", "OAuth integration"],
            estimated_effort_hours=12.0,
            risk_factors=["security implications", "external API dependency"],
            has_ui_changes=True,
            requires_e2e_tests=True,
            external_dependencies=["OAuth provider API"],
            recommended_model_set="heavy",
        )

        assert analysis.task_type == "feature"
        assert analysis.complexity_score == 7.5
        assert analysis.has_ui_changes is True
        assert len(analysis.key_requirements) == 2

    def test_complexity_score_validation(self):
        """Test that complexity_score must be between 1-10."""
        with pytest.raises(ValidationError):
            TaskAnalysis(
                task_type="bug",
                complexity_score=11.0,  # Invalid: > 10
                complexity_level="simple",
                validation_needs="basic",
            )

        with pytest.raises(ValidationError):
            TaskAnalysis(
                task_type="bug",
                complexity_score=0.0,  # Invalid: < 1
                complexity_level="simple",
                validation_needs="basic",
            )

    def test_required_fields(self):
        """Test that required fields must be provided."""
        with pytest.raises(ValidationError):
            TaskAnalysis(
                # Missing required fields
                complexity_score=5.0,
            )


class TestStrategyRecommendation:
    """Tests for StrategyRecommendation model."""

    def test_valid_recommendation(self):
        """Test creating a valid StrategyRecommendation."""
        recommendation = StrategyRecommendation(
            workflow_name="adw_plan_build_test",
            workflow_path="adw/adw_plan_build_test.py",
            template_names=["feature.md", "implement.md", "test.md"],
            validation_strategy="L5 closed-loop with E2E tests",
            confidence_score=0.92,
            reasoning="High complexity feature with UI changes requires full ADW pipeline",
            alternatives=[
                {"workflow": "adw_patch", "confidence": 0.45},
                {"workflow": "manual", "confidence": 0.23},
            ],
            estimated_tokens=85000,
            trade_offs=["Longer execution time", "More thorough validation"],
            recommended_phases=["plan", "build", "test", "review"],
        )

        assert recommendation.confidence_score == 0.92
        assert len(recommendation.template_names) == 3
        assert len(recommendation.alternatives) == 2

    def test_confidence_score_bounds(self):
        """Test that confidence_score must be between 0-1."""
        with pytest.raises(ValidationError):
            StrategyRecommendation(
                workflow_name="test",
                validation_strategy="basic",
                confidence_score=1.5,  # Invalid: > 1
                reasoning="test",
            )


class TestLearningRecord:
    """Tests for LearningRecord model."""

    def test_valid_learning_record(self):
        """Test creating a valid LearningRecord."""
        analysis = TaskAnalysis(
            task_type="bug",
            complexity_score=4.0,
            complexity_level="moderate",
            validation_needs="thorough",
        )

        recommendation = StrategyRecommendation(
            workflow_name="adw_patch",
            validation_strategy="quick fix with tests",
            confidence_score=0.85,
            reasoning="Simple bug fix",
        )

        record = LearningRecord(
            task_description="Fix null pointer in user service",
            task_analysis=analysis,
            recommended_strategy=recommendation,
            selected_strategy="adw_patch",
            outcome="success",
            success_metrics={"time_to_complete": 45, "tests_passed": 12},
            user_satisfaction=4,
            adw_id="abc12345",
            issue_number="42",
        )

        assert record.outcome == "success"
        assert record.user_satisfaction == 4
        assert not record.user_overrode_recommendation

    def test_user_override_detection(self):
        """Test detecting when user overrides recommendation."""
        analysis = TaskAnalysis(
            task_type="feature",
            complexity_score=8.0,
            complexity_level="complex",
            validation_needs="critical",
        )

        recommendation = StrategyRecommendation(
            workflow_name="adw_plan_build_test",
            validation_strategy="full pipeline",
            confidence_score=0.90,
            reasoning="Complex feature",
        )

        record = LearningRecord(
            task_description="Add payment processing",
            task_analysis=analysis,
            recommended_strategy=recommendation,
            selected_strategy="manual",  # User chose different
            user_overrode_recommendation=True,
            outcome="partial",
        )

        assert record.user_overrode_recommendation is True
        assert record.selected_strategy != record.recommended_strategy.workflow_name


class TestTemplateIndexEntry:
    """Tests for TemplateIndexEntry model."""

    def test_valid_template_entry(self):
        """Test creating a valid TemplateIndexEntry."""
        entry = TemplateIndexEntry(
            name="bug.md",
            path=".claude/commands/bug.md",
            size_tokens=1500,
            tags=["debugging", "fix"],
            summary="Bug investigation and fix planning",
            use_cases=["When fixing bugs", "When investigating issues"],
            validation_level="thorough",
            success_rate=0.89,
            use_count=47,
        )

        assert entry.name == "bug.md"
        assert entry.success_rate == 0.89
        assert len(entry.tags) == 2

    def test_success_rate_bounds(self):
        """Test that success_rate must be between 0-1."""
        with pytest.raises(ValidationError):
            TemplateIndexEntry(
                name="test.md",
                size_tokens=100,
                summary="Test",
                success_rate=1.5,  # Invalid
            )


class TestPatternMatch:
    """Tests for PatternMatch model."""

    def test_valid_pattern_match(self):
        """Test creating a valid PatternMatch."""
        match = PatternMatch(
            pattern_name="complex_feature_with_ui",
            match_score=0.87,
            matched_keywords=["feature", "UI", "authentication"],
            recommended_templates=["feature.md", "implement.md", "test_e2e.md"],
            reasoning="Task involves UI changes and requires E2E testing",
        )

        assert match.match_score == 0.87
        assert len(match.recommended_templates) == 3


class TestTemplateIndex:
    """Tests for TemplateIndex model."""

    def test_valid_template_index(self):
        """Test creating a valid TemplateIndex."""
        entry1 = TemplateIndexEntry(
            name="bug.md",
            size_tokens=1500,
            tags=["bug"],
            summary="Bug fixes",
        )

        entry2 = TemplateIndexEntry(
            name="feature.md",
            size_tokens=2000,
            tags=["feature"],
            summary="New features",
        )

        index = TemplateIndex(
            total_templates=2,
            templates={"bug.md": entry1, "feature.md": entry2},
        )

        assert index.total_templates == 2
        assert len(index.templates) == 2
        assert "bug.md" in index.templates


class TestPatternDatabase:
    """Tests for PatternDatabase model."""

    def test_valid_pattern_database(self):
        """Test creating a valid PatternDatabase."""
        entry = PatternDatabaseEntry(
            pattern_id="feature_with_ui",
            task_characteristics={"has_ui": True, "complexity": "high"},
            recommended_workflows=["adw_plan_build_test"],
            success_count=15,
            failure_count=2,
            success_rate=0.88,
        )

        db = PatternDatabase(
            patterns=[entry],
            total_patterns=1,
        )

        assert db.total_patterns == 1
        assert len(db.patterns) == 1
        assert db.patterns[0].success_rate == 0.88


class TestDecisionWeights:
    """Tests for DecisionWeights model."""

    def test_valid_decision_weights(self):
        """Test creating valid DecisionWeights."""
        weights = DecisionWeights(
            weights={
                "template_match": 0.4,
                "complexity_match": 0.3,
                "validation_depth": 0.3,
            },
            thresholds={
                "use_existing": 0.8,
                "adapt_existing": 0.5,
                "create_custom": 0.0,
            },
            learning_rate=0.1,
            min_executions_for_retraining=10,
        )

        assert weights.weights["template_match"] == 0.4
        assert weights.thresholds["use_existing"] == 0.8
        assert weights.learning_rate == 0.1

    def test_learning_rate_bounds(self):
        """Test that learning_rate must be between 0-1."""
        with pytest.raises(ValidationError):
            DecisionWeights(learning_rate=1.5)  # Invalid


class TestModelSerialization:
    """Tests for JSON serialization/deserialization."""

    def test_task_analysis_json_round_trip(self):
        """Test TaskAnalysis can be serialized and deserialized."""
        original = TaskAnalysis(
            task_type="feature",
            complexity_score=6.0,
            complexity_level="moderate",
            validation_needs="thorough",
            key_requirements=["req1", "req2"],
        )

        # Serialize to JSON
        json_data = original.model_dump_json()

        # Deserialize back
        restored = TaskAnalysis.model_validate_json(json_data)

        assert restored.task_type == original.task_type
        assert restored.complexity_score == original.complexity_score
        assert restored.key_requirements == original.key_requirements

    def test_learning_record_json_round_trip(self):
        """Test LearningRecord can be serialized with nested models."""
        analysis = TaskAnalysis(
            task_type="bug",
            complexity_score=3.0,
            complexity_level="simple",
            validation_needs="basic",
        )

        recommendation = StrategyRecommendation(
            workflow_name="adw_patch",
            validation_strategy="quick test",
            confidence_score=0.75,
            reasoning="Simple fix",
        )

        original = LearningRecord(
            task_description="Fix typo",
            task_analysis=analysis,
            recommended_strategy=recommendation,
            selected_strategy="adw_patch",
            outcome="success",
        )

        # Serialize
        json_data = original.model_dump_json()

        # Deserialize
        restored = LearningRecord.model_validate_json(json_data)

        assert restored.task_analysis.task_type == "bug"
        assert restored.recommended_strategy.workflow_name == "adw_patch"
        assert restored.outcome == "success"
