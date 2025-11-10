# Feature Validation Checklist

**Purpose:** Systematic validation checklist for new features before marking complete.

**TAC Principle:** Closed-Loop Validation (Principle 4)

---

## When to Use

- After implementing a new feature
- Before creating pull request
- As part of `/review` command
- Before marking feature as done

---

## Validation Levels

Complete all levels that apply to your feature:

### Level 1: Code Quality ✅

- [ ] **Code compiles/runs without errors**
  ```bash
  # Run appropriate build command
  npm run build  # or: python -m py_compile, cargo build, etc.
  ```

- [ ] **Linting passes**
  ```bash
  npm run lint  # or: pylint, cargo clippy, etc.
  ```

- [ ] **Type checking passes** (if applicable)
  ```bash
  npm run type-check  # or: mypy, tsc --noEmit, etc.
  ```

- [ ] **No console.log / print statements** (unless intentional logging)
  ```bash
  grep -r "console.log" src/  # Check for debug statements
  ```

- [ ] **Code follows project conventions**
  - Check `CLAUDE.md "Project-Specific Context" section` for coding standards
  - Naming conventions followed
  - File organization matches project structure

---

### Level 2: Functional Requirements ✅

- [ ] **All spec requirements implemented**
  - Review `.claude/specs/feature-[name].md`
  - Each functional requirement has been addressed
  - Nothing from "Included" scope is missing

- [ ] **Out of scope items NOT implemented**
  - Verify spec's "Out of Scope" section
  - Confirm no scope creep occurred

- [ ] **Success criteria met**
  - Check each success criterion from spec
  - All checkboxes can be marked complete
  - Objective achieved

- [ ] **Integration points working**
  - All listed integration points tested
  - Data flows correctly between systems
  - No broken connections

---

### Level 3: Testing ✅

#### Unit Tests

- [ ] **Unit tests exist**
  ```bash
  # Check test files exist
  ls tests/unit/*[feature-name]*
  ```

- [ ] **Unit tests pass**
  ```bash
  npm test -- tests/unit/[feature-name]
  # or: pytest tests/unit/test_[feature-name].py
  ```

- [ ] **Coverage target met** (typically >80%)
  ```bash
  npm run test:coverage
  # Review coverage report for this feature
  ```

- [ ] **Edge cases tested**
  - Empty inputs
  - Null/undefined values
  - Boundary conditions
  - Error conditions

#### Integration Tests

- [ ] **Integration tests exist**
  ```bash
  ls tests/integration/*[feature-name]*
  ```

- [ ] **Integration tests pass**
  ```bash
  npm test -- tests/integration/[feature-name]
  ```

- [ ] **Component interactions validated**
  - All integration points from spec tested
  - Data flows work correctly
  - Error handling between components works

#### E2E Tests

- [ ] **E2E tests exist** (for user-facing features)
  ```bash
  ls tests/e2e/*[feature-name]*
  ```

- [ ] **E2E tests pass**
  ```bash
  npm run test:e2e -- [feature-name]
  ```

- [ ] **User workflows validated**
  - All user flows from spec tested
  - Happy path works
  - Error paths work

---

### Level 4: Non-Functional Requirements ✅

#### Performance

- [ ] **Performance targets met** (if specified in spec)
  - Response time < target
  - Resource usage acceptable
  - No memory leaks detected

- [ ] **Performance validation**
  ```bash
  # Run performance tests if defined
  npm run test:perf
  ```

#### Security

- [ ] **No security vulnerabilities introduced**
  ```bash
  npm audit  # or: pip-audit, cargo audit, etc.
  ```

- [ ] **Authentication/authorization correct** (if applicable)
  - Endpoints properly protected
  - User permissions enforced
  - No unauthorized access possible

- [ ] **Input validation implemented**
  - User input sanitized
  - SQL injection prevented
  - XSS vulnerabilities prevented

- [ ] **Secrets not hardcoded**
  ```bash
  grep -r "api_key\|password\|secret" src/
  # Should return no hardcoded secrets
  ```

#### Accessibility (if user-facing)

- [ ] **Semantic HTML used**
- [ ] **ARIA labels present** (where needed)
- [ ] **Keyboard navigation works**
- [ ] **Screen reader compatible**
- [ ] **Color contrast sufficient**

---

### Level 5: Documentation ✅

- [ ] **Code comments added** (for complex logic)
  - Non-obvious decisions explained
  - Complex algorithms documented
  - Public APIs documented

- [ ] **API documentation updated** (if applicable)
  - New endpoints documented
  - Request/response formats specified
  - Examples provided

- [ ] **README updated** (if user-facing changes)
  - Usage instructions added
  - Configuration options documented
  - Examples updated

- [ ] **CHANGELOG updated**
  - Feature added to changelog
  - Version number incremented (if needed)

- [ ] **Project docs updated** (if architectural changes)
  - Architecture diagrams updated
  - Design docs reflect changes

---

### Level 6: Environment & Configuration ✅

- [ ] **Environment variables documented**
  - New env vars added to `.env.example`
  - Documented in CLAUDE.md
  - Deployment docs updated

- [ ] **Configuration files updated**
  - Config changes documented
  - Defaults set appropriately
  - Migration path defined (if breaking)

- [ ] **Database migrations created** (if schema changes)
  ```bash
  # Check migrations exist
  ls migrations/*[feature-name]*
  ```

- [ ] **Dependencies added to package.json/requirements.txt**
  - All new dependencies listed
  - Version constraints specified
  - No unused dependencies

---

### Level 7: Error Handling ✅

- [ ] **Error messages clear and actionable**
  - Users know what went wrong
  - Users know how to fix it
  - Developers have debug context

- [ ] **Errors logged appropriately**
  - Errors sent to logging system
  - Appropriate log levels used
  - Sensitive data not logged

- [ ] **Graceful degradation implemented**
  - Failures don't crash app
  - User gets fallback experience
  - System recovers gracefully

- [ ] **Retry logic** (if applicable for external services)
  - Network failures handled
  - Exponential backoff implemented
  - Circuit breaker pattern used

---

### Level 8: Deployment Readiness ✅

- [ ] **Feature flags implemented** (if phased rollout)
  - Feature can be toggled
  - Rollback plan exists
  - Default state documented

- [ ] **Backward compatibility maintained**
  - Existing functionality not broken
  - API changes versioned
  - Migration path for users

- [ ] **Monitoring/observability added**
  - Key metrics tracked
  - Alerts configured
  - Dashboards updated

- [ ] **Deployment tested in staging**
  - Feature works in staging environment
  - No environment-specific issues
  - Data migrations tested

---

## Automated Validation

Run these commands to automate validation:

```bash
# All tests
npm test

# Coverage
npm run test:coverage

# Linting
npm run lint

# Type checking
npm run type-check

# Build
npm run build

# Security audit
npm audit

# E2E (if applicable)
npm run test:e2e
```

Expected: All commands should succeed with exit code 0.

---

## Manual Validation

Some items require human judgment:

1. **User Experience Review**
   - Does it feel right?
   - Is it intuitive?
   - Any edge cases missed?

2. **Code Review**
   - Is the code maintainable?
   - Are there simpler approaches?
   - Technical debt introduced?

3. **Security Review**
   - Attack vectors considered?
   - Defense in depth applied?
   - Least privilege principle followed?

---

## Completion Criteria

Feature is DONE when:

✅ All applicable checklist items completed
✅ All automated validation passes
✅ Spec definition of done met
✅ No known bugs or issues
✅ Ready for production deployment

---

## Integration with Commands

This checklist is used by:

- `/review` - Runs through this checklist
- `/test` - Executes automated portions
- `/pull_request` - References this in PR template
- `/document` - Ensures docs sections complete

---

## Customization

Modify this checklist for your project:

1. **Add project-specific checks**
   - Custom performance requirements
   - Domain-specific validations
   - Team-specific conventions

2. **Remove irrelevant sections**
   - No backend? Remove database checks
   - No UI? Remove accessibility checks
   - Internal tool? Lighter security

3. **Update commands**
   - Match your test runner
   - Match your linter
   - Match your build process

Save customizations in `.claude/validation-checklists/feature-validation-custom.md`

---

## Quick Reference

**Before creating PR:**
```bash
npm run lint && npm test && npm run build
```

**Full validation:**
```bash
npm run lint && \
npm run type-check && \
npm test && \
npm run test:coverage && \
npm audit && \
npm run build
```

---

**Remember:** This checklist prevents bugs from reaching production, not just code review.
