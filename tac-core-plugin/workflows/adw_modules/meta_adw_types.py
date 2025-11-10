"""Data types for Meta-ADW Strategy System."""

from datetime import datetime
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


# Task complexity levels
ComplexityLevel = Literal["simple", "moderate", "complex", "very_complex"]

# Task types
TaskType = Literal["feature", "bug", "chore", "investigation", "patch", "refactor"]

# Validation depth levels (TAC L5/L6/L7)
ValidationDepth = Literal["basic", "thorough", "critical", "l5_closed_loop", "l6_specialized", "l7_zero_touch"]

# Model sets for Claude execution
ModelSet = Literal["base", "heavy"]


class TaskAnalysis(BaseModel):
    """Analysis of a task's characteristics and requirements."""

    task_type: TaskType = Field(description="Type of task (feature/bug/chore/etc)")
    complexity_score: float = Field(ge=1.0, le=10.0, description="Complexity score from 1-10")
    complexity_level: ComplexityLevel = Field(description="Simplified complexity level")
    validation_needs: ValidationDepth = Field(description="Required validation depth")
    key_requirements: List[str] = Field(
        default_factory=list, description="Key requirements extracted from task"
    )
    estimated_effort_hours: Optional[float] = Field(
        None, ge=0.0, description="Estimated effort in hours"
    )
    risk_factors: List[str] = Field(
        default_factory=list, description="Identified risk factors"
    )
    has_ui_changes: bool = Field(default=False, description="Whether task involves UI changes")
    requires_e2e_tests: bool = Field(default=False, description="Whether E2E tests are needed")
    external_dependencies: List[str] = Field(
        default_factory=list, description="External dependencies or integrations"
    )
    recommended_model_set: ModelSet = Field(
        default="base", description="Recommended model set for execution"
    )
    analysis_timestamp: datetime = Field(
        default_factory=datetime.now, description="When analysis was performed"
    )


class StrategyRecommendation(BaseModel):
    """Recommended strategy for executing a task."""

    workflow_name: str = Field(description="Name of recommended workflow/ADW")
    workflow_path: Optional[str] = Field(
        None, description="Path to workflow script if applicable"
    )
    template_names: List[str] = Field(
        default_factory=list, description="Templates to use in recommended order"
    )
    validation_strategy: str = Field(description="Recommended validation approach")
    confidence_score: float = Field(
        ge=0.0, le=1.0, description="Confidence in recommendation (0-1)"
    )
    reasoning: str = Field(description="Explanation for why this strategy was recommended")
    alternatives: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Alternative strategies with confidence scores"
    )
    estimated_tokens: Optional[int] = Field(
        None, description="Estimated token usage for this strategy"
    )
    trade_offs: List[str] = Field(
        default_factory=list, description="Trade-offs of this approach"
    )
    recommended_phases: List[str] = Field(
        default_factory=list,
        description="Recommended execution phases (plan/build/test/review/document)"
    )
    recommendation_timestamp: datetime = Field(
        default_factory=datetime.now, description="When recommendation was made"
    )


class ExecutionMetrics(BaseModel):
    """Detailed execution metrics for learning."""

    actual_duration_minutes: Optional[float] = Field(None, description="Actual execution time in minutes")
    estimated_duration_minutes: Optional[float] = Field(None, description="Estimated duration")
    duration_accuracy_ratio: Optional[float] = Field(None, description="Actual/Estimated ratio")
    total_token_usage: Optional[int] = Field(None, description="Total tokens used")
    phase_timings: Dict[str, float] = Field(default_factory=dict, description="Time per phase in minutes")
    retry_count: int = Field(default=0, description="Number of retries needed")
    error_count: int = Field(default=0, description="Number of errors encountered")
    files_changed: Optional[int] = Field(None, description="Number of files modified")
    lines_added: Optional[int] = Field(None, description="Lines of code added")
    lines_removed: Optional[int] = Field(None, description="Lines of code removed")
    test_coverage_before: Optional[float] = Field(None, ge=0.0, le=1.0, description="Test coverage before")
    test_coverage_after: Optional[float] = Field(None, ge=0.0, le=1.0, description="Test coverage after")
    tests_passed: Optional[int] = Field(None, description="Number of tests passed")
    tests_failed: Optional[int] = Field(None, description="Number of tests failed")
    test_success_rate: Optional[float] = Field(None, ge=0.0, le=1.0, description="Test pass rate")
    review_approved: Optional[bool] = Field(None, description="Whether code review was approved")
    deployed_successfully: Optional[bool] = Field(None, description="Whether deployment succeeded")


class ErrorRecord(BaseModel):
    """Detailed error tracking."""

    phase: str = Field(description="Which phase error occurred in")
    error_type: str = Field(description="Type of error (e.g., IndentationError)")
    error_message: str = Field(description="Error message")
    resolution: Optional[str] = Field(None, description="How error was resolved")
    time_to_fix_minutes: Optional[float] = Field(None, description="Time to fix the error")
    auto_fixed: bool = Field(default=False, description="Whether error was auto-fixed")


class LearningRecord(BaseModel):
    """Record of a Meta-ADW execution for learning purposes."""

    task_description: str = Field(description="Description of the task")
    task_analysis: TaskAnalysis = Field(description="Task analysis that was performed")
    recommended_strategy: Optional[StrategyRecommendation] = Field(
        None, description="Strategy that was recommended (None for manual sessions)"
    )
    selected_strategy: str = Field(description="Strategy user actually selected")
    user_overrode_recommendation: bool = Field(
        default=False, description="Whether user chose different strategy than primary"
    )
    outcome: Literal["success", "failure", "partial", "unknown", "cancelled"] = Field(
        description="Execution outcome"
    )
    execution_metrics: ExecutionMetrics = Field(
        default_factory=ExecutionMetrics,
        description="Detailed execution metrics"
    )
    # Deprecated: kept for backward compatibility, use execution_metrics instead
    success_metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Legacy metrics - use execution_metrics for new data"
    )
    errors_encountered: List[ErrorRecord] = Field(
        default_factory=list, description="Detailed error records"
    )
    # Deprecated: kept for backward compatibility
    problems_encountered: List[str] = Field(
        default_factory=list, description="Legacy problem list - use errors_encountered"
    )
    false_fix_detected: bool = Field(
        default=False,
        description="Whether agent claimed success but issue persisted"
    )
    user_satisfaction: Optional[int] = Field(
        None, ge=1, le=5, description="User satisfaction rating (1-5)"
    )
    failure_reason: Optional[str] = Field(None, description="Why execution failed if outcome=failure")
    follow_up_issues: List[str] = Field(
        default_factory=list, description="Follow-up issues created after execution"
    )
    execution_timestamp: datetime = Field(
        default_factory=datetime.now, description="When execution occurred"
    )
    execution_start_time: Optional[datetime] = Field(None, description="When execution started")
    execution_end_time: Optional[datetime] = Field(None, description="When execution ended")

    # Session tracking (flexible for both ADW and manual sessions)
    adw_id: Optional[str] = Field(None, description="ADW ID if workflow created one")
    issue_number: Optional[str] = Field(None, description="GitHub issue number (optional)")
    session_id: Optional[str] = Field(None, description="Session ID for manual Claude sessions")
    trigger_type: Literal["adw-automated", "manual-claude", "unknown"] = Field(
        default="unknown", description="How this work was triggered"
    )

    # Learning insights (especially valuable for manual sessions)
    key_learnings: List[str] = Field(
        default_factory=list, description="Key insights and lessons learned"
    )
    what_worked_well: List[str] = Field(
        default_factory=list, description="Approaches that were effective"
    )
    what_to_avoid: List[str] = Field(
        default_factory=list, description="Mistakes or ineffective approaches"
    )
    technical_patterns: List[str] = Field(
        default_factory=list, description="Reusable technical patterns identified"
    )


class TemplateIndexEntry(BaseModel):
    """Entry in the template index for a single template."""

    name: str = Field(description="Template filename (e.g., 'bug.md')")
    path: Optional[str] = Field(None, description="Relative path from .claude/commands/")
    size_tokens: int = Field(ge=0, description="Estimated token count")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    summary: str = Field(description="Brief summary of template purpose")
    use_cases: List[str] = Field(
        default_factory=list, description="When to use this template"
    )
    validation_level: Optional[ValidationDepth] = Field(
        None, description="Validation depth this template provides"
    )
    success_rate: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Historical success rate"
    )
    use_count: int = Field(default=0, ge=0, description="Number of times used")


class PatternMatch(BaseModel):
    """Result of pattern matching against template library."""

    pattern_name: str = Field(description="Name of matched pattern")
    match_score: float = Field(ge=0.0, le=1.0, description="How well pattern matches (0-1)")
    matched_keywords: List[str] = Field(
        default_factory=list, description="Keywords that contributed to match"
    )
    recommended_templates: List[str] = Field(
        description="Templates recommended based on this pattern"
    )
    reasoning: str = Field(description="Why this pattern matched")


class TemplateIndex(BaseModel):
    """Complete template index structure."""

    version: str = Field(default="1.0", description="Index version")
    last_updated: datetime = Field(
        default_factory=datetime.now, description="When index was last updated"
    )
    total_templates: int = Field(ge=0, description="Total number of templates")
    templates: Dict[str, TemplateIndexEntry] = Field(
        default_factory=dict, description="Template entries keyed by filename"
    )


class PatternDatabaseEntry(BaseModel):
    """Entry in the pattern database for learned patterns."""

    pattern_id: str = Field(description="Unique pattern identifier")
    task_characteristics: Dict[str, Any] = Field(
        description="Characteristics of tasks matching this pattern"
    )
    recommended_workflows: List[str] = Field(
        description="Workflows that work well for this pattern"
    )
    success_count: int = Field(default=0, ge=0, description="Number of successful executions")
    failure_count: int = Field(default=0, ge=0, description="Number of failed executions")
    success_rate: float = Field(ge=0.0, le=1.0, description="Success rate")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class PatternDatabase(BaseModel):
    """Complete pattern database structure."""

    version: str = Field(default="1.0")
    last_updated: datetime = Field(default_factory=datetime.now)
    patterns: List[PatternDatabaseEntry] = Field(default_factory=list)
    total_patterns: int = Field(default=0, ge=0)


class DecisionWeights(BaseModel):
    """Weights used by decision engine for pattern matching."""

    version: str = Field(default="1.0")
    last_updated: datetime = Field(default_factory=datetime.now)
    description: str = Field(
        default="Weights for decision engine pattern matching. Adjusted automatically."
    )
    weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "template_match": 0.4,
            "complexity_match": 0.3,
            "validation_depth": 0.3,
        },
        description="Weight for each matching factor"
    )
    thresholds: Dict[str, float] = Field(
        default_factory=lambda: {
            "use_existing": 0.8,
            "adapt_existing": 0.5,
            "create_custom": 0.0,
        },
        description="Confidence thresholds for tier selection"
    )
    learning_rate: float = Field(
        default=0.1, ge=0.0, le=1.0, description="How quickly weights adjust"
    )
    min_executions_for_retraining: int = Field(
        default=10, ge=1, description="Minimum executions before retraining weights"
    )
