# TAC Core Plugin - Installation Guide

## What is This Plugin?

The TAC Core Plugin is a collection of **slash commands**, **Python automation scripts**, and **hooks** for effective AI-assisted development with Claude Code.

**Important**: This is NOT a traditional plugin that you "install" - it's a **collection of files** that you copy to your project.

## Quick Understanding

### What Works WITHOUT API Key
- **All slash commands** (`.md` files) - These just provide instructions to Claude Code
- **All hooks** - Event-driven scripts that enhance Claude Code behavior
- No ANTHROPIC_API_KEY needed for these!

### What REQUIRES API Key
- **ADW workflows** (`workflows/*.py`) - These call Claude API programmatically
- You need: `export ANTHROPIC_API_KEY="sk-ant-..."`

## Installation Methods

### Method 1: Copy Commands Only (Recommended for Beginners)

Copy just the slash commands to get started:

```bash
# In your project directory
cp -r /path/to/tac-core-plugin/commands/* .claude/commands/
```

**What you get:**
- 39 slash commands organized by category
- No API key required
- Commands work immediately in Claude Code

**Example usage:**
```
/begin           # Intelligent task router
/spec            # Generate specification
/feature         # Create feature plan
/implement       # Execute implementation
/test            # Run tests
/review          # Code review
/commit          # Generate commit message
/pull_request    # Create PR description
```

### Method 2: Full Installation (Commands + Workflows)

For complete automation with ADW workflows:

```bash
# In your project directory
# 1. Copy commands
cp -r /path/to/tac-core-plugin/commands/* .claude/commands/

# 2. Copy workflows (requires API key)
cp -r /path/to/tac-core-plugin/workflows ./adw

# 3. Copy hooks (optional)
cp -r /path/to/tac-core-plugin/hooks .claude/hooks/

# 4. Copy documentation
cp -r /path/to/tac-core-plugin/docs .claude/docs/
cp -r /path/to/tac-core-plugin/validation-checklists .claude/
cp -r /path/to/tac-core-plugin/templates ./templates

# 5. Set up environment
export ANTHROPIC_API_KEY="sk-ant-..."
export GITHUB_REPO_URL="https://github.com/owner/repo"  # optional
export GITHUB_PAT="ghp_..."  # optional
```

**What you get:**
- All 39 slash commands
- 14 ADW automation workflows
- 7 production hooks
- Full SDLC automation

## Setup Steps

### 1. Install Dependencies (Only if using workflows)

```bash
pip install anthropic python-dotenv pydantic requests

# Optional: for testing
pip install pytest playwright
```

### 2. Configure Environment

Create `.env` file in your project:

```bash
# Required for ADW workflows
ANTHROPIC_API_KEY=sk-ant-...

# Optional
GITHUB_REPO_URL=https://github.com/yourusername/yourrepo
GITHUB_PAT=ghp_...  # For private repos
CLAUDE_CODE_PATH=/usr/local/bin/claude-code
```

### 3. Create Project Context

Run `/begin` in Claude Code to auto-generate `CLAUDE.md "Project-Specific Context" section`:

```
/begin
```

Claude will:
1. Analyze your project structure
2. Detect tech stack
3. Ask 3-5 clarifying questions
4. Generate complete project context
5. Recommend optimal workflow

## Understanding the Structure

After installation, your project will have:

```
your-project/
├── .claude/
│   ├── commands/           # Slash commands (39 total)
│   │   ├── core/          # install, prime, start, tools, health_check
│   │   ├── planning/      # begin, spec, feature, bug, chore, etc.
│   │   ├── implementation/
│   │   ├── testing/
│   │   ├── validation/
│   │   ├── integration/
│   │   ├── isolation/
│   │   └── e2e/
│   ├── hooks/             # Event-driven scripts (optional)
│   ├── docs/              # TAC documentation
│   └── CLAUDE.md # Auto-generated context
├── adw/                   # ADW workflows (if installed)
│   ├── adw_modules/       # Core automation modules
│   └── adw_*.py          # Workflow scripts
└── .env                   # Your API keys
```

## Usage Examples

### Example 1: Using Slash Commands Only (No API Key)

```bash
# 1. Start your session
/prime

# 2. Get intelligent recommendations
/begin "Add user authentication"

# 3. Create spec
/spec

# 4. Generate feature plan
/feature

# 5. Check implementation
/implement

# 6. Review code
/review

# 7. Generate commit
/commit
```

**Cost**: $0 (uses your existing Claude Code session)

### Example 2: Using ADW Workflows (Requires API Key)

```bash
# Full SDLC automation for GitHub issue #123
cd adw/
uv run adw_sdlc_iso.py 123

# This automatically:
# - Creates isolated worktree
# - Generates specification
# - Implements changes
# - Runs tests (with auto-fix)
# - Performs code review
# - Generates documentation
# - Creates pull request
```

**Cost**: Depends on complexity (uses Anthropic API directly)

## Command Categories

### Core Commands (5)
- `/install` - Install dependencies
- `/prime` - Prime environment
- `/start` - Start servers
- `/tools` - List available tools
- `/health_check` - Check system health

### Planning Commands (11)
- `/begin` - **START HERE** - Intelligent router
- `/spec` - Generate specification
- `/knowledge_gap_check` - Identify missing context
- `/feature`, `/bug`, `/chore` - Create plans
- `/patch` - Quick fixes
- `/classify_issue` - Classify GitHub issues
- `/classify_adw` - Determine workflow
- `/generate_branch_name` - Semantic branch names
- `/track_agentic_kpis` - Track metrics

### Implementation (3)
- `/implement` - Execute plan
- `/conditional_docs` - Check doc needs
- `/prepare_app` - Setup for testing

### Testing (4)
- `/test` - Run tests
- `/test_e2e` - Run E2E tests
- `/resolve_failed_test` - Fix test failures
- `/resolve_failed_e2e_test` - Fix E2E failures

### Validation (3)
- `/review` - Code review
- `/in_loop_review` - Quick review
- `/document` - Generate docs

### Integration (2)
- `/commit` - Generate commits
- `/pull_request` - Create PRs

### Isolation (2)
- `/install_worktree` - Setup worktree
- `/cleanup_worktrees` - Clean up

### E2E Tests (9)
9 Playwright-based test scenarios

## Frequently Asked Questions

### Do I need Claude API key to use this?

**For slash commands**: NO
**For ADW workflows**: YES

### Can I use this without Python?

Yes! The slash commands are just markdown files that work with Claude Code directly. No Python needed.

### Can I customize the commands?

Absolutely! All `.md` files can be edited to fit your project's needs.

### How much does this cost?

- **Slash commands**: Free (uses your Claude Code session)
- **ADW workflows**: Varies based on usage (uses Anthropic API)

### What if I don't have GitHub?

Slash commands work without GitHub. ADW workflows have some GitHub integration but can be adapted.

## Troubleshooting

### "Command not found"

Make sure you copied files to `.claude/commands/` in your project root.

### "API key missing"

Only needed for ADW workflows. Set: `export ANTHROPIC_API_KEY="sk-ant-..."`

### "Python module not found"

Install dependencies: `pip install anthropic python-dotenv pydantic requests`

### "Port already in use"

ADW uses ports 9100-9114 (backend) and 9200-9214 (frontend). Check: `lsof -i :9100`

## Next Steps

1. **Start with `/begin`** - Let AI guide you
2. **Try slash commands** - No API key needed
3. **Explore workflows** - When you need automation
4. **Customize** - Edit commands for your needs
5. **Share** - Help others with your improvements

## Support

- **Issues**: https://github.com/willfung28/agentic-coding-library/issues
- **TAC Course**: https://github.com/willfung28/tac-course
- **Documentation**: See `docs/` directory

---

**Version**: 1.0.0
**License**: MIT
**Author**: willfung28
