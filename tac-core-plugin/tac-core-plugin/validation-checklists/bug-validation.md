# Bug Fix Validation Checklist

**Purpose:** Systematic validation checklist for bug fixes before marking complete.

**TAC Principle:** Closed-Loop Validation (Principle 4)

---

## When to Use

- After implementing a bug fix
- Before creating pull request
- As part of `/review` command
- Before closing bug issue

---

## Validation Levels

Complete all applicable levels:

### Level 1: Bug Resolution ✅

- [ ] **Bug no longer reproducible**
  - Follow reproduction steps from spec
  - Bug behavior does not occur
  - Expected behavior now happens

- [ ] **Fix addresses root cause** (not just symptoms)
  - Review root cause analysis from spec
  - Fix targets the actual problem
  - Not a workaround or band-aid

- [ ] **All affected scenarios fixed**
  - Check all reported instances
  - Verify related edge cases
  - No partial fixes

- [ ] **Validation command passes**
  ```bash
  # Run the specific test/command from spec
  [validation command from spec]
  ```

---

### Level 2: Regression Prevention ✅

- [ ] **Regression test added**
  - Test specifically for this bug
  - Test would fail without the fix
  - Test will catch if bug returns

- [ ] **Test location documented**
  ```bash
  # Location should be in spec
  tests/unit/bugfix-[bug-id].test.js
  # or similar
  ```

- [ ] **Regression test passes**
  ```bash
  npm test -- tests/unit/bugfix-[bug-id]
  # or: pytest tests/test_bugfix_[bug-id].py
  ```

- [ ] **Edge cases covered by tests**
  - Boundary conditions tested
  - Null/undefined cases tested
  - Error conditions tested

---

### Level 3: No New Bugs Introduced ✅

- [ ] **All existing tests still pass**
  ```bash
  npm test  # Full test suite
  ```

- [ ] **No new linting errors**
  ```bash
  npm run lint
  ```

- [ ] **No new type errors** (if applicable)
  ```bash
  npm run type-check
  ```

- [ ] **Code still builds**
  ```bash
  npm run build
  ```

- [ ] **No new console errors**
  - Check browser console (for frontend)
  - Check application logs (for backend)
  - No unintended side effects

---

### Level 4: Related Functionality ✅

- [ ] **Related features still work**
  - Test features that use same code
  - Test features with similar logic
  - No unexpected breakage

- [ ] **Integration points intact**
  - APIs still work correctly
  - Database interactions correct
  - External service calls work

- [ ] **Data integrity maintained**
  - No corrupted data
  - No lost data
  - Migrations safe (if schema changed)

---

### Level 5: Code Quality ✅

- [ ] **Fix is minimal and focused**
  - Only changes necessary code
  - No unrelated refactoring
  - No scope creep

- [ ] **Code follows project conventions**
  - Check `CLAUDE.md "Project-Specific Context" section`
  - Naming conventions followed
  - Style guide adhered to

- [ ] **No TODO comments left** (unless documented)
  ```bash
  grep -r "TODO" src/[affected-files]
  ```

- [ ] **No debug code left**
  ```bash
  grep -r "console.log\|debugger\|print(" src/[affected-files]
  ```

---

### Level 6: Security ✅

- [ ] **Fix doesn't introduce security issues**
  - No new vulnerabilities
  - Input still validated
  - Auth/authz still enforced

- [ ] **Security audit passes**
  ```bash
  npm audit  # Should show no new vulnerabilities
  ```

- [ ] **Fix doesn't expose sensitive data**
  - No secrets in logs
  - No PII in error messages
  - No information leakage

---

### Level 7: Performance ✅

- [ ] **Fix doesn't degrade performance**
  - Response times similar or better
  - Resource usage not increased
  - No new bottlenecks introduced

- [ ] **Performance tests pass** (if applicable)
  ```bash
  npm run test:perf
  ```

- [ ] **No memory leaks introduced**
  - Memory usage stable
  - Resources properly cleaned up
  - Event listeners removed

---

### Level 8: Documentation ✅

- [ ] **Root cause documented**
  - In spec: why it happened
  - In commit message: what was wrong
  - In code comments: why this fix works

- [ ] **Fix approach documented**
  - In spec: technical approach
  - In code: complex logic explained
  - In PR: summary of changes

- [ ] **Known limitations documented** (if any)
  - What the fix doesn't cover
  - Future improvements needed
  - Workarounds still required

- [ ] **CHANGELOG updated**
  - Bug fix noted
  - Version incremented (patch)
  - Impact described

---

### Level 9: Deployment Readiness ✅

- [ ] **Fix tested in staging**
  - Works in staging environment
  - No environment-specific issues
  - Data migration tested (if applicable)

- [ ] **Rollback plan exists**
  - How to revert if needed
  - Feature flag to disable (if applicable)
  - Database rollback script (if schema changed)

- [ ] **Monitoring updated**
  - Alerts configured for recurrence
  - Metrics track fix effectiveness
  - Logging improved for diagnosis

- [ ] **Communication plan ready**
  - Users notified (if user-facing)
  - Team informed
  - Stakeholders updated

---

## Bug-Specific Validations

### For UI Bugs

- [ ] **Visual regression test added** (if applicable)
- [ ] **Tested in all supported browsers**
- [ ] **Tested at different screen sizes**
- [ ] **Accessibility not broken**

### For API Bugs

- [ ] **API contract still valid**
- [ ] **Response format unchanged** (or versioned)
- [ ] **Status codes correct**
- [ ] **Error responses appropriate**

### For Data Bugs

- [ ] **Data migration script tested**
- [ ] **Corrupt data cleaned up**
- [ ] **Future data validated**
- [ ] **Backup verified before deployment**

### For Performance Bugs

- [ ] **Performance improvement measured**
- [ ] **Benchmarks show improvement**
- [ ] **Load testing passes**
- [ ] **Resource limits not exceeded**

### For Security Bugs

- [ ] **Vulnerability patched**
- [ ] **Exploit no longer possible**
- [ ] **Similar code audited**
- [ ] **Security team notified**

---

## Automated Validation

Run these commands to automate validation:

```bash
# All tests (must pass)
npm test

# Linting (must pass)
npm run lint

# Build (must succeed)
npm run build

# Security audit (no new issues)
npm audit

# Type checking (if applicable)
npm run type-check
```

Expected: All commands should succeed.

---

## Manual Validation

Some items require human verification:

### 1. Reproduce Bug (Before Fix)
- [ ] Can reproduce using original steps
- [ ] Bug behavior matches description
- [ ] Impact matches severity

### 2. Verify Fix (After Fix)
- [ ] Cannot reproduce bug anymore
- [ ] Expected behavior now occurs
- [ ] No workarounds needed

### 3. Spot Check Related Areas
- [ ] Similar code works correctly
- [ ] Integration points functional
- [ ] User workflows complete

---

## Completion Criteria

Bug fix is DONE when:

✅ Bug is no longer reproducible
✅ Regression test added and passing
✅ All existing tests still pass
✅ Root cause documented
✅ No new issues introduced
✅ Ready for production deployment

---

## Integration with Commands

This checklist is used by:

- `/resolve_failed_test` - Auto-fixes until this checklist passes
- `/review` - Validates against this checklist
- `/test` - Executes automated portions
- `/pull_request` - References in PR description

---

## Common Pitfalls

### ❌ Pitfall 1: Fixing Symptoms Not Root Cause
**Problem:** Bug seems fixed but returns later

**Prevention:**
- Always do root cause analysis
- Test edge cases thoroughly
- Add comprehensive regression tests

### ❌ Pitfall 2: Introducing New Bugs
**Problem:** Fix breaks something else

**Prevention:**
- Run full test suite
- Test related functionality
- Review code changes carefully

### ❌ Pitfall 3: Incomplete Fix
**Problem:** Bug partially fixed but edge cases remain

**Prevention:**
- Test all reproduction scenarios
- Check boundary conditions
- Verify fix in all environments

### ❌ Pitfall 4: Missing Regression Test
**Problem:** Bug returns in future without detection

**Prevention:**
- Always add regression test
- Test should fail without fix
- Test should pass with fix

---

## Quick Reference

**Before creating PR:**
```bash
# Verify bug fixed
[reproduction steps from spec]

# Run tests
npm test

# Check code quality
npm run lint && npm run build
```

**Full validation:**
```bash
# All checks
npm run lint && \
npm run type-check && \
npm test && \
npm audit && \
npm run build

# Manual verification
[test reproduction steps]
[test edge cases]
[test related features]
```

---

## Customization

Adapt this checklist for your project:

1. **Add project-specific validations**
   - Custom performance checks
   - Domain-specific edge cases
   - Team-specific quality gates

2. **Add bug type sections**
   - Database bugs
   - Integration bugs
   - Configuration bugs

3. **Update automation commands**
   - Match your test framework
   - Match your tooling
   - Match your CI/CD

Save customizations in `.claude/validation-checklists/bug-validation-custom.md`

---

**Remember:** A good bug fix prevents the bug from ever happening again, not just for now.
