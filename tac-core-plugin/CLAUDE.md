# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Repository Overview

**Name:** Agentic Coding Library

**Purpose:** A comprehensive framework library containing TAC (The Agentic Coder) principles, ADW (AI Developer Workflow) automation system, and reusable slash commands for effective AI-assisted development.

**Primary Use:**
1. **Template library** to be copied into new projects to accelerate AI-driven development workflows
2. **Centralized webhook hub** for multi-repository automation via GitHub webhooks

**Current Status:** Production-ready webhook system serving multiple repositories in organization.

---

## 📋 File Organization

**IMPORTANT:** When creating new files, follow the structure defined in `.claude/FILE_ORGANIZATION.md`

**Quick Rules:**
- Documentation → `docs/` (with subdirectories: `setup/`, `architecture/`)
- Python workflows → `adw/`
- Utility scripts → `scripts/`
- Slash commands → `.claude/commands/`
- NEVER create files in root (except CLAUDE.md, README.md)

**See `.claude/FILE_ORGANIZATION.md` for complete guidelines.**

---

## Getting Started

**⭐ New to this project?** Use `/begin` - your intelligent brainstorming partner and workflow advisor.

### Enhanced Collaborative Discovery

**`/begin` now provides a complete 5-phase discovery and planning process:**

**Phase 0: Setup Check**
- Auto-detects if "Project-Specific Context" exists in CLAUDE.md
- If missing → Setup Mode (2-3 min interview → auto-append to CLAUDE.md)
- If exists → Collaborative Discovery Mode

**Phase 1: Collaborative Discovery & Brainstorming**
- Open-ended exploration: "What would you like to work on?"
- Active brainstorming: Provides ideas, suggestions, alternatives
- Helps crystallize vague ideas into clear objectives
- Scope refinement with user collaboration
- **Result:** Clear objective, scope, and success criteria confirmed by user

**Phase 2: Knowledge Gap Analysis**
- **Searches codebase** for existing context (specs, code patterns, tests, recent work)
- **Identifies knowledge gaps** (framework versions, APIs, domain knowledge)
- **Checks MCP resources** for official documentation availability
- **Requests web search permission** for latest best practices
- **Result:** Complete understanding of what's known vs. what's needed

**Phase 3: Context Gathering & Validation**
- Reads relevant codebase files
- Fetches external documentation (via MCP or web search with permission)
- Gathers domain knowledge from user
- Validates completeness before proceeding
- **Result:** Complete context summary with high confidence level

**Phase 4: Task Analysis**
- Classifies task type and complexity (1-10 scale)
- Estimates effort accurately
- Identifies constraints and requirements from codebase
- Assesses risks (technical, knowledge, process)
- **Result:** Informed understanding of task characteristics

**Phase 5: Workflow Recommendation**
- Recommends optimal workflow based on complete context
- Provides detailed implementation plan with exact commands
- Explains reasoning (why this approach fits)
- Suggests alternatives with trade-offs
- **Result:** Clear, actionable plan with user in control

**Command:** `/begin` (located in `tac-core-plugin/commands/begin.md`)

**Time Investment:** 5-10 minutes of discovery and context gathering

**Payoff:** Saves 30+ minutes of rework from missing knowledge or wrong approach

**Key Features:**
- ✅ Conversational and collaborative (not just Q&A)
- ✅ Provides ideas and suggestions (helps brainstorm)
- ✅ Proactive knowledge gap identification (integrated `/knowledge_gap_check`)
- ✅ Automatic codebase search (finds related work)
- ✅ External docs fetching (via MCP or web search)
- ✅ User always in control (permissions for searches)
- ✅ Flexible (can skip phases if context is complete)

---

## Key Systems

### 1. TAC Framework (The Agentic Coder)

Five core principles for effective AI coding:

1. **Spec-First Development** - Always write specifications before code
2. **Knowledge Gap Pre-Fill** - Identify and fill AI knowledge gaps upfront using `/knowledge_gap_check`
3. **Agent Perspective** - Structure for AI consumption, not human convenience
4. **Closed-Loop Validation** - Every task includes automated validation
5. **Template Engineering** - Reusable patterns and workflows

**Key Files:**
- `.claude/TAC-PRINCIPLES.md` - Full framework documentation
- `.claude/TAC-QUICK-START.md` - 5-minute getting started guide
- `.claude/TAC-IMPROVEMENTS-SUMMARY.md` - Implementation details

### 2. ADW System (AI Developer Workflow)

Automated SDLC workflows using isolated git worktrees. The `_iso` suffix means workflows run in isolated environments.

**Core Concept:** Each workflow gets a unique 8-character ADW ID (e.g., `abc12345`) and runs in its own worktree at `trees/<adw_id>/` with dedicated ports.

**Architecture:**
- **Isolation:** Git worktrees prevent conflicts (up to 15 concurrent instances)
- **Port Allocation:** Backend 9100-9114, Frontend 9200-9214
- **State Management:** Persistent state in `agents/<adw_id>/adw_state.json`
- **Modular Phases:** Plan → Build → Test → Review → Document → Ship

**Entry Points (Create Worktrees):**
- `adw/adw_plan_iso.py` - Planning phase
- `adw/adw_patch_iso.py` - Quick patches

**Dependent Workflows (Require Existing Worktree):**
- `adw/adw_build_iso.py` - Implementation
- `adw/adw_test_iso.py` - Testing with auto-fix
- `adw/adw_review_iso.py` - Review with screenshots
- `adw/adw_document_iso.py` - Documentation generation

**Orchestrators:**
- `adw/adw_sdlc_iso.py` - Complete SDLC pipeline
- `adw/adw_sdlc_zte_iso.py` - Zero-Touch Execution (auto-ships to main)
- `adw/adw_ship_iso.py` - Approve and merge PR

**Important:** ADW workflows require environment variables: `GITHUB_REPO_URL`, `ANTHROPIC_API_KEY`, and optionally `GITHUB_PAT`, `CLAUDE_CODE_PATH`.

### 3. Meta-ADW Strategy System

**Intelligent workflow advisor** that recommends optimal ADW workflows for any task.

**Problem Solved:** Decision paralysis from 30+ available templates. No guidance on validation strategy (L5 vs L6 vs L7).

**How it Works:**
1. **Interviews** you about task (7 questions: type, complexity, testing needs, etc.)
2. **Analyzes** task characteristics (complexity 1-10, effort, risks)
3. **Recommends** optimal workflow with confidence score + 2 alternatives
4. **Learns** from outcomes to improve future recommendations

**Quick Start:**
```bash
cd adw/
uv run meta_strategy.py <issue-number>
```

**Strategy Templates:**
- `/strategy/interview` - Gathers task information
- `/strategy/analyze` - Analyzes complexity and requirements
- `/strategy/recommend` - Recommends workflow strategy
- `/strategy/validate_plan` - Checks for validation gaps
- `/strategy/design_custom_adw` - Creates custom workflows for novel tasks

**Docs:**
- `adw/META_ADW_README.md` - Usage guide
- `adw/META_ADW_ARCHITECTURE.md` - Technical architecture
- `.tac/docs/meta-adw-examples.md` - Real-world examples

**When to Use:**
- Unsure which workflow to use
- Novel or complex task
- Want validation strategy recommendations
- Building learning data

### 4. TAC Core Plugin

**Single source of truth** for slash commands and workflows, distributed to target repositories.

**Location:** `tac-core-plugin/` - Contains all commands, workflows, templates, and validation checklists.

**Distribution:** Automatically installed into target repositories by webhook system when processing issues.

**Key Directories:**
- `tac-core-plugin/commands/` - Slash command templates
- `tac-core-plugin/workflows/` - ADW workflow definitions
- `tac-core-plugin/validation-checklists/` - Quality gates
- `tac-core-plugin/templates/` - Specification templates
- `tac-core-plugin/docs/` - Documentation
- `tac-core-plugin/scripts/` - Utility scripts

### 5. Webhook Multi-Repo System

**Centralized automation hub** that processes GitHub issues across multiple repositories.

**How it Works:**
1. GitHub organization webhook points to this repository's webhook server
2. Any repository in the organization can create issues with ADW labels
3. Webhook server receives event, clones target repo to `repos/<repo-name>/`
4. Auto-installs `tac-core-plugin/` into target repo
5. Executes ADW workflow in isolated worktree
6. Posts results back to GitHub issue

**Triggering Methods:**
- **Labels** (recommended): Add labels like `adw-plan`, `adw-sdlc`, `adw-patch` to issues
- **Issue body** (fallback): Include `adw_plan_iso` or similar commands in issue body
- **Comments** (manual): Comment `adw_plan_iso` on existing issues

**Label Support:** 19 predefined labels for different workflows:
- Planning: `adw-plan`, `adw-design`
- Quick fixes: `adw-patch`, `adw-hotfix`
- Complete workflows: `adw-sdlc`, `adw-full`, `adw-zte`
- Combined workflows: `adw-plan-build`, `adw-pbt`, `adw-pbtr`
- Testing: `adw-test`, `adw-e2e`
- Review: `adw-review`, `adw-document`
- Implementation: `adw-implement`, `adw-build`
- Model selection: `adw-heavy`, `adw-fast`
- Meta strategy: `adw-strategy`

**Setup:**
```bash
# Start webhook server
./start_adw_services_simple.sh

# Setup labels across all repos in organization
./scripts/setup_labels.sh

# Monitor webhook activity
tail -f /tmp/adw_logs/webhook.log
```

**Documentation:**
- `docs/WEBHOOK_LABEL_GUIDE.md` - Complete label reference
- `docs/WEBHOOK_MAINTENANCE.md` - Operations guide
- `docs/WEBHOOK_ARCHITECTURE_GUIDE.md` - Architecture decisions

**Repository Structure:**
- `repos/` - Cloned target repositories (gitignored)
- `agents/` - ADW state for each workflow instance (gitignored)
- `trees/` - Worktrees for isolated execution (gitignored)
- `logs/` - Execution logs (gitignored)

### 6. Slash Commands

Reusable workflow templates in `tac-core-plugin/commands/` for AI task execution.

**Core Commands:**
- `/begin` - **START HERE** - Intelligent router that analyzes your task and recommends the optimal workflow
- `/spec` - Generate detailed specifications (TAC Principle #1)
- `/knowledge_gap_check` - Identify missing context before starting work
- `/feature`, `/bug`, `/chore` - Create implementation plans
- `/implement` - Execute a plan
- `/review` - Validate against spec
- `/test` - Run validation tests with auto-fix
- `/commit` - Generate semantic commits
- `/pull_request` - Create PR descriptions

**Key Patterns:**
- Commands reference TAC principles at the top
- All specs use structured markdown with placeholders
- Validation commands are always included
- Commands are tech-stack agnostic (customized via project-context.md)

---

### 7. Learning System

**Self-improving AI** that learns from test outcomes, code reviews, deployment results, and manual Claude Code sessions to reduce mistakes over time.

**Purpose:** Passively collect feedback from every ADW execution AND manual Claude sessions, using deep code analysis to extract actionable insights that improve decision-making, prompt quality, and workflow recommendations.

**Key Files:**
- `adw/adw_modules/learning_extractor.py` - **NEW** Deep git diff analysis for actionable insights (600+ lines)
- `adw/adw_modules/manual_session_logger.py` - **NEW** Automatic manual session logging (450+ lines)
- `adw/adw_modules/learning_feedback.py` - Test, Review, and Deployment feedback collectors
- `adw/adw_modules/cross_project_learning.py` - Cross-project pattern aggregation
- `adw/adw_modules/prompt_refiner.py` - Self-Refine prompt improvement engine
- `adw/adw_modules/meta_adw_types.py` - Learning record schemas (supports both ADW & manual sessions)
- `.tac/learning/` - Local learning data (patterns, execution logs)
- `~/agentic-coding-library/.tac/learning/global/` - Global patterns shared across all projects

**How It Works:**

1. **Feedback Collection** (automatic for ALL work):

   **A. ADW-Automated Sessions:**
   - **Test Feedback** - Parses pytest output for pass/fail rates and failure patterns
   - **Review Feedback** - Fetches PR reviews via GitHub API, categorizes changes
   - **Deployment Feedback** - Checks deployment status and post-deployment errors

   **B. Manual Claude Code Sessions (NEW):**
   - **Automatic at conversation end** - Analyzes last 3 hours of git commits
   - **Intelligent decision logic** - Skips trivial work (1 file, <20 lines, <10 min)
   - **Logs valuable work** - 3+ files, 200+ lines, 30+ min, tests, or complexity indicators
   - **Deep code analysis** - Extracts actual learnings from git diffs, not just commit messages
   - **Session tracking** - Unique session IDs for manual work (format: `session-YYYYMMDD-HHMMSS-{hash}`)

2. **Enhanced Pattern Extraction (NEW):**

   **Traditional extraction:**
   - Creates `LearningRecord` with execution metrics
   - Stores in `.tac/learning/execution_logs/<adw-id>.json` or `session-{id}.json`

   **Deep code analysis** (uses `learning_extractor.py`):
   - **Error Pattern Detection** - Finds AttributeError, TypeError, KeyError patterns from diffs
   - **Schema Change Analysis** - Identifies Optional[] migrations, field additions, defaults
   - **API Change Tracking** - Detects function signature and return type changes
   - **Defensive Coding** - Finds None checks, early returns, try-except additions
   - **Problem-Solving Flow** - Categorizes as error-driven, test-driven, or feature-driven

   **Output format:**
   - `key_learnings` - Top 7 specific learnings (e.g., "Made task_type Optional to support multiple use cases")
   - `what_worked_well` - Top 5 best practices (e.g., "✓ Check if task_type is None before accessing")
   - `what_to_avoid` - Error patterns to prevent
   - `technical_patterns` - Top 5 reusable guidelines (e.g., "Use Optional[] for fields that don't apply to all record types")

   **Actionability:** 9/10 vs 2/10 with basic extraction (specific vs generic)

3. **Weight Retraining**:
   - Adjusts decision weights based on success rate (target: 70% → 85%)
   - Retrains after minimum 10 executions
   - Saves updated weights to `.tac/learning/decision_weights.json`

4. **Prompt Refinement** (Self-Refine pattern):
   - Generates suggestions from feedback (e.g., "Add security checklist" after security review changes)
   - Applies 3-5 iterations of refinement
   - Saves versioned prompts to `.tac/prompts/`
   - Tracks refinement history

5. **Cross-Project Learning**:
   - Aggregates patterns from local `.tac/learning/` to global store
   - Syncs best patterns back to all projects
   - Weighted averaging based on use counts
   - Tracks contributing projects

**Feature Flag:**
```bash
# Enable (default)
export ENABLE_ADW_LEARNING=true

# Disable
export ENABLE_ADW_LEARNING=false
```

**Manual Session Logging (NEW):**
```bash
# Trigger manually (if not automatic)
cd adw/
python -c "from adw_modules.manual_session_logger import log_manual_session; log_manual_session()"

# Force log even if decision logic says skip
python -c "from adw_modules.manual_session_logger import log_manual_session; log_manual_session(force=True)"

# Custom description and issue number
python -c "from adw_modules.manual_session_logger import log_manual_session; log_manual_session('Implemented auth feature', issue_number='123')"
```

**View Learning Data:**
```bash
# Local patterns
cat .tac/learning/pattern_database.json

# Execution logs - ADW sessions
ls .tac/learning/execution_logs/
cat .tac/learning/execution_logs/<adw-id>.json

# Execution logs - Manual sessions (NEW)
cat .tac/learning/execution_logs/session-20251108-104636-11e103f6.json

# Global patterns (shared across all projects)
cat ~/agentic-coding-library/.tac/learning/global/global_pattern_database.json

# Prompt refinement history
cat .tac/prompts/refinement_history.json

# Refined prompts
ls .tac/prompts/
```

**Example Learning Record Output:**
```json
{
  "key_learnings": [
    "Made task_type Optional to support multiple use cases",
    "Made complexity_score Optional to support multiple use cases"
  ],
  "what_worked_well": [
    "✓ Check if task_type is None before accessing attributes",
    "✓ Check if complexity_score is None before accessing attributes"
  ],
  "what_to_avoid": [],
  "technical_patterns": [
    "Use Optional[] for fields that don't apply to all record types",
    "Backward compatibility: make new fields Optional, not required",
    "Validate inputs early and return/skip if invalid"
  ]
}
```

**Success Metrics:**
- Test success rate: % of tests passing
- False fix rate: % of "fixes" that don't actually work
- Review change rate: % of PRs needing human changes
- Deployment success rate: % of successful deployments

**Goal:** Improve from 70% → 85% success rate over 50 executions.

**Integration:**
Learning is integrated into `meta_strategy.py` and called automatically after workflow completion when `ENABLE_ADW_LEARNING=true`.

---

## Development Commands

### ADW Workflows

```bash
# Process single issue with plan + build + test
cd adw/
uv run adw_plan_build_test_iso.py <issue-number>

# Complete SDLC (plan → build → test → review → document)
uv run adw_sdlc_iso.py <issue-number>

# Zero-Touch Execution (⚠️ auto-merges to main!)
uv run adw_sdlc_zte_iso.py <issue-number>

# Run individual phases (requires existing worktree from plan/patch)
uv run adw_build_iso.py <issue-number> <adw-id>
uv run adw_test_iso.py <issue-number> <adw-id>
uv run adw_review_iso.py <issue-number> <adw-id>
uv run adw_ship_iso.py <issue-number> <adw-id>

# Cleanup worktrees
git worktree list
git worktree remove trees/<adw_id>
```

### Validation

```bash
# These commands are used within specs for validation
cd app/server && uv run pytest                    # Backend tests
cd app/client && bun tsc --noEmit                 # Type checking
cd app/client && bun run build                    # Frontend build
```

---

## Repository Structure

```
agentic-coding-library/
├── tac-core-plugin/                  # Single source of truth for commands
│   ├── commands/                     # Slash command templates
│   │   ├── spec.md                   # Specification generation
│   │   ├── knowledge_gap_check.md    # Knowledge gap identification
│   │   ├── feature.md, bug.md        # Implementation planning
│   │   ├── implement.md              # Plan execution
│   │   ├── test.md                   # Validation testing
│   │   └── review.md                 # Spec compliance review
│   ├── workflows/                    # ADW workflow definitions
│   │   └── adw_modules/              # ⚠️ Core ADW modules (single source of truth)
│   │       ├── agent_sdk.py          # Agent SDK for slash commands
│   │       ├── data_types.py         # ADWState and models
│   │       ├── learning_extractor.py # **NEW** Deep git diff analysis (600+ lines)
│   │       ├── manual_session_logger.py # **NEW** Auto manual session logging (450+ lines)
│   │       ├── meta_adw_types.py     # Learning schemas (ADW & manual sessions)
│   │       ├── learning_feedback.py  # Feedback collectors
│   │       ├── learning_query.py     # Learning data queries
│   │       ├── decision_engine.py    # Strategy recommendation engine
│   │       ├── workflow_ops.py       # Workflow logic
│   │       ├── worktree_ops.py       # Worktree management
│   │       ├── git_ops.py            # Git operations
│   │       └── github.py             # GitHub API
│   ├── validation-checklists/        # Quality gates
│   │   ├── feature-validation.md
│   │   ├── bug-validation.md
│   │   └── chore-validation.md
│   ├── templates/                    # Specification templates
│   ├── docs/                         # Documentation
│   └── scripts/                      # Utility scripts
├── adw/                              # ADW workflow scripts (imports from tac-core-plugin)
│   ├── adw_plan_iso.py               # Planning workflow
│   ├── adw_build_iso.py              # Implementation workflow
│   ├── adw_test_iso.py               # Testing workflow
│   ├── adw_review_iso.py             # Review workflow
│   ├── adw_sdlc_iso.py               # Complete SDLC
│   └── adw_triggers/                 # Automation triggers
│       ├── trigger_cron.py           # Polling monitor
│       └── trigger_webhook.py        # Multi-repo webhook server
├── docs/                             # Webhook documentation
│   ├── WEBHOOK_LABEL_GUIDE.md        # Label-based triggering
│   ├── WEBHOOK_MAINTENANCE.md        # Operations guide
│   └── WEBHOOK_ARCHITECTURE_GUIDE.md # Architecture decisions
├── scripts/                          # Utility scripts
│   ├── setup_labels.sh               # Deploy labels to all repos
│   ├── cleanup_repos.sh              # Clean old repos/worktrees
│   └── tac-local-trigger.sh          # TAC issue fetcher
├── templates/                        # Project templates
│   ├── spec-template.md              # Specification template
│   └── project-context template.md   # Project setup template
├── start_adw_services_simple.sh      # Start webhook server
├── repos/                            # Cloned target repos (gitignored)
├── agents/                           # ADW workflow state (gitignored)
├── trees/                            # Isolated worktrees (gitignored)
├── logs/                             # Execution logs (gitignored)
└── specs/                            # Generated specifications
```

---

## Architecture Patterns

### ADW State Management

Each workflow creates persistent state in `agents/<adw_id>/adw_state.json`:

```python
{
  "adw_id": "abc12345",           # Unique workflow ID
  "issue_number": 123,            # GitHub issue number
  "branch_name": "feat-123-...",  # Git branch
  "plan_file": "specs/...",       # Implementation plan path
  "issue_class": "/feature",      # Issue type
  "worktree_path": "trees/...",   # Isolated worktree location
  "backend_port": 9107,           # Allocated backend port
  "frontend_port": 9207,          # Allocated frontend port
  "model_set": "base"             # "base" or "heavy" models
}
```

### Worktree Isolation

- Each ADW runs in `trees/<adw_id>/` with complete repo copy
- Deterministic port allocation based on ADW ID hash
- `.ports.env` file in worktree configures environment
- State stored outside worktree in `agents/<adw_id>/`

### Model Selection

Commands support "base" (fast/cheap) or "heavy" (complex tasks) model sets:

- Specify in GitHub issue: `model_set heavy`
- Default: "base" (uses Sonnet for most commands)
- Heavy: Uses Opus for `/implement`, `/document`, `/review`, etc.
- Mapping defined in `adw_modules/workflow_ops.py::SLASH_COMMAND_MODEL_MAP`

### Command Composition

Commands are composable:
1. Entry commands create worktrees (`/classify_issue` → `/feature` → plan)
2. Implementation commands require worktree (`/implement` in worktree context)
3. Validation commands run anywhere (`/test`, `/review`)
4. Integration commands finalize (`/commit`, `/pull_request`)

---

## Critical Workflows

### Starting New Work - Always Use `/begin` First! ⭐

**Best Practice:** Always start with `/begin` for any new task, even if you think you know what to do.

**Why `/begin` first:**
- Collaborative discovery helps crystallize vague ideas
- Proactive knowledge gap identification prevents rework
- Automatic codebase search finds relevant existing context
- Fetches latest external documentation when needed
- Recommends optimal workflow based on complete context
- 5-10 min upfront saves 30+ min of rework

**After `/begin` recommends a workflow, follow the suggested steps:**

### Manual Workflow (Recommended by `/begin` for exploratory work)

1. `/spec` - Create specification document
2. `/feature` or `/bug` or `/chore` - Generate implementation plan
3. `/implement` - Execute the plan
4. `/test` - Validate with auto-fix
5. `/review` - Check against spec
6. `/commit` - Generate semantic commit
7. `/pull_request` - Create PR description

**Note:** `/knowledge_gap_check` is now integrated into `/begin` Phase 2, so you don't need to run it separately!

### Automated SDLC (ADW)

```bash
# Full pipeline in isolated worktree
uv run adw/adw_sdlc_iso.py <issue-number>

# Pipeline creates:
# 1. Worktree at trees/<adw_id>/
# 2. Implementation plan in specs/
# 3. Implementation with tests
# 4. Review with screenshots
# 5. Documentation in app_docs/
# 6. Pull request on GitHub
```

### Zero-Touch Execution

```bash
# Complete SDLC + auto-ship (⚠️ merges to main!)
uv run adw/adw_sdlc_zte_iso.py <issue-number>

# Only use when:
# - Tests are comprehensive
# - Code review is automated
# - Ready for production deployment
```

---

## Important Conventions

### Branch Naming

Format: `{type}-{issue_number}-{adw_id}-{slug}`

Example: `feat-456-e5f6g7h8-add-user-authentication`

### Commit Messages

Follow semantic commit format via `/commit` command:
- `feat:` - New features
- `fix:` - Bug fixes
- `chore:` - Maintenance tasks
- `docs:` - Documentation
- `test:` - Test updates

### Specification Structure

All specs follow TAC Principle #1 (Spec-First):
- Clear objective
- Measurable success criteria
- Technical approach
- Step-by-step tasks
- Validation commands
- Out of scope items

---

## Common Pitfalls

1. **Skipping Knowledge Gap Check** - Using `/knowledge_gap_check` prevents outdated patterns
2. **Code-First Development** - Always create spec first, even for small tasks
3. **Manual Validation** - Include executable validation commands in specs
4. **Missing ADW ID** - Dependent workflows require existing worktree and ADW ID
5. **Port Conflicts** - Check `lsof -i :<port>` if ports are busy
6. **Worktree Cleanup** - Remove old worktrees with `git worktree remove`

---

## Setup Options

### Option 1: Webhook Automation (Recommended for Organizations)

**Zero setup per repository** - Use centralized webhook for all repos in your organization.

**Setup Once (5 minutes):**

1. **Start webhook server** in this repository:
   ```bash
   cd ~/agentic-coding-library
   ./start_adw_services_simple.sh
   ```

2. **Configure organization webhook** in GitHub:
   - Go to: `https://github.com/organizations/YOUR-ORG/settings/hooks`
   - Payload URL: `https://YOUR-TUNNEL-URL/gh-webhook` (from webhook startup logs)
   - Content type: `application/json`
   - Secret: (from `.env` file)
   - Events: Select "Issues" and "Issue comments"

3. **Deploy labels** to all repos:
   ```bash
   ./scripts/setup_labels.sh
   ```

**Use in any repo:**
1. Create GitHub issue
2. Add label (e.g., `adw-sdlc`, `adw-plan`, `adw-patch`)
3. Webhook automatically processes the issue
4. Results posted back to issue

**Benefits:**
- Zero per-repo configuration
- Automatic plugin distribution
- Centralized monitoring and logs
- Works across unlimited repositories

### Option 2: Manual Plugin Copy (For Single Projects)

**For projects outside your organization or local development.**

1. **Copy the plugin:**
   ```bash
   cd /path/to/your-new-project
   cp -r ~/agentic-coding-library/tac-core-plugin .
   ```

2. **Run `/begin`:**
   ```
   /begin
   ```

3. **Answer 3-5 questions:**
   - AI auto-detects your tech stack
   - AI auto-generates `tac-core-plugin/project-context.md`
   - AI asks only what it cannot infer
   - Time: 3-5 minutes

4. **Start working immediately:**
   - Tell AI what you want to do
   - AI recommends the optimal workflow
   - Follow the exact steps provided

### Option 3: Local ADW Automation

**For running ADW workflows locally without webhook.**

```bash
# Copy ADW system
cp -r ~/agentic-coding-library/adw /path/to/your-project/
cp -r ~/agentic-coding-library/tac-core-plugin /path/to/your-project/

# Configure environment
export GITHUB_REPO_URL="https://github.com/owner/repo"
export ANTHROPIC_API_KEY="sk-ant-..."

# Run workflows
cd adw/
uv run adw_sdlc_iso.py <issue-number>
```

**For Customization:**
- Commands in `tac-core-plugin/commands/` can be edited for project-specific needs
- Validation checklists in `tac-core-plugin/validation-checklists/` are customizable
- `project-context.md` can be manually updated anytime

---

## Testing the Framework

```bash
# Test model selection
python adw/adw_tests/test_model_selection.py

# Test worktree operations
git worktree list

# Test command availability
ls .claude/commands/
```

---

## Support Resources

**Webhook System:**
- `docs/WEBHOOK_LABEL_GUIDE.md` - Complete label reference with examples
- `docs/WEBHOOK_MAINTENANCE.md` - Monitoring, troubleshooting, cleanup
- `docs/WEBHOOK_ARCHITECTURE_GUIDE.md` - Architecture decisions

**TAC Framework:**
- `tac-core-plugin/docs/` - TAC principles and guides
- `SETUP_CHECKLIST.md` - Manual setup guide
- `TEMPLATE_SETUP.md` - Template customization

**ADW System:**
- `adw/README.md` - ADW automation details
- `adw/META_ADW_README.md` - Meta-strategy system
- `scripts/README.md` - Utility scripts

**Getting Started:**
- `QUICK_START_NO_DOMAIN.md` - Quick start without custom domain
- `CLOUDFLARE_TUNNEL_SETUP.md` - Cloudflare tunnel setup
- `DEPLOYMENT_OPTIONS.md` - Production deployment options

---

## Working with This Repository

This is a **library repository** serving two purposes:
1. **Template library** for copying to new projects
2. **Webhook hub** serving multiple repositories via GitHub webhooks

When making changes:

1. **Updating Commands:** Edit `tac-core-plugin/commands/*.md` files
2. **Updating ADW:** Modify `adw/adw_modules/` and workflow scripts
3. **Updating Webhook:** Modify `adw/adw_triggers/trigger_webhook.py`
4. **Testing Changes:**
   - For plugin: Copy to test project and validate
   - For webhook: Test with non-critical repository first
5. **Documentation:** Update this file when architecture changes
6. **Version Control:** All `tac-core-plugin/` and `adw/` changes should be committed

**⚠️ Important:**
- Changes to `tac-core-plugin/` affect all repositories using webhook automation
- Changes to webhook server affect all repositories in organization
- Test thoroughly before committing

**Webhook Restart Required:**
- After modifying `trigger_webhook.py`
- After updating `tac-core-plugin/` (for new repos only)
- Restart: Kill webhook process and run `./start_adw_services_simple.sh`

## Monitoring and Maintenance

**Webhook Logs:**
```bash
# Watch real-time activity
tail -f /tmp/adw_logs/webhook.log

# Check specific workflow
cat agents/<adw-id>/adw_state.json
cat logs/<session-id>/chat.json
```

**Cleanup:**
```bash
# Manual cleanup
./scripts/cleanup_repos.sh

# Check disk usage
du -sh repos/ trees/ agents/ logs/
```

**Health Checks:**
```bash
# Verify webhook is running
ps aux | grep trigger_webhook

# Check active worktrees
git worktree list

# List all ADW instances
ls -la agents/
```

---

## Project-Specific Context

> **Generated by `/begin`** 
> This section contains lean, high-value information that AI cannot infer from code alone.
> Run `/begin` to regenerate or update this section.

### Detected Tech Stack
- **Language:** Python 3.12
- **Framework:** N/A (library/framework repository)
- **Package Manager:** uv (detected from workflows)
- **Key Tools:** pytest, ruff, Claude Code CLI, Cloudflare tunnel

### Coding Conventions
- Follow standard Python conventions (PEP 8)
- Use snake_case for functions and variables
- Comprehensive docstrings for all public modules
- Type hints where beneficial

### Development Workflow Notes
**Commands:**
- Install: `uv sync` (for Python dependencies)
- Run webhook: `./tac-core-plugin/scripts/start_adw_services_simple.sh`
- Run tests: `pytest` (when implemented)
- Cleanup: `./scripts/cleanup_repos.sh`

**Critical notes:**
- Webhook server requires `GITHUB_WEBHOOK_SECRET`, `ANTHROPIC_API_KEY`, `GITHUB_PAT`
- ADW workflows need `GITHUB_REPO_URL` environment variable
- Webhook uses port 8000 (avoid conflicts with AirPlay on macOS)
- Multiple simultaneous worktrees supported (up to 15)

### AI Behavioral Rules

**🚫 NEVER do without approval:**
- Modify webhook server core logic (`trigger_webhook.py`, `queue_worker.py`)
- Change ADW state management (`adw_state.json` structure)
- Modify git worktree management (breaking changes affect all projects)
- Delete or restructure `tac-core-plugin/` (used by all target repos)

**✅ ALWAYS do:**
- Follow FILE_ORGANIZATION.md when creating new files
- Test webhook changes with non-critical repository first
- Update CLAUDE.md when architecture changes
- Keep commands in `tac-core-plugin/commands/` not `.claude/commands/`

**❓ ASK FIRST:**
- Adding new Python dependencies
- Changing ADW workflow behavior
- Modifying plugin distribution structure
- Changes affecting all target repositories

