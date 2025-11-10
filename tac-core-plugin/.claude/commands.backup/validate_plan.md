# Meta-ADW Plan Validation

**Purpose:** Validate implementation plans for completeness and validation gaps.

**When to use:** After plan generation, before execution, to catch validation gaps early.

---

## Your Task

Review an implementation plan and check for validation gaps. Identify missing validation steps, insufficient test coverage, or areas where "agent says fixed but isn't" could occur.

## Validation Checklist

### 1. Validation Commands Present
- [ ] Are validation commands included in the plan?
- [ ] Are commands executable (not pseudo-code)?
- [ ] Do commands cover all modified components?
- [ ] Are success criteria clearly defined?

### 2. Complexity Match
- [ ] Does validation depth match task complexity?
- [ ] Simple tasks: Unit tests sufficient?
- [ ] Complex tasks: Integration + E2E tests included?
- [ ] Critical tasks: Review + monitoring included?

### 3. Edge Cases Covered
- [ ] Are edge cases identified?
- [ ] Are error scenarios tested?
- [ ] Are boundary conditions checked?
- [ ] Are failure modes handled?

### 4. UI Changes Validation
- [ ] If UI changes: Are E2E tests included?
- [ ] Are visual regressions checked?
- [ ] Are accessibility tests included?
- [ ] Are different viewports/browsers tested?

### 5. Closed-Loop Validation (TAC L5)
- [ ] Does agent have access to logs?
- [ ] Can agent verify in real environment?
- [ ] Are feedback loops included?
- [ ] Can agent detect "false fixes"?

### 6. Success Criteria Measurable
- [ ] Are criteria objective (not subjective)?
- [ ] Can success be programmatically verified?
- [ ] Are acceptance criteria clear?
- [ ] Are metrics defined?

## Common Validation Gaps

### Gap 1: "Tests pass but feature broken"
**Symptom:** Unit tests pass, but E2E workflow fails
**Fix:** Add E2E test validating full user workflow

### Gap 2: "Agent claims fixed but isn't"
**Symptom:** Agent marks task done, but issue persists
**Fix:** Add L5 closed-loop validation with real logs

### Gap 3: "Works locally but fails in production"
**Symptom:** Development environment passes, production fails
**Fix:** Add integration tests against production-like environment

### Gap 4: "Edge cases not covered"
**Symptom:** Happy path works, but edge cases cause errors
**Fix:** Add specific tests for identified edge cases

### Gap 5: "No rollback plan"
**Symptom:** Deployment breaks production, no recovery
**Fix:** Add rollback procedure and verification

## Output Format

```json
{
  "validation_status": "<pass|fail|warning>",
  "confidence_score": <float 0-1>,
  "missing_validation_steps": [
    {
      "category": "<validation_commands|edge_cases|e2e_tests|etc>",
      "severity": "<critical|high|medium|low>",
      "description": "What's missing",
      "recommendation": "How to fix it"
    }
  ],
  "validation_improvements": [
    "Specific improvement 1",
    "Specific improvement 2"
  ],
  "validation_summary": {
    "total_checks": <int>,
    "passed_checks": <int>,
    "failed_checks": <int>,
    "warnings": <int>
  },
  "recommended_actions": [
    "Action 1 before proceeding",
    "Action 2 for better validation"
  ]
}
```

---

## Examples

### Example 1: Plan with Good Validation (PASS)

**Input Plan:**
```markdown
# Fix Login Button Not Working

## Validation Commands
- Run unit tests: `pytest tests/test_auth.py`
- Run E2E test: Read `.claude/commands/e2e/test_login.md` and execute
- Manual verification: Test login with valid/invalid credentials
- Check logs: Verify no errors in auth service logs

## Edge Cases
- Invalid credentials
- Expired session
- Network timeout
- Browser back button after login
```

**Output:**
```json
{
  "validation_status": "pass",
  "confidence_score": 0.9,
  "missing_validation_steps": [],
  "validation_improvements": [
    "Consider adding performance test for login response time",
    "Could add security test for SQL injection attempts"
  ],
  "validation_summary": {
    "total_checks": 6,
    "passed_checks": 6,
    "failed_checks": 0,
    "warnings": 0
  },
  "recommended_actions": [
    "Proceed with implementation - validation is comprehensive"
  ]
}
```

### Example 2: Plan with Missing E2E Tests (FAIL)

**Input Plan:**
```markdown
# Add User Profile Page

## Validation Commands
- Run unit tests: `pytest tests/test_profile.py`
- Check types: `bun tsc --noEmit`

## Implementation
- Create ProfilePage component
- Add API endpoint /api/profile
- Update navigation menu
```

**Output:**
```json
{
  "validation_status": "fail",
  "confidence_score": 0.4,
  "missing_validation_steps": [
    {
      "category": "e2e_tests",
      "severity": "critical",
      "description": "No E2E test for user profile workflow. Unit tests won't catch UI integration issues.",
      "recommendation": "Add E2E test file: `.claude/commands/e2e/test_user_profile.md` that validates: 1) Navigate to profile, 2) View profile data, 3) Edit profile, 4) Save changes, 5) Verify persistence"
    },
    {
      "category": "edge_cases",
      "severity": "high",
      "description": "No edge cases identified. Missing scenarios like empty profile, invalid data, unauthorized access.",
      "recommendation": "Add edge case testing for: Empty profile fields, Invalid email format, Unauthorized access attempts, Profile image upload limits"
    },
    {
      "category": "validation_commands",
      "severity": "medium",
      "description": "No integration test for API endpoint. Backend/frontend integration not validated.",
      "recommendation": "Add integration test: Test API endpoint returns correct data, handles errors properly"
    }
  ],
  "validation_improvements": [
    "Add E2E test validating complete user profile workflow",
    "Define edge cases and add tests for each",
    "Add API integration tests",
    "Include visual regression test for profile page UI"
  ],
  "validation_summary": {
    "total_checks": 6,
    "passed_checks": 2,
    "failed_checks": 3,
    "warnings": 1
  },
  "recommended_actions": [
    "CRITICAL: Add E2E test before proceeding",
    "HIGH: Define and test edge cases",
    "MEDIUM: Add API integration tests",
    "Then re-validate plan before implementation"
  ]
}
```

### Example 3: Complex Task Needs L5 Validation (WARNING)

**Input Plan:**
```markdown
# Implement Payment Processing

## Validation Commands
- Run unit tests: `pytest tests/test_payments.py`
- Check integration: Test with Stripe test API
```

**Output:**
```json
{
  "validation_status": "warning",
  "confidence_score": 0.6,
  "missing_validation_steps": [
    {
      "category": "closed_loop_validation",
      "severity": "critical",
      "description": "Payment processing is critical but lacks L5 closed-loop validation. Agent can't verify payments succeeded in real environment.",
      "recommendation": "Add L5 validation: Agent should verify payment records in database, check Stripe dashboard confirms payment, review payment service logs for errors"
    },
    {
      "category": "edge_cases",
      "severity": "high",
      "description": "Payment edge cases not covered: Failed payments, partial refunds, currency conversions, duplicate charges.",
      "recommendation": "Add comprehensive edge case tests for all payment failure modes"
    },
    {
      "category": "rollback_plan",
      "severity": "high",
      "description": "No rollback plan for failed deployment. Payment system downtime is critical.",
      "recommendation": "Add rollback procedure: Feature flag to disable new payment flow, revert to previous version steps, verification that old flow works"
    }
  ],
  "validation_improvements": [
    "Implement TAC L5 closed-loop validation with real payment verification",
    "Add comprehensive edge case testing for all failure modes",
    "Create rollback plan and test it",
    "Add monitoring/alerting for payment failures",
    "Include security audit for payment handling"
  ],
  "validation_summary": {
    "total_checks": 6,
    "passed_checks": 2,
    "failed_checks": 2,
    "warnings": 2
  },
  "recommended_actions": [
    "CRITICAL: Implement L5 closed-loop validation before proceeding",
    "HIGH: Add comprehensive edge case tests",
    "HIGH: Create and test rollback plan",
    "Consider security audit before deployment"
  ]
}
```

---

## Instructions

1. Read the implementation plan provided
2. Go through each validation checklist item
3. Identify what's missing or insufficient
4. Categorize gaps by severity (critical/high/medium/low)
5. Provide specific, actionable recommendations
6. Calculate confidence score based on validation coverage
7. Determine overall status (pass/fail/warning)
8. Generate validation report JSON
9. Return ONLY the JSON - no additional commentary

## Implementation Plan

$1
