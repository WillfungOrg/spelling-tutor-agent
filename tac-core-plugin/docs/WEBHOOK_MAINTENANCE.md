# Webhook Server Maintenance Guide

This guide covers maintaining the centralized webhook server for multi-repo ADW automation.

## Overview

The webhook server at `agentic-coding-library` serves as a centralized hub that:
- Receives webhooks from all repos in your GitHub organization
- Clones target repositories into `repos/<repo-name>/`
- Automatically installs `tac-core-plugin/` into cloned repos
- Executes ADW workflows in isolated worktrees
- Creates PRs in the target repositories

## Repository Lifecycle

```
┌─────────────────────────────────────────────┐
│ 1. GitHub Issue Created                     │
│    (in any org repo)                        │
└─────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│ 2. Webhook Event Received                   │
│    - Extract repo info from payload         │
│    - Clone repo if new                      │
│    - Pull latest if existing                │
│    - Install plugin if missing              │
└─────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│ 3. ADW Workflow Execution                   │
│    - Create worktree in repos/X/trees/Y    │
│    - Execute workflow (plan/build/test)     │
│    - Create PR in target repo               │
└─────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│ 4. Post-Merge State                         │
│    - Cloned repo stays in repos/X/          │
│    - Worktree stays in repos/X/trees/Y     │
│    - State stays in repos/X/agents/Y       │
│    ⚠️  Accumulates over time!               │
└─────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│ 5. Cleanup (Automated or Manual)            │
│    - Remove old worktrees (>30 days)       │
│    - Remove inactive repos (>30 days)      │
│    - Free disk space                        │
└─────────────────────────────────────────────┘
```

## Maintenance Tasks

### Daily Monitoring

**Check webhook server health:**
```bash
# Check if webhook server is running
ps aux | grep trigger_webhook

# Check webhook logs
tail -f /tmp/adw_logs/webhook.log

# Check disk usage
df -h
du -sh repos/
```

**Monitor resource usage:**
```bash
# Check CPU/memory
top -o cpu

# Check number of running workflows
ps aux | grep adw_ | wc -l

# Check webhook server endpoint
curl http://localhost:8000/health
```

### Weekly Cleanup (Automated)

**Set up automated cleanup:**
```bash
# Edit crontab
crontab -e

# Add weekly cleanup (Sundays at 2am)
0 2 * * 0 /path/to/agentic-coding-library/scripts/cleanup_repos.sh --days 7

# Or daily cleanup with longer retention
0 2 * * * /path/to/agentic-coding-library/scripts/cleanup_repos.sh --days 30
```

**Manual cleanup:**
```bash
# Dry run to see what would be deleted
./scripts/cleanup_repos.sh --dry-run --days 30

# Actually delete old worktrees and repos
./scripts/cleanup_repos.sh --days 30

# Aggressive cleanup (keep only last 7 days)
./scripts/cleanup_repos.sh --days 7
```

### Monthly Review

**Review repository growth:**
```bash
# List all cloned repos with sizes
du -sh repos/* | sort -h

# Count worktrees per repo
for repo in repos/*; do
    echo "$(basename $repo): $(ls $repo/trees 2>/dev/null | wc -l) worktrees"
done

# Check total size over time
echo "$(date): $(du -sh repos/)" >> docs/repo_growth.log
```

**Review webhook statistics:**
```bash
# Count webhook events by repo (from logs)
grep "Received webhook" /tmp/adw_logs/webhook.log | \
    grep -oP "repo=\K[^,]+" | \
    sort | uniq -c | sort -rn

# Count workflow types executed
grep "Launching" /tmp/adw_logs/webhook.log | \
    grep -oP "Launching \K\w+" | \
    sort | uniq -c | sort -rn
```

### Troubleshooting

**Issue: Disk space full**
```bash
# Find largest repos
du -sh repos/* | sort -h | tail -10

# Remove specific repo
rm -rf repos/<repo-name>
# (Will be re-cloned on next webhook)

# Run aggressive cleanup
./scripts/cleanup_repos.sh --days 1
```

**Issue: Webhook server not responding**
```bash
# Check if process is running
ps aux | grep trigger_webhook

# Check logs for errors
tail -100 /tmp/adw_logs/webhook.log

# Restart webhook server
# (Kill old processes first)
pkill -f trigger_webhook
pkill -f cloudflared

# Start fresh
cd /path/to/agentic-coding-library
./start_adw_services_simple.sh
```

**Issue: Git operations failing**
```bash
# Check git worktrees
cd repos/<repo-name>
git worktree list

# Prune broken worktrees
git worktree prune

# Check for locks
find . -name "*.lock" -type f

# Remove locks if safe
find . -name "*.lock" -type f -delete
```

**Issue: Plugin not found in cloned repo**
```bash
# Check if plugin exists
ls -la repos/<repo-name>/tac-core-plugin/

# Manually install plugin
cd repos/<repo-name>
cp -r ../../tac-core-plugin .

# Or delete repo (will be re-cloned with plugin)
cd ../..
rm -rf repos/<repo-name>
```

## Resource Requirements

### Minimum Specs (Small Team, 5-10 repos)
- **CPU:** 2 cores
- **RAM:** 4GB
- **Disk:** 50GB
- **Network:** 10 Mbps

### Recommended Specs (Medium Team, 10-30 repos)
- **CPU:** 4 cores
- **RAM:** 8GB
- **Disk:** 200GB
- **Network:** 50 Mbps

### High-Scale Specs (Large Org, 50+ repos)
- **CPU:** 8+ cores
- **RAM:** 16GB+
- **Disk:** 500GB+ (or distributed storage)
- **Network:** 100 Mbps+
- **Consider:** Queue system, load balancing

## Scaling Considerations

### When Current Design Struggles:
1. **Disk usage >80%** → Need cleanup or larger disk
2. **CPU usage >80%** → Need rate limiting or more cores
3. **Memory usage >80%** → Need to limit concurrent workflows
4. **Webhook delays >30s** → Need queue system

### Scaling Options:

**Option 1: Vertical Scaling (Simple)**
- Upgrade server resources
- Add larger disk
- Works up to ~50 repos

**Option 2: Add Queue System (Medium)**
- Install Redis/RabbitMQ
- Limit concurrent workflows
- Better resource management
- Works up to ~200 repos

**Option 3: Horizontal Scaling (Complex)**
- Multiple webhook servers
- Load balancer
- Distributed storage
- Works for any scale

## Backup Strategy

**What to backup:**
```bash
# Backup ADW state (small, important)
tar -czf backup-agents-$(date +%F).tar.gz agents/

# Backup webhook configuration
cp .env .env.backup
cp adw/adw_triggers/trigger_webhook.py backup/

# Backup cleanup logs
cp docs/repo_growth.log backup/
```

**What NOT to backup:**
- `repos/` - Can be re-cloned from GitHub
- `trees/` - Temporary worktrees
- `logs/` - Can be regenerated

## Monitoring Checklist

Daily:
- [ ] Webhook server is running
- [ ] Disk usage <80%
- [ ] No error spikes in logs

Weekly:
- [ ] Run cleanup script
- [ ] Review largest repos
- [ ] Check for failed workflows

Monthly:
- [ ] Review repo growth log
- [ ] Review webhook statistics
- [ ] Test webhook with sample issue
- [ ] Update this document if needed

## Emergency Procedures

**If everything breaks:**
```bash
# 1. Stop all services
pkill -f trigger_webhook
pkill -f cloudflared
pkill -f adw_

# 2. Clear everything (nuclear option)
rm -rf repos/
rm -rf agents/
rm -rf trees/
rm -rf logs/

# 3. Restart webhook server
./start_adw_services_simple.sh

# 4. Test with single issue
# Create test issue in one repo
# Verify webhook receives it and processes correctly
```

## Best Practices

1. **Monitor regularly** - Set up alerts for disk usage
2. **Clean proactively** - Don't wait for disk to fill
3. **Test changes** - Use dry-run before destructive operations
4. **Document incidents** - Keep log of issues and resolutions
5. **Plan for growth** - Review scaling needs quarterly
6. **Keep plugin updated** - Sync `tac-core-plugin/` regularly

## Getting Help

If issues persist:
1. Check `/tmp/adw_logs/webhook.log` for errors
2. Check `agents/<adw-id>/*/execution.log` for workflow errors
3. Check GitHub webhook delivery page for failed deliveries
4. Verify environment variables are set correctly
5. Test with simple workflow (adw_plan_iso) first

---

**Last Updated:** 2025-11-06
**Maintainer:** You (update this as team grows)
