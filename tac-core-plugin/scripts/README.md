# Scripts Directory

This directory contains utility scripts for ADW automation and maintenance.

## 📋 Available Scripts

### Webhook & Monitoring Scripts

#### `health_check.sh`

**Purpose:** Check health status of webhook services and runtime environment.

**Usage:**
```bash
# Human-readable output
./scripts/health_check.sh

# JSON output for monitoring systems
./scripts/health_check.sh --json
```

**What it checks:**
- Environment variables (ANTHROPIC_API_KEY, GITHUB_PAT, etc.)
- Webhook server process and responsiveness
- Queue worker process
- Cloudflare tunnel status
- Runtime directory structure
- Disk usage
- Active git worktrees
- Recent errors in logs

**Exit codes:**
- 0: All checks passed (healthy)
- 1: One or more checks failed (unhealthy)

---

### Cleanup Scripts

#### `cleanup_repos.sh`

**Purpose:** Clean up old cloned repositories and worktrees in webhook-hub/runtime/repos/.

**Usage:**
```bash
# Dry run (see what would be deleted)
./scripts/cleanup_repos.sh --dry-run

# Clean repos older than 30 days (default)
./scripts/cleanup_repos.sh

# Clean repos older than 7 days
./scripts/cleanup_repos.sh --days 7
```

**What it does:**
1. Scans webhook-hub/runtime/repos/ for inactive repositories
2. Removes old git worktrees within each repo
3. Deletes entire repos not accessed in N days
4. Shows before/after disk usage

---

#### `cleanup_test_artifacts.sh`

**Purpose:** Clean up ADW test artifacts (worktrees, agent state, logs).

**Usage:**
```bash
# Dry run
./scripts/cleanup_test_artifacts.sh --dry-run

# Clean artifacts older than 7 days (default)
./scripts/cleanup_test_artifacts.sh

# Clean all artifacts
./scripts/cleanup_test_artifacts.sh --all

# Clean specific ADW ID
./scripts/cleanup_test_artifacts.sh --adw-id abc12345

# Include learning logs in cleanup
./scripts/cleanup_test_artifacts.sh --remove-learning
```

**What it cleans:**
- Git worktrees (trees/ and webhook-hub/runtime/trees/)
- Agent state files (agents/ and webhook-hub/runtime/agents/)
- Git branches with ADW IDs
- Session logs (logs/ and webhook-hub/runtime/logs/)
- Learning logs (optional, preserved by default)

---

#### `setup_labels.sh`

**Purpose:** Deploy ADW workflow labels to all repositories in your organization.

**Usage:**
```bash
./scripts/setup_labels.sh
```

**Requirements:**
- GitHub CLI (`gh`) installed
- Organization admin access

**Labels created:**
- `adw-plan`, `adw-build`, `adw-test`, etc. (19 total)

---

### Legacy Scripts

### `tac-local-trigger.sh`

**Purpose:** Pull pending GitHub issues and prepare them for agent processing.

**Usage:**
```bash
./scripts/tac-local-trigger.sh
```

**What it does:**
1. Fetches all issues labeled `tac:pending` from GitHub
2. Shows you a list of pending tasks
3. Lets you select which task to process
4. Downloads the issue details to `.tac/current-issue.json`
5. Updates the issue label to `tac:in-progress`
6. Provides instructions for processing in Claude Desktop

**Requirements:**
- GitHub CLI (`gh`) installed and authenticated
- Repo access (update REPO variable in script for new projects)

---

## 🎯 Workflow Overview

### From Mobile (Anywhere):
1. Go to your repo's issues: `https://github.com/YOUR_USERNAME/YOUR_REPO/issues/new/choose`
2. Select "TAC Task" template
3. Fill in task details
4. Submit (automatically gets `tac:pending` label)

### From Development Machine:
1. Run `./scripts/tac-local-trigger.sh`
2. Select the issue you want to work on
3. Open Claude Desktop
4. Tell Claude: "Process the TAC issue from .tac/current-issue.json"
5. Agent completes the task and creates a PR

---

## 🔧 Setup for New Projects

When copying this to a new project:

1. **Update the REPO variable** in `tac-local-trigger.sh`:
   ```bash
   # Line 8: Change to your repo
   REPO="your-username/your-repo-name"
   ```

2. **Create GitHub labels** for the new repo:
   ```bash
   gh label create "tac:pending" --color "fbca04" --description "TAC: Waiting to be processed" --repo YOUR_USERNAME/YOUR_REPO
   gh label create "tac:in-progress" --color "0052cc" --description "TAC: Currently being worked on" --repo YOUR_USERNAME/YOUR_REPO
   gh label create "tac:completed" --color "0e8a16" --description "TAC: Task completed" --repo YOUR_USERNAME/YOUR_REPO
   ```

3. **Test it works**:
   ```bash
   ./scripts/tac-local-trigger.sh
   # Should show: "No pending TAC tasks found"
   ```

---

## 🏷️ TAC Labels

- `tac:pending` - Issue waiting to be processed
- `tac:in-progress` - Agent is currently working on this
- `tac:completed` - Task finished, PR created

---

## 📁 File Structure

```
scripts/
├── README.md                      # This file
├── health_check.sh                # Health monitoring for webhook services
├── cleanup_repos.sh               # Clean old cloned repositories
├── cleanup_test_artifacts.sh      # Clean ADW worktrees and state
├── setup_labels.sh                # Deploy labels to GitHub repos
└── tac-local-trigger.sh           # Legacy: Issue fetcher (pre-webhook)
```

---

## 🔧 Common Tasks

### Check webhook service health
```bash
./scripts/health_check.sh
```

### Clean up old data
```bash
# See what would be cleaned (recommended first step)
./scripts/cleanup_repos.sh --dry-run
./scripts/cleanup_test_artifacts.sh --dry-run

# Actually clean
./scripts/cleanup_repos.sh --days 30
./scripts/cleanup_test_artifacts.sh --age 7
```

### Monitor services
```bash
# Check health
./scripts/health_check.sh

# View logs
tail -f /tmp/adw_logs/webhook.log
tail -f /tmp/adw_logs/queue_worker.log
```

### Deploy labels to new org repos
```bash
./scripts/setup_labels.sh
```

---

## 📊 Maintenance Schedule

**Recommended:**
- Daily: Run `health_check.sh` to monitor services
- Weekly: Run `cleanup_test_artifacts.sh --age 7` to clean old worktrees
- Monthly: Run `cleanup_repos.sh --days 30` to clean inactive repos
- As needed: Review disk usage if runtime/ grows large

---

## 🚨 Troubleshooting

### Services won't start
```bash
# Check health
./scripts/health_check.sh

# Common fixes
# 1. Missing env vars
cp .env.example .env
nano .env

# 2. Port conflicts
lsof -i :8000

# 3. Stale PIDs
pkill -f trigger_webhook
pkill -f queue_worker
```

### Disk space issues
```bash
# Check current usage
du -sh webhook-hub/runtime/*

# Clean old data
./scripts/cleanup_repos.sh --days 7
./scripts/cleanup_test_artifacts.sh --all

# Check again
du -sh webhook-hub/runtime/*
```

### Too many worktrees
```bash
# List all worktrees
git worktree list

# Clean old ones
./scripts/cleanup_test_artifacts.sh --age 7

# Prune invalid references
git worktree prune
```

---

## 📖 See Also

- `docs/MIGRATION_GUIDE.md` - Migration instructions for updates
- `docs/WEBHOOK_MAINTENANCE.md` - Webhook operations guide
- `webhook-hub/hub_modules/README.md` - Module ownership rules
