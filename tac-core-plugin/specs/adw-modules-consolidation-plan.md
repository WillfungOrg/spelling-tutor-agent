# ADW Modules Consolidation - Implementation Plan

## Executive Summary
The adw_modules codebase has confusing structure with empty `adw/adw_modules/` directory while the real source lives in `tac-core-plugin/workflows/adw_modules/`. This plan consolidates everything into tac-core-plugin for single source of truth.

## Current State Analysis

### Directory Structure
```
agentic-coding-library/
├── adw/
│   ├── adw_modules/           ← EMPTY (only __pycache__)
│   └── adw_triggers/          ← EMPTY
└── tac-core-plugin/
    └── workflows/
        ├── adw_modules/       ← ALL 22 MODULES (real source)
        │   ├── __init__.py
        │   ├── agent.py
        │   ├── agent_sdk.py
        │   ├── workflow_ops.py (JUST FIXED: removed execute_template_async)
        │   ├── data_types.py
        │   ├── state.py
        │   ├── git_ops.py
        │   ├── github.py
        │   ├── worktree_ops.py
        │   ├── utils.py
        │   ├── learning_*.py (6 files)
        │   └── ... (22 files total)
        ├── adw_*.py           ← 15+ workflow scripts
        └── adw_triggers/      ← Trigger files
```

### Problems Identified
1. ❌ Empty `adw/adw_modules/` misleads developers
2. ❌ Webhook tries to copy from `adw/` (which doesn't exist)
3. ❌ Import confusion between `tac-core-plugin/workflows/adw_modules` and expected `adw/adw_modules`
4. ❌ Recent bug: `execute_template_async` import error (FIXED)

## Solution Design

### Approach
**Keep everything in tac-core-plugin** (it's already there!) and:
1. Delete empty `adw/` directory entirely
2. Remove webhook code that tries to copy from `adw/`
3. Ensure tac-core-plugin is the ONLY thing distributed

### Benefits
✅ Single source of truth (`tac-core-plugin/workflows/adw_modules/`)
✅ No confusion about which directory to update
✅ Simpler webhook (only copies tac-core-plugin)
✅ No library_root path bugs
✅ Clear module import paths

## Implementation Steps

### Step 1: Verify Current State ✓
- [x] Confirm `adw/adw_modules/` is empty
- [x] Confirm all modules in `tac-core-plugin/workflows/adw_modules/`
- [x] Count files: 22 Python modules

### Step 2: Remove Empty Directories
```bash
# Remove empty adw directory structure
rm -rf adw/
```

### Step 3: Update Webhook Distribution Code
**File:** `webhook-hub/triggers/trigger_webhook.py`

**Current Code (lines 199-216):**
```python
# Check if adw directory exists in target repo
adw_path = os.path.join(repo_path, "adw")

if not os.path.exists(adw_path):
    logger.info(f"Installing adw modules in {repo_name}")
    # Copy adw from library to target repo
    library_root = os.path.dirname(webhook_hub_dir)
    library_adw = os.path.join(library_root, "adw")

    if os.path.exists(library_adw):
        import shutil
        shutil.copytree(library_adw, adw_path)
        logger.info(f"ADW modules installed in {repo_name}")
    else:
        logger.error(f"ADW source not found at {library_adw}")
        raise FileNotFoundError(f"ADW source not found at {library_adw}")
else:
    logger.info(f"ADW modules already exist in {repo_name}")
```

**Action:** DELETE this entire block (lines 199-216)
**Reason:** adw_modules is already inside tac-core-plugin, so copying tac-core-plugin is sufficient

### Step 4: Verify No Other References to `adw/`
Search for references:
```bash
grep -r "adw/" --include="*.py" --exclude-dir=".git" --exclude-dir="__pycache__"
grep -r "adw_modules" --include="*.py" --exclude-dir=".git" --exclude-dir="__pycache__"
```

### Step 5: Test the Changes
1. Delete old cloned repo to force fresh installation
2. Trigger webhook for test issue
3. Verify tac-core-plugin is copied correctly
4. Verify workflows can import from `workflows.adw_modules`
5. Check no ImportError or ModuleNotFoundError

### Step 6: Update Documentation
Files to update:
- `CLAUDE.md` - Update repository structure diagram
- `docs/WEBHOOK_ARCHITECTURE_GUIDE.md` - Update distribution description
- `README.md` - Update if it mentions adw/ directory

## Validation Checklist

### Pre-Refactor Checks
- [ ] Backup current state: `git stash` or create branch
- [ ] Document current webhook behavior
- [ ] Note all files in `adw/`

### Post-Refactor Checks
- [ ] `adw/` directory deleted
- [ ] Webhook code updated (adw copy code removed)
- [ ] No references to `adw/adw_modules` in code
- [ ] Test webhook triggers issue successfully
- [ ] Workflows can import modules correctly
- [ ] No ImportError or ModuleNotFoundError
- [ ] Documentation updated

### Success Criteria
1. ✅ Only ONE location for adw_modules: `tac-core-plugin/workflows/adw_modules/`
2. ✅ Webhook only copies tac-core-plugin (not adw/)
3. ✅ All workflows run without import errors
4. ✅ No confusion about which files to update
5. ✅ Clean, simple architecture

## Rollback Plan
If issues occur:
```bash
# Restore from git
git checkout adw/
git checkout webhook-hub/triggers/trigger_webhook.py

# Or restore from stash
git stash pop
```

## Timeline
Estimated: 30-45 minutes
1. Verification: 5 min
2. Code changes: 10 min
3. Testing: 15-20 min
4. Documentation: 10 min

## Dependencies
- None (self-contained refactor)
- No external services affected
- Webhook can continue running during changes (will use new code on next trigger)

## Risks & Mitigation
| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing workflows | High | Test with non-critical issue first |
| Import path issues | Medium | Verify imports in all workflow files |
| Webhook fails to copy plugin | High | Keep library_root fix (commit 41cef2e) |

## Notes
- The `execute_template_async` bug (commit 41cef2e) proves modules are in tac-core-plugin
- Empty `adw/adw_modules/` was likely a remnant from old architecture
- This refactor simplifies and clarifies the codebase
