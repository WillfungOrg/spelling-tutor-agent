# Simple Chore Template

## Chore Information

**Issue Number:** #[issue-number]

**Chore Title:** [Brief description of the maintenance task]

**Type:** [Refactoring / Dependency Update / Cleanup / Infrastructure / Performance / Documentation]

**Priority:** [High / Medium / Low]

**Requested By:** [Requester name/username]

**Date Requested:** [YYYY-MM-DD]

---

## Stage 1: Planning

### Objective

**What needs to be done?**
[Clear description of the maintenance task]

**Why is this important?**
[Rationale: tech debt reduction, security, performance, maintainability, etc.]

### Rationale

**Current State:**
[What's the situation now?]

**Problem/Opportunity:**
[What issue does this address or what improvement does it provide?]

**Desired State:**
[What will be better after this chore?]

**Impact if NOT done:**
[What happens if we don't do this?]

### Scope

**Included in this chore:**
- [ ] [Specific task 1]
- [ ] [Specific task 2]
- [ ] [Specific task 3]

**Explicitly NOT included:**
- [Future improvement]
- [Related but separate task]
- [Out of scope work]

**Boundaries:**
- Time estimate: [1-4 hours]
- Files affected: [1-5 files]
- Risk level: [Low / Medium - behavior should not change]

### Success Criteria

**Chore is complete when:**
- [ ] [Specific measurable criterion 1]
- [ ] [Specific measurable criterion 2]
- [ ] All existing tests still pass
- [ ] No functionality broken
- [ ] Behavior unchanged (for refactoring/cleanup)

**Example (Dependency Update):**
- [ ] React updated from 18.2.0 to 18.3.0
- [ ] No security vulnerabilities in audit
- [ ] All tests pass
- [ ] Application starts without errors

**Example (Refactoring):**
- [ ] Duplicated date formatting code extracted to utility
- [ ] All 3 usage sites updated to use utility
- [ ] Tests pass (proving behavior unchanged)
- [ ] Code complexity reduced

### Affected Files

**Files to Modify:**
- [ ] `[path/to/file1]` - [what changes]
- [ ] `[path/to/file2]` - [what changes]

**Files to Create (if any):**
- [ ] `[path/to/new/utility.ts]` - [purpose]

**Files to Delete (if cleanup):**
- [ ] `[path/to/deprecated/file.ts]` - [reason for deletion]

### Validation Strategy

**How to verify success:**

**Automated:**
```bash
cd app/server && uv run pytest -v
cd app/client && bun tsc --noEmit
cd app/client && bun run build
```

**Manual (for critical paths):**
1. [Test critical functionality]
2. [Verify behavior unchanged]

**Specific to chore type:**
- Dependency update: `npm audit` shows no new vulnerabilities
- Refactoring: All tests pass, behavior identical
- Cleanup: Removed code not referenced anywhere
- Performance: Benchmarks show improvement

---

## Stage 2: Implementation

### Changes Made

**Type-Specific Implementation:**

#### For Dependency Updates:
**Package:** [package-name]
**From:** [old-version]
**To:** [new-version]

**Command used:**
```bash
[e.g., bun update package-name@version]
```

**Breaking changes (if any):**
[List breaking changes from CHANGELOG and how you addressed them]

**Migration steps taken:**
- [Step 1]
- [Step 2]

#### For Refactoring:
**Before:**
```typescript
// Duplicated code in file1.ts
[paste original code]
```

```typescript
// Duplicated code in file2.ts
[paste original code]
```

**After:**
```typescript
// New utility: utils/formatDate.ts
[paste extracted utility]
```

```typescript
// Updated file1.ts
[paste refactored code using utility]
```

**Complexity Improvement:**
- Reduced duplication: [X lines → Y lines]
- Function count: [before → after]
- Cyclomatic complexity: [before → after]

#### For Cleanup:
**Removed:**
- [File/code removed]
- [Reason for removal]

**Impact:**
- Dead code removed: [X lines]
- Unused dependencies removed: [list]

#### For Infrastructure:
**Configuration Changes:**
- [File/setting changed]
- [Reason for change]

**Environment Variables:**
- Added: [VAR_NAME] - [purpose]
- Modified: [VAR_NAME] - [change]
- Removed: [VAR_NAME] - [reason]

### Behavior Verification

**Critical assertion:**
> Behavior is unchanged. All functionality works exactly as before.

**How verified:**
- [ ] All existing tests pass
- [ ] Manual testing of affected features
- [ ] No user-facing changes

**If behavior changed (should be rare):**
[Explain why and justify the change]

---

## Stage 3: Testing

### Test Results

**Full Test Suite:**
```bash
cd app/server && uv run pytest -v
cd app/client && bun tsc --noEmit
cd app/client && bun run build
```

**Results:**
- Unit tests: [X passed, Y total] [✅ All passing / ❌ Failures]
- Type checking: [✅ No errors / ❌ Errors found]
- Build: [✅ Success / ❌ Failed]

**Test Coverage:**
```bash
cd app/server && uv run pytest --cov=app
```

**Results:**
- Coverage before: [X%]
- Coverage after: [Y%]
- Change: [Maintained / Improved / Decreased with justification]

### Type-Specific Validation

#### For Dependency Updates:
**Security Audit:**
```bash
npm audit
# or: pip-audit
```
**Results:**
- Vulnerabilities before: [number]
- Vulnerabilities after: [number]
- [✅ No new vulnerabilities / ❌ New issues found]

**Compatibility Check:**
- [ ] App starts without errors
- [ ] No console warnings
- [ ] Critical features tested manually

#### For Refactoring:
**Behavior Verification:**
- [ ] Unit tests prove behavior unchanged
- [ ] Integration tests pass
- [ ] Manual testing confirms identical behavior

**Performance:**
- [ ] No performance regression
- [ ] Benchmarks show no degradation

#### For Cleanup:
**Dead Code Verification:**
```bash
# Search for references to removed code
grep -r "[removed-function]" src/
# Should return no results
```

**Unused Dependencies:**
```bash
# Verify dependencies removed from package.json
# Build and tests still pass
```

### Manual Testing

**Critical Paths Tested:**
1. [Test scenario 1] - ✅ Pass / ❌ Fail
2. [Test scenario 2] - ✅ Pass / ❌ Fail
3. [Test scenario 3] - ✅ Pass / ❌ Fail

**Smoke Testing:**
- [ ] Application starts
- [ ] Core functionality works
- [ ] No console errors
- [ ] No performance degradation

---

## Stage 4: Review

### Chore Validation Checklist

**Level 1: Objective Achieved**
- [ ] Chore objective completed
- [ ] Success criteria met
- [ ] Out of scope items NOT done

**Level 2: No Functionality Broken**
- [ ] All existing tests pass
- [ ] Application still runs
- [ ] No breaking changes (or properly handled)
- [ ] Manual smoke testing passed

**Level 3: Code Quality**
- [ ] Linting passes
- [ ] Type checking passes
- [ ] Code builds successfully
- [ ] No dead code introduced
- [ ] Code follows project conventions

**Level 4: Type-Specific Checks**

_For Dependency Updates:_
- [ ] Dependencies updated successfully
- [ ] No security vulnerabilities
- [ ] Breaking changes handled
- [ ] Lockfile updated

_For Refactoring:_
- [ ] Behavior unchanged
- [ ] Code complexity reduced
- [ ] Performance not degraded
- [ ] Tests still relevant

_For Infrastructure:_
- [ ] Works in all environments
- [ ] Configuration updated
- [ ] Deployment tested

_For Cleanup:_
- [ ] Target debt removed
- [ ] No new debt introduced
- [ ] Documentation updated

**Level 5: Documentation**
- [ ] Changes documented in code (if needed)
- [ ] README updated (if relevant)
- [ ] CHANGELOG updated
- [ ] Team notified (if affects workflow)

### Self-Review

**Quality Assessment:**
[Review the changes for maintainability and clarity]

**Risk Assessment:**
[What could go wrong? How likely? Mitigation?]

**Impact:**
[What's the positive impact of this chore?]

---

## Stage 5: Deployment

### Commit Message

```
chore: [short description of chore]

[Detailed description of what changed and why.
Include any important context or decisions made.]

[Related-to / Updates / Closes] #[issue-number]
```

**Examples:**

_Dependency Update:_
```
chore: update React to 18.3.0 for security patch

Updated React from 18.2.0 to 18.3.0 to address CVE-2024-XXXX.
No breaking changes. All tests passing.

Closes #789
```

_Refactoring:_
```
chore: extract date formatting logic to shared utility

Extracted duplicated date formatting code from 3 components
into shared utils/formatDate.ts utility. Reduces duplication
and improves maintainability. Behavior unchanged.

Closes #123
```

_Cleanup:_
```
chore: remove deprecated user profile API endpoints

Removed v1 user profile endpoints that were replaced by v2
in release 3.0. No clients still using v1 endpoints based on
analytics. Reduces maintenance burden.

Closes #456
```

### Pull Request Description

**Title:** `chore: [description] (#[issue-number])`

**Description:**
```markdown
## Summary
[Brief description of the chore and its value]

## Objective
[What this chore accomplishes]

## Changes
- [Specific change 1]
- [Specific change 2]
- [Specific change 3]

## Impact
- Behavior: [Unchanged / Changed with justification]
- Performance: [Same / Improved]
- Security: [Improved / Same]
- Maintainability: [Improved]

## Testing
- [x] All existing tests pass
- [x] No new errors or warnings
- [x] Manual smoke testing complete
- [x] Behavior verified unchanged (for refactoring)

## Validation Results
```bash
cd app/server && uv run pytest -v  # ✅ All passed
cd app/client && bun tsc --noEmit  # ✅ No errors
cd app/client && bun run build     # ✅ Success
npm audit                          # ✅ No vulnerabilities (if applicable)
```

[Related-to / Updates / Closes] #[issue-number]
```

### Deployment Considerations

**Risk Level:** [Low / Medium]

**Rollback Plan:**
[How to revert if needed]

**Monitoring:**
- [ ] Watch error logs for issues
- [ ] Monitor performance metrics
- [ ] Check for user reports

**Post-Deployment:**
- [ ] Verify app works in production
- [ ] Check monitoring dashboards
- [ ] Cleanup (remove old branches/worktrees)

### Team Communication

**Notify team if:**
- Workflow changes
- Configuration changes
- Environment variable changes
- Infrastructure changes

**Communication:**
[Draft message to team, if applicable]

---

## Notes

### Technical Notes

[Any technical details, decisions made, or context for future reference]

### Lessons Learned

[What did you learn? How can we improve similar chores in the future?]

### Future Work

[Related chores or improvements to consider later]

**Potential future chores:**
- [Future chore 1]
- [Future chore 2]

### Dependencies

**New Dependencies Added:**
[Should be rare for chores, but list if applicable]

**Dependencies Removed:**
[List any dependencies that are no longer needed]

---

## Quick Checklist

Before marking chore complete:

- [ ] Objective achieved
- [ ] All tests passing
- [ ] No functionality broken
- [ ] Code quality maintained
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] Team notified (if needed)
- [ ] PR created and approved
- [ ] Changes deployed and verified

---

## Chore Type Quick References

### Dependency Update Checklist
- [ ] Review package CHANGELOG
- [ ] Check for breaking changes
- [ ] Update code for new APIs
- [ ] Run security audit
- [ ] Test in all environments

### Refactoring Checklist
- [ ] All tests pass (proves behavior unchanged)
- [ ] Code complexity reduced
- [ ] No performance degradation
- [ ] Documentation reflects new structure

### Cleanup Checklist
- [ ] Target debt removed
- [ ] No references to removed code
- [ ] Unused dependencies removed
- [ ] Documentation cleaned up

### Infrastructure Checklist
- [ ] Works in dev, staging, production
- [ ] Environment variables documented
- [ ] Configuration migration tested
- [ ] Rollback procedure defined

### Performance Optimization Checklist
- [ ] Baseline metrics captured
- [ ] Improvement measured and quantified
- [ ] No correctness trade-offs
- [ ] Load testing passed

---

**Remember:** Chores improve code quality without changing behavior. If behavior changes, it's not a chore—it's a feature or bug fix.
