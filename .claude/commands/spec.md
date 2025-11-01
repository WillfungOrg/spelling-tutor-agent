# Create Specification

**Purpose:** Generate a detailed, AI-executable specification before starting any implementation.

**When to use:** Before every feature, bug fix, or significant change.

**TAC Principle:** Spec-First Development (Principle 1)

---

## What This Command Does

1. Performs knowledge gap check
2. Gathers requirements from user
3. Creates structured specification
4. Saves to `.claude/specs/[name].md`
5. Validates spec is AI-executable

---

## Instructions for AI

You are creating a specification document. Follow this process:

### Phase 1: Knowledge Gap Check

**First, check for knowledge gaps:**

```markdown
Before creating the spec, I need to ensure I have current knowledge.

Let me check:
1. Project context: [Read .claude/project-context.md]
2. Framework versions: [From project-context.md]
3. Similar past work: [Check git log or existing specs]
4. Required resources: [MCP servers, docs, etc.]
```

**If gaps exist:**
- Report them to user
- Request necessary resources
- Fill gaps before proceeding

### Phase 2: Gather Requirements

Ask the user for essential information:

#### For Features:
```markdown
To create a complete spec, I need:

1. **Objective:** What should this feature accomplish?
2. **User Story:** Who needs this and why?
3. **Success Criteria:** How will we know it's done?
4. **Constraints:** Any technical limitations or requirements?
5. **Integration Points:** What does this interact with?
```

#### For Bugs:
```markdown
To create a complete spec, I need:

1. **Current Behavior:** What's happening now?
2. **Expected Behavior:** What should happen?
3. **Reproduction Steps:** How to trigger the bug?
4. **Impact:** Who/what is affected?
5. **Root Cause (if known):** Any insights into why?
```

#### For Chores:
```markdown
To create a complete spec, I need:

1. **Objective:** What needs to be maintained/refactored?
2. **Motivation:** Why now? What's the driver?
3. **Scope:** What's included and excluded?
4. **Success Criteria:** How to validate it's complete?
5. **Risks:** What could break?
```

### Phase 3: Create Specification

Use the appropriate template based on task type:

#### Feature Specification Template

```markdown
# [Feature Name] - Specification

**Type:** Feature
**Created:** [Date]
**Status:** Draft
**Assigned To:** AI Agent

---

## Context

### Project Context
- **Project:** [From project-context.md]
- **Tech Stack:** [From project-context.md]
- **Related Work:** [Link to similar features/PRs]

### Knowledge Resources
- [List MCP servers connected]
- [List documentation referenced]
- [List code files reviewed]

---

## Objective

[Clear, one-sentence objective]

### User Story
As a [user type], I want [capability] so that [benefit].

### Success Criteria
- [ ] [Measurable outcome 1]
- [ ] [Measurable outcome 2]
- [ ] [Measurable outcome 3]

---

## Requirements

### Functional Requirements
1. **[Requirement 1]**
   - Description: [What it does]
   - Validation: [How to verify]

2. **[Requirement 2]**
   - Description: [What it does]
   - Validation: [How to verify]

### Non-Functional Requirements
- **Performance:** [Targets, e.g., <300ms response time]
- **Security:** [Requirements, e.g., auth required]
- **Scalability:** [Capacity needs]
- **Accessibility:** [A11y requirements]

### Out of Scope
- [Explicitly list what's NOT included]
- [Prevents scope creep]

---

## Technical Approach

### Architecture
[High-level technical design]

### Components
1. **[Component 1]**
   - Purpose: [What it does]
   - Location: [File path]
   - Dependencies: [What it uses]

2. **[Component 2]**
   - Purpose: [What it does]
   - Location: [File path]
   - Dependencies: [What it uses]

### Data Model Changes
[Database schema changes, if any]

### API Changes
[New/modified endpoints, if any]

### Integration Points
- [System 1]: [How they interact]
- [System 2]: [How they interact]

---

## Implementation Plan

### Phase 1: Setup
**Goal:** Prepare environment and dependencies

**Steps:**
1. [Specific action with validation]
2. [Specific action with validation]

**Validation:**
```bash
[Command to verify phase 1 complete]
```

### Phase 2: Core Implementation
**Goal:** Build main functionality

**Steps:**
1. [Specific action with validation]
2. [Specific action with validation]

**Validation:**
```bash
[Command to verify phase 2 complete]
```

### Phase 3: Testing & Validation
**Goal:** Ensure quality and correctness

**Steps:**
1. [Specific action with validation]
2. [Specific action with validation]

**Validation:**
```bash
[Command to verify phase 3 complete]
```

---

## Testing Strategy

### Unit Tests
- **Location:** `tests/unit/[feature-name].test.js`
- **Coverage Target:** >80%
- **Key Test Cases:**
  1. [Test case 1]
  2. [Test case 2]

### Integration Tests
- **Location:** `tests/integration/[feature-name].test.js`
- **Key Scenarios:**
  1. [Scenario 1]
  2. [Scenario 2]

### E2E Tests
- **Location:** `tests/e2e/[feature-name].spec.js`
- **User Flows:**
  1. [Flow 1]
  2. [Flow 2]

### Validation Commands
```bash
# Unit tests
npm test -- tests/unit/[feature-name]

# Integration tests
npm test -- tests/integration/[feature-name]

# E2E tests
npm run test:e2e -- tests/e2e/[feature-name]

# All tests
npm test
```

---

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| [Risk 1] | High/Med/Low | High/Med/Low | [How to prevent/handle] |
| [Risk 2] | High/Med/Low | High/Med/Low | [How to prevent/handle] |

---

## Definition of Done

- [ ] All functional requirements implemented
- [ ] All tests passing (unit, integration, e2e)
- [ ] Code review completed
- [ ] Documentation updated
- [ ] Performance targets met
- [ ] Security review passed (if applicable)
- [ ] Deployed to staging
- [ ] User acceptance testing passed

---

## References

- **Related Specs:** [Links to related specs]
- **Documentation:** [Links to relevant docs]
- **Design:** [Links to design files]
- **Issues:** [Link to GitHub issue]

---

## Changelog

- **[Date]:** Initial draft created
- **[Date]:** [Update description]
```

#### Bug Fix Specification Template

```markdown
# [Bug Name] - Fix Specification

**Type:** Bug Fix
**Created:** [Date]
**Status:** Draft
**Priority:** [High/Medium/Low]

---

## Context

### Project Context
- **Project:** [From project-context.md]
- **Component:** [Affected system]
- **Version:** [When bug introduced, if known]

---

## Problem Statement

### Current Behavior
[Describe what's happening]

### Expected Behavior
[Describe what should happen]

### Impact
- **Users Affected:** [Who/how many]
- **Severity:** [Critical/High/Medium/Low]
- **Frequency:** [Always/Often/Rarely]

---

## Reproduction

### Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Environment
- **OS:** [Operating system]
- **Browser/Runtime:** [If applicable]
- **Version:** [App version]

### Test Data
[Any specific data needed to reproduce]

---

## Root Cause Analysis

### Investigation Findings
[What you discovered]

### Root Cause
[The actual problem]

### Why It Happened
[How it got introduced]

---

## Solution

### Proposed Fix
[High-level description of the fix]

### Technical Approach
[Specific changes needed]

### Files to Modify
1. `[file1.js]` - [What changes]
2. `[file2.js]` - [What changes]

---

## Testing Strategy

### Regression Tests
```bash
# Tests to ensure fix works
[command to test the fix]
```

### Validation Steps
1. [Step to verify fix]
2. [Step to verify no new issues]

### Edge Cases to Test
- [Edge case 1]
- [Edge case 2]

---

## Definition of Done

- [ ] Bug no longer reproducible
- [ ] Regression test added
- [ ] All existing tests still pass
- [ ] Root cause documented
- [ ] Deployed to staging
- [ ] Verified in production

---

## References

- **Issue:** [Link to GitHub issue]
- **Related Bugs:** [Similar issues]
- **Logs:** [Error logs, if any]
```

#### Chore Specification Template

```markdown
# [Chore Name] - Specification

**Type:** Chore
**Created:** [Date]
**Status:** Draft

---

## Context

### Motivation
[Why this chore is needed now]

### Impact
[What improves after this chore]

---

## Objective

[Clear description of what needs to be done]

---

## Scope

### Included
- [What's part of this chore]
- [Specific files/systems affected]

### Excluded
- [What's NOT part of this chore]
- [Future work items]

---

## Approach

### Changes Required
1. [Change 1]
2. [Change 2]

### Validation
```bash
[Commands to verify chore complete]
```

---

## Risks

### Breaking Changes
- [Potential issues]
- [Mitigation strategies]

### Rollback Plan
[How to revert if needed]

---

## Definition of Done

- [ ] All changes implemented
- [ ] Tests still passing
- [ ] Documentation updated
- [ ] No breaking changes introduced
- [ ] Team notified of changes

---

## References

- **Related Work:** [Links]
```

### Phase 4: Save Specification

Save the spec to the appropriate location:

```bash
# Feature specs
.claude/specs/feature-[feature-name].md

# Bug fix specs
.claude/specs/bug-[bug-name].md

# Chore specs
.claude/specs/chore-[chore-name].md
```

### Phase 5: Validate Spec is AI-Executable

Verify the spec meets AI-executable criteria:

✅ **Explicit Context:** All necessary context included
✅ **Clear Objective:** One-sentence goal
✅ **Success Criteria:** Measurable, testable outcomes
✅ **Validation Commands:** Executable test commands
✅ **Phase Breakdown:** Step-by-step implementation plan
✅ **No Ambiguity:** Specific, not vague instructions

### Phase 6: Confirm with User

Present the spec to the user:

```markdown
I've created the specification at `.claude/specs/[name].md`

**Summary:**
- Objective: [One-sentence summary]
- Success Criteria: [List top 3]
- Implementation: [Number] phases
- Tests: Unit, Integration, E2E defined

**Ready to proceed with implementation?**

Options:
1. `/implement` - Start implementation now
2. Review/edit spec first
3. `/knowledge_gap_check` - Verify no missing context
```

---

## Example Usage

### Example: User Wants OAuth Feature

**User:** `/spec` for OAuth authentication

**AI:**
```markdown
I'll create an OAuth authentication specification.

First, let me check for knowledge gaps:
- ✅ Project context loaded (Node.js + Express)
- ❓ OAuth provider preference (Google? GitHub? Auth0?)
- ❓ Token strategy (JWT? Sessions?)
- ❓ Existing auth system to integrate with?

Before I create the spec, please clarify:
1. Which OAuth provider?
2. What should happen after successful auth?
3. Any existing authentication I should integrate with?
```

**User:** "Google OAuth, redirect to dashboard, no existing auth"

**AI:**
```markdown
Perfect! Creating spec with:
- Provider: Google OAuth 2.0
- Success redirect: /dashboard
- Fresh implementation (no integration needed)

Let me check if I need Google OAuth docs...
[Checks for MCP server with Google docs]

Creating specification at `.claude/specs/feature-google-oauth.md`...

[Generates full spec using template]

**Spec Created!**

Summary:
- Objective: Implement Google OAuth 2.0 authentication
- Success Criteria:
  ✓ Users can sign in with Google
  ✓ Token stored securely
  ✓ Redirects to /dashboard on success
- Implementation: 3 phases (setup, core auth, testing)
- Tests: 8 test cases defined

Ready to `/implement`?
```

---

## Integration with Other Commands

### Before This Command:
- `/knowledge_gap_check` - Ensure you have context (optional, this command does it)
- `/prime` - Understand the codebase

### After This Command:
- `/implement` - Execute the spec
- `/feature` or `/bug` or `/chore` - If using workflow commands

### Outputs Used By:
- All implementation commands reference the spec
- Test commands validate against spec criteria
- Review commands check spec compliance

---

## Success Criteria

A good spec:

✅ Can be executed by AI without clarification
✅ Has measurable success criteria
✅ Includes validation commands
✅ Breaks work into phases
✅ Identifies risks and mitigations
✅ Takes 5-15 minutes to create

❌ Vague objectives like "make it better"
❌ Missing validation commands
❌ No success criteria
❌ Assumes implicit knowledge

---

## Tips for Better Specs

1. **Be specific:** "Reduce login time to <300ms" not "make it faster"
2. **Include examples:** Show expected input/output
3. **Test commands:** Every requirement should have a validation command
4. **Out of scope:** Explicitly list what's NOT included
5. **Reference existing work:** Link to similar features/fixes

---

## Related Resources

- **TAC Principles:** `.claude/TAC-PRINCIPLES.md` - Principle 1
- **Spec Template:** `templates/spec-template.md` - Base template
- **Project Context:** `.claude/project-context.md` - Project info
- **Validation Checklists:** `.claude/validation-checklists/` - Quality gates

---

**Remember:** Time spent on a good spec saves hours of implementation iteration.
