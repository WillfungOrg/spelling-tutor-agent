# Migration Guide

This guide helps you migrate from older versions of the agentic-coding-library to the current structure.

## Recent Breaking Changes

### November 2024: Runtime Directory Reorganization

**What Changed:**
- Runtime directories moved from root to `webhook-hub/runtime/`
- Simplified .gitignore structure
- Updated cleanup scripts

**Migration Steps:**

If you have an existing installation, follow these steps:

1. **Stop all running services:**
   ```bash
   # Find and kill running services
   pkill -f trigger_webhook
   pkill -f queue_worker
   pkill -f cloudflared
   ```

2. **Pull latest changes:**
   ```bash
   cd ~/agentic-coding-library
   git pull origin master
   ```

3. **Move existing runtime data:**
   ```bash
   # Create new runtime structure
   mkdir -p webhook-hub/runtime/{repos,agents,trees,logs}

   # Move existing data (if present)
   [ -d repos ] && mv repos/* webhook-hub/runtime/repos/ 2>/dev/null || true
   [ -d agents ] && mv agents/* webhook-hub/runtime/agents/ 2>/dev/null || true
   [ -d trees ] && mv trees/* webhook-hub/runtime/trees/ 2>/dev/null || true
   [ -d logs ] && mv logs/* webhook-hub/runtime/logs/ 2>/dev/null || true

   # Clean up old directories
   rm -rf repos agents trees logs
   ```

4. **Verify .gitignore:**
   ```bash
   # Ensure webhook-hub/runtime/ is ignored
   grep "webhook-hub/runtime/" .gitignore
   ```

5. **Restart services:**
   ```bash
   ./start_adw_services_simple.sh
   ```

6. **Verify health:**
   ```bash
   ./scripts/health_check.sh
   ```

### November 2024: Module Consolidation (adw_modules → hub_modules)

**What Changed:**
- `webhook-hub/adw_modules/` renamed to `webhook-hub/hub_modules/`
- `webhook-hub/adw_triggers/` renamed to `webhook-hub/triggers/`
- Removed 9 learning system modules (moved to plugin)

**Migration Steps:**

1. **Pull latest changes:**
   ```bash
   git pull origin master
   ```

2. **Update any custom scripts:**
   If you have custom scripts importing from `adw_modules`, update them:
   ```python
   # Old
   from adw_modules.utils import make_adw_id

   # New
   from hub_modules.utils import make_adw_id
   ```

3. **No data migration needed** - This was just a rename.

### November 2024: ADW Rename (adw/ → webhook-hub/)

**What Changed:**
- Main `adw/` directory renamed to `webhook-hub/`
- Reflects the purpose: centralized webhook hub for multi-repo automation

**Migration Steps:**

1. **Pull latest changes:**
   ```bash
   git pull origin master
   ```

2. **Update any scripts referencing old paths:**
   ```bash
   # Old path
   cd adw/

   # New path
   cd webhook-hub/
   ```

3. **Environment variables remain the same** - No changes needed to `.env` file.

## Version-Specific Migrations

### From Pre-Plugin Consolidation

If you're migrating from before the plugin consolidation (before commit 7f7e83b):

1. **Backup your customizations:**
   ```bash
   # Backup any custom commands you created
   cp -r .claude/commands .claude/commands.backup
   ```

2. **Pull latest changes:**
   ```bash
   git pull origin master
   ```

3. **Restore custom commands:**
   ```bash
   # Restore to new plugin location
   cp .claude/commands.backup/* tac-core-plugin/commands/
   ```

4. **Update CLAUDE.md references:**
   - Old: `.claude/commands/`
   - New: `tac-core-plugin/commands/`

### From Manual Setup to Webhook Automation

If you're currently using manual ADW workflows and want to enable webhook automation:

1. **Verify webhook-hub structure exists:**
   ```bash
   ls -la webhook-hub/
   # Should see: hub_modules/, triggers/, runtime/
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add:
   # - ANTHROPIC_API_KEY
   # - GITHUB_WEBHOOK_SECRET (auto-generated on first run)
   # - GITHUB_PAT (recommended)
   ```

3. **Start webhook services:**
   ```bash
   ./start_adw_services_simple.sh
   ```

4. **Configure GitHub webhook:**
   - Copy the webhook URL from startup logs
   - Go to GitHub repo → Settings → Webhooks → Add webhook
   - Paste URL, add secret, select "Issues" and "Issue comments" events

5. **Deploy labels to repositories:**
   ```bash
   ./scripts/setup_labels.sh
   ```

## Common Migration Issues

### Issue: Old runtime directories not properly cleaned up

**Symptoms:**
```bash
git status
# Shows: repos/, agents/, trees/, logs/ as modified
```

**Solution:**
```bash
# Move data if needed
mv repos/* webhook-hub/runtime/repos/ 2>/dev/null || true
mv agents/* webhook-hub/runtime/agents/ 2>/dev/null || true
mv trees/* webhook-hub/runtime/trees/ 2>/dev/null || true
mv logs/* webhook-hub/runtime/logs/ 2>/dev/null || true

# Force remove old directories
rm -rf repos agents trees logs

# Verify they're gone
git status
```

### Issue: Webhook server won't start after migration

**Symptoms:**
```bash
./start_adw_services_simple.sh
# Error: ANTHROPIC_API_KEY not set
```

**Solution:**
```bash
# Create .env from example
cp .env.example .env

# Edit and add your key
nano .env
# or
echo "ANTHROPIC_API_KEY=sk-ant-your-key" >> .env
```

### Issue: Import errors after module rename

**Symptoms:**
```python
ModuleNotFoundError: No module named 'adw_modules'
```

**Solution:**
```bash
# Update all imports in your custom code
find . -type f -name "*.py" -exec sed -i '' 's/from adw_modules/from hub_modules/g' {} +
find . -type f -name "*.py" -exec sed -i '' 's/import adw_modules/import hub_modules/g' {} +
```

### Issue: Worktrees from old location still exist

**Symptoms:**
```bash
git worktree list
# Shows: trees/abc12345 [branch] (error)
```

**Solution:**
```bash
# Prune invalid worktrees
git worktree prune

# List remaining worktrees
git worktree list

# Manually remove stuck ones if needed
git worktree remove trees/abc12345 --force
```

## Rollback Procedures

### Rollback to Previous Version

If you need to rollback to a previous version:

1. **Check your git log:**
   ```bash
   git log --oneline -10
   ```

2. **Rollback to specific commit:**
   ```bash
   # Example: rollback to before runtime reorganization
   git reset --hard af15fd3
   ```

3. **Restart services:**
   ```bash
   ./start_adw_services_simple.sh
   ```

**Warning:** Only rollback if absolutely necessary. Forward migration is always preferred.

## Getting Help

If you encounter issues during migration:

1. **Run health check:**
   ```bash
   ./scripts/health_check.sh
   ```

2. **Check logs:**
   ```bash
   tail -f /tmp/adw_logs/webhook.log
   tail -f /tmp/adw_logs/queue_worker.log
   ```

3. **File an issue:**
   - Include output from `./scripts/health_check.sh --json`
   - Include relevant error messages
   - Describe your migration path (what version you're coming from)

## Best Practices

1. **Always backup before migrating:**
   ```bash
   # Backup your .env
   cp .env .env.backup

   # Backup custom commands
   cp -r tac-core-plugin/commands tac-core-plugin/commands.backup
   ```

2. **Test in non-production first:**
   - If possible, test migration on a clone of your setup
   - Verify webhook functionality before updating production

3. **Follow the changelog:**
   - Review `git log` before pulling updates
   - Read commit messages for breaking changes

4. **Keep runtime data separate:**
   - Don't commit runtime data (repos/, agents/, etc.)
   - Let .gitignore handle exclusions automatically

## Future Migration Considerations

When new versions are released:

1. **Check for breaking changes** in commit messages
2. **Read updated docs** in `docs/` directory
3. **Run health checks** before and after migration
4. **Keep .env up to date** with new required variables

---

**Last Updated:** November 2024
**Current Version:** Post-runtime reorganization (commit 5e7dcbb+)
