# File Organization Guide

This document defines the canonical file structure for the agentic-coding-library repository. All AI agents and developers MUST follow these conventions when creating new files.

## 🎯 Core Principle

**Every file has a designated location. No files should be created in the root directory except those explicitly listed below.**

---

## 📁 Directory Structure & Rules

### Root Directory (/)
**ONLY these files are allowed in root:**
- `CLAUDE.md` - Claude Code instructions
- `README.md` - Main project documentation
- `.gitignore` - Git ignore rules
- `.env` - Environment variables (gitignored)
- `pyproject.toml` or `package.json` - Project dependencies (if applicable)

**NEVER create new markdown files or scripts in root.**

---

### `.claude/` - Claude Code Configuration
**Purpose:** Claude Code configuration and framework documentation

**Subdirectories:**
```
.claude/
├── commands/              # Slash commands (*.md) - NOT IN USE (deprecated, use tac-core-plugin/)
├── validation-checklists/ # Quality gates (*.md) - NOT IN USE (deprecated, use tac-core-plugin/)
├── specs/                 # Specification templates - NOT IN USE (deprecated, use tac-core-plugin/)
└── FILE_ORGANIZATION.md   # This file (library organization guide)
```

**Important:** The `.claude/` directory structure above is for the library itself. In target projects, this directory will be empty except for CLAUDE.md.

**Rules for Target Projects:**
- `CLAUDE.md` → Root of repository (contains framework docs + project-specific context)
- Commands → Use from `tac-core-plugin/commands/` (installed as plugin)
- Validation checklists → Use from `tac-core-plugin/validation-checklists/`
- Specification templates → Use from `tac-core-plugin/specs/`

---

### `adw/` - AI Developer Workflows (Automation)
**Purpose:** Python scripts for automated SDLC workflows

**Subdirectories:**
```
adw/
├── adw_modules/           # Shared Python modules
│   ├── agent.py           # Claude Code CLI integration
│   ├── data_types.py      # Pydantic models & ADWState
│   ├── workflow_ops.py    # Workflow operations
│   ├── worktree_ops.py    # Git worktree management
│   ├── git_ops.py         # Git operations
│   ├── github.py          # GitHub API
│   └── utils.py           # Utilities
├── adw_triggers/          # Webhook & automation triggers
│   ├── trigger_webhook.py # Webhook server
│   ├── trigger_cron.py    # Polling monitor
│   └── queue_worker.py    # Background worker
├── adw_plan_iso.py        # Planning workflow
├── adw_build_iso.py       # Implementation workflow
├── adw_test_iso.py        # Testing workflow
├── adw_patch_iso.py       # Quick patches
└── adw_sdlc_iso.py        # Complete SDLC pipeline
```

**Rules:**
- New workflow scripts → `adw/adw_*.py`
- Shared modules → `adw/adw_modules/`
- Triggers & webhooks → `adw/adw_triggers/`
- NEVER create Python files in root

---

### `tac-core-plugin/` - Single Source of Truth for Commands
**Purpose:** TAC Core Plugin distributed to target repositories

**Subdirectories:**
```
tac-core-plugin/
├── commands/              # Slash commands (copied to repos)
├── validation-checklists/ # Validation templates
├── specs/                 # Spec templates
├── workflows/             # ADW Python modules (symlink to ../../adw)
└── scripts/               # Startup scripts
    ├── start_adw_services_simple.sh
    └── install_worktree.sh
```

**Rules:**
- This is the distribution package
- Commands here override `.claude/commands/` in target repos
- DO NOT duplicate files - use symlinks where possible

---

### `docs/` - Documentation
**Purpose:** All project documentation and guides

**Subdirectories:**
```
docs/
├── setup/                 # Setup & deployment guides
│   ├── CLOUDFLARE_TUNNEL_SETUP.md
│   ├── WEBHOOK_SETUP.md
│   ├── QUICK_START_NO_DOMAIN.md
│   └── ...
├── architecture/          # Architecture & design docs
│   ├── PLUGIN_ARCHITECTURE.md
│   ├── PLUGIN_VS_SKILL_ANALYSIS.md
│   └── ...
├── WEBHOOK_LABEL_GUIDE.md        # Reference docs (root of docs/)
├── WEBHOOK_MAINTENANCE.md
└── FILE_MANAGEMENT_GUIDE.md
```

**Rules:**
- Setup guides → `docs/setup/`
- Architecture docs → `docs/architecture/`
- Reference guides → `docs/` root
- NEVER create `.md` files in project root

---

### `scripts/` - Utility Scripts
**Purpose:** Standalone utility scripts and tools

**Current files:**
```
scripts/
├── README.md                 # Script documentation
├── tac-local-trigger.sh      # Issue fetcher (in use)
├── setup_labels.sh           # Label deployment (in use)
├── cleanup_repos.sh          # Cleanup utility (in use)
└── [DEPRECATED - see below]
```

**Rules:**
- Utility bash scripts → `scripts/*.sh`
- Utility Python scripts → `scripts/*.py`
- Each script must have a purpose comment
- Update `scripts/README.md` when adding new scripts

**DEPRECATED Scripts (can be removed):**
- `tac_auto_processor.py` - Old TAC processor (replaced by ADW)
- `tac_auto_processor_cli.py` - Old CLI (replaced by ADW)
- `webhook_server.py` - Old webhook (replaced by adw/adw_triggers/)
- `build_template_index.py` - Template indexer (no longer used)
- `cleanup-template.sh` - Template cleanup (superseded by cleanup_repos.sh)

---

### `templates/` - Project Templates
**Purpose:** Boilerplate files for new projects

**Current structure:**
```
templates/
├── spec-template.md              # Feature specification template
├── project-context template.md   # Project context template
└── ...
```

**Rules:**
- Project templates only
- Each template must have clear placeholder markers
- Templates should be technology-agnostic

---

### `specs/` - Generated Specifications
**Purpose:** Implementation specifications created by workflows

**Rules:**
- Generated by ADW workflows
- Naming: `issue-{number}-adw-{id}-{description}.md`
- DO NOT manually edit generated specs
- These are git-tracked for reference

---

### `archive/` - Historical/Deprecated Code
**Purpose:** Old code kept for reference

**Rules:**
- Move deprecated code here instead of deleting
- Include a README explaining why code was archived
- Eventually can be deleted when no longer needed

---

### Runtime Directories (Git-Ignored)

#### `agents/` - ADW State Storage
**Purpose:** Persistent state for each ADW workflow instance
```
agents/
└── {adw-id}/
    ├── adw_state.json         # State persistence
    ├── adw_plan_iso/          # Logs per phase
    ├── adw_build_iso/
    └── ...
```

#### `repos/` - Multi-Repo Clones
**Purpose:** Cloned repositories for webhook system
```
repos/
└── {repo-name}/
    ├── ...                    # Cloned repo files
    └── trees/{adw-id}/        # Worktrees for this repo
```

#### `trees/` - Worktree Instances
**Purpose:** Isolated git worktrees for parallel workflows
```
trees/
└── {adw-id}/                  # One worktree per ADW instance
```

#### `logs/` - Execution Logs
**Purpose:** Agent execution logs and chat histories
```
logs/
└── {session-id}/
    ├── chat.json
    └── pre_compact.json
```

**Rules for Runtime Directories:**
- All git-ignored
- Auto-created by workflows
- Can be cleaned up periodically
- NEVER commit these directories

---

## 🚫 What NOT to Do

### ❌ DON'T create files in root
```
# BAD
/my-new-doc.md
/helper-script.py
/test-file.txt
```

### ❌ DON'T create random directories
```
# BAD
/misc/
/temp/
/old/
```

### ❌ DON'T duplicate documentation
```
# BAD - creates duplicate setup guide
/NEW_SETUP_GUIDE.md

# GOOD - uses existing structure
/docs/setup/NEW_SETUP_GUIDE.md
```

### ❌ DON'T put scripts in wrong locations
```
# BAD - utility script in adw/
/adw/my_utility.py

# GOOD - utility scripts in scripts/
/scripts/my_utility.py
```

---

## ✅ Decision Tree: Where Should This File Go?

### Is it a documentation file (.md)?
- **Setup guide?** → `docs/setup/`
- **Architecture doc?** → `docs/architecture/`
- **Reference guide?** → `docs/`
- **TAC framework doc?** → `.claude/`
- **Project README?** → Stay in root (exception)

### Is it a Python script?
- **ADW workflow?** → `adw/adw_*.py`
- **ADW module?** → `adw/adw_modules/`
- **Utility script?** → `scripts/`
- **Webhook/trigger?** → `adw/adw_triggers/`

### Is it a bash script?
- **Utility script?** → `scripts/`
- **Startup script?** → `tac-core-plugin/scripts/`
- **Cleanup script?** → `scripts/`

### Is it a slash command?
- **New command?** → `.claude/commands/`
- **Command override?** → `tac-core-plugin/commands/`

### Is it a template?
- **Specification template?** → `.claude/specs/` or `templates/`
- **Project template?** → `templates/`

### Is it configuration?
- **Claude Code config?** → `.claude/`
- **Environment vars?** → `.env` (root)
- **Python dependencies?** → `pyproject.toml` (root, if applicable)

---

## 📋 Cleanup Checklist

### Files to Remove:
- [ ] `scripts/tac_auto_processor.py` (deprecated)
- [ ] `scripts/tac_auto_processor_cli.py` (deprecated)
- [ ] `scripts/webhook_server.py` (replaced by adw/adw_triggers/)
- [ ] `scripts/build_template_index.py` (no longer used)
- [ ] `scripts/cleanup-template.sh` (replaced by cleanup_repos.sh)

### Directories to Remove:
- [ ] `.claude.backup/` (old backup)
- [ ] `.claude-plugin/` (old plugin structure)
- [ ] `tac-plugin-clean/` (temporary cleanup copy)

---

## 🔄 Migration Notes

When copying this library to a new project:

1. **Copy `CLAUDE.md` to project root** (framework documentation)
2. **Run `/begin` in target project** (auto-generates project-specific context in CLAUDE.md)
3. **Install `tac-core-plugin/` if using commands** (optional - provides slash commands)
4. **Copy `adw/` if using ADW workflows** (optional - for automation)
5. **DO NOT copy:** `agents/`, `repos/`, `trees/`, `logs/`, `.claude.backup/`, `templates/`

**Note:** No need to manually fill templates - `/begin` handles setup automatically!

---

## 📝 Maintaining This Guide

When adding new directories or changing structure:

1. Update this file first
2. Update `CLAUDE.md` references
3. Update `README.md` structure section
4. Document in relevant module READMEs

**This document is the source of truth for file organization.**
