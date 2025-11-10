# Cloudflare Tunnel Setup Guide

This guide walks you through setting up Cloudflare Tunnel to expose your local webhook server to GitHub.

## Prerequisites

- Cloudflare account (free tier is sufficient)
- Domain name added to Cloudflare
- MacBook with admin access
- Terminal access

## Installation

### 1. Install cloudflared CLI

```bash
brew install cloudflare/cloudflare/cloudflared
```

Verify installation:

```bash
cloudflared --version
```

## Configuration

### 2. Authenticate with Cloudflare

```bash
cloudflared tunnel login
```

This opens a browser where you'll:
1. Log in to your Cloudflare account
2. Select your domain
3. Authorize cloudflared

A certificate will be saved to `~/.cloudflared/cert.pem`.

### 3. Create Tunnel

```bash
cloudflared tunnel create adw-webhook
```

**Output example:**
```
Tunnel credentials written to ~/.cloudflared/<tunnel-id>.json
Created tunnel adw-webhook with id <tunnel-id>
```

**Important:** Save the `<tunnel-id>` - you'll need it next!

### 4. Configure DNS

Choose a subdomain for your webhook (e.g., `adw.yourdomain.com`):

```bash
cloudflared tunnel route dns adw-webhook adw.yourdomain.com
```

Replace `yourdomain.com` with your actual domain.

This creates a CNAME record pointing `adw.yourdomain.com` to your tunnel.

### 5. Create Configuration File

Create `~/.cloudflared/config.yml`:

```yaml
tunnel: <tunnel-id-from-step-3>
credentials-file: /Users/<your-username>/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: adw.yourdomain.com
    service: http://localhost:5000
  - service: http_status:404
```

**Replace:**
- `<tunnel-id-from-step-3>` with your actual tunnel ID
- `<your-username>` with your Mac username
- `adw.yourdomain.com` with your chosen subdomain

### 6. Generate Webhook Secret

```bash
# Create ADW config directory
mkdir -p ~/.adw

# Generate strong random secret
openssl rand -hex 32 > ~/.adw/webhook_secret

# Display the secret (you'll need this for GitHub)
cat ~/.adw/webhook_secret
```

### 7. Add to Environment Variables

Add to your `.env` file in the project root:

```bash
echo "GITHUB_WEBHOOK_SECRET=$(cat ~/.adw/webhook_secret)" >> .env
```

Verify:

```bash
grep GITHUB_WEBHOOK_SECRET .env
```

## Testing

### 8. Test Tunnel Connection

Start the tunnel:

```bash
cloudflared tunnel run adw-webhook
```

**Expected output:**
```
2025-11-05 Registered tunnel connection
2025-11-05 Connection established
```

Leave this running and open a new terminal.

### 9. Test Webhook Server

In a new terminal:

```bash
cd adw/adw_triggers
uv run trigger_webhook.py
```

**Expected output:**
```
INFO:webhook:Starting webhook server on http://0.0.0.0:5000
INFO:     Started server process [...]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 10. Test Public Endpoint

In another terminal:

```bash
curl https://adw.yourdomain.com/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "service": "adw-webhook-server",
  "version": "2.0.0",
  "queue": {
    "pending": 0,
    "processing": 0,
    "rate_limited": 0
  },
  "webhook_secret_configured": true
}
```

✅ If you see this, your tunnel is working!

## GitHub Configuration

### 11. Configure GitHub Webhook

1. Go to your GitHub repository
2. Click **Settings** → **Webhooks** → **Add webhook**

3. Configure webhook:
   - **Payload URL:** `https://adw.yourdomain.com/gh-webhook`
   - **Content type:** `application/json`
   - **Secret:** Paste secret from `~/.adw/webhook_secret`
   - **Events:** Select "Let me select individual events"
     - ✅ Check "Issues"
     - ✅ Check "Issue comments"
   - **Active:** ✅ Checked

4. Click **Add webhook**

5. Test delivery:
   - Click your new webhook
   - Go to "Recent Deliveries"
   - Click "Redeliver" on the ping event
   - Should show **200 OK** with green checkmark

## Usage

### Starting Services

Use the automated start script:

```bash
./start_adw_services.sh
```

This starts:
- Cloudflare Tunnel
- Webhook Server
- Queue Worker

All three services run in the background.

### Stopping Services

Press **Ctrl+C** in the terminal running `start_adw_services.sh`

Or manually:

```bash
# Get PIDs
cat /tmp/adw_services.pids

# Kill services
kill $(cat /tmp/adw_services.pids)
```

### Monitoring

**View logs:**
```bash
tail -f /tmp/adw_logs/tunnel.log     # Tunnel logs
tail -f /tmp/adw_logs/webhook.log    # Webhook logs
tail -f /tmp/adw_logs/queue_worker.log  # Worker logs
```

**Check queue status:**
```bash
curl http://localhost:5000/queue/stats | python3 -m json.tool
```

**Check health:**
```bash
curl http://localhost:5000/health | python3 -m json.tool
```

## Creating Issues from Phone

### Labels

Add one of these labels when creating an issue:

- **`auto-sdlc`** - Full SDLC (plan → build → test → review → document → PR)
- **`auto-plan`** - Planning only (creates spec and plan)
- **`auto-build`** - Plan + Build (implementation)
- **`auto-test`** - Plan + Build + Test

### Workflow

1. **On Phone:** Open GitHub app
2. **Create Issue:**
   - Title: Describe what you want
   - Body: Provide context/requirements
   - Labels: Add `auto-sdlc` (or other label)
3. **Submit Issue**
4. **Wait:** Within seconds, you'll receive a comment confirming workflow started
5. **Review PR:** 10-30 minutes later (depending on workflow), PR notification arrives
6. **Merge:** Review and merge PR from phone

## Troubleshooting

### Tunnel Not Connecting

**Problem:** `cloudflared tunnel run` fails

**Solutions:**
```bash
# Check tunnel exists
cloudflared tunnel list

# Check DNS configuration
nslookup adw.yourdomain.com

# Recreate tunnel if needed
cloudflared tunnel delete adw-webhook
cloudflared tunnel create adw-webhook
# Reconfigure DNS (step 4)
```

### Webhook Returns 401 Unauthorized

**Problem:** GitHub webhook delivery shows 401 error

**Solutions:**
```bash
# Verify secret matches
cat ~/.adw/webhook_secret
# Compare with GitHub webhook settings

# Regenerate secret
openssl rand -hex 32 > ~/.adw/webhook_secret
# Update .env
echo "GITHUB_WEBHOOK_SECRET=$(cat ~/.adw/webhook_secret)" >> .env
# Update GitHub webhook settings with new secret
```

### Webhook Returns 502 Bad Gateway

**Problem:** GitHub can reach tunnel but webhook server isn't running

**Solutions:**
```bash
# Check if webhook server is running
ps aux | grep trigger_webhook

# Check webhook logs
tail -f /tmp/adw_logs/webhook.log

# Restart webhook server
cd adw/adw_triggers
uv run trigger_webhook.py
```

### Issues Stuck in Queue

**Problem:** Issues are queued but not processing

**Solutions:**
```bash
# Check queue worker is running
ps aux | grep queue_worker

# Check worker logs
tail -f /tmp/adw_logs/queue_worker.log

# Check queue stats
curl http://localhost:5000/queue/stats

# Restart worker
cd adw/adw_triggers
uv run queue_worker.py
```

### Rate Limit Hit

**Problem:** Many issues queued with "rate_limited" status

**Solution:**
- Wait 5 hours for Claude Code quota to reset
- Queue worker will automatically retry

**Check when quota resets:**
```bash
curl http://localhost:5000/queue/stats
# Look at rate_limited count
```

## Security Notes

1. **Keep webhook secret private:** Never commit `~/.adw/webhook_secret` to git
2. **HTTPS only:** Cloudflare Tunnel provides automatic HTTPS/TLS
3. **DDoS protection:** Cloudflare provides automatic DDoS protection
4. **Signature verification:** All webhook requests are HMAC-verified
5. **Firewall:** No ports need to be opened on your MacBook

## Maintenance

### Updating Tunnel

```bash
brew upgrade cloudflare/cloudflare/cloudflared
```

### Rotating Webhook Secret

```bash
# Generate new secret
openssl rand -hex 32 > ~/.adw/webhook_secret

# Update .env
sed -i '' '/GITHUB_WEBHOOK_SECRET/d' .env
echo "GITHUB_WEBHOOK_SECRET=$(cat ~/.adw/webhook_secret)" >> .env

# Update GitHub webhook settings
# (manually update secret in GitHub UI)

# Restart webhook server
# (kill and restart or run ./start_adw_services.sh)
```

### Cleaning Up Old Queue Items

Automatic cleanup runs every hour (keeps last 7 days).

Manual cleanup:

```python
from adw.adw_triggers.queue_manager import QueueManager
queue = QueueManager()
deleted = queue.cleanup_old_items(days=7)
print(f"Deleted {deleted} items")
```

## Auto-Start on MacBook Login (Optional)

To automatically start services when you log in:

### Create LaunchAgent

Create `~/Library/LaunchAgents/com.adw.webhook.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.adw.webhook</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/path/to/agentic-coding-library/start_adw_services.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/adw_launchagent.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/adw_launchagent_error.log</string>
</dict>
</plist>
```

**Replace `/path/to/agentic-coding-library/` with your actual path.**

### Load LaunchAgent

```bash
launchctl load ~/Library/LaunchAgents/com.adw.webhook.plist
```

### Unload LaunchAgent

```bash
launchctl unload ~/Library/LaunchAgents/com.adw.webhook.plist
```

## Support

- **Cloudflare Tunnel Docs:** https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/
- **GitHub Webhooks Docs:** https://docs.github.com/en/webhooks
- **Issue Tracker:** Create GitHub issue for bugs/feature requests

---

**Setup Complete!** 🎉

You can now create GitHub issues from your phone and have them automatically processed into PRs.
