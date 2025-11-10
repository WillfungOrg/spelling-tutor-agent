# Start Webhook Server

**Purpose:** Start the ADW webhook automation system for phone-to-PR workflows.

**When to use:** Enable automatic issue processing via GitHub webhooks.

---

## Instructions

Start the webhook server and display setup instructions:

```bash
.claude/scripts/start_adw_services_simple.sh
```

This will:
1. ✅ Start Cloudflare tunnel (temporary public URL)
2. ✅ Start webhook server (port 8000)
3. ✅ Start queue worker (background processing)
4. 📋 Display your webhook URL and GitHub setup steps

## What You'll See

```
╔════════════════════════════════════════╗
║   All Services Running Successfully    ║
╚════════════════════════════════════════╝

Payload URL:
https://random-words-1234.trycloudflare.com/gh-webhook

Secret:
b81beb2589279c8f11e139833a78136c476d659a9f63219af26d472021851962

📋 Quick Setup Checklist:
☐ Copy webhook URL above
☐ Copy webhook secret above
☐ Go to GitHub repo → Settings → Webhooks
☐ Add webhook with URL and secret
☐ Select 'Issues' and 'Issue comments' events
☐ Test by creating issue with 'auto-plan' label
```

## Configure GitHub Webhook

1. **Go to:** `https://github.com/YOUR_ORG/YOUR_REPO/settings/hooks`
2. **Click:** "Add webhook"
3. **Enter:**
   - **Payload URL:** (copy from script output)
   - **Content type:** `application/json`
   - **Secret:** (copy from script output)
   - **Events:** Select "Issues" and "Issue comments"
   - **Active:** ✅ Checked
4. **Click:** "Add webhook"

## Test It Works

Create a GitHub issue with this body:

```markdown
# Test Issue

Testing webhook automation.

**Workflow:** adw_plan_iso
```

The webhook will:
- ✅ Detect `adw_plan_iso` in the body
- ✅ Create isolated worktree
- ✅ Generate implementation plan
- ✅ Post status comments to issue
- ✅ Create PR when complete

## Stop Services

```bash
# The script shows PIDs when starting
kill <TUNNEL_PID> <WEBHOOK_PID> <WORKER_PID>

# Or press Ctrl+C in the terminal where script is running
```

## Logs

Monitor what's happening:

```bash
tail -f /tmp/adw_logs/webhook.log      # Webhook events
tail -f /tmp/adw_logs/queue_worker.log # Background processing
tail -f /tmp/adw_logs/tunnel.log       # Cloudflare tunnel
```

## Supported Workflows

Include these in issue body or comments:

| Trigger | Workflow | Actions |
|---------|----------|---------|
| `adw_plan_iso` | Planning only | Plan → Spec |
| `adw_plan_build_iso` | Plan + Build | Plan → Implement |
| `adw_plan_build_test_iso` | Plan + Build + Test | Plan → Implement → Validate |
| `adw_sdlc_iso` | Complete SDLC | Plan → Build → Test → Review → PR |
| `adw_sdlc_zte_iso` | Zero-touch (⚠️ auto-merges!) | Complete SDLC → Auto-ship |

## Prerequisites

- **cloudflared** installed: `brew install cloudflare/cloudflare/cloudflared`
- **Environment variables** set (script checks these)
- **GitHub repo** with webhook access

## Troubleshooting

**Q: Webhook not receiving events?**
- Check URL is correct in GitHub webhook settings
- Verify secret matches
- Check logs: `tail -f /tmp/adw_logs/webhook.log`

**Q: Services not starting?**
- Run: `.claude/scripts/start_adw_services_simple.sh`
- Check logs in `/tmp/adw_logs/`
- Verify ports 8000 not in use: `lsof -i :8000`

**Q: URL changes every restart?**
- Yes! Free Cloudflare tunnels generate new URLs
- Must update GitHub webhook after each restart
- For static URL, use paid Cloudflare tunnel with domain

## Advanced: Persistent Tunnel

For production use with static URL:

1. Create Cloudflare account
2. Create named tunnel: `cloudflared tunnel create my-tunnel`
3. Configure DNS
4. Update startup script to use named tunnel

See Cloudflare Tunnel documentation for details.

---

**Related:**
- `/health_check` - Verify system status
- See `QUICK_START_NO_DOMAIN.md` for detailed webhook setup guide
