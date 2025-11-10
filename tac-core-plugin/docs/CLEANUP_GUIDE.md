# ADW Test Artifacts Cleanup Guide

## What Files Are Created During ADW Workflows?

When you run an ADW workflow (e.g., `adw_sdlc_iso.py`), several types of files are created:

### 1. **Worktrees** (Git Working Directories)
- **Location:** `trees/<adw_id>/` or `adw/trees/<adw_id>/`
- **Purpose:** Isolated git checkout for the workflow to work in
- **Size:** 10-20 MB each (full repo copy)
- **Cleanup:** Must be removed with `git worktree remove` before deleting directory

### 2. **Agent State** (ADW Configuration)
- **Location:** `agents/<adw_id>/`
- **Purpose:** Stores workflow state, configuration, and agent outputs
- **Contains:**
  - `adw_state.json` - Workflow metadata (branch, ports, etc.)
  - `<agent_name>/output.jsonl` - Agent execution logs
- **Size:** 10-50 KB
- **Cleanup:** Can be deleted directly (no special handling needed)

### 3. **Git Branches**
- **Location:** Git repository branches
- **Purpose:** Each ADW creates a feature branch
- **Naming:** `feature-issue-<N>-adw-<adw_id>-<description>`
- **Cleanup:** Must be deleted with `git branch -D <branch_name>`

### 4. **Session Logs** (Claude Code Execution Logs)
- **Location:** `logs/<session_id>/`
- **Purpose:** Stores Claude Code agent chat logs
- **Contains:**
  - `chat.json` - Full conversation history
  - `stop.json` - Session metadata
- **Size:** 50 KB - 5 MB each
- **Cleanup:** Can be deleted when no longer needed for debugging

### 5. **Learning Logs** (AI Learning System)
- **Location:** `adw/.tac/learning/execution_logs/<adw_id>.json`
- **Purpose:** Stores learning data for self-improving AI
- **Contains:**
  - Task analysis (complexity, type, requirements)
  - Strategy recommendations
  - Execution outcomes (success/failure)
  - Problems encountered
- **Size:** 1-3 KB each
- **Cleanup:** **KEEP THESE!** They enable the learning system to improve over time

## What Gets Deleted When You Remove a Worktree?

**When you run `git worktree remove trees/<adw_id>`:**

✅ **Deleted:**
- The working directory files in `trees/<adw_id>/`
- The `.git` worktree reference

❌ **NOT Deleted (Manual Cleanup Needed):**
- Git branch (still exists in repo)
- Agent state in `agents/<adw_id>/`
- Session logs in `logs/`
- Learning logs in `adw/.tac/learning/`

**This is why we need the cleanup script!**

## Automated Cleanup Script

### Basic Usage

```bash
# Dry run - see what would be deleted
./scripts/cleanup_test_artifacts.sh --dry-run

# Clean artifacts older than 7 days (default)
./scripts/cleanup_test_artifacts.sh

# Clean all test artifacts (regardless of age)
./scripts/cleanup_test_artifacts.sh --all

# Clean specific ADW ID
./scripts/cleanup_test_artifacts.sh --adw-id b7724708
```

### Advanced Options

```bash
# Clean artifacts older than 30 days
./scripts/cleanup_test_artifacts.sh --age 30

# Clean everything including learning logs (NOT recommended!)
./scripts/cleanup_test_artifacts.sh --all --remove-learning

# Dry run with specific age threshold
./scripts/cleanup_test_artifacts.sh --dry-run --age 14
```

### What the Script Does

1. **Removes Worktrees:**
   - Uses `git worktree remove --force`
   - Cleans up directory if git command fails

2. **Deletes Agent State:**
   - Removes entire `agents/<adw_id>/` directory
   - Includes all agent outputs and state files

3. **Deletes Git Branches:**
   - Uses `git branch -D` to force delete
   - Finds branches by ADW ID pattern

4. **Cleans Session Logs:**
   - Only removes orphaned logs (not referenced by any active ADW)
   - Preserves logs for active workflows

5. **Preserves Learning Logs:**
   - By default, keeps all learning data
   - Use `--remove-learning` to delete (not recommended)

## Automation Options

### Option 1: Manual Cleanup (Recommended)

Run cleanup periodically when disk space gets low:

```bash
# Check disk usage
du -sh agents/ trees/ logs/

# Run cleanup
./scripts/cleanup_test_artifacts.sh --age 7
```

### Option 2: Cron Job (Daily Cleanup)

Add to crontab to run daily at 2 AM:

```bash
# Edit crontab
crontab -e

# Add this line
0 2 * * * cd /Users/williamfung/agentic-coding-library && ./scripts/cleanup_test_artifacts.sh --age 7 >> /tmp/adw_cleanup.log 2>&1
```

### Option 3: Post-Workflow Cleanup Hook

Add to your workflow scripts to clean up after completion:

```python
# At the end of your workflow script
import subprocess

# Clean up this specific ADW instance after completion
subprocess.run([
    "./scripts/cleanup_test_artifacts.sh",
    "--adw-id", adw_id
], cwd=repo_root)
```

### Option 4: GitHub Actions (Weekly Cleanup)

Create `.github/workflows/cleanup.yml`:

```yaml
name: Weekly ADW Cleanup
on:
  schedule:
    - cron: '0 2 * * 0'  # Sunday at 2 AM
  workflow_dispatch:  # Allow manual trigger

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run cleanup
        run: ./scripts/cleanup_test_artifacts.sh --age 7
      - name: Commit changes
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add -A
          git commit -m "chore: automated cleanup of old test artifacts" || true
          git push
```

## What Should You Keep vs Delete?

### ✅ ALWAYS KEEP

1. **Learning Logs** (`adw/.tac/learning/execution_logs/*.json`)
   - Essential for the self-improving learning system
   - Small file size (1-3 KB each)
   - No downside to keeping them

2. **Active Worktrees** (workflows currently running)
   - Check with `git worktree list`
   - Don't delete if ADW is still running

3. **Recent Agent State** (last 7 days)
   - Useful for debugging recent issues
   - Contains valuable execution context

### ⚠️ CONDITIONALLY DELETE

1. **Old Worktrees** (older than 7 days)
   - Safe to delete if workflow completed
   - Check git worktree list first

2. **Old Agent State** (older than 7 days)
   - Safe to delete after workflow completion
   - Keep if you need execution logs for debugging

3. **Old Branches** (merged or abandoned)
   - Safe to delete if PR was merged or closed
   - Check GitHub PR status first

### ✅ ALWAYS DELETE

1. **Orphaned Session Logs** (no matching ADW)
   - No longer useful
   - Can accumulate quickly (MB-GB range)

2. **Failed Workflow Artifacts** (if you're not debugging)
   - Clean up after fixing the issue
   - No value after problem is resolved

## Recommended Cleanup Schedule

| Frequency | Command | Purpose |
|-----------|---------|---------|
| **Daily** | `./scripts/cleanup_test_artifacts.sh --age 7` | Keep disk usage low |
| **Weekly** | `./scripts/cleanup_test_artifacts.sh --age 14` | Deep clean |
| **Monthly** | Review learning logs, archive old ones | Organize learning data |
| **After Each Test** | `./scripts/cleanup_test_artifacts.sh --adw-id <id>` | Immediate cleanup |

## Disk Space Recovery

**Typical cleanup results:**

```
Before:
agents/  - 2.5 MB  (25 ADW instances)
trees/   - 150 MB  (9 worktrees)
logs/    - 50 MB   (15 session logs)
Total:   ~202 MB

After (--age 7):
agents/  - 200 KB  (2 recent ADWs)
trees/   - 0 MB    (all cleaned)
logs/    - 5 MB    (2 recent logs)
Total:   ~5 MB

Recovered: ~197 MB (97% reduction)
```

## Troubleshooting

### "Cannot remove worktree" Error

```bash
# Force remove even if dirty
git worktree remove trees/<adw_id> --force

# Or manually delete
rm -rf trees/<adw_id>
git worktree prune
```

### "Branch in use" Error

```bash
# Check if branch is checked out elsewhere
git worktree list

# Remove worktree first, then branch
git worktree remove trees/<adw_id> --force
git branch -D <branch_name>
```

### Script Can't Find ADW Directories

The script looks in:
- `trees/` - Standard location
- `adw/trees/` - Alternative location
- `agents/` - Always checked

If your directories are elsewhere, update the script or use `--adw-id`.

## Best Practices

1. **Run dry-run first:** Always use `--dry-run` to preview changes
2. **Keep learning logs:** Never delete unless absolutely necessary
3. **Clean regularly:** Don't let artifacts accumulate
4. **Check active workflows:** Don't delete running ADW instances
5. **Document custom ADW IDs:** Keep a log of important test runs

## Summary

**Quick Reference:**

```bash
# 1. See what would be deleted
./scripts/cleanup_test_artifacts.sh --dry-run --all

# 2. Clean old artifacts (keeps learning logs)
./scripts/cleanup_test_artifacts.sh --age 7

# 3. Clean specific ADW after testing
./scripts/cleanup_test_artifacts.sh --adw-id <adw_id>

# 4. Check remaining usage
du -sh agents/ trees/ logs/
```

**Remember:**
- Worktrees = Large (10-20 MB), safe to delete when done
- Agent state = Small (10-50 KB), keep for debugging
- Learning logs = Tiny (1-3 KB), **ALWAYS KEEP**
- Session logs = Medium (50 KB - 5 MB), delete orphaned ones
