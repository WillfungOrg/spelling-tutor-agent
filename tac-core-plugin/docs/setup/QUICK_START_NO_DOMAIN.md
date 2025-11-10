# Quick Start - No Domain Required

**Setup time: 5 minutes** ⏱️

This guide gets you up and running without needing a domain. Perfect for testing!

## Prerequisites

Install cloudflared:
```bash
brew install cloudflare/cloudflare/cloudflared
```

That's it! No domain, no DNS configuration, no account needed.

## Start Services

**From this repository (agentic-coding-library):**
```bash
./start_adw_services_simple.sh
```

**From other projects (using tac-core plugin):**
```bash
# After loading plugin: /plugin load github:willfung28/agentic-coding-library/tac-core-plugin
.claude/scripts/start_adw_services_simple.sh
```

**Output shows:**
1. ✅ All services started
2. 🌐 **Your webhook URL** (e.g., `https://random-words-1234.trycloudflare.com/gh-webhook`)
3. 🔑 **Your webhook secret**
4. 📋 **Step-by-step GitHub setup instructions**

## Configure GitHub Webhook

The script displays everything you need. Just:

1. **Copy the webhook URL** from script output
2. **Copy the webhook secret** from script output
3. **Go to:** Your GitHub repo → Settings → Webhooks → Add webhook
4. **Paste:**
   - Payload URL: `https://your-url.trycloudflare.com/gh-webhook`
   - Secret: (paste the secret shown in terminal)
   - Content type: `application/json`
   - Events: Check "Issues" and "Issue comments"
5. **Click:** "Add webhook"

## Test It!

**From your phone or computer:**

1. Create a new GitHub issue
2. Add label: `auto-plan` (for quick test)
3. Submit issue
4. Within seconds: Comment appears confirming workflow started
5. Wait 2-5 minutes: PR notification arrives!

**Test successful?** ✅ Try other labels:
- `auto-sdlc` - Full SDLC (takes 10-30 min)
- `auto-build` - Plan + Build
- `auto-test` - Plan + Build + Test

## Important Notes

⚠️ **URL Changes on Restart**

The temporary URL changes each time you restart the services.

**When you restart:**
1. Run `./start_adw_services_simple.sh` again
2. Note the new URL
3. Update GitHub webhook with new URL

**To avoid updating webhook each time:**
- Get a domain ($10-15/year) and use `start_adw_services.sh` instead
- See `CLOUDFLARE_TUNNEL_SETUP.md` for permanent setup

## Daily Usage

**Start services:**
```bash
./start_adw_services_simple.sh
```

Keep terminal open or it will stop.

**Stop services:**
Press `Ctrl+C` in the terminal

**Create issues from phone:**
Just add one of the labels (`auto-sdlc`, `auto-plan`, etc.) and submit!

## Monitoring

**Check health:**
```bash
curl http://localhost:5000/health | python3 -m json.tool
```

**Check queue:**
```bash
curl http://localhost:5000/queue/stats | python3 -m json.tool
```

**View logs:**
```bash
tail -f /tmp/adw_logs/webhook.log
tail -f /tmp/adw_logs/queue_worker.log
```

## Troubleshooting

**Services won't start:**
```bash
# Check if cloudflared is installed
cloudflared --version

# Check if port 5000 is available
lsof -i :5000

# If port is busy, kill it:
kill $(lsof -t -i :5000)
```

**Webhook shows 401 error:**
- Verify secret matches in GitHub webhook settings
- Secret is displayed when you run the script
- Also saved in `~/.adw/webhook_secret`

**Can't find webhook URL:**
```bash
# URL is saved here after startup
cat /tmp/adw_tunnel_url.txt
```

**Issues not processing:**
```bash
# Check webhook server logs
tail -f /tmp/adw_logs/webhook.log

# Check worker logs
tail -f /tmp/adw_logs/queue_worker.log
```

## What's Happening Behind the Scenes

```
Your MacBook:
  ├─ Cloudflare Tunnel (creates public HTTPS URL)
  ├─ Webhook Server (receives GitHub webhooks)
  └─ Queue Worker (processes queued workflows)

Flow:
Phone → GitHub Issue (with label)
  ↓
GitHub sends webhook to tunnel URL
  ↓
Webhook server spawns ADW workflow
  ↓
Workflow uses Agent SDK (your claude auth login session)
  ↓
Creates PR
  ↓
Phone gets notification
```

## Upgrading to Permanent Setup

**When you're ready for a stable URL:**

1. Get a domain (any domain registrar)
2. Add domain to Cloudflare (free)
3. Follow `CLOUDFLARE_TUNNEL_SETUP.md`
4. Use `start_adw_services.sh` instead

**Benefits of permanent setup:**
- URL never changes
- No need to update GitHub webhook
- Can use custom subdomain (e.g., `adw.yourdomain.com`)

## Next Steps

✅ Services running
✅ GitHub webhook configured
✅ First issue created and processed

**Now you can:**
- Create issues from phone anytime
- Add `auto-sdlc` label for full automation
- Review PRs from phone
- Merge from phone

**Tips:**
- Use `auto-plan` for quick tests (2-5 min)
- Use `auto-sdlc` for complete features (10-30 min)
- Create multiple issues - queue handles it automatically!
- System processes up to 15 issues in parallel

---

**That's it!** 🎉 You now have Phone-to-PR automation working without a domain.
