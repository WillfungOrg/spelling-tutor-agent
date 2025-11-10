#!/bin/bash
# Start ADW Automation Services (Simple - No Domain Required)
#
# Uses Cloudflare temporary tunnel URLs
# URL changes each restart - update GitHub webhook accordingly

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   ADW Simple Setup (No Domain)        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"

# Check prerequisites
echo -e "${GREEN}[1/5]${NC} Checking prerequisites..."

if ! command -v cloudflared &> /dev/null; then
    echo -e "${RED}Error: cloudflared not found${NC}"
    echo "Install with: brew install cloudflare/cloudflare/cloudflared"
    exit 1
fi

if ! command -v uv &> /dev/null; then
    echo -e "${RED}Error: uv not found${NC}"
    echo "Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo -e "  ✅ All prerequisites found\n"

# Validate environment variables
echo -e "${GREEN}[2/5]${NC} Validating environment variables..."

# Load .env if it exists
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Check for ANTHROPIC_API_KEY (optional when using OAuth)
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "  ${YELLOW}ℹ️  ANTHROPIC_API_KEY not set (using OAuth authentication)${NC}"
    echo -e "  ${CYAN}Note:${NC} Workflows will use Claude Code OAuth for API access"
else
    echo -e "  ✅ ANTHROPIC_API_KEY found in environment"
fi

# Warn if GITHUB_PAT is missing (not required but recommended)
if [ -z "$GITHUB_PAT" ]; then
    echo -e "  ${YELLOW}⚠️  GITHUB_PAT not set (recommended for API rate limits)${NC}"
fi

echo -e "  ✅ Environment validated\n"

# Create log directory
mkdir -p /tmp/adw_logs

# Generate webhook secret if it doesn't exist
if [ ! -f "$HOME/.adw/webhook_secret" ]; then
    echo -e "${GREEN}[3/5]${NC} Generating webhook secret..."
    mkdir -p "$HOME/.adw"
    openssl rand -hex 32 > "$HOME/.adw/webhook_secret"
    echo -e "  ✅ Secret generated: ${YELLOW}$(cat $HOME/.adw/webhook_secret)${NC}"
    echo -e "  📝 Saved to: ~/.adw/webhook_secret\n"

    # Update .env
    if [ -f ".env" ]; then
        sed -i '' '/GITHUB_WEBHOOK_SECRET/d' .env 2>/dev/null || true
    fi
    echo "GITHUB_WEBHOOK_SECRET=$(cat $HOME/.adw/webhook_secret)" >> .env
    echo -e "  ✅ Added to .env\n"
else
    echo -e "${GREEN}[3/5]${NC} Using existing webhook secret"
    echo -e "  📝 Secret: ${YELLOW}$(cat $HOME/.adw/webhook_secret)${NC}\n"
fi

# Start Cloudflare Tunnel (temporary URL)
echo -e "${GREEN}[4/5]${NC} Starting Cloudflare Tunnel (temporary URL)..."
cloudflared tunnel --url http://localhost:8000 > /tmp/adw_logs/tunnel.log 2>&1 &
TUNNEL_PID=$!
echo -e "  📡 Tunnel PID: ${YELLOW}$TUNNEL_PID${NC}"

# Wait for tunnel to generate URL (check logs)
echo -e "  ⏳ Waiting for tunnel URL..."
# Set port (use 8000 to avoid conflict with macOS AirPlay on 5000)
export PORT=8000

TUNNEL_URL=""
for i in {1..30}; do
    sleep 1
    if [ -f /tmp/adw_logs/tunnel.log ]; then
        # Look for the URL in logs (format: https://random-words-1234.trycloudflare.com)
        TUNNEL_URL=$(grep -oE 'https://[a-zA-Z0-9-]+\.trycloudflare\.com' /tmp/adw_logs/tunnel.log | head -1)
        if [ ! -z "$TUNNEL_URL" ]; then
            break
        fi
    fi
done

if [ -z "$TUNNEL_URL" ]; then
    echo -e "${RED}  ❌ Failed to get tunnel URL${NC}"
    echo "Check logs: tail -f /tmp/adw_logs/tunnel.log"
    kill $TUNNEL_PID 2>/dev/null
    exit 1
fi

echo -e "  ✅ Tunnel running\n"

# Start Webhook Server
echo -e "${GREEN}[5/5]${NC} Starting Webhook Server..."
cd webhook-hub
uv run triggers/trigger_webhook.py > /tmp/adw_logs/webhook.log 2>&1 &
WEBHOOK_PID=$!
cd ..
echo -e "  🔗 Webhook PID: ${YELLOW}$WEBHOOK_PID${NC}"

# Wait for webhook server to initialize
sleep 3

if ! ps -p $WEBHOOK_PID > /dev/null; then
    echo -e "${RED}  ❌ Webhook server failed to start${NC}"
    echo "Check logs: tail -f /tmp/adw_logs/webhook.log"
    kill $TUNNEL_PID 2>/dev/null
    exit 1
fi
echo -e "  ✅ Webhook server running\n"

# Start Queue Worker
echo -e "${GREEN}[6/6]${NC} Starting Queue Worker..."
cd webhook-hub
uv run triggers/queue_worker.py > /tmp/adw_logs/queue_worker.log 2>&1 &
WORKER_PID=$!
cd ..
echo -e "  ⚙️  Worker PID: ${YELLOW}$WORKER_PID${NC}"

# Wait for worker to initialize
sleep 2

if ! ps -p $WORKER_PID > /dev/null; then
    echo -e "${RED}  ❌ Queue worker failed to start${NC}"
    echo "Check logs: tail -f /tmp/adw_logs/queue_worker.log"
    kill $TUNNEL_PID $WEBHOOK_PID 2>/dev/null
    exit 1
fi
echo -e "  ✅ Queue worker running\n"

# Display important information
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   All Services Running Successfully    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}\n"

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                  IMPORTANT - GITHUB WEBHOOK SETUP          ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}\n"

echo -e "${YELLOW}⚠️  TEMPORARY URL - Changes on restart!${NC}\n"

echo -e "${BLUE}1. Go to your GitHub repository → Settings → Webhooks → Add webhook${NC}\n"

echo -e "${BLUE}2. Configure webhook with these values:${NC}"
echo -e "   ${CYAN}Payload URL:${NC}"
echo -e "   ${GREEN}${TUNNEL_URL}/gh-webhook${NC}\n"

echo -e "   ${CYAN}Content type:${NC}"
echo -e "   application/json\n"

echo -e "   ${CYAN}Secret:${NC}"
echo -e "   ${GREEN}$(cat $HOME/.adw/webhook_secret)${NC}\n"

echo -e "   ${CYAN}Events:${NC}"
echo -e "   ☑️  Issues"
echo -e "   ☑️  Issue comments\n"

echo -e "   ${CYAN}Active:${NC}"
echo -e "   ☑️  Checked\n"

echo -e "${BLUE}3. Click 'Add webhook'${NC}\n"

echo -e "${BLUE}4. Test by creating an issue with one of these labels:${NC}"
echo -e "   • ${GREEN}auto-sdlc${NC}  - Full SDLC (plan → build → test → review → PR)"
echo -e "   • ${GREEN}auto-plan${NC}  - Planning only"
echo -e "   • ${GREEN}auto-build${NC} - Plan + Build"
echo -e "   • ${GREEN}auto-test${NC}  - Plan + Build + Test\n"

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                    SERVICE INFORMATION                     ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}\n"

echo -e "${BLUE}Service PIDs:${NC}"
echo -e "  Tunnel:  ${YELLOW}$TUNNEL_PID${NC}"
echo -e "  Webhook: ${YELLOW}$WEBHOOK_PID${NC}"
echo -e "  Worker:  ${YELLOW}$WORKER_PID${NC}\n"

echo -e "${BLUE}Public Webhook URL:${NC}"
echo -e "  ${GREEN}${TUNNEL_URL}/gh-webhook${NC}\n"

echo -e "${BLUE}Local Endpoints:${NC}"
echo -e "  Health:      http://localhost:8000/health"
echo -e "  Queue Stats: http://localhost:8000/queue/stats\n"

echo -e "${BLUE}Logs:${NC}"
echo -e "  Tunnel:  tail -f /tmp/adw_logs/tunnel.log"
echo -e "  Webhook: tail -f /tmp/adw_logs/webhook.log"
echo -e "  Worker:  tail -f /tmp/adw_logs/queue_worker.log\n"

echo -e "${BLUE}Health Check:${NC}"
echo -e "  ./scripts/health_check.sh\n"

echo -e "${BLUE}Stop Services:${NC}"
echo -e "  ${YELLOW}Press Ctrl+C${NC} or run: kill $TUNNEL_PID $WEBHOOK_PID $WORKER_PID\n"

# Save PIDs and URL to file
echo "$TUNNEL_PID $WEBHOOK_PID $WORKER_PID" > /tmp/adw_services.pids
echo "$TUNNEL_URL" > /tmp/adw_tunnel_url.txt

echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}\n"
echo -e "${YELLOW}📋 Quick Setup Checklist:${NC}"
echo -e "  ☐ Copy webhook URL above"
echo -e "  ☐ Copy webhook secret above"
echo -e "  ☐ Go to GitHub repo → Settings → Webhooks"
echo -e "  ☐ Add webhook with URL and secret"
echo -e "  ☐ Select 'Issues' and 'Issue comments' events"
echo -e "  ☐ Test by creating issue with 'auto-plan' label\n"

echo -e "${GREEN}Ready to receive webhooks!${NC} 🚀\n"
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}\n"

# Wait and handle Ctrl+C gracefully
trap "echo -e '\n${YELLOW}Stopping services...${NC}'; kill $TUNNEL_PID $WEBHOOK_PID $WORKER_PID 2>/dev/null; rm -f /tmp/adw_services.pids /tmp/adw_tunnel_url.txt; echo -e '${GREEN}Services stopped${NC}'; exit" INT TERM

# Keep script running
wait
