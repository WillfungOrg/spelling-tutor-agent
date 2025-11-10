"""Decision Engine for Meta-ADW Strategy System.

Pattern matching and template selection logic for recommending optimal workflows.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime

from adw_modules.meta_adw_types import (
    TaskAnalysis,
    TemplateIndex,
    PatternDatabase,
    DecisionWeights,
    PatternMatch,
    StrategyRecommendation,
)
from adw_modules.learning_query import LearningDataAccess


logger = logging.getLogger(__name__)


class DecisionEngine:
    """Decision engine for pattern matching and workflow recommendation."""

    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize decision engine.

        Args:
            repo_root: Path to repository root. If None, uses current directory.
        """
        self.repo_root = repo_root or Path.cwd()
        self.template_index: Optional[TemplateIndex] = None
        self.pattern_database: Optional[PatternDatabase] = None
        self.decision_weights: Optional[DecisionWeights] = None

        # Initialize learning data access
        learning_dir = self.repo_root / ".tac" / "learning"
        self.learning_data = LearningDataAccess(learning_dir)

    def load_template_index(self) -> TemplateIndex:
        """Load template index from .tac/template_index.json.

        Returns:
            TemplateIndex object

        Raises:
            FileNotFoundError: If template index doesn't exist
            ValueError: If template index is invalid
        """
        index_path = self.repo_root / ".tac" / "template_index.json"

        if not index_path.exists():
            raise FileNotFoundError(
                f"Template index not found at {index_path}. "
                "Run 'python scripts/build_template_index.py --rebuild' to create it."
            )

        try:
            with open(index_path, 'r') as f:
                data = json.load(f)

            # Convert compact format to TemplateIndex
            templates = {}
            for name, entry in data.get("t", {}).items():
                templates[name] = {
                    "name": name,
                    "size_tokens": entry.get("t", 0),
                    "tags": entry.get("g", []),
                    "summary": entry.get("s", ""),
                }

            self.template_index = TemplateIndex(
                version=data.get("v", "1.0"),
                total_templates=data.get("n", 0),
                templates=templates,
            )

            logger.info(f"Loaded template index with {self.template_index.total_templates} templates")
            return self.template_index

        except Exception as e:
            raise ValueError(f"Failed to load template index: {e}")

    def load_learning_data(self) -> Tuple[PatternDatabase, DecisionWeights]:
        """Load pattern database and decision weights from .tac/learning/.

        Returns:
            Tuple of (PatternDatabase, DecisionWeights)
        """
        learning_dir = self.repo_root / ".tac" / "learning"

        # Load pattern database
        pattern_path = learning_dir / "pattern_database.json"
        if pattern_path.exists():
            try:
                with open(pattern_path, 'r') as f:
                    pattern_data = json.load(f)
                self.pattern_database = PatternDatabase.model_validate(pattern_data)
            except Exception as e:
                logger.warning(f"Failed to load pattern database: {e}. Using empty database.")
                self.pattern_database = PatternDatabase()
        else:
            self.pattern_database = PatternDatabase()

        # Load decision weights
        weights_path = learning_dir / "decision_weights.json"
        if weights_path.exists():
            with open(weights_path, 'r') as f:
                weights_data = json.load(f)
            self.decision_weights = DecisionWeights.model_validate(weights_data)
        else:
            self.decision_weights = DecisionWeights()

        logger.info(
            f"Loaded learning data: {self.pattern_database.total_patterns} patterns, "
            f"{len(self.decision_weights.weights)} weight factors"
        )

        return self.pattern_database, self.decision_weights

    def match_patterns(self, task_analysis: TaskAnalysis) -> List[PatternMatch]:
        """Match task against template library using pattern matching.

        Args:
            task_analysis: TaskAnalysis object with task characteristics

        Returns:
            List of PatternMatch objects sorted by match score (highest first)
        """
        if not self.template_index:
            self.load_template_index()
        if not self.decision_weights:
            self.load_learning_data()

        matches = []

        # Extract keywords from task requirements
        task_keywords = set()
        for req in task_analysis.key_requirements:
            task_keywords.update(req.lower().split())

        # Match against each template
        for template_name, template_entry in self.template_index.templates.items():
            # Keyword matching
            template_keywords = set()
            summary = template_entry.get("summary") if isinstance(template_entry, dict) else template_entry.summary
            tags = template_entry.get("tags") if isinstance(template_entry, dict) else template_entry.tags

            template_keywords.update((summary or "").lower().split())
            template_keywords.update(tags or [])

            keyword_score = len(task_keywords & template_keywords) / max(len(task_keywords), 1)

            # Complexity matching (prefer templates for similar complexity)
            complexity_map = {"simple": 2, "moderate": 5, "complex": 8, "very_complex": 10}
            task_complexity = complexity_map.get(task_analysis.complexity_level, 5)
            size_tokens = template_entry.get("size_tokens") if isinstance(template_entry, dict) else template_entry.size_tokens
            template_complexity = (size_tokens or 1000) / 500  # Rough estimate
            complexity_score = 1.0 - abs(task_complexity - template_complexity) / 10
            complexity_score = max(0.0, min(1.0, complexity_score))

            # Validation depth matching
            validation_score = 0.5  # Default neutral score
            # Would need validation_level in template to improve this

            # Historical success rate
            success_rate = template_entry.get("success_rate") if isinstance(template_entry, dict) else template_entry.success_rate
            historical_score = success_rate or 0.0

            # Weighted combination
            weights = self.decision_weights.weights
            match_score = (
                keyword_score * weights.get("template_match", 0.4) +
                complexity_score * weights.get("complexity_match", 0.3) +
                validation_score * weights.get("validation_depth", 0.3)
            )

            # Boost by historical success
            match_score = match_score * (0.7 + 0.3 * historical_score)

            if match_score > 0.1:  # Only include reasonable matches
                matches.append(PatternMatch(
                    pattern_name=template_name,
                    match_score=match_score,
                    matched_keywords=list(task_keywords & template_keywords)[:5],
                    recommended_templates=[template_name],
                    reasoning=f"Keyword overlap: {len(task_keywords & template_keywords)} terms, "
                             f"Complexity fit: {complexity_score:.2f}, "
                             f"Historical success: {historical_score:.2f}"
                ))

        # Sort by match score descending
        matches.sort(key=lambda m: m.match_score, reverse=True)

        return matches

    def rank_workflows(self, task_analysis: TaskAnalysis, pattern_matches: List[PatternMatch]) -> List[Dict[str, Any]]:
        """Rank workflows based on pattern matches and historical learning data.

        Args:
            task_analysis: TaskAnalysis object
            pattern_matches: List of PatternMatch objects from match_patterns()

        Returns:
            List of ranked workflow recommendations with confidence scores
        """
        workflows = []

        # Map template patterns to ADW workflows
        workflow_mapping = {
            "feature.md": "adw_plan_build_test_iso",
            "bug.md": "adw_patch_iso",
            "patch.md": "adw_patch_iso",
            "chore.md": "adw_plan_build_iso",
            "test.md": "adw_test_iso",
            "review.md": "adw_review_iso",
        }

        # Query similar past tasks to inform decision
        similar_tasks = self.learning_data.query_similar_tasks(
            task_type=task_analysis.task_type,
            complexity_score=task_analysis.complexity_score,
            complexity_tolerance=2.0,
            has_ui_changes=task_analysis.has_ui_changes,
            requires_e2e_tests=task_analysis.requires_e2e_tests,
            limit=10,
            min_similarity=0.3,
        )

        # Determine optimal workflow based on task characteristics
        if task_analysis.task_type == "feature":
            if task_analysis.complexity_score > 7:
                primary_workflow = "adw_sdlc_iso"  # Full SDLC for complex features
                base_confidence = 0.9
                base_reasoning = "Complex feature requires full SDLC pipeline"
            elif task_analysis.requires_e2e_tests:
                primary_workflow = "adw_plan_build_test_iso"
                base_confidence = 0.85
                base_reasoning = "Feature with E2E tests needs plan+build+test"
            else:
                primary_workflow = "adw_plan_build_iso"
                base_confidence = 0.8
                base_reasoning = "Standard feature development workflow"

        elif task_analysis.task_type == "bug":
            if task_analysis.complexity_score < 4:
                primary_workflow = "adw_patch_iso"
                base_confidence = 0.9
                base_reasoning = "Simple bug fix can use quick patch workflow"
            else:
                primary_workflow = "adw_plan_build_test_iso"
                base_confidence = 0.85
                base_reasoning = "Complex bug needs full investigation and testing"

        elif task_analysis.task_type == "patch":
            primary_workflow = "adw_patch_iso"
            base_confidence = 0.95
            base_reasoning = "Patch tasks use direct patch workflow"

        elif task_analysis.task_type == "chore":
            primary_workflow = "adw_plan_build_iso"
            base_confidence = 0.8
            base_reasoning = "Maintenance tasks need planning and implementation"

        else:
            primary_workflow = "adw_plan_build_test_iso"
            base_confidence = 0.7
            base_reasoning = "Standard workflow for general tasks"

        # Enhance with historical performance data
        performance = self.learning_data.get_workflow_performance(
            workflow_name=primary_workflow,
            task_type=task_analysis.task_type,
            min_complexity=task_analysis.complexity_score - 2,
            max_complexity=task_analysis.complexity_score + 2,
        )

        # Blend rule-based confidence with historical success rate
        if performance["total_executions"] > 0:
            historical_weight = min(0.5, performance["total_executions"] / 20)  # Increase weight as we get more data
            confidence = (1 - historical_weight) * base_confidence + historical_weight * performance["success_rate"]

            # Add historical context to reasoning
            reasoning = f"{base_reasoning}. Historical: {performance['success_rate']:.1%} success ({performance['total_executions']} similar tasks)"

            # Add warnings about common failures
            if performance["common_errors"]:
                top_errors = performance["common_errors"][:2]
                reasoning += f". Watch for: {', '.join(top_errors)}"
        else:
            confidence = base_confidence
            reasoning = base_reasoning

        # Get average actual effort from similar tasks
        avg_effort_minutes = self.learning_data.get_average_actual_effort(
            task_type=task_analysis.task_type,
            complexity_score=task_analysis.complexity_score,
            complexity_tolerance=2.0,
        )
        avg_effort_hours = (avg_effort_minutes / 60.0) if avg_effort_minutes else None

        # Use historical token usage if available
        estimated_tokens = int(performance.get("avg_token_usage") or 80000)

        # Add context from similar tasks
        if similar_tasks:
            similar_context = f" Based on {len(similar_tasks)} similar past tasks"
            reasoning += similar_context

        # Add primary recommendation
        workflows.append({
            "workflow_name": primary_workflow,
            "confidence": confidence,
            "reasoning": reasoning,
            "templates": [m.pattern_name for m in pattern_matches[:3]],
            "estimated_tokens": estimated_tokens,
            "historical_data": {
                "success_rate": performance.get("success_rate"),
                "total_executions": performance.get("total_executions"),
                "avg_duration_minutes": performance.get("avg_duration_minutes"),
                "avg_effort_hours": avg_effort_hours,
                "similar_tasks_count": len(similar_tasks),
            }
        })

        # Add alternatives with historical data
        alternatives = [
            "adw_sdlc_iso",
            "adw_plan_build_test_review_iso",
            "adw_plan_build_iso",
            "adw_patch_iso",
        ]

        for alt_workflow in alternatives:
            if alt_workflow != primary_workflow:
                alt_performance = self.learning_data.get_workflow_performance(
                    workflow_name=alt_workflow,
                    task_type=task_analysis.task_type,
                    min_complexity=task_analysis.complexity_score - 2,
                    max_complexity=task_analysis.complexity_score + 2,
                )

                # Calculate alternative confidence based on its historical performance
                if alt_performance["total_executions"] > 0:
                    alt_confidence = base_confidence * 0.7 * (0.5 + 0.5 * alt_performance["success_rate"])
                    alt_reasoning = f"Alternative: {alt_workflow} ({alt_performance['success_rate']:.1%} success, {alt_performance['total_executions']} executions)"
                else:
                    alt_confidence = base_confidence * 0.7
                    alt_reasoning = f"Alternative approach using {alt_workflow} (no historical data)"

                workflows.append({
                    "workflow_name": alt_workflow,
                    "confidence": alt_confidence,
                    "reasoning": alt_reasoning,
                    "templates": [],
                    "estimated_tokens": int(alt_performance.get("avg_token_usage") or 70000),
                    "historical_data": {
                        "success_rate": alt_performance.get("success_rate"),
                        "total_executions": alt_performance.get("total_executions"),
                    }
                })
                if len(workflows) >= 3:
                    break

        return workflows

    def calculate_confidence(self, match_score: float, task_analysis: TaskAnalysis) -> float:
        """Calculate confidence score for a recommendation.

        Args:
            match_score: Pattern match score (0-1)
            task_analysis: TaskAnalysis object

        Returns:
            Confidence score (0-1)
        """
        # Base confidence from match score
        confidence = match_score

        # Boost confidence for standard tasks
        if task_analysis.complexity_level in ["simple", "moderate"]:
            confidence *= 1.1

        # Reduce confidence for novel/unique tasks
        # (We'd need novelty info in TaskAnalysis for this)

        # Clamp to [0, 1]
        return max(0.0, min(1.0, confidence))

    def recommend_strategy(self, task_analysis: TaskAnalysis) -> StrategyRecommendation:
        """Generate strategy recommendation for a task.

        Args:
            task_analysis: TaskAnalysis object with task characteristics

        Returns:
            StrategyRecommendation object with learning-enhanced insights
        """
        # Ensure data is loaded
        if not self.template_index:
            self.load_template_index()
        if not self.decision_weights:
            self.load_learning_data()

        # Match patterns
        pattern_matches = self.match_patterns(task_analysis)

        # Rank workflows (now includes learning data)
        ranked_workflows = self.rank_workflows(task_analysis, pattern_matches)

        # Primary recommendation
        primary = ranked_workflows[0]

        # Get common failure modes for this workflow
        failure_modes = self.learning_data.get_common_failure_modes(
            workflow_name=primary["workflow_name"],
            task_type=task_analysis.task_type,
            limit=3
        )

        # Enhance reasoning with failure insights
        enhanced_reasoning = primary["reasoning"]
        if failure_modes:
            failure_list = [f"{fm['error_type']}" for fm in failure_modes[:2]]
            enhanced_reasoning += f"\n\nCommon pitfalls to avoid: {', '.join(failure_list)}"

        # Get prediction accuracy stats (not filtered by workflow or task type)
        prediction_accuracy = self.learning_data.get_prediction_accuracy()

        # Adjust estimated effort based on historical accuracy
        historical_data = primary.get("historical_data", {})
        avg_effort_hours = historical_data.get("avg_effort_hours")
        if avg_effort_hours and avg_effort_hours > 0:
            # Use historical average if available
            adjusted_effort = avg_effort_hours
            enhanced_reasoning += f"\n\nHistorical average effort: {avg_effort_hours:.1f} hours (vs estimated {task_analysis.estimated_effort_hours or 0:.1f})"
        else:
            adjusted_effort = task_analysis.estimated_effort_hours

        # Build trade-offs with historical context
        base_trade_offs = self._identify_trade_offs(primary["workflow_name"])
        if historical_data.get("avg_duration_minutes"):
            avg_duration = historical_data["avg_duration_minutes"]
            base_trade_offs.append(f"Historical avg duration: {avg_duration:.0f} minutes")

        # Build recommendation
        recommendation = StrategyRecommendation(
            workflow_name=primary["workflow_name"],
            workflow_path=f"adw/{primary['workflow_name']}.py",
            template_names=primary.get("templates", []),
            validation_strategy=self._determine_validation_strategy(task_analysis),
            confidence_score=primary["confidence"],
            reasoning=enhanced_reasoning,
            alternatives=ranked_workflows[1:3],
            estimated_tokens=primary.get("estimated_tokens"),
            trade_offs=base_trade_offs,
            recommended_phases=self._determine_phases(primary["workflow_name"]),
        )

        return recommendation

    def _determine_validation_strategy(self, task_analysis: TaskAnalysis) -> str:
        """Determine validation strategy based on task analysis."""
        if task_analysis.validation_needs in ["critical", "l6_specialized", "l7_zero_touch"]:
            return "L6: Specialized validation agents with comprehensive checks"
        elif task_analysis.validation_needs in ["thorough", "l5_closed_loop"]:
            return "L5: Closed-loop validation with real environment feedback"
        else:
            return "Basic: Unit and integration tests"

    def _identify_trade_offs(self, workflow_name: str) -> List[str]:
        """Identify trade-offs for a workflow."""
        trade_offs_map = {
            "adw_sdlc_iso": [
                "Longer execution time (full pipeline)",
                "More comprehensive validation",
                "Higher token usage",
            ],
            "adw_patch_iso": [
                "Faster execution",
                "Less comprehensive testing",
                "Best for simple fixes",
            ],
            "adw_plan_build_test_iso": [
                "Balanced approach",
                "Good test coverage",
                "Moderate token usage",
            ],
        }
        return trade_offs_map.get(workflow_name, ["Standard trade-offs"])

    def _determine_phases(self, workflow_name: str) -> List[str]:
        """Determine recommended execution phases for a workflow."""
        phase_map = {
            "adw_sdlc_iso": ["plan", "build", "test", "review", "document"],
            "adw_patch_iso": ["patch", "test"],
            "adw_plan_build_test_iso": ["plan", "build", "test"],
            "adw_plan_build_iso": ["plan", "build"],
            "adw_plan_build_test_review_iso": ["plan", "build", "test", "review"],
        }
        return phase_map.get(workflow_name, ["plan", "build"])


def load_decision_engine(repo_root: Optional[Path] = None) -> DecisionEngine:
    """Convenience function to load and initialize decision engine.

    Args:
        repo_root: Path to repository root

    Returns:
        Initialized DecisionEngine
    """
    engine = DecisionEngine(repo_root)
    engine.load_template_index()
    engine.load_learning_data()
    return engine
