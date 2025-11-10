# Meta-ADW Strategy Recommendation

**Purpose:** Recommend optimal workflow strategy based on task analysis.

**When to use:** After task analysis, to select best execution approach.

---

## Your Task

Based on the TaskAnalysis provided, recommend the optimal Meta-ADW workflow strategy. Use pattern matching and historical data to make an informed recommendation.

## Input Format

You will receive a TaskAnalysis JSON:

```json
{
  "task_type": "...",
  "complexity_score": <float>,
  "complexity_level": "...",
  "validation_needs": "...",
  "key_requirements": [...],
  "estimated_effort_hours": <float>,
  "risk_factors": [...],
  "has_ui_changes": <boolean>,
  "requires_e2e_tests": <boolean>,
  "external_dependencies": [...],
  "recommended_model_set": "..."
}
```

## Recommendation Logic

### Workflow Selection Rules

**For Features:**
- **Simple features** (complexity < 4, no UI): `adw_plan_build_iso`
  - Plan + Build workflow
  - ~60K tokens
  - 2-4 hours

- **Moderate features** (complexity 4-7, may have UI): `adw_plan_build_test_iso`
  - Plan + Build + Test workflow
  - ~80K tokens
  - 4-8 hours

- **Complex features** (complexity > 7, critical): `adw_sdlc_iso`
  - Full SDLC: Plan + Build + Test + Review + Document
  - ~120K tokens
  - 8-16 hours

**For Bugs:**
- **Simple bugs** (complexity < 4): `adw_patch_iso`
  - Quick patch workflow
  - ~40K tokens
  - 1-2 hours

- **Complex bugs** (complexity >= 4): `adw_plan_build_test_iso`
  - Full investigation + fix + test
  - ~80K tokens
  - 4-8 hours

**For Chores:**
- **Standard chores**: `adw_plan_build_iso`
  - Plan + Build workflow
  - ~60K tokens
  - 2-6 hours

- **Critical chores** (affects production): `adw_plan_build_test_review_iso`
  - Plan + Build + Test + Review
  - ~100K tokens
  - 6-12 hours

### Validation Strategy Mapping

- `basic` → Unit and integration tests
- `thorough` → L5: Closed-loop validation with logs
- `critical` → L6: Specialized validation agents
- `l5_closed_loop` → TAC L5 pattern
- `l6_specialized` → TAC L6 pattern
- `l7_zero_touch` → TAC L7 pattern (full automation)

### Confidence Scoring

**High Confidence (0.8-1.0):**
- Clear task type (feature/bug/patch)
- Standard complexity range
- Existing templates match well
- Historical success with similar tasks

**Medium Confidence (0.5-0.8):**
- Some ambiguity in requirements
- Moderate complexity
- Partial template matches
- Limited historical data

**Low Confidence (0.0-0.5):**
- Novel/unique scenario
- Very high complexity
- No good template matches
- May need custom ADW

## Output Format

Generate a StrategyRecommendation JSON:

```json
{
  "workflow_name": "<workflow_name>",
  "workflow_path": "adw/<workflow_name>.py",
  "template_names": [
    "template1.md",
    "template2.md"
  ],
  "validation_strategy": "<validation description>",
  "confidence_score": <float 0-1>,
  "reasoning": "<why this strategy was chosen>",
  "alternatives": [
    {
      "workflow": "<alternative_workflow>",
      "confidence": <float>,
      "reasoning": "<why this could work>"
    }
  ],
  "estimated_tokens": <int>,
  "trade_offs": [
    "trade-off 1",
    "trade-off 2"
  ],
  "recommended_phases": [
    "plan",
    "build",
    "test"
  ],
  "recommendation_timestamp": "<ISO 8601 timestamp>"
}
```

---

## Examples

### Example 1: Simple Bug Fix

**Input:**
```json
{
  "task_type": "bug",
  "complexity_score": 2.0,
  "complexity_level": "simple",
  "validation_needs": "basic",
  "key_requirements": ["Fix typo in error message"],
  "estimated_effort_hours": 0.5,
  "risk_factors": [],
  "has_ui_changes": true,
  "requires_e2e_tests": false,
  "external_dependencies": [],
  "recommended_model_set": "base"
}
```

**Output:**
```json
{
  "workflow_name": "adw_patch_iso",
  "workflow_path": "adw/adw_patch_iso.py",
  "template_names": ["patch.md", "test.md"],
  "validation_strategy": "Basic: Unit tests to verify fix",
  "confidence_score": 0.95,
  "reasoning": "Simple cosmetic bug fix - patch workflow is ideal. Low risk, quick execution.",
  "alternatives": [
    {
      "workflow": "adw_plan_build_test_iso",
      "confidence": 0.6,
      "reasoning": "Overkill for simple fix but more thorough"
    }
  ],
  "estimated_tokens": 35000,
  "trade_offs": [
    "Faster execution (minutes vs hours)",
    "Less comprehensive testing",
    "Best for isolated fixes"
  ],
  "recommended_phases": ["patch", "test"],
  "recommendation_timestamp": "2025-11-03T19:30:00Z"
}
```

### Example 2: Complex Feature

**Input:**
```json
{
  "task_type": "feature",
  "complexity_score": 8.5,
  "complexity_level": "complex",
  "validation_needs": "critical",
  "key_requirements": [
    "Implement OAuth authentication",
    "Secure API endpoints",
    "Handle token refresh"
  ],
  "estimated_effort_hours": 18.0,
  "risk_factors": [
    "Security critical",
    "Affects all users",
    "External OAuth provider"
  ],
  "has_ui_changes": true,
  "requires_e2e_tests": true,
  "external_dependencies": ["OAuth provider API"],
  "recommended_model_set": "heavy"
}
```

**Output:**
```json
{
  "workflow_name": "adw_sdlc_iso",
  "workflow_path": "adw/adw_sdlc_iso.py",
  "template_names": [
    "feature.md",
    "implement.md",
    "test.md",
    "test_e2e.md",
    "review.md",
    "document.md"
  ],
  "validation_strategy": "L6: Specialized validation - security testing, E2E flows, OAuth integration tests, code review",
  "confidence_score": 0.92,
  "reasoning": "Complex security-critical feature requires full SDLC pipeline. High risk demands comprehensive validation including specialized security checks and E2E testing.",
  "alternatives": [
    {
      "workflow": "adw_plan_build_test_review_iso",
      "confidence": 0.75,
      "reasoning": "Slightly lighter without documentation phase"
    },
    {
      "workflow": "adw_plan_build_test_iso",
      "confidence": 0.55,
      "reasoning": "Minimum viable but skips critical review step"
    }
  ],
  "estimated_tokens": 125000,
  "trade_offs": [
    "Longest execution time (8-12 hours)",
    "Most comprehensive validation",
    "Highest confidence in quality",
    "Requires heavy model set",
    "Generates full documentation"
  ],
  "recommended_phases": [
    "plan",
    "build",
    "test",
    "review",
    "document"
  ],
  "recommendation_timestamp": "2025-11-03T19:30:00Z"
}
```

### Example 3: Moderate Chore

**Input:**
```json
{
  "task_type": "chore",
  "complexity_score": 5.0,
  "complexity_level": "moderate",
  "validation_needs": "thorough",
  "key_requirements": [
    "Upgrade database library",
    "Update queries for new API"
  ],
  "estimated_effort_hours": 4.0,
  "risk_factors": [
    "Data integrity",
    "Breaking changes possible"
  ],
  "has_ui_changes": false,
  "requires_e2e_tests": false,
  "external_dependencies": ["Database library v2"],
  "recommended_model_set": "base"
}
```

**Output:**
```json
{
  "workflow_name": "adw_plan_build_test_iso",
  "workflow_path": "adw/adw_plan_build_test_iso.py",
  "template_names": [
    "chore.md",
    "implement.md",
    "test.md"
  ],
  "validation_strategy": "L5: Closed-loop validation with integration tests against real database",
  "confidence_score": 0.85,
  "reasoning": "Moderate complexity chore affecting data layer. Needs careful planning and comprehensive testing to avoid data integrity issues.",
  "alternatives": [
    {
      "workflow": "adw_plan_build_iso",
      "confidence": 0.65,
      "reasoning": "Faster but skips dedicated testing phase"
    },
    {
      "workflow": "adw_sdlc_iso",
      "confidence": 0.55,
      "reasoning": "More thorough but likely overkill"
    }
  ],
  "estimated_tokens": 75000,
  "trade_offs": [
    "Balanced execution time (4-6 hours)",
    "Good test coverage for data changes",
    "Moderate token usage",
    "Includes integration test phase"
  ],
  "recommended_phases": [
    "plan",
    "build",
    "test"
  ],
  "recommendation_timestamp": "2025-11-03T19:30:00Z"
}
```

---

## Instructions

1. Read the TaskAnalysis JSON provided
2. Identify task type, complexity, and risk factors
3. Apply workflow selection rules above
4. Determine validation strategy based on validation_needs
5. Calculate confidence score (higher for standard tasks, lower for novel)
6. Provide clear reasoning for recommendation
7. Suggest 1-2 alternative workflows with lower confidence
8. List trade-offs of recommended approach
9. Determine execution phases
10. Generate StrategyRecommendation JSON
11. Include current timestamp in ISO 8601 format
12. Return ONLY the JSON - no additional commentary

## TaskAnalysis

$1
