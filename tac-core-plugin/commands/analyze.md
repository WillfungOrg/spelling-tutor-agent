# Meta-ADW Task Analysis

**Purpose:** Analyze task complexity and requirements to inform strategy selection.

**When to use:** After interview phase, before strategy recommendation.

---

## Your Task

Analyze the task based on interview responses and generate a detailed TaskAnalysis. This analysis will be used by the decision engine to recommend the optimal workflow strategy.

## Input Format

You will receive interview results in JSON format:

```json
{
  "task_description": "...",
  "task_type": "...",
  "complexity_level": "...",
  "user_interaction_layer": "...",
  "testing_requirements": "...",
  "validation_needs": "...",
  "timeline": "...",
  "novelty": "...",
  "additional_context": "..."
}
```

## Analysis Factors

Analyze the task across these dimensions:

### 1. Complexity Scoring (1-10 scale)

**Factors to consider:**
- Number of files likely to be modified (1-3 files = low, 4-10 = medium, 10+ = high)
- Cross-cutting concerns (affects multiple layers/modules)
- External dependencies (third-party APIs, services)
- Testing complexity (simple unit tests vs complex E2E scenarios)
- Risk level (business impact, data sensitivity, user-facing)

**Scoring guide:**
- 1-3: Simple, isolated changes
- 4-6: Moderate, multiple files or some complexity
- 7-8: Complex, cross-cutting or high risk
- 9-10: Very complex, critical systems or novel scenarios

### 2. Validation Depth Required

Map user's validation_needs to TAC patterns:
- `basic` → Basic validation (tests pass, no errors)
- `thorough` → L5 validation (closed-loop feedback, verify in real environment)
- `critical` → L6 validation (specialized validation agents, comprehensive checks)
- `l5_closed_loop` → TAC L5: Agent has access to logs/reality
- `l6_specialized` → TAC L6: Specialized validation agents for different aspects
- `l7_zero_touch` → TAC L7: Full automation with confidence

### 3. Effort Estimation

Estimate effort in hours based on:
- Complexity level
- Number of components affected
- Testing requirements
- Novelty (novel tasks take 2-3x longer)

**Estimation formula:**
- Simple: 1-2 hours
- Moderate: 2-6 hours
- Complex: 6-16 hours
- Very complex: 16+ hours
- Add 50% if novel, 100% if unique

### 4. Risk Assessment

Identify risk factors:
- Security implications (authentication, authorization, data access)
- Data integrity risks (database changes, migrations)
- User impact (affects all users, critical workflows)
- External dependencies (third-party service failures)
- Business impact (revenue, compliance, legal)

### 5. Requirements Extraction

Extract key requirements from task description:
- What must the solution do?
- What are the constraints?
- What are the success criteria?
- What validation is needed?

### 6. Model Set Recommendation

Recommend model set for execution:
- `base` (Sonnet): Most tasks, straightforward implementation
- `heavy` (Opus): Novel scenarios, complex architecture, critical systems

**Use heavy for:**
- Complexity score > 7
- Novel or unique tasks
- Critical validation needs
- Complex cross-cutting concerns

## Output Format

Generate a TaskAnalysis JSON matching the Pydantic model:

```json
{
  "task_type": "<feature|bug|chore|investigation|patch|refactor>",
  "complexity_score": <float between 1.0 and 10.0>,
  "complexity_level": "<simple|moderate|complex|very_complex>",
  "validation_needs": "<basic|thorough|critical|l5_closed_loop|l6_specialized|l7_zero_touch>",
  "key_requirements": [
    "requirement 1",
    "requirement 2",
    "..."
  ],
  "estimated_effort_hours": <float>,
  "risk_factors": [
    "risk 1",
    "risk 2",
    "..."
  ],
  "has_ui_changes": <boolean>,
  "requires_e2e_tests": <boolean>,
  "external_dependencies": [
    "dependency 1",
    "..."
  ],
  "recommended_model_set": "<base|heavy>",
  "analysis_timestamp": "<ISO 8601 timestamp>"
}
```

---

## Examples

### Example 1: Simple Bug Fix

**Input:**
```json
{
  "task_description": "Fix typo in error message",
  "task_type": "bug",
  "complexity_level": "simple",
  "user_interaction_layer": "UI",
  "testing_requirements": "unit",
  "validation_needs": "basic",
  "timeline": "quick-patch",
  "novelty": "standard"
}
```

**Output:**
```json
{
  "task_type": "bug",
  "complexity_score": 1.5,
  "complexity_level": "simple",
  "validation_needs": "basic",
  "key_requirements": [
    "Correct typo in error message text",
    "Verify message displays correctly in UI"
  ],
  "estimated_effort_hours": 0.5,
  "risk_factors": [
    "Minimal risk - cosmetic change only"
  ],
  "has_ui_changes": true,
  "requires_e2e_tests": false,
  "external_dependencies": [],
  "recommended_model_set": "base",
  "analysis_timestamp": "2025-11-03T19:00:00Z"
}
```

### Example 2: Complex Feature

**Input:**
```json
{
  "task_description": "Add user authentication with OAuth",
  "task_type": "feature",
  "complexity_level": "complex",
  "user_interaction_layer": "full-stack",
  "testing_requirements": "all",
  "validation_needs": "critical",
  "timeline": "comprehensive",
  "novelty": "novel"
}
```

**Output:**
```json
{
  "task_type": "feature",
  "complexity_score": 8.5,
  "complexity_level": "complex",
  "validation_needs": "critical",
  "key_requirements": [
    "Implement OAuth 2.0 authentication flow",
    "Create login/logout UI components",
    "Build backend authentication middleware",
    "Secure API endpoints with auth checks",
    "Handle token refresh and expiry",
    "Store user sessions securely"
  ],
  "estimated_effort_hours": 18.0,
  "risk_factors": [
    "Security-critical: authentication vulnerabilities could expose user data",
    "External dependency: OAuth provider availability",
    "User impact: affects all users and workflows",
    "Session management: token storage and expiry handling"
  ],
  "has_ui_changes": true,
  "requires_e2e_tests": true,
  "external_dependencies": [
    "OAuth provider API (Google/GitHub/etc)",
    "Token validation library"
  ],
  "recommended_model_set": "heavy",
  "analysis_timestamp": "2025-11-03T19:00:00Z"
}
```

### Example 3: Moderate Chore

**Input:**
```json
{
  "task_description": "Upgrade database library to latest version",
  "task_type": "chore",
  "complexity_level": "moderate",
  "user_interaction_layer": "backend",
  "testing_requirements": "integration",
  "validation_needs": "thorough",
  "timeline": "normal",
  "novelty": "standard"
}
```

**Output:**
```json
{
  "task_type": "chore",
  "complexity_score": 5.0,
  "complexity_level": "moderate",
  "validation_needs": "thorough",
  "key_requirements": [
    "Update database library dependency version",
    "Review and apply breaking changes if any",
    "Update database queries to use new APIs",
    "Verify backward compatibility",
    "Test all database operations"
  ],
  "estimated_effort_hours": 4.0,
  "risk_factors": [
    "Data integrity: query changes could affect data operations",
    "Breaking changes: library upgrade may require code updates",
    "Performance: new version performance characteristics unknown"
  ],
  "has_ui_changes": false,
  "requires_e2e_tests": false,
  "external_dependencies": [
    "Database library (new version)"
  ],
  "recommended_model_set": "base",
  "analysis_timestamp": "2025-11-03T19:00:00Z"
}
```

---

## Instructions

**IMPORTANT: This is programmatic analysis. Output ONLY pure JSON.**

1. Read the interview results provided below
2. Analyze complexity across all factors (files, dependencies, risk, testing)
3. Calculate complexity score (1-10) based on scoring guide
4. Identify all key requirements from task description
5. Assess risk factors comprehensively
6. Estimate effort considering complexity and novelty
7. Determine if UI changes or E2E tests are needed
8. List external dependencies
9. Recommend model set (base for most, heavy for complex/novel)
10. Generate TaskAnalysis JSON matching the Pydantic model
11. Include current timestamp in ISO 8601 format
12. **Output ONLY valid JSON that can be parsed by `json.loads()`**
13. **DO NOT** include any explanatory text before or after the JSON
14. **DO NOT** add comments, questions, or conversational text

## Interview Results

$1

---

## Your Response

**CRITICAL:** Your entire response must be ONLY the JSON object. Start your response with `{` and end with `}`. Do not include markdown code fences, explanatory text, or any other characters.

Example of correct output format (one line, no formatting):
```
{"task_type":"feature","complexity_score":6.5,"complexity_level":"moderate","validation_needs":"thorough","key_requirements":["Requirement 1","Requirement 2"],"estimated_effort_hours":10.0,"risk_factors":["Risk 1"],"has_ui_changes":true,"requires_e2e_tests":true,"external_dependencies":[],"recommended_model_set":"base","analysis_timestamp":"2025-11-03T00:00:00Z"}
```

Now analyze the interview results and output your TaskAnalysis JSON:
