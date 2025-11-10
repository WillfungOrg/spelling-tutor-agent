# TAC Core Plugin

> Complete TAC (Tactical Agentic Coding) framework for AI-driven development workflows

## Overview

The TAC Core Plugin provides a comprehensive set of commands, workflows, hooks, and automation tools for effective AI-assisted software development. It consolidates best practices from TAC-5, TAC-6, and TAC-7, focusing on production-ready isolation patterns and full SDLC automation.

## Features

### 🎯 Core Capabilities

- **39 Slash Commands** - Organized by workflow stage (planning, implementation, testing, validation, integration)
- **14 ADW Workflows** - Isolated worktree-based automation (plan, build, test, review, document, ship)
- **7 Hook System** - Extensible event-driven architecture
- **9 E2E Test Commands** - Comprehensive end-to-end testing scenarios

### 🔒 Worktree Isolation

- Each ADW runs in isolated git worktree: `trees/<adw_id>/`
- Deterministic port allocation (Backend: 9100-9114, Frontend: 9200-9214)
- Concurrent execution support (up to 15 instances)
- Persistent state management: `agents/<adw_id>/adw_state.json`

### 🚀 Zero-Touch Execution

- Full SDLC automation: Plan → Build → Test → Review → Document → Ship
- Optional auto-merge to main branch (`adw_sdlc_zte_iso.py`)
- Confidence-based workflow selection (85%+ threshold)

## Installation

### Quick Setup

1. **Copy plugin to your project:**
   ```bash
   cp -r path/to/tac-core-plugin /path/to/your-project/.claude/plugins/tac-core
   ```

2. **Install dependencies:**
   ```bash
   cd /path/to/your-project
   pip install anthropic python-dotenv pydantic requests
   # Optional: pytest playwright (for E2E testing)
   ```

3. **Configure environment:**
   ```bash
   # Required
   export ANTHROPIC_API_KEY="sk-ant-..."

   # Optional (for ADW automation)
   export GITHUB_REPO_URL="https://github.com/owner/repo"
   export GITHUB_PAT="ghp_..."
   export CLAUDE_CODE_PATH="/path/to/claude-code"
   ```

4. **Initialize with `/begin`:**
   - Run `/begin` in Claude Code
   - AI will analyze your project
   - Auto-generates `CLAUDE.md "Project-Specific Context" section`
   - Recommends optimal workflows

## Commands

### Core Commands (`/commands/core/`)

| Command | Description | Use When |
|---------|-------------|----------|
| `/install` | Install project dependencies | Initial setup |
| `/prime` | Prepare environment and context | Starting session |
| `/start` | Start development servers | Running application |
| `/tools` | List available development tools | Exploring capabilities |
| `/health_check` | Verify system health | Debugging issues |

### Planning Commands (`/commands/planning/`)

| Command | Description | Use When |
|---------|-------------|----------|
| `/begin` | **START HERE** - Intelligent router | Every new task |
| `/spec` | Generate detailed specifications | Before coding |
| `/knowledge_gap_check` | Identify missing context | Complex tasks |
| `/feature` | Create feature implementation plan | New features |
| `/bug` | Create bug fix plan | Resolving bugs |
| `/chore` | Create maintenance plan | Refactoring/cleanup |
| `/patch` | Create focused patch plan | Quick fixes |
| `/classify_issue` | Classify GitHub issue type | ADW automation |
| `/classify_adw` | Determine optimal ADW workflow | Workflow selection |
| `/generate_branch_name` | Generate semantic branch names | Git operations |
| `/track_agentic_kpis` | Update ADW performance metrics | Performance tracking |

### Implementation Commands (`/commands/implementation/`)

| Command | Description | Use When |
|---------|-------------|----------|
| `/implement` | Execute implementation plan | Building features |
| `/conditional_docs` | Determine documentation needs | Post-implementation |
| `/prepare_app` | Setup app for testing/review | Before validation |

### Testing Commands (`/commands/testing/`)

| Command | Description | Use When |
|---------|-------------|----------|
| `/test` | Run backend/frontend tests | Validating changes |
| `/test_e2e` | Execute E2E tests with Playwright | UI validation |
| `/resolve_failed_test` | Fix failing unit tests | Test failures |
| `/resolve_failed_e2e_test` | Fix failing E2E tests | E2E failures |

### Validation Commands (`/commands/validation/`)

| Command | Description | Use When |
|---------|-------------|----------|
| `/review` | Comprehensive code review | Pre-merge validation |
| `/in_loop_review` | Quick in-loop review | During development |
| `/document` | Generate documentation | Post-review |

### Integration Commands (`/commands/integration/`)

| Command | Description | Use When |
|---------|-------------|----------|
| `/commit` | Generate semantic commits | Committing changes |
| `/pull_request` | Create PR description | Opening PRs |

### Isolation Commands (`/commands/isolation/`)

| Command | Description | Use When |
|---------|-------------|----------|
| `/install_worktree` | Setup isolated worktree | ADW initialization |
| `/cleanup_worktrees` | Remove old worktrees | Cleanup |

### E2E Test Commands (`/commands/e2e/`)

9 comprehensive E2E test scenarios covering:
- Basic and complex queries
- SQL injection protection
- Input debouncing
- Random query generation
- Export functionality (CSV, JSON)
- Enhanced drop zone interactions
- Data generation

## ADW Workflows

### Entry Points (Create Worktrees)

```bash
# Planning workflow - creates worktree and spec
uv run workflows/adw_plan_iso.py <issue-number>

# Patch workflow - creates worktree for quick fixes
uv run workflows/adw_patch_iso.py <issue-number>
```

### Single Phase Workflows (Require Existing Worktree)

```bash
# Implementation phase
uv run workflows/adw_build_iso.py <issue-number> <adw-id>

# Testing phase with auto-fix
uv run workflows/adw_test_iso.py <issue-number> <adw-id>

# Review phase with screenshots
uv run workflows/adw_review_iso.py <issue-number> <adw-id>

# Documentation generation
uv run workflows/adw_document_iso.py <issue-number> <adw-id>
```

### Multi-Phase Workflows

```bash
# Plan + Build
uv run workflows/adw_plan_build_iso.py <issue-number>

# Plan + Build + Test
uv run workflows/adw_plan_build_test_iso.py <issue-number>

# Plan + Build + Review (skip test)
uv run workflows/adw_plan_build_review_iso.py <issue-number>

# Plan + Build + Test + Review
uv run workflows/adw_plan_build_test_review_iso.py <issue-number>

# Plan + Build + Document
uv run workflows/adw_plan_build_document_iso.py <issue-number>
```

### Complete SDLC Workflows

```bash
# Full pipeline: Plan → Build → Test → Review → Document → PR
uv run workflows/adw_sdlc_iso.py <issue-number>

# Zero-Touch Execution (⚠️ auto-merges to main!)
uv run workflows/adw_sdlc_zte_iso.py <issue-number>
```

### Finalization

```bash
# Approve and ship PR to main
uv run workflows/adw_ship_iso.py <issue-number> <adw-id>
```

## Hook System

The plugin includes 7 production-ready hooks:

| Hook | Purpose | Event |
|------|---------|-------|
| `notification.py` | Event notifications | All tool calls |
| `pre_tool_use.py` | Tool execution interception | Before tool use |
| `post_tool_use.py` | Tool result processing | After tool use |
| `stop.py` | Workflow control | Agent stop |
| `subagent_stop.py` | Subagent control | Subagent stop |
| `pre_compact.py` | Context optimization | Before compaction |
| `user_prompt_submit.py` | Prompt processing | User input |

### Hook Configuration

To enable hooks, add to `.claude/settings.json`:

```json
{
  "hooks": {
    "notification": {
      "enabled": true,
      "script": ".claude/plugins/tac-core/hooks/notification.py"
    },
    "pre_tool_use": {
      "enabled": true,
      "script": ".claude/plugins/tac-core/hooks/pre_tool_use.py"
    }
  }
}
```

## Webhook Automation (Phone-to-PR)

Enable fully automated workflows triggered by GitHub issues:

### Quick Start

**1. Start the webhook server:**
```bash
# From your project root (after loading plugin)
.claude/scripts/start_adw_services_simple.sh
```

**2. Tell AI to start it:**
Just say:
```
Start the webhook server
```

Or add to your project's `CLAUDE.md "Project-Specific Context" section`:
```markdown
## Webhook Automation

To enable phone-to-PR automation:
```bash
.claude/scripts/start_adw_services_simple.sh
```

This starts:
- Cloudflare tunnel (temporary public URL)
- Webhook server (receives GitHub events)
- Queue worker (processes workflows in background)

The script will display your webhook URL and GitHub setup instructions.
```

**3. Configure GitHub webhook:**
The startup script displays exact setup instructions. Copy the URL and secret shown.

### How It Works

1. **Create GitHub issue** with `adw_plan_iso` in the body
2. **Webhook receives** the issue creation event
3. **Workflow launches** automatically in isolated worktree
4. **PR created** when complete
5. **Zero laptop interaction** required!

### Supported Triggers

Include these in issue body or comments:
- `adw_plan_iso` - Planning only
- `adw_sdlc_iso` - Full SDLC (plan → build → test → review → PR)
- `adw_sdlc_zte_iso` - Zero-touch execution (auto-merges!)

### Advanced: Label-Based Routing

Configure labels in GitHub (requires queue_manager.py):
- `auto-plan` - Planning workflow
- `auto-build` - Plan + Build
- `auto-test` - Plan + Build + Test
- `auto-sdlc` - Complete SDLC

See `QUICK_START_NO_DOMAIN.md` for detailed setup guide.

---

## Architecture

### ADW State Structure

Each workflow maintains persistent state in `agents/<adw_id>/adw_state.json`:

```json
{
  "adw_id": "abc12345",
  "issue_number": 123,
  "branch_name": "feat-123-add-authentication",
  "plan_file": "specs/feat-123-spec.md",
  "issue_class": "/feature",
  "worktree_path": "trees/abc12345/",
  "backend_port": 9107,
  "frontend_port": 9207,
  "model_set": "base"
}
```

### Workflow Modules

The `workflows/adw_modules/` directory contains core orchestration logic:

- `agent.py` - Claude Code CLI integration
- `data_types.py` - ADW state and data models
- `workflow_ops.py` - Workflow orchestration logic
- `worktree_ops.py` - Git worktree management
- `git_ops.py` - Git operations
- `github.py` - GitHub API integration
- `state.py` - State persistence
- `utils.py` - Utility functions

## Usage Examples

### Example 1: Feature Development (Manual)

```bash
# 1. Start with intelligent router
/begin "Add user authentication"

# 2. AI recommends workflow, you choose to go manual
# 3. Check for knowledge gaps
/knowledge_gap_check

# 4. Create specification
/spec

# 5. Generate feature plan
/feature

# 6. Implement
/implement

# 7. Test
/test

# 8. Review
/review

# 9. Commit and PR
/commit
/pull_request
```

### Example 2: Feature Development (Automated)

```bash
# Complete SDLC in one command (issue #456)
cd workflows/
uv run adw_sdlc_iso.py 456

# Workflow automatically:
# 1. Creates isolated worktree
# 2. Generates specification
# 3. Implements changes
# 4. Runs tests (with auto-fix)
# 5. Performs review (with screenshots)
# 6. Generates documentation
# 7. Creates pull request
```

### Example 3: Zero-Touch Execution

```bash
# Fully automated with auto-merge (⚠️ use carefully!)
uv run adw_sdlc_zte_iso.py 789

# After successful SDLC, automatically:
# - Ships to main branch
# - Deletes feature branch
# - Cleans up worktree
```

## Configuration Files

### Required: `CLAUDE.md`

Use `/begin` to auto-generate, or manually create:

```markdown
# Project Context

## Tech Stack
- Backend: FastAPI (Python)
- Frontend: Vite + React (TypeScript)
- Database: PostgreSQL

## Key Components
- Authentication: JWT-based
- API: RESTful with OpenAPI
- Testing: Pytest + Playwright

## Development Workflow
1. Feature branches from `main`
2. PR review required
3. CI/CD via GitHub Actions
```

### Optional: `settings.example.json`

Example configuration included in plugin. Copy to `.claude/settings.json` and customize.

## Best Practices

### 1. Always Start with `/begin`

The intelligent router saves time by:
- Analyzing your project context
- Understanding task requirements
- Recommending optimal approach
- Providing exact next steps

### 2. Use Knowledge Gap Check

Before complex tasks:
```bash
/knowledge_gap_check
```

Prevents outdated patterns and missing context.

### 3. Spec-First Development

Never skip specification:
```bash
/spec
```

Even for small changes. Specs prevent scope creep and ensure clarity.

### 4. Leverage ADW Automation

For standard workflows, use ADW instead of manual commands:
- Faster execution (parallel operations)
- Consistent quality (automated validation)
- Better tracking (persistent state)

### 5. Cleanup Worktrees

After merging PRs:
```bash
git worktree list
git worktree remove trees/<adw_id>
# Or use: /cleanup_worktrees
```

## Troubleshooting

### Port Conflicts

```bash
# Check port usage
lsof -i :9100

# ADW uses deterministic port allocation:
# Backend: 9100-9114
# Frontend: 9200-9214
```

### Worktree Issues

```bash
# List all worktrees
git worktree list

# Remove stuck worktree
git worktree remove trees/<adw_id> --force

# Prune references
git worktree prune
```

### Claude Code CLI Not Found

```bash
# Set CLAUDE_CODE_PATH
export CLAUDE_CODE_PATH="/path/to/claude-code-cli"

# Or install globally
npm install -g @anthropic-ai/claude-code
```

## Compatibility

- **Python**: >= 3.11
- **Claude Code**: >= 1.0.0
- **TAC Versions**: TAC-5, TAC-6, TAC-7 compatible
- **Git**: >= 2.30 (for worktree support)

## Repository Structure

```
tac-core-plugin/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── commands/
│   ├── core/                    # Core commands (5)
│   ├── planning/                # Planning commands (11)
│   ├── implementation/          # Implementation commands (3)
│   ├── testing/                 # Testing commands (4)
│   ├── validation/              # Validation commands (3)
│   ├── integration/             # Integration commands (2)
│   ├── isolation/               # Isolation commands (2)
│   └── e2e/                     # E2E tests (9)
├── workflows/
│   ├── adw_modules/             # Core workflow modules
│   ├── adw_*_iso.py            # ADW workflow scripts (14)
│   ├── adw_tests/              # Test utilities
│   └── adw_triggers/           # Automation triggers
├── hooks/
│   ├── *.py                     # Hook implementations (7)
│   └── utils/                   # Hook utilities
├── docs/
│   ├── TAC-PRINCIPLES.md       # Framework principles
│   ├── TAC-QUICK-START.md      # Getting started guide
│   └── TAC-IMPROVEMENTS-SUMMARY.md
├── validation-checklists/
│   ├── feature-validation.md
│   ├── bug-validation.md
│   └── chore-validation.md
├── templates/
│   ├── spec-template.md
│   └── project-context template.md
├── settings.example.json        # Configuration example
└── README.md                    # This file
```

## Contributing

This plugin consolidates TAC framework best practices. When contributing:

1. Test changes in isolated project first
2. Update plugin.json if adding commands/workflows
3. Document new features in this README
4. Follow TAC principles (spec-first, closed-loop validation)

## License

MIT License - See parent repository for details

## Support

- **Documentation**: See `docs/` directory
- **Issues**: https://github.com/willfung28/agentic-coding-library/issues
- **TAC Course**: https://github.com/willfung28/tac-course

---

**Version**: 1.0.0
**Author**: willfung28
**Repository**: https://github.com/willfung28/agentic-coding-library
