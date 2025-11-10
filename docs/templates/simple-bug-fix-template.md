# Simple Bug Fix Template

## Bug Information

**Issue Number:** #[issue-number]

**Bug Title:** [Brief description of the bug]

**Severity:** [Critical / High / Medium / Low]

**Reported By:** [Reporter name/username]

**Date Reported:** [YYYY-MM-DD]

---

## Stage 1: Planning

### Problem Description

**What is broken?**
[Describe what's not working correctly]

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happens]

**Impact:**
[Who is affected and how? E.g., "All users cannot reset passwords"]

### Reproduction Steps

1. [First step to reproduce]
2. [Second step]
3. [Third step]
4. [Observe the bug]

**Frequency:** [Always / Sometimes / Rarely]

**Environment:**
- Browser/Platform: [e.g., Chrome 120, iOS 17]
- Version: [App version if applicable]
- Environment: [Production / Staging / Development]

### Root Cause Analysis

**Root Cause:**
[What is the underlying cause of the bug? Not just symptoms.]

**Why it happened:**
[Explanation of how this bug was introduced]

**Affected Code:**
- File: [path/to/file.ts]
- Function: [functionName()]
- Lines: [42-58]

### Solution Approach

**Fix Strategy:**
[Describe how you'll fix the root cause]

**Files to Modify:**
- [ ] `[path/to/file1.ts]` - [what changes]
- [ ] `[path/to/file2.ts]` - [what changes]

**Testing Strategy:**
- [ ] Regression test to prevent recurrence
- [ ] Manual reproduction test
- [ ] Related functionality test

### Acceptance Criteria

- [ ] Bug is no longer reproducible using reproduction steps
- [ ] Expected behavior now occurs in all scenarios
- [ ] Regression test fails without fix, passes with fix
- [ ] No new bugs introduced
- [ ] Related functionality still works

### Out of Scope

[List what this fix does NOT address]
- [Related but different issue]
- [Future improvements]

---

## Stage 2: Implementation

### Changes Made

**File: [path/to/file.ts]**
```typescript
// Before (buggy code):
[paste original code]

// After (fixed code):
[paste fixed code]
```

**Explanation:**
[Why this fix works]

### Regression Test Added

**File: [path/to/test_file.test.ts]**
```typescript
describe('[Bug description]', () => {
  it('should [expected behavior]', () => {
    // Test that would fail without fix
    [test code]
  });
});
```

**Test validates:**
- [ ] Test fails without the fix
- [ ] Test passes with the fix
- [ ] Test covers the bug scenario

### Other Code Changes

**Modified Files:**
- `[file1]` - [reason for change]
- `[file2]` - [reason for change]

**New Files:**
- `[test file]` - Regression test

---

## Stage 3: Testing

### Regression Test Results

```bash
# Run regression test
[command to run test]

# Expected output:
[paste passing test output]
```

**Status:** ✅ Passing / ❌ Failing

### Manual Reproduction Test

**Attempt to reproduce bug:**
1. [Follow reproduction steps]
2. [Verify expected behavior occurs]
3. [Confirm bug no longer happens]

**Result:** ✅ Bug fixed / ❌ Bug still occurs

### Full Test Suite

```bash
# Backend tests
cd app/server && uv run pytest -v

# Frontend type checking
cd app/client && bun tsc --noEmit

# Frontend build
cd app/client && bun run build
```

**Results:**
- Unit tests: [X passed, Y total]
- Type checking: [✅ No errors / ❌ Errors found]
- Build: [✅ Success / ❌ Failed]

### Related Functionality Testing

**Tested:**
- [ ] [Related feature 1] - Still works
- [ ] [Related feature 2] - Still works
- [ ] [Integration point] - Still works

**Edge Cases Tested:**
- [ ] [Edge case 1]
- [ ] [Edge case 2]
- [ ] [Error condition]

---

## Stage 4: Review

### Bug Validation Checklist

**Level 1: Bug Resolution**
- [ ] Bug no longer reproducible
- [ ] Fix addresses root cause (not symptoms)
- [ ] All affected scenarios fixed
- [ ] Validation command passes

**Level 2: Regression Prevention**
- [ ] Regression test added
- [ ] Regression test passes
- [ ] Edge cases covered by tests

**Level 3: No New Bugs**
- [ ] All existing tests still pass
- [ ] No new linting errors
- [ ] No new type errors
- [ ] Code still builds

**Level 4: Code Quality**
- [ ] Fix is minimal and focused
- [ ] Code follows project conventions
- [ ] No TODO comments left
- [ ] No debug code left

**Level 5: Documentation**
- [ ] Root cause documented (in this template)
- [ ] Fix approach documented (in code comments if needed)
- [ ] CHANGELOG updated

### Self-Review Notes

**Code Review:**
[Notes from reviewing your own changes]

**Concerns:**
[Any concerns or trade-offs made]

**Follow-up:**
[Any follow-up work needed (create separate issues)]

---

## Stage 5: Deployment

### Commit Message

```
fix: [short description of fix]

[Detailed description of what was wrong and how it was fixed.
Include root cause and fix approach.]

Fixes #[issue-number]
```

**Example:**
```
fix: resolve email service integration for password reset

Updated email service API from v1 to v2 endpoint and added
proper error handling with logging. The root cause was the
deprecated v1 endpoint returning 500 errors.

Fixes #123
```

### Pull Request Description

**Title:** `fix: [description] (#[issue-number])`

**Description:**
```markdown
## Summary
Fixes bug where [brief description].

## Root Cause
[What caused the bug]

## Changes
- Updated [file] to [change]
- Added regression test in [test file]
- Fixed [specific issue]

## Testing
- [x] Regression test added and passing
- [x] Bug no longer reproducible
- [x] All existing tests pass
- [x] Manual testing complete

## Validation Results
```bash
cd app/server && uv run pytest -v  # ✅ All passed
cd app/client && bun tsc --noEmit  # ✅ No errors
cd app/client && bun run build     # ✅ Success
```

Fixes #[issue-number]
```

### Post-Deployment Verification

**Monitor for:**
- [ ] Error logs for related issues
- [ ] User reports of same/similar bug
- [ ] Performance impact

**Verification (after deploy):**
- [ ] Test in production (if safe)
- [ ] Check monitoring dashboards
- [ ] Close GitHub issue

---

## Notes

### Lessons Learned

[What did you learn from this bug? How can we prevent similar bugs?]

### Future Improvements

[Related improvements that are out of scope for this fix]

### Related Issues

- Related bug: #[number]
- Follow-up work: #[number]

---

## Quick Checklist

Before marking bug fix complete:

- [ ] Bug no longer reproducible
- [ ] Regression test added and passing
- [ ] Root cause documented
- [ ] All tests passing
- [ ] Code reviewed
- [ ] CHANGELOG updated
- [ ] PR created and approved
- [ ] Deployed and verified

---

**Remember:** Fix the root cause, not the symptoms. A good bug fix prevents the bug from ever happening again.
