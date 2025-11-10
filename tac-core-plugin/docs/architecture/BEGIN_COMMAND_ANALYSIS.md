# `/begin` Command - Analysis & Improvement Recommendations

> **📅 Last Updated:** 2025-11-07
> **✅ Status:** Refactored to use lean context approach (eliminates redundant project-context.md)

## Recent Improvements (Nov 2025)

**Completed:**
- ✅ Eliminated separate `project-context.md` file (redundant with CLAUDE.md + README)
- ✅ Refactored `/begin` to append lean context directly to CLAUDE.md
- ✅ Reduced setup questions from 5-7 to 3 focused, high-value questions
- ✅ Focused only on information AI cannot infer (conventions, behavioral rules)
- ✅ Improved time savings: 12-17 minutes (down from 10-15 minutes)

**Rationale:**
- project-context.md was redundant - overlapped with CLAUDE.md and README
- 70% of generated content (tech stack, directory structure, dependencies) can be inferred
- Only 30% (coding conventions, behavioral rules) provides genuine value
- Single file (CLAUDE.md) easier to maintain than split across multiple files

---

## What `/begin` Does

The `/begin` command is an **intelligent task router** that serves as the primary entry point for working with the agentic coding framework. It operates in two distinct modes:

### Mode 1: Setup Mode (First-Time Use)

**Trigger:** When `.claude/project-context.md` does not exist

**What it does:**
1. **Auto-detects tech stack** by checking for:
   - `package.json` → Node.js/JavaScript/TypeScript
   - `pyproject.toml`, `requirements.txt` → Python
   - `go.mod` → Go
   - `Cargo.toml` → Rust
   - `pom.xml`, `build.gradle` → Java

2. **Analyzes existing files** to minimize user questions:
   - Reads `README.md` for project name, purpose, description
   - Reads `package.json`/`pyproject.toml` for dependencies
   - Scans directory structure to understand layout
   - Checks for `.env.example` to list environment variables
   - Detects CI/CD setup (`.github/workflows`, `.gitlab-ci.yml`)

3. **Interviews user** with only 3-5 focused questions:
   - Project purpose (if not in README)
   - Development stage (MVP / Development / Production)
   - Dev commands (if not obvious from scripts)
   - Critical context (what AI should never do / ask first)

4. **Auto-generates `.claude/project-context.md`** with:
   - Tech stack (language, framework, database, dependencies)
   - Codebase structure
   - Environment variables
   - Coding conventions
   - Development workflow (setup, dev, test, build commands)
   - AI behavioral rules (always do, never do, ask first)

**Time Saved:** 10-15 minutes (vs manual template filling)

### Mode 2: Task Routing Mode (Normal Use)

**Trigger:** When `.claude/project-context.md` exists

**What it does:**

1. **Gathers Context:**
   - Reads `.claude/project-context.md` to understand project
   - Runs `git status` and `git branch` to check current state
   - Asks user: "What would you like to work on today?"

2. **Analyzes Task Type** by detecting keywords:
   - **New Development:** "add", "create", "build", "implement"
   - **GitHub Issue:** "issue #123", "fix issue", "work on #45"
   - **Bug Fix:** "bug", "broken", "not working", "error"
   - **Investigation:** "understand", "explain", "how does"
   - **Maintenance:** "refactor", "cleanup", "chore"
   - **Testing:** "test", "validate", "check"
   - **Documentation:** "document", "write docs"

3. **Checks Prerequisites:**
   - For ADW workflows: Environment variables, `adw/` directory, GitHub issue
   - For manual workflows: Commands availability
   - For complex tasks: Knowledge gap check needed

4. **Recommends Optimal Workflow** with:
   - **Task classification** (Feature/Bug/Chore/Investigation)
   - **Best approach** (Manual Commands / ADW Automated / Setup Required)
   - **Reasoning** (3 reasons why this approach fits)
   - **Time estimate** (hands-on vs total time)
   - **Exact next steps** (copy-paste ready commands)
   - **Decision factors** (why this was recommended)
   - **Alternative approaches** (other valid options)

5. **Provides 6 Common Workflow Patterns:**
   - **Pattern A:** Manual feature (spec → feature → implement → test → review)
   - **Pattern B:** Automated feature (`adw_sdlc_iso.py`)
   - **Pattern C:** Quick manual bug fix
   - **Pattern D:** Automated bug fix (`adw_plan_build_test_iso.py`)
   - **Pattern E:** Codebase investigation (`/prime`)
   - **Pattern F:** Zero-touch automation (`adw_sdlc_zte_iso.py`)

---

## Current Strengths

### 1. **Zero Manual Setup**
- Eliminates 15-20 minutes of template filling
- AI does the heavy lifting of project detection
- Only asks what it cannot infer

### 2. **Intelligent Detection**
- Supports 5+ programming languages
- Reads existing files to extract information
- Understands project structure automatically

### 3. **Context-Aware Routing**
- Analyzes task type from natural language
- Checks prerequisites before recommending workflows
- Provides reasoning for recommendations

### 4. **Actionable Guidance**
- Exact commands (copy-paste ready)
- Clear decision factors
- Alternative approaches offered

### 5. **Comprehensive Pattern Library**
- 6 pre-defined workflow patterns
- Covers manual and automated approaches
- Includes time estimates

---

## Identified Gaps & Limitations

### Gap 1: No Integration with Meta-ADW Strategy System

**Problem:**
- `/begin` has hardcoded pattern recommendations (Pattern A-F)
- Meta-ADW system (`adw/meta_strategy.py`) provides intelligent workflow recommendations based on task complexity, but `/begin` doesn't use it
- No learning from past successes/failures

**Impact:**
- Users get generic recommendations instead of optimized ones
- No confidence scores for recommendations
- Missing alternative workflow suggestions from meta-ADW
- Can't leverage strategy validation checks

**Example:**
User says "Add authentication" → `/begin` suggests manual workflow
But meta-ADW would:
1. Interview about complexity (simple OAuth vs custom JWT system)
2. Analyze task characteristics (complexity 1-10, effort, risks)
3. Recommend workflow with 85% confidence
4. Provide 2 alternatives with tradeoffs
5. Suggest validation strategy (L5/L6/L7)

### Gap 2: Limited Task Type Detection

**Problem:**
- Only 7 task types recognized (Feature/Bug/Chore/Investigation/Testing/Documentation/Maintenance)
- Keyword-based classification is simplistic
- No complexity assessment (1-10 scale)
- No effort estimation beyond time
- No risk analysis

**Impact:**
- Can miss nuanced task requirements
- No differentiation between "simple feature" and "complex feature"
- All features treated equally in recommendations

**Example:**
"Add a button" vs "Add real-time collaborative editing" → both classified as "Feature" with same recommendation

### Gap 3: No Validation Strategy Recommendations

**Problem:**
- `/begin` recommends workflows but doesn't specify validation level
- Doesn't suggest whether to use:
  - L5 (unit tests only)
  - L6 (unit + integration)
  - L7 (unit + integration + E2E)
- No guidance on test coverage expectations

**Impact:**
- Users might under-test critical features
- Over-test simple features (wasting time)
- No alignment between task risk and validation rigor

### Gap 4: Static Workflow Patterns

**Problem:**
- 6 hardcoded patterns (A-F)
- Can't adapt to novel task types
- No custom workflow creation
- No learning from project-specific patterns

**Impact:**
- Users with unique workflows forced into pre-defined patterns
- Can't handle edge cases effectively
- No project-specific optimization

**Example:**
Project with custom deployment pipeline → `/begin` can't recommend custom workflow

### Gap 5: No Project History Analysis

**Problem:**
- Doesn't check recent commits (`git log`)
- Doesn't check GitHub issue history
- Doesn't learn from past workflow successes
- No pattern recognition from previous work

**Impact:**
- Can't say "last 3 features used Pattern B successfully"
- Can't detect project velocity trends
- No proactive suggestions based on history

### Gap 6: Limited Multi-Repo Support

**Problem:**
- Doesn't detect if this is a monorepo
- No guidance for coordinating changes across multiple repos
- Assumes single-repo workflow

**Impact:**
- Poor recommendations for monorepo projects
- No guidance on cross-repo dependencies

### Gap 7: No Time/Cost Estimation

**Problem:**
- Generic time estimates ("15-20 min planning, 45-60 min implementation")
- No API cost estimation for ADW workflows
- No consideration of model selection (base vs heavy)

**Impact:**
- Users surprised by long-running workflows
- No budget awareness for API usage

### Gap 8: Missing Environment Health Check

**Problem:**
- Checks if environment variables exist, but doesn't validate them
- Doesn't check API key validity
- Doesn't check GitHub PAT permissions
- Doesn't verify Claude Code CLI availability

**Impact:**
- Recommends ADW workflows that will fail
- User wastes time starting workflows that error out

---

## Improvement Recommendations

### Priority 1: Integrate Meta-ADW Strategy System

**Implementation:**

1. **Modify `/begin` to call Meta-ADW when ADW workflows are viable:**

```markdown
## Step 4: Recommend Workflow (UPDATED)

### If ADW is available and task is complex:

1. Call meta-ADW strategy system:
   ```bash
   cd adw/
   uv run meta_strategy.py --task-description "<user_input>"
   ```

2. Parse meta-ADW recommendation:
   - Primary workflow (with confidence score)
   - Alternative workflows
   - Validation strategy (L5/L6/L7)
   - Complexity score (1-10)
   - Estimated effort
   - Risk factors

3. Present recommendation using meta-ADW output:
   ```
   ## 🎯 Recommended Workflow (AI-Optimized)

   **Task Complexity:** 7/10
   **Recommended Approach:** ADW SDLC Pipeline (85% confidence)
   **Validation Strategy:** L6 (Unit + Integration tests)

   **Why This Approach:**
   - High complexity benefits from automated SDLC
   - Integration tests needed for cross-module changes
   - Similar tasks succeeded with this workflow (3/3 past cases)

   **Alternative Approaches:**
   - Manual workflow (if you want more control) - 65% confidence
   - ADW Plan+Build only (if time-constrained) - 70% confidence
   ```

4. Fallback to hardcoded patterns if meta-ADW unavailable
```

**Benefits:**
- Intelligent recommendations based on task analysis
- Confidence scores help users make informed decisions
- Learning from past outcomes improves over time
- Validation strategy alignment with task risk

**Effort:** 2-3 hours
**Risk:** Low (meta-ADW is already built, just needs integration)

---

### Priority 2: Enhanced Task Classification

**Implementation:**

Add complexity assessment to task analysis:

```markdown
## Step 2: Analyze Task Type (UPDATED)

After classifying task type, assess complexity:

1. **Ask clarifying questions:**
   - "Does this involve new external APIs or services?" (+2 complexity)
   - "Does this require database schema changes?" (+2 complexity)
   - "Does this affect multiple modules/services?" (+1 complexity)
   - "Is this security-critical?" (+2 complexity)
   - "Is this user-facing?" (+1 complexity)

2. **Calculate complexity score (1-10):**
   - 1-3: Simple (single file, < 100 LOC, no dependencies)
   - 4-6: Moderate (multiple files, some dependencies)
   - 7-9: Complex (cross-module, external services, testing required)
   - 10: Critical (security, data migration, high risk)

3. **Use complexity to tune recommendations:**
   - Simple (1-3): Manual workflow, quick iteration
   - Moderate (4-6): Manual or ADW based on user preference
   - Complex (7-9): ADW recommended, validation critical
   - Critical (10): ADW + heavy model + L7 validation + manual review
```

**Benefits:**
- Differentiate between trivial and complex features
- Right-size validation effort
- Better model selection (base vs heavy)

**Effort:** 1-2 hours
**Risk:** Low (additive feature)

---

### Priority 3: Add Validation Strategy Recommendations

**Implementation:**

```markdown
## Step 4.5: Recommend Validation Strategy (NEW)

Based on task complexity and risk:

### L5 Validation (Unit Tests Only)
**When:**
- Complexity: 1-3
- Low risk: Internal refactoring, style changes, docs
- No external dependencies affected

**Commands:**
```bash
/test  # Run unit tests with auto-fix
```

### L6 Validation (Unit + Integration)
**When:**
- Complexity: 4-6
- Medium risk: API changes, module interactions
- External dependencies but controlled

**Commands:**
```bash
/test                  # Unit tests
/test --integration    # Integration tests
```

### L7 Validation (Unit + Integration + E2E)
**When:**
- Complexity: 7-10
- High risk: User-facing changes, security, data integrity
- Critical paths affected

**Commands:**
```bash
/test                  # Unit tests
/test --integration    # Integration tests
/test --e2e           # End-to-end tests
/review               # Manual review
```

**Present validation strategy in recommendation:**
```
## 🧪 Recommended Validation Strategy: L6

Based on task complexity (6/10) and medium risk profile:
- ✓ Unit tests (fast feedback)
- ✓ Integration tests (catch cross-module issues)
- ✗ E2E tests (not needed for internal API)

Estimated validation time: 10-15 minutes
```
```

**Benefits:**
- Right-sized testing effort
- Clear expectations on validation rigor
- Reduces under-testing and over-testing

**Effort:** 1 hour
**Risk:** Low (documentation-focused)

---

### Priority 4: Environment Health Check

**Implementation:**

```markdown
## Step 0.5: Environment Health Check (NEW)

Before recommending ADW workflows, validate environment:

1. **Check environment variables:**
   ```bash
   # Check if set
   echo $GITHUB_REPO_URL
   echo $ANTHROPIC_API_KEY
   echo $GITHUB_PAT  # optional

   # Validate API key
   curl https://api.anthropic.com/v1/messages \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01"
   ```

2. **Check GitHub access:**
   ```bash
   gh auth status
   gh repo view $GITHUB_REPO_URL
   ```

3. **Check Claude Code CLI:**
   ```bash
   which claude || echo "Claude CLI not found"
   ```

4. **Check worktree availability:**
   ```bash
   git worktree list | wc -l  # Max 15 worktrees
   ```

5. **Report health status:**
   ```
   ## ✅ Environment Health Check

   ✓ ANTHROPIC_API_KEY valid
   ✓ GitHub access configured
   ✓ Claude CLI available at /usr/local/bin/claude
   ✓ 3/15 worktrees in use

   ADW workflows are ready to use!
   ```

   Or:
   ```
   ## ⚠️ Environment Health Check

   ✗ GITHUB_PAT not set (some ADW features unavailable)
   ⚠️ 14/15 worktrees in use (close to limit)

   Recommendation: Use manual workflows or clean up worktrees
   ```
```

**Benefits:**
- Prevents workflow failures
- Clear feedback on what's misconfigured
- Proactive worktree management

**Effort:** 2 hours
**Risk:** Low (read-only checks)

---

### Priority 5: Project History Analysis

**Implementation:**

```markdown
## Step 1.5: Analyze Project History (NEW)

Before recommending workflow, learn from past work:

1. **Check recent commits:**
   ```bash
   git log --oneline -10
   ```
   Parse commit messages to identify:
   - Common task types (feat: / fix: / chore:)
   - Frequency of features vs bugs
   - Recent areas of activity

2. **Check GitHub issue patterns:**
   ```bash
   gh issue list --state closed --limit 20
   ```
   Analyze:
   - Average issue completion time
   - Which labels are used most
   - Success rate of auto- labels

3. **Check ADW history:**
   ```bash
   ls agents/ | wc -l  # How many ADW workflows run
   ls agents/*/adw_state.json | xargs grep "all_adws"
   ```
   Identify:
   - Most common ADW pattern
   - Success rate (completed vs abandoned)

4. **Use history to inform recommendation:**
   ```
   ## 📊 Project Context

   Based on recent history:
   - 8/10 recent tasks were features (you're in growth mode)
   - 6/8 used ADW SDLC pipeline successfully
   - Average completion time: 45 minutes

   Recommendation: Continue with ADW SDLC for consistency
   ```
```

**Benefits:**
- Learn from project-specific patterns
- Recommend what has worked before
- Detect project velocity trends

**Effort:** 2-3 hours
**Risk:** Medium (parsing git/GitHub data)

---

### Priority 6: Custom Workflow Design

**Implementation:**

Integrate with Meta-ADW's `/strategy/design_custom_adw` command:

```markdown
## Step 4: Recommend Workflow (UPDATED)

### If task doesn't fit standard patterns:

1. Detect novel task:
   - No matching keyword pattern
   - User says "I want to do something custom"
   - Complexity score > 8 with unique requirements

2. Offer custom workflow design:
   ```
   ## 🎯 Custom Workflow Needed

   This task doesn't fit standard patterns. I can design a custom workflow for you.

   Would you like me to:
   1. Use /strategy/design_custom_adw to create a tailored workflow
   2. Adapt an existing pattern to your needs
   3. Walk you through manual steps interactively
   ```

3. If user chooses #1, run:
   ```
   /strategy/design_custom_adw
   ```
   This will:
   - Interview about task requirements
   - Design custom ADW workflow
   - Generate workflow script
   - Provide validation checklist
```

**Benefits:**
- Handle edge cases gracefully
- Empower users with unique workflows
- Expand pattern library over time

**Effort:** 1 hour (integration only, design_custom_adw exists)
**Risk:** Low (uses existing Meta-ADW feature)

---

### Priority 7: Multi-Repo Detection

**Implementation:**

```markdown
## Step 1.5: Detect Multi-Repo Setup (NEW)

1. **Check for monorepo markers:**
   - `lerna.json`, `nx.json` → Monorepo
   - Multiple `package.json` in subdirs → Monorepo
   - `workspaces` in root `package.json` → Monorepo

2. **Check for multi-repo coordination:**
   - `.git/config` has multiple remotes → Multi-repo
   - `repos/` directory exists → Multi-repo hub

3. **Adjust recommendations for multi-repo:**
   ```
   ## 🏗️ Multi-Repo Detected

   This is a monorepo with 4 packages detected.

   **Recommended Workflow:**
   - Use ADW with `--repo` flag to target specific package
   - Consider impact on sibling packages
   - Run integration tests across all affected packages

   **Example:**
   ```bash
   uv run adw_sdlc_iso.py <issue> --repo packages/api
   ```
   ```
```

**Benefits:**
- Better recommendations for monorepos
- Avoid breaking sibling packages
- Proper test coordination

**Effort:** 2 hours
**Risk:** Medium (depends on monorepo structure variety)

---

### Priority 8: Cost & Time Estimation

**Implementation:**

```markdown
## Step 4: Recommend Workflow (UPDATED)

Add detailed estimates to recommendations:

### Time Estimation:
```
**Estimated Timeline:**
- Planning: 5-10 minutes
- Implementation: 30-45 minutes
- Testing: 10-15 minutes
- Review: 5 minutes
**Total: 50-75 minutes** (15 min hands-on, 35-60 min automated)
```

### Cost Estimation (for ADW workflows):
```
**Estimated API Cost:**
- Planning agent: ~$0.50 (Sonnet)
- Implementation agent: ~$2.00 (Sonnet)
- Testing agent: ~$1.00 (Sonnet with retries)
- Review agent: ~$1.50 (Sonnet)
**Total: ~$5.00**

Using heavy model set would cost ~$15-20.
```

### Model Selection Recommendation:
```
**Recommended Model Set:** Base (Sonnet)

Reasons:
- Task complexity (6/10) doesn't require Opus
- Cost-effective for iterative development
- Upgrade to heavy if base fails

Switch to heavy model by adding to issue description:
```
model_set heavy
```
```
```

**Benefits:**
- No surprises on time or cost
- Informed decision on model selection
- Budget awareness

**Effort:** 2 hours
**Risk:** Low (estimation logic only)

---

## Implementation Roadmap

### Phase 1: Quick Wins (4-6 hours)
- ✅ Priority 3: Validation strategy recommendations
- ✅ Priority 6: Custom workflow integration
- ✅ Priority 8: Cost/time estimation

### Phase 2: Core Enhancements (8-10 hours)
- ✅ Priority 1: Meta-ADW integration
- ✅ Priority 2: Enhanced task classification
- ✅ Priority 4: Environment health check

### Phase 3: Advanced Features (6-8 hours)
- ✅ Priority 5: Project history analysis
- ✅ Priority 7: Multi-repo detection

### Total Effort: 18-24 hours

---

## Success Metrics

After implementing improvements, measure:

1. **Setup Time Reduction:**
   - Target: < 3 minutes average setup time
   - Track: Time from `/begin` to first task start

2. **Recommendation Accuracy:**
   - Target: 80%+ users accept primary recommendation
   - Track: How often users choose alternative workflows

3. **Workflow Success Rate:**
   - Target: 85%+ workflows complete without errors
   - Track: ADW completion rate after `/begin` recommendation

4. **User Satisfaction:**
   - Target: "Very helpful" rating from 80%+ users
   - Track: Feedback on recommendation quality

5. **Cost Efficiency:**
   - Target: < $10 average per feature implementation
   - Track: API costs for completed workflows

---

## Conclusion

The `/begin` command is already powerful, but integrating with Meta-ADW, adding environment health checks, and providing validation strategy recommendations would make it **truly intelligent**.

**Biggest Impact Changes:**
1. **Meta-ADW Integration** - Transforms static patterns into learning system
2. **Environment Health Check** - Prevents 90% of workflow failures
3. **Validation Strategy** - Right-sizes testing effort

**Next Steps:**
1. Implement Phase 1 quick wins
2. Test with real projects
3. Iterate based on usage data
4. Roll out Phase 2 & 3
