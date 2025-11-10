#!/bin/bash
# Health check script for ADW webhook services
#
# Usage:
#   ./scripts/health_check.sh [--json]
#
# Options:
#   --json    Output in JSON format for monitoring systems

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
JSON_OUTPUT=false
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LIBRARY_ROOT="$(dirname "$SCRIPT_DIR")"
RUNTIME_DIR="$LIBRARY_ROOT/webhook-hub/runtime"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--json]"
            exit 1
            ;;
    esac
done

# Health check results
declare -A CHECKS
OVERALL_HEALTHY=true

# Function to record check result
record_check() {
    local name="$1"
    local status="$2"
    local message="$3"

    CHECKS["$name"]="$status|$message"

    if [ "$status" = "fail" ] || [ "$status" = "error" ]; then
        OVERALL_HEALTHY=false
    fi
}

# Check 1: Verify required environment variables
check_env_vars() {
    local status="pass"
    local message="All required variables set"

    # Load .env if it exists
    if [ -f "$LIBRARY_ROOT/.env" ]; then
        export $(grep -v '^#' "$LIBRARY_ROOT/.env" | xargs 2>/dev/null || true)
    fi

    if [ -z "$ANTHROPIC_API_KEY" ]; then
        status="fail"
        message="ANTHROPIC_API_KEY not set"
    elif [ -z "$GITHUB_WEBHOOK_SECRET" ]; then
        status="warn"
        message="GITHUB_WEBHOOK_SECRET not set"
    elif [ -z "$GITHUB_PAT" ]; then
        status="warn"
        message="GITHUB_PAT not set (recommended)"
    fi

    record_check "env_vars" "$status" "$message"
}

# Check 2: Verify webhook server is running
check_webhook_server() {
    local status="pass"
    local message="Webhook server running"
    local pid=""

    pid=$(pgrep -f "trigger_webhook.py" || echo "")

    if [ -z "$pid" ]; then
        status="fail"
        message="Webhook server not running"
    else
        message="Webhook server running (PID: $pid)"

        # Check if server is responsive
        if command -v curl &> /dev/null; then
            local port="${PORT:-8000}"
            if ! curl -s -f "http://localhost:$port/health" > /dev/null 2>&1; then
                status="warn"
                message="Webhook server running but not responsive on port $port"
            fi
        fi
    fi

    record_check "webhook_server" "$status" "$message"
}

# Check 3: Verify queue worker is running
check_queue_worker() {
    local status="pass"
    local message="Queue worker running"
    local pid=""

    pid=$(pgrep -f "queue_worker.py" || echo "")

    if [ -z "$pid" ]; then
        status="warn"
        message="Queue worker not running (may not be started yet)"
    else
        message="Queue worker running (PID: $pid)"
    fi

    record_check "queue_worker" "$status" "$message"
}

# Check 4: Verify Cloudflare tunnel is running
check_tunnel() {
    local status="pass"
    local message="Cloudflare tunnel running"
    local pid=""

    pid=$(pgrep -f "cloudflared tunnel" || echo "")

    if [ -z "$pid" ]; then
        status="warn"
        message="Cloudflare tunnel not running"
    else
        message="Cloudflare tunnel running (PID: $pid)"

        # Try to get tunnel URL
        if [ -f "/tmp/adw_tunnel_url.txt" ]; then
            local url=$(cat /tmp/adw_tunnel_url.txt)
            message="$message - URL: $url"
        fi
    fi

    record_check "tunnel" "$status" "$message"
}

# Check 5: Verify runtime directories exist
check_runtime_dirs() {
    local status="pass"
    local message="All runtime directories exist"
    local missing=()

    for dir in "repos" "agents" "trees" "logs"; do
        if [ ! -d "$RUNTIME_DIR/$dir" ]; then
            missing+=("$dir")
        fi
    done

    if [ ${#missing[@]} -gt 0 ]; then
        status="warn"
        message="Missing directories: ${missing[*]}"
    fi

    record_check "runtime_dirs" "$status" "$message"
}

# Check 6: Check disk usage of runtime directories
check_disk_usage() {
    local status="pass"
    local message=""

    if [ -d "$RUNTIME_DIR" ]; then
        local size=$(du -sh "$RUNTIME_DIR" 2>/dev/null | cut -f1)
        message="Runtime size: $size"

        # Get size in MB for comparison
        local size_mb=$(du -sm "$RUNTIME_DIR" 2>/dev/null | cut -f1)

        if [ "$size_mb" -gt 10000 ]; then  # > 10GB
            status="warn"
            message="$message (consider cleanup)"
        fi
    else
        status="warn"
        message="Runtime directory does not exist"
    fi

    record_check "disk_usage" "$status" "$message"
}

# Check 7: Verify active worktrees
check_worktrees() {
    local status="pass"
    local message=""

    cd "$LIBRARY_ROOT"
    local count=$(git worktree list | tail -n +2 | wc -l | tr -d ' ')

    message="$count active worktree(s)"

    if [ "$count" -gt 10 ]; then
        status="warn"
        message="$message (consider cleanup if old)"
    fi

    record_check "worktrees" "$status" "$message"
}

# Check 8: Check log files for recent errors
check_logs() {
    local status="pass"
    local message="No recent errors"
    local error_count=0

    # Check webhook log
    if [ -f "/tmp/adw_logs/webhook.log" ]; then
        # Count errors in last 100 lines
        error_count=$(tail -100 /tmp/adw_logs/webhook.log 2>/dev/null | grep -i "error\|exception\|failed" | wc -l | tr -d ' ')

        if [ "$error_count" -gt 10 ]; then
            status="warn"
            message="$error_count errors in webhook log (last 100 lines)"
        fi
    fi

    record_check "logs" "$status" "$message"
}

# Run all checks
check_env_vars
check_webhook_server
check_queue_worker
check_tunnel
check_runtime_dirs
check_disk_usage
check_worktrees
check_logs

# Output results
if [ "$JSON_OUTPUT" = true ]; then
    # JSON output for monitoring systems
    echo -n '{"healthy":'
    if [ "$OVERALL_HEALTHY" = true ]; then
        echo -n 'true'
    else
        echo -n 'false'
    fi
    echo -n ',"checks":{'

    first=true
    for check in "${!CHECKS[@]}"; do
        IFS='|' read -r status message <<< "${CHECKS[$check]}"

        if [ "$first" = false ]; then
            echo -n ','
        fi
        first=false

        echo -n "\"$check\":{\"status\":\"$status\",\"message\":\"$message\"}"
    done

    echo '}}'
else
    # Human-readable output
    echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║   ADW Webhook Services Health Check   ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"

    for check in env_vars webhook_server queue_worker tunnel runtime_dirs disk_usage worktrees logs; do
        if [ -n "${CHECKS[$check]}" ]; then
            IFS='|' read -r status message <<< "${CHECKS[$check]}"

            case $status in
                pass)
                    echo -e "  ${GREEN}✓${NC} $(printf '%-20s' "$check:") $message"
                    ;;
                warn)
                    echo -e "  ${YELLOW}⚠${NC} $(printf '%-20s' "$check:") $message"
                    ;;
                fail|error)
                    echo -e "  ${RED}✗${NC} $(printf '%-20s' "$check:") $message"
                    ;;
            esac
        fi
    done

    echo ""
    echo -e "${BLUE}═══════════════════════════════════════${NC}\n"

    if [ "$OVERALL_HEALTHY" = true ]; then
        echo -e "${GREEN}Overall Status: Healthy ✓${NC}\n"
        exit 0
    else
        echo -e "${RED}Overall Status: Unhealthy ✗${NC}\n"
        echo -e "${YELLOW}Suggestions:${NC}"

        # Check specific failures and provide suggestions
        if [[ "${CHECKS[env_vars]}" == fail* ]]; then
            echo -e "  • Check .env file and ensure ANTHROPIC_API_KEY is set"
        fi

        if [[ "${CHECKS[webhook_server]}" == fail* ]]; then
            echo -e "  • Start webhook services: ./start_adw_services_simple.sh"
        fi

        if [[ "${CHECKS[disk_usage]}" == warn* ]]; then
            echo -e "  • Run cleanup: ./scripts/cleanup_repos.sh"
        fi

        if [[ "${CHECKS[worktrees]}" == warn* ]]; then
            echo -e "  • Clean old worktrees: git worktree prune"
        fi

        echo ""
        exit 1
    fi
fi
