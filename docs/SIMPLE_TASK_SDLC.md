# Simple Task SDLC Framework

## Introduction

This document establishes a lightweight, formalized Software Development Life Cycle (SDLC) framework specifically designed for simple, routine development tasks in the spelling-tutor-agent project.

### Purpose

The Simple Task SDLC provides a clear, systematic approach to executing routine development work while maintaining quality standards and preventing technical debt. It integrates seamlessly with the existing AI Developer Workflow (ADW) system while also supporting manual execution for very simple tasks.

### Who Should Use This

- Developers working on bug fixes, small features, or maintenance tasks
- Contributors executing tasks that can be completed in 1-4 hours
- Teams seeking consistency in routine development processes
- Anyone using the ADW system for automated workflows

### What is a "Simple Task"?

A simple task is defined as work that meets these criteria:

**Scope Characteristics:**
- **Time:** Can be completed in 1-4 hours by a single developer
- **File Impact:** Touches 1-5 files
- **Clarity:** Has clear, unambiguous requirements
- **Risk:** Minimal risk of breaking existing functionality
- **Dependencies:** Limited or no external dependencies

**Common Simple Task Types:**
1. **Bug Fixes** - Fixing defects with clear reproduction steps
2. **Small Features** - Adding minor enhancements or capabilities
3. **Configuration Changes** - Updating settings, environment variables, or constants
4. **Documentation Updates** - Improving or correcting documentation
5. **Code Cleanup** - Refactoring small modules, removing dead code
6. **Dependency Updates** - Updating libraries to patch versions
7. **Test Additions** - Adding missing test coverage for existing code

**Not Simple Tasks (Use Full ADW SDLC):**
- Major features requiring multiple days of work
- Architectural changes affecting multiple systems
- Database schema migrations with data transformations
- Security-sensitive changes requiring extensive review
- Performance optimizations requiring benchmarking and profiling

### Framework Philosophy

**Lightweight but Rigorous:**
- Process is streamlined for speed
- Quality gates remain non-negotiable
- Documentation is concise but complete

**Flexible Execution:**
- ADW automation available but optional
- Manual execution supported for trivial tasks
- Hybrid approaches encouraged (manual + selective automation)

**Closed-Loop Validation:**
- Every stage includes validation
- No task is complete without verification
- Automated tests prevent regressions

---

## Process Overview

The Simple Task SDLC consists of five core stages executed sequentially:

```
┌─────────────┐    ┌──────────────┐    ┌─────────┐    ┌────────┐    ┌────────────┐
│  Planning   │ -> │Implementation│ -> │ Testing │ -> │ Review │ -> │ Deployment │
└─────────────┘    └──────────────┘    └─────────┘    └────────┘    └────────────┘
      │                   │                  │             │               │
   Spec & Plan      Code & Tests        Validate      Quality        Ship to Prod
```

### Execution Modes

**Mode 1: Fully Manual** (For trivial 30-minute tasks)
- Execute each stage manually using slash commands
- Use `/feature`, `/bug`, or `/chore` for planning
- Use `/implement`, `/test`, `/review`, `/commit`, `/pull_request` for execution
- Best for: Documentation updates, typo fixes, simple config changes

**Mode 2: ADW Automated** (For standard 1-4 hour tasks)
- Run complete SDLC with `adw_sdlc_iso.py`
- Automated planning, implementation, testing, review, and documentation
- Best for: Bug fixes, small features, routine maintenance

**Mode 3: Hybrid** (For complex simple tasks requiring oversight)
- Use ADW for planning (`adw_plan_iso.py`)
- Manually implement and review
- Use ADW for testing and deployment
- Best for: Tasks requiring design decisions or experimentation

### Decision Tree: Choosing Your Approach

```
Start
  │
  ├─ Is task < 30 minutes? ──Yes──> Fully Manual
  │
  ├─ Is task routine/repetitive? ──Yes──> ADW Automated
  │
  ├─ Requires experimentation? ──Yes──> Hybrid (Manual Implement)
  │
  └─ Standard 1-4 hour task? ──Yes──> ADW Automated
```

---

## Stage 1: Planning

### Objective

Create a clear, actionable plan that defines what will be built, why it's valuable, and how success will be measured.

### Activities

1. **Requirement Gathering**
   - Read the GitHub issue or task description
   - Identify the problem or opportunity
   - Clarify acceptance criteria
   - Identify edge cases

2. **Scope Definition**
   - Define what IS included
   - Define what is NOT included (out of scope)
   - Set clear boundaries
   - Estimate effort (ensure it qualifies as "simple")

3. **Technical Approach**
   - Identify files to modify or create
   - Determine implementation strategy
   - Identify potential risks
   - Note any unknowns requiring investigation

4. **Validation Planning**
   - Define how success will be validated
   - List specific validation commands
   - Identify manual testing steps
   - Plan regression prevention

### Deliverables

- **Specification Document** (`specs/issue-{N}-adw-{ID}-{name}.md`)
  - Problem statement
  - Solution approach
  - Acceptance criteria
  - Step-by-step tasks
  - Validation commands
  - Out of scope items

### ADW Integration

**Automated Planning:**
```bash
# Create worktree and generate plan
cd adw/
uv run adw_plan_iso.py <issue-number>

# Workflow executes:
# 1. Fetches issue from GitHub
# 2. Classifies issue type (/feature, /bug, /chore)
# 3. Runs planning slash command in isolated worktree
# 4. Generates spec in specs/ directory
# 5. Commits and pushes spec
# 6. Creates/updates pull request
```

**Manual Planning:**
```bash
# Use slash commands directly
/feature    # For new capabilities
/bug        # For defect fixes
/chore      # For maintenance tasks

# Each command:
# 1. Analyzes the codebase
# 2. Creates structured spec
# 3. Includes validation commands
# 4. Lists step-by-step tasks
```

### Quality Gate

**Question:** Is the task well-defined and scoped appropriately?

**Pass Criteria:**
- [ ] Problem and solution are clearly stated
- [ ] Acceptance criteria are measurable
- [ ] Tasks are specific and actionable
- [ ] Validation approach is defined
- [ ] Scope is limited (1-5 files, 1-4 hours)
- [ ] Out of scope items are documented

**Fail Actions:**
- Refine requirements with stakeholder
- Break into multiple simple tasks
- Escalate to full SDLC if too complex

### Common Pitfalls

**❌ Vague Requirements**
- "Make it better" → Need specific improvement criteria
- "Fix the bug" → Need reproduction steps and expected behavior

**❌ Scope Creep**
- Adding "nice to have" features
- Refactoring unrelated code
- Fixing multiple unrelated bugs

**❌ Missing Validation**
- No clear success criteria
- No validation commands listed
- Vague "it should work" statements

### Examples

**Good Planning:**
```markdown
## Problem Statement
Users cannot reset their password because the email service
integration is broken (throws 500 error when sending emails).

## Solution Statement
Fix the email service integration by updating the API endpoint
from v1 to v2 and adding proper error handling.

## Acceptance Criteria
- Password reset emails are sent successfully
- Users receive emails within 30 seconds
- Email service errors are logged with context
- Existing password reset flow works end-to-end

## Validation Commands
- cd app/server && uv run pytest tests/test_email_service.py -v
- cd app/server && uv run pytest tests/test_password_reset.py -v
- Manual: Test password reset with real email address
```

---

## Stage 2: Implementation

### Objective

Implement the solution defined in the planning stage following project standards and best practices.

### Activities

1. **Code Implementation**
   - Follow the step-by-step tasks from the spec
   - Write clean, maintainable code
   - Follow project coding conventions
   - Add inline comments for complex logic

2. **Test Creation**
   - Write unit tests for new code
   - Add regression tests for bug fixes
   - Update existing tests if needed
   - Ensure tests are deterministic

3. **Incremental Progress**
   - Make small, focused commits
   - Test each change before proceeding
   - Keep changes minimal and focused
   - Avoid unrelated refactoring

4. **Error Handling**
   - Add appropriate error handling
   - Validate inputs
   - Log errors with context
   - Fail gracefully

### Deliverables

- **Working Code** that implements the spec
- **Unit Tests** with good coverage
- **Updated Tests** for modified code
- **Code Comments** for non-obvious logic

### ADW Integration

**Automated Implementation:**
```bash
# Requires existing worktree from planning phase
cd adw/
uv run adw_build_iso.py <issue-number> <adw-id>

# Workflow executes:
# 1. Loads spec from planning phase
# 2. Runs /implement slash command
# 3. Follows step-by-step tasks
# 4. Creates code and tests
# 5. Commits implementation
# 6. Pushes to PR branch
```

**Manual Implementation:**
```bash
# Execute the spec using slash command
/implement

# Then manually:
# 1. Read the spec carefully
# 2. Execute each task in order
# 3. Write tests alongside code
# 4. Validate as you go
```

### Quality Gate

**Question:** Does the code work and follow project standards?

**Pass Criteria:**
- [ ] All tasks from spec are completed
- [ ] Code follows project conventions (see `.claude/project-context.md`)
- [ ] Unit tests exist for new/modified code
- [ ] No linting errors (`cd app/client && bun run lint` or equivalent)
- [ ] No type errors (`cd app/client && bun tsc --noEmit`)
- [ ] Code builds successfully (`cd app/client && bun run build`)
- [ ] No debug statements left (console.log, debugger, etc.)

**Fail Actions:**
- Fix linting/type errors
- Add missing tests
- Refactor code to meet standards
- Remove debug code

### Coding Best Practices

**Do:**
- Follow existing patterns in the codebase
- Keep functions small and focused
- Use descriptive variable names
- Add comments for "why" not "what"
- Write tests first for bug fixes (TDD)
- Validate inputs early
- Handle errors explicitly

**Don't:**
- Mix multiple concerns in one function
- Use magic numbers or strings
- Catch and ignore errors silently
- Modify code unrelated to the task
- Leave TODO comments without tickets
- Copy-paste code (extract to function)

### Common Pitfalls

**❌ Scope Creep**
- Refactoring unrelated code
- Adding features not in spec
- Fixing multiple bugs at once

**❌ Insufficient Testing**
- Only testing happy path
- Missing edge cases
- No negative test cases

**❌ Poor Error Handling**
- Silent failures
- Generic error messages
- No logging for debugging

### Code Review Checklist (Self-Review)

Before moving to testing stage:

**Functionality:**
- [ ] Code implements spec requirements
- [ ] Edge cases are handled
- [ ] Error conditions are covered

**Quality:**
- [ ] Code is readable and maintainable
- [ ] No code duplication
- [ ] Functions have single responsibility
- [ ] Variable names are descriptive

**Testing:**
- [ ] Unit tests exist and pass
- [ ] Tests cover happy path
- [ ] Tests cover edge cases
- [ ] Tests are deterministic (no flaky tests)

**Standards:**
- [ ] Follows project style guide
- [ ] No linting errors
- [ ] No type errors
- [ ] No security vulnerabilities introduced

---

## Stage 3: Testing

### Objective

Validate that the implementation works correctly and doesn't break existing functionality.

### Activities

1. **Unit Testing**
   - Run unit tests for modified code
   - Run full unit test suite
   - Verify tests pass consistently
   - Check test coverage

2. **Integration Testing**
   - Test integration points
   - Verify data flows correctly
   - Test error handling between components

3. **Manual Testing**
   - Execute manual test scenarios from spec
   - Test happy path manually
   - Test edge cases manually
   - Verify user experience

4. **Regression Testing**
   - Run full test suite
   - Verify no existing tests fail
   - Test related features manually
   - Check for unintended side effects

### Deliverables

- **Passing Tests** (all automated tests pass)
- **Test Coverage** (no decrease in coverage %)
- **Manual Test Results** (documented in PR or comments)
- **Fixed Tests** (if any were broken)

### ADW Integration

**Automated Testing:**
```bash
# Requires existing worktree from build phase
cd adw/
uv run adw_test_iso.py <issue-number> <adw-id>

# Workflow executes:
# 1. Runs unit tests in worktree
# 2. Auto-fixes test failures (using /resolve_failed_test)
# 3. Optionally runs E2E tests
# 4. Commits test fixes
# 5. Reports results in PR comment
```

**Manual Testing:**
```bash
# Run tests manually
cd app/server && uv run pytest
cd app/client && bun test
cd app/client && bun run build

# Use slash command for auto-fix
/test    # Runs tests and auto-fixes failures
```

### Validation Commands

**Required for All Simple Tasks:**
```bash
# Backend tests
cd app/server && uv run pytest -v

# Frontend type checking
cd app/client && bun tsc --noEmit

# Frontend build
cd app/client && bun run build

# Test coverage (if applicable)
cd app/server && uv run pytest --cov=app --cov-report=term
```

**Optional but Recommended:**
```bash
# E2E tests (for UI changes)
# Read .claude/commands/test_e2e.md for instructions

# Linting
cd app/client && bun run lint

# Security audit
cd app/client && bun audit
cd app/server && pip-audit
```

### Quality Gate

**Question:** Do all tests pass with no regressions?

**Pass Criteria:**
- [ ] All unit tests pass (100% pass rate)
- [ ] All integration tests pass (if applicable)
- [ ] No existing tests broken
- [ ] Test coverage maintained or improved
- [ ] Build succeeds
- [ ] No type errors
- [ ] Manual testing confirms expected behavior

**Fail Actions:**
- Fix failing tests
- Add missing tests
- Debug broken functionality
- Revert if unfixable

### Testing Strategy by Task Type

**Bug Fixes:**
1. Write regression test that fails without fix
2. Apply fix
3. Verify regression test passes
4. Run full test suite
5. Manual reproduction test

**Small Features:**
1. Write unit tests for new code
2. Write integration tests for integration points
3. Run full test suite
4. Manual feature walkthrough
5. E2E test (if UI feature)

**Chores (Refactoring/Cleanup):**
1. Ensure all existing tests still pass
2. No new tests typically required
3. Verify behavior unchanged
4. Performance benchmarks (if optimization)

### Common Pitfalls

**❌ Only Testing Happy Path**
- Missing edge cases
- No negative testing
- No error condition testing

**❌ Flaky Tests**
- Tests pass/fail inconsistently
- Timing-dependent tests
- Tests dependent on external services

**❌ Skipping Manual Testing**
- Automated tests aren't enough
- User experience needs validation
- Visual bugs only caught manually

---

## Stage 4: Review

### Objective

Ensure the implementation meets all quality standards and spec requirements before deployment.

### Activities

1. **Spec Compliance Review**
   - Verify all requirements implemented
   - Check acceptance criteria met
   - Confirm out-of-scope items excluded
   - Validate against success criteria

2. **Code Quality Review**
   - Review code for readability
   - Check for code smells
   - Verify best practices followed
   - Ensure no technical debt introduced

3. **Validation Checklist**
   - Use appropriate validation checklist:
     - `.claude/validation-checklists/feature-validation.md` for features
     - `.claude/validation-checklists/bug-validation.md` for bugs
     - `.claude/validation-checklists/chore-validation.md` for chores
   - Complete applicable checklist levels
   - Document any skipped items with justification

4. **Documentation Review**
   - Verify code comments adequate
   - Check if README needs updating
   - Ensure CHANGELOG updated
   - Validate any new documentation

### Deliverables

- **Completed Validation Checklist**
- **Review Report** (in PR comment or review)
- **Screenshots** (for UI changes)
- **Quality Sign-off** (checklist complete)

### ADW Integration

**Automated Review:**
```bash
# Requires existing worktree from test phase
cd adw/
uv run adw_review_iso.py <issue-number> <adw-id>

# Workflow executes:
# 1. Runs /review slash command
# 2. Validates against spec
# 3. Captures screenshots (for UI changes)
# 4. Auto-resolves blockers if possible
# 5. Uploads screenshots to PR
# 6. Posts review summary
```

**Manual Review:**
```bash
# Use slash command
/review

# Then manually:
# 1. Go through validation checklist
# 2. Review code diff
# 3. Test manually
# 4. Document findings
```

### Quality Gate

**Question:** Does the change meet all quality standards?

**Pass Criteria:**

**For Features:**
- [ ] All spec requirements implemented
- [ ] Success criteria met
- [ ] No out-of-scope items included
- [ ] Tests passing
- [ ] Code follows conventions
- [ ] Documentation updated

**For Bug Fixes:**
- [ ] Bug no longer reproducible
- [ ] Root cause addressed (not just symptoms)
- [ ] Regression test added
- [ ] No new bugs introduced
- [ ] Related functionality still works

**For Chores:**
- [ ] Objective achieved
- [ ] No functionality broken
- [ ] All tests still passing
- [ ] Documentation updated
- [ ] Team notified (if workflow changes)

**Fail Actions:**
- Fix identified issues
- Update documentation
- Add missing tests
- Refactor problematic code

### Review Checklist for Simple Tasks

**Simplified Feature Validation:**
1. Code Quality (Level 1)
   - [ ] Code compiles/builds
   - [ ] Linting passes
   - [ ] Type checking passes

2. Functional Requirements (Level 2)
   - [ ] All spec requirements implemented
   - [ ] Success criteria met
   - [ ] Out of scope items NOT included

3. Testing (Level 3)
   - [ ] Unit tests exist and pass
   - [ ] No existing tests broken
   - [ ] Manual testing confirms behavior

4. Documentation (Level 5 - Simplified)
   - [ ] Code comments for complex logic
   - [ ] README updated if needed
   - [ ] CHANGELOG updated

**Simplified Bug Fix Validation:**
1. Bug Resolution
   - [ ] Bug no longer reproducible
   - [ ] Fix addresses root cause
   - [ ] Validation command passes

2. Regression Prevention
   - [ ] Regression test added
   - [ ] Regression test passes

3. No New Bugs
   - [ ] All existing tests pass
   - [ ] No new linting/type errors

**Simplified Chore Validation:**
1. Objective Achieved
   - [ ] Chore objective completed
   - [ ] Success criteria met

2. No Functionality Broken
   - [ ] All tests pass
   - [ ] Application still runs

3. Code Quality
   - [ ] Linting passes
   - [ ] Code builds

### Common Pitfalls

**❌ Rubber Stamp Review**
- Just checking boxes without verification
- Trusting automated tests without manual validation
- Skipping edge case testing

**❌ Scope Creep in Review**
- Finding unrelated issues to fix
- Expanding requirements during review
- Adding features not in spec

**❌ Missing Documentation**
- No CHANGELOG entry
- No code comments for complex logic
- README outdated

---

## Stage 5: Deployment

### Objective

Ship the change to production safely with proper documentation and communication.

### Activities

1. **Pre-Deployment**
   - Ensure all quality gates passed
   - Verify all tests passing
   - Review validation checklist completion
   - Confirm PR has necessary approvals

2. **Commit Creation**
   - Create semantic commit message
   - Link to issue/spec
   - Summarize changes clearly
   - Follow commit conventions

3. **Pull Request**
   - Create PR with descriptive title
   - Link to GitHub issue
   - Summarize implementation approach
   - Include validation results
   - Add screenshots (if UI changes)

4. **Merge and Deploy**
   - Get PR approval
   - Merge to main branch
   - Verify CI/CD passes
   - Monitor deployment
   - Clean up worktree/branch

### Deliverables

- **Semantic Commit(s)** on feature branch
- **Pull Request** with complete description
- **Merged Code** in main branch
- **Deployment** to production
- **Cleaned Worktree** (if using ADW)

### ADW Integration

**Automated Deployment:**
```bash
# Manual ship (requires approval decision)
cd adw/
uv run adw_ship_iso.py <issue-number> <adw-id>

# Workflow executes:
# 1. Validates all state fields populated
# 2. Finds PR for branch
# 3. Approves the PR
# 4. Merges to main (squash merge)

# Full SDLC with auto-ship (⚠️ careful!)
cd adw/
uv run adw_sdlc_zte_iso.py <issue-number>
# Zero Touch Execution - merges automatically if all passes
```

**Manual Deployment:**
```bash
# Create commit
/commit
# Generates semantic commit message

# Create PR
/pull_request
# Generates PR description with summary

# Then manually:
# 1. Get PR approval
# 2. Merge via GitHub UI
# 3. Monitor deployment
# 4. Cleanup branch
```

### Commit Message Convention

**Format:**
```
<type>: <short summary>

<detailed description>

Fixes #<issue-number>
```

**Types:**
- `feat:` - New features
- `fix:` - Bug fixes
- `chore:` - Maintenance tasks
- `docs:` - Documentation
- `test:` - Test updates
- `refactor:` - Code refactoring

**Example:**
```
fix: resolve email service integration for password reset

Updated email service API from v1 to v2 endpoint and added
proper error handling with logging. Password reset emails now
send successfully within 30 seconds.

Fixes #123
```

### Pull Request Template

**Title Format:**
```
<type>: <short description> (#<issue-number>)
```

**Description Structure:**
```markdown
## Summary
Brief description of what changed and why.

## Changes
- List of specific changes made
- Files modified or added
- Key implementation details

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing complete
- [ ] No regressions

## Validation
- Ran: cd app/server && uv run pytest -v ✅
- Ran: cd app/client && bun tsc --noEmit ✅
- Ran: cd app/client && bun run build ✅

## Screenshots
(if UI changes)

Fixes #<issue-number>
```

### Quality Gate

**Question:** Is the change ready for production?

**Pass Criteria:**
- [ ] All previous quality gates passed
- [ ] PR has clear description
- [ ] Commit messages follow convention
- [ ] PR linked to issue
- [ ] Tests passing in CI/CD
- [ ] No merge conflicts
- [ ] Required approvals obtained

**Fail Actions:**
- Fix failing CI/CD checks
- Resolve merge conflicts
- Address review comments
- Update PR description

### Post-Deployment

**Monitoring:**
- Check application logs for errors
- Verify feature works in production
- Monitor performance metrics
- Watch for user reports

**Cleanup:**
```bash
# If using ADW worktrees
git worktree list
git worktree remove trees/<adw-id>

# Delete local branch
git branch -d <branch-name>

# Delete remote branch (if not auto-deleted)
git push origin --delete <branch-name>
```

**Communication:**
- Update issue status (close issue)
- Notify stakeholders if needed
- Document any follow-up work
- Update project boards

### Common Pitfalls

**❌ Vague Commit Messages**
- "fix bug" → Need specifics
- "update code" → What changed?
- "stuff" → Completely unhelpful

**❌ Missing PR Context**
- No description
- No link to issue
- No validation results
- No screenshots for UI changes

**❌ Premature Deployment**
- Merging before approval
- Skipping CI/CD checks
- Not monitoring post-deployment

---

## Integration with ADW

### ADW Workflow Mapping

The Simple Task SDLC maps directly to ADW workflows:

| SDLC Stage | ADW Workflow | Slash Commands | Outputs |
|------------|--------------|----------------|---------|
| Planning | `adw_plan_iso.py` | `/feature`, `/bug`, `/chore` | Spec file, PR |
| Implementation | `adw_build_iso.py` | `/implement` | Code, tests, commits |
| Testing | `adw_test_iso.py` | `/test`, `/resolve_failed_test` | Test results, fixes |
| Review | `adw_review_iso.py` | `/review` | Screenshots, validation |
| Deployment | `adw_ship_iso.py` | `/commit`, `/pull_request` | Merged PR |

### Complete ADW SDLC Execution

**Option 1: Full Automated SDLC**
```bash
cd adw/
uv run adw_sdlc_iso.py <issue-number>

# Executes all 5 stages automatically:
# 1. Planning  → Creates spec
# 2. Build     → Implements solution
# 3. Test      → Validates with auto-fix
# 4. Review    → Captures screenshots
# 5. Document  → Generates docs

# Result: Complete PR ready for approval
```

**Option 2: Zero Touch Execution (Auto-Ship)**
```bash
cd adw/
uv run adw_sdlc_zte_iso.py <issue-number>

# ⚠️ WARNING: Auto-merges to main if all passes!
# Use only for:
# - Low-risk simple tasks
# - Well-tested changes
# - When you trust automation fully
```

**Option 3: Individual Phases**
```bash
# Phase 1: Planning (creates worktree)
cd adw/
uv run adw_plan_iso.py <issue-number>
# Note the ADW ID returned (e.g., abc12345)

# Phase 2: Implementation (requires ADW ID)
uv run adw_build_iso.py <issue-number> abc12345

# Phase 3: Testing (requires ADW ID)
uv run adw_test_iso.py <issue-number> abc12345

# Phase 4: Review (requires ADW ID)
uv run adw_review_iso.py <issue-number> abc12345

# Phase 5: Documentation (optional, requires ADW ID)
uv run adw_document_iso.py <issue-number> abc12345

# Phase 6: Ship (requires ADW ID)
uv run adw_ship_iso.py <issue-number> abc12345
```

**Option 4: Hybrid Approaches**
```bash
# Automated planning, manual implementation
uv run adw_plan_iso.py <issue-number>
# Manual: cd trees/<adw-id>/ and implement
uv run adw_test_iso.py <issue-number> <adw-id>
uv run adw_review_iso.py <issue-number> <adw-id>

# Automated plan+build, manual review
uv run adw_plan_build_iso.py <issue-number>
# Manual review, then:
uv run adw_test_iso.py <issue-number> <adw-id>
uv run adw_ship_iso.py <issue-number> <adw-id>
```

### When to Use Each ADW Workflow

**Use Full ADW SDLC (`adw_sdlc_iso.py`):**
- Standard 1-4 hour simple tasks
- Routine bug fixes with clear reproduction
- Well-defined small features
- When you want complete automation

**Use Zero Touch Execution (`adw_sdlc_zte_iso.py`):**
- ⚠️ Use sparingly and carefully
- Only for very low-risk changes
- Documentation updates
- Configuration changes with full test coverage
- When CI/CD and tests are comprehensive

**Use Plan-Build-Test (`adw_plan_build_test_iso.py`):**
- When you want to manually review before shipping
- For tasks requiring human judgment before merge
- When you're less confident in full automation

**Use Individual Phases:**
- When you want control over each stage
- For learning the SDLC process
- When some stages need manual oversight
- For debugging failed automated workflows

**Use Manual (Slash Commands):**
- Tasks under 30 minutes
- Simple documentation updates
- Configuration changes
- When learning the process
- When ADW automation is not available

### ADW Isolated Execution Benefits

**Isolation Advantages:**
- Each workflow runs in dedicated git worktree
- No interference with main repo
- Dedicated ports (backend: 9100-9114, frontend: 9200-9214)
- Multiple workflows can run in parallel (up to 15 concurrent)

**State Management:**
- Persistent state in `agents/<adw-id>/adw_state.json`
- Tracks worktree path, branch, ports, plan file
- Enables resuming workflows
- Shares data between phases

**Port Allocation:**
- Deterministic based on ADW ID
- Automatic fallback if ports busy
- Configured via `.ports.env` in worktree

**Cleanup:**
```bash
# Remove worktree after PR merge
git worktree remove trees/<adw-id>

# Or use cleanup script
./scripts/purge_tree.sh <adw-id>
```

---

## Decision Guide

### Should I Use Manual or ADW?

**Decision Tree:**
```
Is this a simple task (1-4 hours, 1-5 files)?
├─ No  → Use full ADW SDLC (not this guide)
└─ Yes → Continue

Is the task < 30 minutes?
├─ Yes → Use Manual (slash commands)
└─ No  → Continue

Is the task routine and well-defined?
├─ Yes → Use ADW Automated (adw_sdlc_iso.py)
└─ No  → Continue

Does it require experimentation?
├─ Yes → Use Hybrid (manual implement, ADW test/review)
└─ No  → Use ADW Automated (adw_sdlc_iso.py)
```

### Manual Process (Slash Commands)

**Best For:**
- Documentation updates
- Typo fixes
- Simple configuration changes
- Learning the SDLC process

**Workflow:**
```bash
# 1. Planning
/feature    # or /bug or /chore

# 2. Implementation
/implement

# 3. Testing
/test

# 4. Review
/review

# 5. Deployment
/commit
/pull_request
# Then merge via GitHub
```

**Time:** 30 minutes - 2 hours

**Pros:**
- Full control over each step
- Good for learning
- Flexible for experimentation

**Cons:**
- More manual work
- Easier to skip steps
- No automated validation

### ADW Automated Process

**Best For:**
- Bug fixes with clear reproduction
- Small well-defined features
- Routine maintenance tasks
- Consistency and speed

**Workflow:**
```bash
# One command for complete SDLC
cd adw/
uv run adw_sdlc_iso.py <issue-number>

# Result: Fully validated PR ready for review
```

**Time:** 1-4 hours (mostly automated)

**Pros:**
- Fully automated
- Consistent process
- No steps skipped
- Validation enforced

**Cons:**
- Less control
- May need tweaking for edge cases
- Requires ADW setup

### Hybrid Process

**Best For:**
- Tasks requiring design decisions
- Experimental implementations
- Learning complex codebases

**Workflow:**
```bash
# ADW planning
cd adw/
uv run adw_plan_iso.py <issue-number>

# Manual implementation in worktree
cd trees/<adw-id>/
# Implement manually

# ADW testing and review
cd adw/
uv run adw_test_iso.py <issue-number> <adw-id>
uv run adw_review_iso.py <issue-number> <adw-id>
uv run adw_ship_iso.py <issue-number> <adw-id>
```

**Time:** 2-4 hours

**Pros:**
- Control where needed
- Automation where valuable
- Best of both worlds

**Cons:**
- More complex
- Requires understanding both approaches

---

## Task Type Templates

### Bug Fix Template

See: `docs/templates/simple-bug-fix-template.md`

**Quick Reference:**
1. **Planning:** Identify reproduction steps, root cause, fix approach
2. **Implementation:** Fix root cause (not symptoms), add regression test
3. **Testing:** Verify bug no longer reproducible, all tests pass
4. **Review:** Use bug-validation.md checklist
5. **Deployment:** Include "Fixes #N" in commit

**Key Quality Gates:**
- Regression test would fail without fix
- Root cause documented
- No new bugs introduced

### Small Feature Template

See: `docs/templates/simple-feature-template.md`

**Quick Reference:**
1. **Planning:** Clear user story, acceptance criteria, scope boundaries
2. **Implementation:** Implement minimal viable version, add tests
3. **Testing:** Unit tests + manual feature walkthrough
4. **Review:** Use feature-validation.md checklist (simplified levels)
5. **Deployment:** Include screenshots if UI changes

**Key Quality Gates:**
- All acceptance criteria met
- Out of scope items excluded
- Feature works end-to-end

### Chore/Maintenance Template

See: `docs/templates/simple-chore-template.md`

**Quick Reference:**
1. **Planning:** Objective, rationale, success criteria
2. **Implementation:** Make changes, ensure behavior unchanged
3. **Testing:** All existing tests still pass
4. **Review:** Use chore-validation.md checklist
5. **Deployment:** Document any workflow changes

**Key Quality Gates:**
- Objective achieved
- No functionality broken
- Team notified of changes

---

## Examples

### Example 1: Fixing a Typo Bug

**Task:** Fix typo in error message (shows "Sever Error" instead of "Server Error")

**Execution Mode:** Manual (< 30 minutes)

**Process:**
```bash
# 1. Planning (2 minutes)
/bug
# Creates spec with:
# - Problem: Typo in error message
# - Solution: Fix string constant
# - Validation: Trigger error, verify message

# 2. Implementation (5 minutes)
/implement
# Changes: src/errors.ts line 42
# Before: "Sever Error occurred"
# After: "Server Error occurred"

# 3. Testing (2 minutes)
/test
# Runs: npm test
# Manual: Trigger error, check message

# 4. Review (2 minutes)
/review
# Checklist: Code quality, no regressions

# 5. Deployment (5 minutes)
/commit
# Message: "fix: correct server error message typo"

/pull_request
# Title: "fix: correct server error message typo (#234)"
# Merge via GitHub
```

**Total Time:** 16 minutes

### Example 2: Adding Small Feature (Search Placeholder)

**Task:** Add configurable placeholder text to search input

**Execution Mode:** ADW Automated

**Process:**
```bash
# Complete SDLC in one command
cd adw/
uv run adw_sdlc_iso.py 456

# Automated execution:
# 1. Planning (10 min)
#    - Creates spec with user story
#    - Defines acceptance criteria
#    - Lists files to modify

# 2. Implementation (20 min)
#    - Adds placeholder prop to SearchInput component
#    - Updates tests
#    - Adds default value

# 3. Testing (15 min)
#    - Runs all tests
#    - Auto-fixes any failures
#    - Validates type checking

# 4. Review (10 min)
#    - Validates against spec
#    - Captures screenshots
#    - Checks quality gates

# 5. Documentation (10 min)
#    - Generates component docs
#    - Updates CHANGELOG

# Result: PR ready for approval
```

**Total Time:** ~65 minutes (mostly automated)

### Example 3: Dependency Update

**Task:** Update React from 18.2.0 to 18.3.0 (patch version)

**Execution Mode:** Manual with ADW testing

**Process:**
```bash
# 1. Planning (5 minutes) - Manual
/chore
# Spec:
# - Objective: Update React to 18.3.0
# - Rationale: Security patch
# - Validation: All tests pass, app starts

# 2. Implementation (10 minutes) - Manual
cd app/client
bun update react@18.3.0
bun install

# 3. Testing (ADW automated)
cd ../../adw
uv run adw_test_iso.py 789 <adw-id>
# Runs all tests with auto-fix

# 4. Review (5 minutes) - Manual
/review
# Checklist: No breaking changes, tests pass

# 5. Deployment (5 minutes) - Manual
/commit
# Message: "chore: update React to 18.3.0 for security patch"

/pull_request
# Merge via GitHub
```

**Total Time:** ~25 minutes (hybrid approach)

### Example 4: Refactoring Utility Function

**Task:** Extract duplicated date formatting logic to utility function

**Execution Mode:** Hybrid (ADW plan, manual refactor, ADW test)

**Process:**
```bash
# 1. Planning (ADW)
cd adw/
uv run adw_plan_iso.py 321

# 2. Implementation (Manual in worktree)
cd trees/<adw-id>/
# Manually refactor:
# - Create src/utils/formatDate.ts
# - Extract duplicated logic
# - Update 3 files to use utility
# - Ensure behavior unchanged

# 3. Testing (ADW)
cd ../../adw/
uv run adw_test_iso.py 321 <adw-id>
# Validates no behavior change

# 4. Review (ADW)
uv run adw_review_iso.py 321 <adw-id>
# Validates code quality

# 5. Deployment (ADW)
uv run adw_ship_iso.py 321 <adw-id>
# Creates PR and merges
```

**Total Time:** ~90 minutes (manual refactoring takes thought)

---

## Quick Reference

### Commands Cheatsheet

**Planning:**
```bash
/feature    # New capabilities
/bug        # Defect fixes
/chore      # Maintenance
```

**Implementation:**
```bash
/implement  # Execute spec
```

**Testing:**
```bash
/test                      # Run tests with auto-fix
/resolve_failed_test       # Fix specific test failure
/test_e2e                  # E2E testing
```

**Review:**
```bash
/review     # Validate against spec
```

**Deployment:**
```bash
/commit         # Generate semantic commit
/pull_request   # Create PR description
```

### ADW Workflows Cheatsheet

**Entry Points (Create Worktree):**
```bash
adw_plan_iso.py <issue>           # Planning only
adw_patch_iso.py <issue>          # Quick patch
```

**Complete Workflows:**
```bash
adw_sdlc_iso.py <issue>           # Full SDLC
adw_sdlc_zte_iso.py <issue>       # Auto-ship (⚠️)
adw_plan_build_test_iso.py <issue>  # Plan+Build+Test
```

**Individual Phases (Require ADW ID):**
```bash
adw_build_iso.py <issue> <adw-id>
adw_test_iso.py <issue> <adw-id>
adw_review_iso.py <issue> <adw-id>
adw_document_iso.py <issue> <adw-id>
adw_ship_iso.py <issue> <adw-id>
```

### Validation Commands

**Always Run:**
```bash
cd app/server && uv run pytest -v
cd app/client && bun tsc --noEmit
cd app/client && bun run build
```

**Recommended:**
```bash
cd app/client && bun run lint
cd app/server && uv run pytest --cov=app
```

### Quality Gates Summary

| Stage | Key Question | Pass Criteria |
|-------|-------------|---------------|
| Planning | Well-defined? | Clear requirements, scope, validation |
| Implementation | Follows standards? | Code works, tests exist, no lint errors |
| Testing | No regressions? | All tests pass, coverage maintained |
| Review | Meets quality? | Checklist complete, spec satisfied |
| Deployment | Production ready? | Approved, CI/CD passing, monitored |

### Decision Flowchart

```
Start → Is task simple? (1-4hr, 1-5 files)
          ├─ No → Use full ADW SDLC (not this guide)
          └─ Yes → Is task < 30min?
                    ├─ Yes → Manual (slash commands)
                    └─ No → Is task routine?
                             ├─ Yes → ADW Automated
                             └─ No → Hybrid or Manual
```

### Troubleshooting

**Problem:** Tests failing after implementation
- **Solution:** Use `/resolve_failed_test` or `adw_test_iso.py` for auto-fix

**Problem:** Don't know which workflow to use
- **Solution:** Start with `/begin` or use `adw_sdlc_iso.py` for standard tasks

**Problem:** ADW worktree conflicts
- **Solution:** `git worktree list` then `git worktree remove trees/<adw-id>`

**Problem:** Scope unclear
- **Solution:** Spend more time in Planning stage, clarify with stakeholders

**Problem:** Task too big for "simple"
- **Solution:** Break into multiple simple tasks or use full ADW SDLC

---

## Common Pitfalls

### Pitfall 1: Skipping Planning

**Problem:** Jumping straight to coding without a plan.

**Symptoms:**
- Implementing wrong solution
- Missing edge cases
- Unclear acceptance criteria
- Scope creep during implementation

**Prevention:**
- Always create a spec first (use `/feature`, `/bug`, or `/chore`)
- Define validation commands upfront
- Get stakeholder confirmation on approach

### Pitfall 2: Insufficient Testing

**Problem:** Only testing happy path or skipping tests.

**Symptoms:**
- Regressions in production
- Edge cases fail
- No way to detect if bug returns

**Prevention:**
- Write tests alongside code
- Test edge cases and error conditions
- Run full test suite before deployment
- Add regression tests for bugs

### Pitfall 3: Vague Validation

**Problem:** No clear way to verify success.

**Symptoms:**
- "It should work" mentality
- No executable validation commands
- Manual testing steps undefined

**Prevention:**
- List specific validation commands in spec
- Include expected outputs
- Manual steps should be reproducible
- Validation should be binary (pass/fail)

### Pitfall 4: Scope Creep

**Problem:** Expanding task beyond original intent.

**Symptoms:**
- "While I'm here, I'll also..."
- Refactoring unrelated code
- Adding features not in spec
- Task taking much longer than estimated

**Prevention:**
- Define "out of scope" in planning
- Stick to spec requirements
- Create new issues for additional work
- Review scope in Review stage

### Pitfall 5: Skipping Review

**Problem:** Merging without proper validation.

**Symptoms:**
- Bugs in production
- Missing edge cases
- Technical debt introduced
- Standards not followed

**Prevention:**
- Complete validation checklist
- Use `/review` command
- Manual testing before merge
- Self-review code diff

### Pitfall 6: Poor Documentation

**Problem:** Changes not documented.

**Symptoms:**
- Team doesn't know what changed
- CHANGELOG outdated
- Complex code unexplained
- Future developers confused

**Prevention:**
- Update CHANGELOG for every change
- Add code comments for non-obvious logic
- Update README if behavior changes
- Write clear commit messages

---

## Customization

This framework is designed to be adapted to your project's needs.

### Project-Specific Additions

Add to your `.claude/project-context.md`:

```markdown
## Simple Task SDLC Customizations

### Validation Commands (Override Defaults)
```bash
# Our project uses different commands
npm run test:unit      # instead of npm test
npm run verify:types   # instead of tsc
```

### Additional Quality Gates
- Performance: Response time < 200ms
- Security: No OWASP Top 10 vulnerabilities
- Accessibility: WCAG 2.1 AA compliance

### Team-Specific Conventions
- Always add `[JIRA-123]` prefix to commits
- Screenshots required for all UI changes
- Database changes need DBA approval
```

### Adding Custom Templates

Create custom templates in `docs/templates/`:

```bash
# Example: E-commerce specific bug fix template
docs/templates/cart-bug-fix-template.md
```

### Modifying Validation Checklists

Create project-specific checklists:

```bash
.claude/validation-checklists/feature-validation-custom.md
```

Include project-specific requirements:
- Custom performance benchmarks
- Domain-specific edge cases
- Compliance requirements

### Extending ADW Workflows

For project-specific workflow needs:

```bash
# Create custom workflow
adw/adw_custom_workflow_iso.py

# Combine existing phases in new ways
# Example: Plan + Build + Custom Validation + Ship
```

---

## Success Metrics

Track these metrics to measure Simple Task SDLC effectiveness:

### Quality Metrics

**Regression Rate:**
- **Target:** < 5% of simple tasks cause regressions
- **Measure:** Bugs found in production from simple task changes
- **Track:** Percentage of simple tasks that need follow-up fixes

**First-Time Quality:**
- **Target:** > 90% of simple tasks pass review on first attempt
- **Measure:** PRs that need changes after initial review
- **Track:** Review feedback iterations

**Test Coverage:**
- **Target:** Maintain or improve coverage %
- **Measure:** Code coverage before and after simple task
- **Track:** Coverage trends over time

### Efficiency Metrics

**Cycle Time:**
- **Target:** < 4 hours from start to PR merge (for ADW automated)
- **Measure:** Time from issue creation to PR merge
- **Track:** Average cycle time per task type

**Planning Accuracy:**
- **Target:** > 80% of tasks completed within estimated time
- **Measure:** Estimated vs actual time
- **Track:** Estimation accuracy improvements

**Automation Adoption:**
- **Target:** > 60% of simple tasks use ADW workflows
- **Measure:** Manual vs automated executions
- **Track:** Adoption trends

### Process Metrics

**Validation Compliance:**
- **Target:** 100% of simple tasks have validation commands
- **Measure:** Specs with validation commands listed
- **Track:** Percentage with complete validation

**Documentation Completeness:**
- **Target:** 100% of simple tasks have CHANGELOG entry
- **Measure:** PRs with CHANGELOG updates
- **Track:** Documentation compliance rate

**Scope Control:**
- **Target:** < 10% of simple tasks exceed simple task criteria
- **Measure:** Tasks that should have used full SDLC
- **Track:** Scope classification accuracy

### Collecting Metrics

**Automated (via ADW):**
- Cycle time tracked in `adw_state.json`
- Validation results logged
- Test coverage captured

**Manual Tracking:**
```bash
# Add to PR template
- [ ] Task completed within estimated time? (Y/N)
- [ ] Validation commands executed? (Y/N)
- [ ] Any regressions found? (Y/N)
```

**Review Dashboard:**
- Track metrics in project management tool
- Weekly review of trends
- Quarterly process improvements

---

## Version History

**v1.0.0** - Initial release
- Complete 5-stage SDLC framework
- ADW integration guide
- Task type templates
- Validation checklists
- Examples and quick reference

---

## Additional Resources

**Related Documentation:**
- `adw/README.md` - Complete ADW system documentation
- `.claude/TAC-PRINCIPLES.md` - TAC framework principles
- `.claude/validation-checklists/` - Detailed validation checklists
- `docs/templates/` - Task-specific templates

**Validation Checklists:**
- `.claude/validation-checklists/feature-validation.md`
- `.claude/validation-checklists/bug-validation.md`
- `.claude/validation-checklists/chore-validation.md`

**Slash Commands:**
- `.claude/commands/feature.md`
- `.claude/commands/bug.md`
- `.claude/commands/chore.md`
- `.claude/commands/implement.md`
- `.claude/commands/test.md`
- `.claude/commands/review.md`

**ADW Workflows:**
- `adw/adw_plan_iso.py`
- `adw/adw_build_iso.py`
- `adw/adw_test_iso.py`
- `adw/adw_review_iso.py`
- `adw/adw_sdlc_iso.py`
- `adw/adw_sdlc_zte_iso.py`

---

## Getting Help

**Questions about this framework?**
- Review examples in this document
- Check ADW documentation: `adw/README.md`
- Consult validation checklists
- Ask team members for guidance

**Process not working?**
- Review common pitfalls section
- Check if task qualifies as "simple"
- Consider using full SDLC for complex tasks
- Provide feedback for framework improvements

**Contributing Improvements:**
- Submit issues for unclear sections
- Propose new examples
- Share project-specific customizations
- Contribute to template library

---

**Remember:** The goal is high-quality simple task execution with minimal overhead. Start with the full process, then optimize based on your context.
