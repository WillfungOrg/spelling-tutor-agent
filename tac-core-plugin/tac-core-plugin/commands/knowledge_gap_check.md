# Knowledge Gap Check

**Purpose:** Identify AI knowledge gaps before starting work to prevent outdated or incorrect implementations.

**When to use:** Before starting any feature, bug fix, or significant work.

**TAC Principle:** Knowledge Gap Pre-Fill (Principle 2)

---

## What This Command Does

1. Analyzes the task requirements
2. Identifies what knowledge/context AI needs
3. Checks for training data cutoff issues
4. Recommends resources to fill gaps
5. Verifies environment and project context

---

## Instructions for AI

You are performing a knowledge gap check. Follow these steps systematically:

### Step 1: Understand the Task

First, clearly understand what needs to be done:
- What is the objective?
- What technologies/frameworks are involved?
- What parts of the codebase will be affected?

### Step 2: Identify Knowledge Gaps

Check for potential knowledge gaps in these categories:

#### A. Framework/Library Versions
- What frameworks/libraries are required?
- What versions are being used in this project?
- Is my training data current for these versions?
- Have there been breaking changes since my knowledge cutoff?

#### B. Project-Specific Context
- Does CLAUDE.md have a "Project-Specific Context" section?
- Do I understand the codebase structure?
- Do I know the coding conventions?
- Are environment variables documented?

#### C. External Dependencies
- Are there external APIs or services?
- Do I have current documentation for them?
- Are there authentication/authorization patterns I need to know?

#### D. Domain Knowledge
- Is there domain-specific terminology?
- Are there business rules I need to understand?
- Are there compliance/regulatory requirements?

### Step 3: Check Available Resources

Before asking the user, check what's already available:

1. **Read Project-Specific Context from CLAUDE.md:**
   ```bash
   Read CLAUDE.md
   # Look for "Project-Specific Context" section
   ```

2. **Check for specs:**
   ```bash
   Glob pattern: .claude/specs/*.md
   ```

3. **List available MCP servers:**
   - Can I access official documentation via MCP?
   - Are there project-specific MCP resources?

4. **Review recent similar work:**
   ```bash
   git log --oneline --all -20
   ```

### Step 4: Report Knowledge Gaps

Present findings in this format:

```markdown
## Knowledge Gap Analysis

### ✅ What I Know
- [List what you're confident about]
- [Include versions/patterns you're familiar with]
- [Note any recent similar work]

### ❓ What I Need to Know
- [List specific knowledge gaps]
- [Note why each gap matters]
- [Estimate impact if gap isn't filled]

### 🔧 How to Fill Gaps
- [Specific resources needed]
- [MCP servers to connect]
- [Files to read]
- [Documentation to reference]

### ⚠️ Risks of Proceeding Without Filling Gaps
- [What could go wrong]
- [Outdated patterns that might be used]
- [Potential rework required]
```

### Step 5: Recommend Next Steps

Based on the analysis, recommend:

1. **If no gaps:** Proceed with confidence
2. **If minor gaps:** Suggest quick reads/references
3. **If major gaps:** Request specific resources before proceeding
4. **If critical gaps:** Recommend research phase first

---

## Example Usage

### Example 1: Adding OAuth2 Authentication

**User:** "I want to add OAuth2 authentication"

**AI Response:**
```markdown
## Knowledge Gap Analysis

### ✅ What I Know
- OAuth2 flow patterns (authorization code, client credentials, etc.)
- General security best practices
- Your tech stack: Node.js + Express (from CLAUDE.md Project-Specific Context)

### ❓ What I Need to Know
- Which OAuth2 library you prefer (passport? oauth4webapi? custom?)
- Your identity provider (Google? Auth0? Custom?)
- Token storage strategy (sessions? JWT? cookies?)
- Current authentication implementation (to integrate with)

### 🔧 How to Fill Gaps
1. Check for existing auth code:
   - Grep pattern: "auth|login|session"
   - Look for passport config or JWT middleware
2. If using specific library, would benefit from:
   - Official docs via Archon MCP
   - Your preferred OAuth provider's docs
3. Read:
   - .claude/specs/ (any existing auth specs?)
   - Environment variables (.env.example)

### ⚠️ Risks of Proceeding Without Filling Gaps
- Might choose incompatible library
- Could conflict with existing auth patterns
- May not follow your security standards
- Potential rework if assumptions are wrong

**Recommendation:** Please clarify OAuth provider and preferred library before I create the spec.
```

### Example 2: Fixing a Performance Bug

**User:** "API endpoint /users is slow"

**AI Response:**
```markdown
## Knowledge Gap Analysis

### ✅ What I Know
- Your stack: Python + FastAPI (from CLAUDE.md Project-Specific Context)
- General performance optimization techniques
- Database query optimization patterns

### ❓ What I Need to Know
- Current performance metrics (how slow? target?)
- Database being used (PostgreSQL? MongoDB?)
- ORM/database library (SQLAlchemy? Prisma?)
- Whether caching is already implemented
- Load patterns (concurrent users? data volume?)

### 🔧 How to Fill Gaps
1. **Immediate checks I can do:**
   - Read /users endpoint code
   - Check for N+1 queries
   - Look for missing indexes
   - Review error logs

2. **Would benefit from:**
   - Performance monitoring data (New Relic? DataDog?)
   - Database query logs
   - Recent load test results

3. **MCP resources:**
   - FastAPI latest docs (if using patterns from 2024+)
   - Database-specific optimization guides

### ⚠️ Risks of Proceeding Without Filling Gaps
- Might optimize wrong bottleneck
- Could miss database-specific optimization
- May not meet performance target
- Potential unnecessary infrastructure changes

**Recommendation:**
1. Let me analyze the endpoint code first
2. Then provide current vs target performance metrics
3. I'll create focused spec based on findings
```

---

## When to Skip This Check

You can skip explicit knowledge gap check for:

- **Trivial changes:** Typo fixes, formatting
- **Familiar patterns:** Repeated similar work in same codebase
- **Emergency hotfixes:** Fix first, document after
- **Exploratory work:** Learning by doing is the goal

For everything else, **always check knowledge gaps first**.

---

## Integration with Other Commands

### Automatically Triggered By:
- `/start` - Includes knowledge gap check
- `/prime` - Comprehensive project analysis includes gaps

### Manually Use Before:
- `/feature` - Before creating feature plan
- `/bug` - Before creating bug fix plan
- `/implement` - Before executing any implementation

### Outputs Used By:
- `/spec` - Gap analysis informs spec creation
- Project context updates
- Resource gathering phase

---

## Success Criteria

A good knowledge gap check:

✅ Identifies specific gaps, not vague "I might need..."
✅ Explains why each gap matters
✅ Provides actionable steps to fill gaps
✅ Estimates risk of proceeding without filling
✅ Takes <2 minutes to complete

❌ Avoid generic "I might need documentation"
❌ Don't list gaps that don't affect this specific task
❌ Don't ask for resources that are already available

---

## Common Knowledge Gaps by Task Type

### For Features
- Latest framework/library versions
- API design patterns in this project
- Authentication/authorization approach
- Testing patterns (unit/integration/e2e)

### For Bugs
- Expected vs actual behavior
- Recent changes that might have caused it
- Relevant error logs
- Reproduction steps

### For Chores
- Project conventions (formatting, linting)
- Dependency update policies
- Breaking change migration patterns
- Team workflow preferences

---

## Related Resources

- **TAC Principles:** TAC-PRINCIPLES.md in docs - Principle 2
- **Project Context:** CLAUDE.md "Project-Specific Context" section - Should answer most gaps
- **MCP Servers:** Connect to official docs when needed
- **Similar Work:** `git log` shows recent patterns

---

**Remember:** 2 minutes checking gaps saves hours of wrong-direction work.
