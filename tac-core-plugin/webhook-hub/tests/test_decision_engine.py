"""Unit tests for decision engine pattern matching."""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from decision_engine import DecisionEngine, load_decision_engine
from hub_modules.meta_adw_types import TaskAnalysis, StrategyRecommendation


class TestDecisionEngine:
    """Test suite for DecisionEngine class."""

    @pytest.fixture
    def temp_repo_root(self, tmp_path):
        """Create temporary repository structure."""
        # Create required directories
        tac_dir = tmp_path / ".tac"
        tac_dir.mkdir()
        learning_dir = tac_dir / "learning"
        learning_dir.mkdir()

        # Create template index
        template_index = {
            "v": "1.0",
            "n": 3,
            "t": {
                "feature.md": {
                    "t": 1500,
                    "g": ["feature", "planning"],
                    "s": "Plan new features with detailed requirements",
                },
                "bug.md": {
                    "t": 1200,
                    "g": ["bug", "debugging"],
                    "s": "Fix bugs with root cause analysis",
                },
                "patch.md": {
                    "t": 800,
                    "g": ["patch", "quick"],
                    "s": "Quick patches for simple fixes",
                },
            },
        }
        with open(tac_dir / "template_index.json", 'w') as f:
            json.dump(template_index, f)

        # Create pattern database
        pattern_db = {
            "patterns": [],
            "version": "1.0",
            "last_updated": "2025-11-03T00:00:00Z",
            "total_patterns": 0,
        }
        with open(learning_dir / "pattern_database.json", 'w') as f:
            json.dump(pattern_db, f)

        # Create decision weights
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
        }
        with open(learning_dir / "decision_weights.json", 'w') as f:
            json.dump(weights, f)

        return tmp_path

    @pytest.fixture
    def engine(self, temp_repo_root):
        """Create DecisionEngine instance with temp repository."""
        return DecisionEngine(repo_root=temp_repo_root)

    def test_load_template_index(self, engine):
        """Test loading template index from file."""
        template_index = engine.load_template_index()

        assert template_index.version == "1.0"
        assert template_index.total_templates == 3
        assert "feature.md" in template_index.templates
        assert "bug.md" in template_index.templates
        assert "patch.md" in template_index.templates

    def test_load_learning_data(self, engine):
        """Test loading pattern database and decision weights."""
        pattern_db, weights = engine.load_learning_data()

        assert pattern_db.version == "1.0"
        assert pattern_db.total_patterns == 0
        assert weights.weights["template_match"] == 0.4
        assert weights.weights["complexity_match"] == 0.3
        assert weights.weights["validation_depth"] == 0.3

    def test_match_patterns_feature(self, engine):
        """Test pattern matching for feature task."""
        engine.load_template_index()
        engine.load_learning_data()

        task_analysis = TaskAnalysis(
            task_type="feature",
            complexity_score=5.0,
            complexity_level="moderate",
            validation_needs="thorough",
            key_requirements=["Build new feature", "Add user interface"],
            estimated_effort_hours=8.0,
            risk_factors=[],
            has_ui_changes=True,
            requires_e2e_tests=True,
            external_dependencies=[],
            recommended_model_set="base",
        )

        matches = engine.match_patterns(task_analysis)

        assert len(matches) > 0
        # Feature template should match
        assert any(m.pattern_name == "feature.md" for m in matches)

    def test_match_patterns_simple_bug(self, engine):
        """Test pattern matching for simple bug fix."""
        engine.load_template_index()
        engine.load_learning_data()

        task_analysis = TaskAnalysis(
            task_type="bug",
            complexity_score=2.0,
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

        matches = engine.match_patterns(task_analysis)

        assert len(matches) > 0
        # Patch template should score well for simple bugs
        assert any(m.pattern_name == "patch.md" for m in matches)

    def test_rank_workflows_feature(self, engine):
        """Test workflow ranking for feature."""
        engine.load_template_index()
        engine.load_learning_data()

        task_analysis = TaskAnalysis(
            task_type="feature",
            complexity_score=8.0,
            complexity_level="complex",
            validation_needs="critical",
            key_requirements=["Complex feature"],
            estimated_effort_hours=20.0,
            risk_factors=["High risk"],
            has_ui_changes=True,
            requires_e2e_tests=True,
            external_dependencies=[],
            recommended_model_set="heavy",
        )

        pattern_matches = engine.match_patterns(task_analysis)
        workflows = engine.rank_workflows(task_analysis, pattern_matches)

        assert len(workflows) > 0
        # Complex feature should recommend full SDLC
        assert workflows[0]["workflow_name"] == "adw_sdlc_iso"
        assert workflows[0]["confidence"] >= 0.8

    def test_rank_workflows_simple_bug(self, engine):
        """Test workflow ranking for simple bug."""
        engine.load_template_index()
        engine.load_learning_data()

        task_analysis = TaskAnalysis(
            task_type="bug",
            complexity_score=2.0,
            complexity_level="simple",
            validation_needs="basic",
            key_requirements=["Quick fix"],
            estimated_effort_hours=1.0,
            risk_factors=[],
            has_ui_changes=False,
            requires_e2e_tests=False,
            external_dependencies=[],
            recommended_model_set="base",
        )

        pattern_matches = engine.match_patterns(task_analysis)
        workflows = engine.rank_workflows(task_analysis, pattern_matches)

        assert len(workflows) > 0
        # Simple bug should recommend patch workflow
        assert workflows[0]["workflow_name"] == "adw_patch_iso"
        assert workflows[0]["confidence"] >= 0.8

    def test_calculate_confidence(self, engine):
        """Test confidence calculation."""
        task_analysis = TaskAnalysis(
            task_type="feature",
            complexity_score=5.0,
            complexity_level="moderate",
            validation_needs="thorough",
            key_requirements=[],
            estimated_effort_hours=8.0,
            risk_factors=[],
            has_ui_changes=True,
            requires_e2e_tests=False,
            external_dependencies=[],
            recommended_model_set="base",
        )

        # High match score
        confidence = engine.calculate_confidence(0.9, task_analysis)
        assert confidence > 0.9  # Boosted for moderate complexity

        # Low match score
        confidence = engine.calculate_confidence(0.3, task_analysis)
        assert 0.0 <= confidence <= 1.0

    def test_recommend_strategy(self, engine):
        """Test full strategy recommendation."""
        engine.load_template_index()
        engine.load_learning_data()

        task_analysis = TaskAnalysis(
            task_type="feature",
            complexity_score=6.0,
            complexity_level="moderate",
            validation_needs="thorough",
            key_requirements=["Build feature", "Add tests"],
            estimated_effort_hours=10.0,
            risk_factors=[],
            has_ui_changes=True,
            requires_e2e_tests=True,
            external_dependencies=[],
            recommended_model_set="base",
        )

        recommendation = engine.recommend_strategy(task_analysis)

        assert isinstance(recommendation, StrategyRecommendation)
        assert recommendation.workflow_name in [
            "adw_plan_build_test_iso",
            "adw_sdlc_iso",
        ]
        assert 0.0 <= recommendation.confidence_score <= 1.0
        assert len(recommendation.reasoning) > 0
        assert recommendation.estimated_tokens > 0

    def test_validation_strategy_mapping(self, engine):
        """Test validation strategy determination."""
        # Basic validation
        task_basic = TaskAnalysis(
            task_type="bug",
            complexity_score=2.0,
            complexity_level="simple",
            validation_needs="basic",
            key_requirements=[],
            estimated_effort_hours=1.0,
            risk_factors=[],
            has_ui_changes=False,
            requires_e2e_tests=False,
            external_dependencies=[],
            recommended_model_set="base",
        )
        strategy = engine._determine_validation_strategy(task_basic)
        assert "Basic" in strategy or "Unit" in strategy

        # Critical validation (L6)
        task_critical = TaskAnalysis(
            task_type="feature",
            complexity_score=9.0,
            complexity_level="very_complex",
            validation_needs="critical",
            key_requirements=[],
            estimated_effort_hours=24.0,
            risk_factors=["Security"],
            has_ui_changes=True,
            requires_e2e_tests=True,
            external_dependencies=[],
            recommended_model_set="heavy",
        )
        strategy = engine._determine_validation_strategy(task_critical)
        assert "L6" in strategy or "Specialized" in strategy

    def test_trade_offs_identification(self, engine):
        """Test trade-offs identification for workflows."""
        # SDLC workflow
        trade_offs = engine._identify_trade_offs("adw_sdlc_iso")
        assert len(trade_offs) > 0
        assert any("comprehensive" in t.lower() for t in trade_offs)

        # Patch workflow
        trade_offs = engine._identify_trade_offs("adw_patch_iso")
        assert len(trade_offs) > 0
        assert any("fast" in t.lower() or "quick" in t.lower() for t in trade_offs)

    def test_phases_determination(self, engine):
        """Test phase determination for workflows."""
        # Full SDLC
        phases = engine._determine_phases("adw_sdlc_iso")
        assert "plan" in phases
        assert "build" in phases
        assert "test" in phases
        assert "review" in phases
        assert "document" in phases

        # Patch workflow
        phases = engine._determine_phases("adw_patch_iso")
        assert "patch" in phases
        assert "test" in phases
        assert len(phases) == 2

    def test_load_decision_engine_convenience_function(self, temp_repo_root):
        """Test convenience function for loading engine."""
        engine = load_decision_engine(repo_root=temp_repo_root)

        assert engine.template_index is not None
        assert engine.pattern_database is not None
        assert engine.decision_weights is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
