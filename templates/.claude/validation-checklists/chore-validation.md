# Chore Validation Checklist

**Purpose:** Systematic validation checklist for maintenance tasks before marking complete.

**TAC Principle:** Closed-Loop Validation (Principle 4)

---

## When to Use

- After completing refactoring
- After dependency updates
- After infrastructure changes
- Before marking chore as done

---

## Validation Levels

Complete all applicable levels:

### Level 1: Objective Achieved ✅

- [ ] **Chore objective completed**
  - Review objective from spec
  - All items in scope completed
  - Nothing from "Included" missing

- [ ] **Success criteria met**
  - Check spec success criteria
  - All checkboxes can be marked
  - Measurable outcomes achieved

- [ ] **Out of scope items NOT done**
  - Verify spec's "Excluded" section
  - No scope creep occurred
  - Future work properly deferred

---

### Level 2: No Functionality Broken ✅

- [ ] **All existing tests pass**
  ```bash
  npm test  # Full test suite must pass
  ```

- [ ] **Application still runs**
  ```bash
  npm start  # or equivalent
  # Verify app starts without errors
  ```

- [ ] **No breaking changes introduced**
  - Public APIs unchanged (or versioned)
  - Configuration backward compatible
  - Existing features still work

- [ ] **Manual smoke testing passed**
  - Test critical user workflows
  - Verify core functionality works
  - Check integration points

---

### Level 3: Code Quality ✅

- [ ] **Linting passes**
  ```bash
  npm run lint
  ```

- [ ] **Type checking passes** (if applicable)
  ```bash
  npm run type-check
  ```

- [ ] **Code builds successfully**
  ```bash
  npm run build
  ```

- [ ] **No dead code introduced**
  - Unused imports removed
  - Unreachable code removed
  - Commented-out code removed

- [ ] **Code follows project conventions**
  - Check `.claude/project-context.md`
  - Naming conventions followed
  - File organization matches structure

---

### Level 4: Chore-Specific Validations ✅

#### For Dependency Updates

- [ ] **Dependencies updated successfully**
  ```bash
  npm install  # or: pip install, bundle install, etc.
  ```

- [ ] **No security vulnerabilities**
  ```bash
  npm audit
  ```

- [ ] **Breaking changes handled**
  - Migration guides reviewed
  - Code updated for new APIs
  - Deprecation warnings addressed

- [ ] **Lockfile updated**
  ```bash
  git status  # Should show package-lock.json updated
  ```

- [ ] **Changelog reviewed**
  - Check CHANGELOG of updated packages
  - Note breaking changes
  - Document significant updates

#### For Refactoring

- [ ] **Behavior unchanged**
  - All tests pass (regression proof)
  - Manual testing shows same behavior
  - No unintended side effects

- [ ] **Code complexity reduced**
  - Cyclomatic complexity improved
  - Duplicate code eliminated
  - Clearer logic flow

- [ ] **Performance not degraded**
  - Response times same or better
  - Resource usage not increased
  - Benchmarks show no regression

- [ ] **Tests still relevant**
  - Update tests for refactored code
  - Remove obsolete tests
  - Add tests for new patterns

#### For Infrastructure Changes

- [ ] **Infrastructure works in all environments**
  - Local development works
  - Staging environment works
  - Production environment ready

- [ ] **Configuration updated**
  - Environment variables documented
  - Config files updated
  - Secrets migrated (if needed)

- [ ] **Deployment process tested**
  - Deploy to staging successful
  - Rollback procedure tested
  - Zero-downtime verified

- [ ] **Monitoring updated**
  - New metrics tracked
  - Alerts configured
  - Dashboards updated

#### For Performance Optimization

- [ ] **Performance improvement measured**
  - Baseline metrics captured
  - Post-optimization metrics show improvement
  - Improvement quantified (e.g., "30% faster")

- [ ] **Benchmarks pass**
  ```bash
  npm run benchmark
  ```

- [ ] **No accuracy/correctness trade-offs**
  - Results still correct
  - Edge cases still handled
  - No data loss

- [ ] **Load testing passed**
  - System handles expected load
  - Resource limits respected
  - Graceful degradation under stress

#### For Cleanup/Tech Debt

- [ ] **Target debt removed**
  - Identified code removed/improved
  - TODO comments resolved
  - Workarounds replaced with proper solutions

- [ ] **No new debt introduced**
  - No new TODO comments
  - No new hacks/workarounds
  - Clean implementation

- [ ] **Documentation updated**
  - Outdated docs removed
  - Architecture docs reflect reality
  - Comments updated

---

### Level 5: Testing ✅

- [ ] **Appropriate tests added**
  - New code has test coverage
  - Changed code has updated tests
  - Edge cases covered

- [ ] **Test coverage maintained or improved**
  ```bash
  npm run test:coverage
  # Coverage % should not decrease
  ```

- [ ] **Integration tests pass**
  ```bash
  npm run test:integration
  ```

- [ ] **E2E tests pass** (if applicable)
  ```bash
  npm run test:e2e
  ```

---

### Level 6: Documentation ✅

- [ ] **Changes documented in code**
  - Complex logic commented
  - Non-obvious decisions explained
  - API changes documented

- [ ] **README updated** (if relevant)
  - Installation steps current
  - Configuration options updated
  - Examples still valid

- [ ] **CHANGELOG updated**
  - Chore listed under appropriate version
  - Impact described
  - Breaking changes noted

- [ ] **Migration guide created** (if breaking changes)
  - Step-by-step migration steps
  - Before/after examples
  - Common pitfalls noted

- [ ] **Team notified** (if affects workflow)
  - Slack/email notification sent
  - Changes explained
  - Action items communicated

---

### Level 7: Cleanup ✅

- [ ] **Temporary files removed**
  ```bash
  git status  # Should show no unwanted files
  ```

- [ ] **Debug code removed**
  ```bash
  grep -r "console.log\|debugger\|print(" src/
  # Should return no debug statements
  ```

- [ ] **Old code removed** (if refactoring)
  - No dead code left behind
  - No commented-out code blocks
  - Clean git diff

- [ ] **Dependencies cleaned up**
  ```bash
  npm prune  # Remove unused packages
  # or: pip-autoremove, etc.
  ```

---

### Level 8: Rollback Safety ✅

- [ ] **Changes are reversible**
  - Git commit is atomic
  - Database migrations reversible
  - Configuration changes documented

- [ ] **Rollback procedure documented**
  - Steps to revert defined
  - Tested in staging
  - Team aware of procedure

- [ ] **Feature flags used** (if gradual rollout)
  - Can disable changes if needed
  - Flag cleanup plan exists
  - Default state documented

---

## Chore Type Quick Checks

### Dependency Update
```bash
npm install && npm audit && npm test && npm run build
```

### Refactoring
```bash
npm test && npm run lint && npm run type-check
# Then manual smoke testing
```

### Infrastructure
```bash
# Deploy to staging
# Run smoke tests
# Check monitoring
# Verify rollback works
```

### Performance Optimization
```bash
npm run benchmark  # Compare before/after
npm test  # Ensure behavior unchanged
npm run test:e2e  # Verify user experience
```

### Cleanup/Tech Debt
```bash
npm test  # Everything still works
git diff  # Review changes carefully
npm run lint  # Code quality maintained
```

---

## Automated Validation

Run these commands to automate validation:

```bash
# Full test suite
npm test

# Code quality
npm run lint

# Type checking
npm run type-check

# Build
npm run build

# Security
npm audit

# Coverage
npm run test:coverage
```

Expected: All commands should succeed.

---

## Manual Validation

Some items require human judgment:

### 1. Smoke Testing
- [ ] Start application locally
- [ ] Test critical paths manually
- [ ] Verify expected behavior
- [ ] Check for console errors

### 2. Code Review
- [ ] Changes make sense
- [ ] No over-engineering
- [ ] Maintainability improved
- [ ] Technical debt reduced

### 3. Impact Assessment
- [ ] Team workflow not disrupted
- [ ] Deployment process still works
- [ ] Monitoring still effective
- [ ] Documentation accurate

---

## Completion Criteria

Chore is DONE when:

✅ Objective from spec achieved
✅ All tests passing
✅ No functionality broken
✅ Documentation updated
✅ Team notified (if needed)
✅ Ready for deployment

---

## Integration with Commands

This checklist is used by:

- `/review` - Validates against this checklist
- `/test` - Executes automated portions
- `/pull_request` - References in PR description
- `/chore` - Creates spec that defines validation

---

## Common Pitfalls

### ❌ Pitfall 1: Breaking Changes in "Simple" Updates
**Problem:** Dependency update breaks production

**Prevention:**
- Always run full test suite
- Check package changelogs
- Test in staging first
- Use semantic versioning

### ❌ Pitfall 2: Refactoring That Changes Behavior
**Problem:** "Cleanup" accidentally changes logic

**Prevention:**
- Tests must pass before and after
- Code coverage should stay high
- Manual testing critical paths
- Small, focused refactors

### ❌ Pitfall 3: Undocumented Infrastructure Changes
**Problem:** Team can't deploy/run locally

**Prevention:**
- Update documentation
- Communicate changes
- Provide migration guide
- Test clean setup

### ❌ Pitfall 4: Performance "Optimization" That Degrades
**Problem:** Optimization makes things slower

**Prevention:**
- Measure before and after
- Use benchmarks, not intuition
- Profile before optimizing
- Test under realistic load

---

## Risk Assessment

### Low Risk Chores
- Typo fixes
- Comment updates
- Formatting changes
- Documentation improvements

**Validation:** Minimal (linting + build)

### Medium Risk Chores
- Dependency updates (patch versions)
- Code refactoring (single module)
- Configuration tweaks
- Performance optimizations

**Validation:** Full test suite + manual testing

### High Risk Chores
- Major dependency updates
- Large refactoring
- Infrastructure changes
- Database migrations

**Validation:** Full checklist + staging deployment + gradual rollout

---

## Quick Reference

**Before creating PR:**
```bash
npm test && npm run lint && npm run build
```

**Full validation:**
```bash
npm run lint && \
npm run type-check && \
npm test && \
npm run test:coverage && \
npm audit && \
npm run build

# Plus manual smoke testing
```

**Deployment checklist:**
```bash
# Staging first
# Smoke test staging
# Review monitoring
# Test rollback procedure
# Deploy to production
# Monitor closely
```

---

## Customization

Adapt this checklist for your project:

1. **Add project-specific checks**
   - Custom build steps
   - Domain-specific validations
   - Team-specific conventions

2. **Add chore-type sections**
   - Config updates
   - Schema migrations
   - CI/CD changes

3. **Update automation commands**
   - Match your tooling
   - Match your workflow
   - Match your environments

Save customizations in `.claude/validation-checklists/chore-validation-custom.md`

---

**Remember:** Chores improve code quality without changing behavior. If behavior changes, it's not a chore.
