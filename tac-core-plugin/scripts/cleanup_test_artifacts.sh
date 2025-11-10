#!/bin/bash
# Automated cleanup script for ADW test artifacts
# This script safely removes test worktrees and related files

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DRY_RUN=false
KEEP_LEARNING=true  # Always keep learning logs by default
AGE_DAYS=7  # Default: clean up artifacts older than 7 days

# Usage function
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Cleanup ADW test artifacts including worktrees, agent state, and logs.

OPTIONS:
    -d, --dry-run              Show what would be deleted without deleting
    -a, --age DAYS             Only clean artifacts older than DAYS (default: 7)
    --all                      Clean all test artifacts regardless of age
    --keep-learning            Keep learning logs (default: true)
    --remove-learning          Also remove learning logs
    --adw-id ID                Clean specific ADW ID only
    -h, --help                 Show this help message

EXAMPLES:
    # Dry run to see what would be deleted
    $0 --dry-run

    # Clean artifacts older than 7 days
    $0 --age 7

    # Clean all test artifacts (dangerous!)
    $0 --all

    # Clean specific ADW ID
    $0 --adw-id b7724708

    # Clean everything including learning logs
    $0 --all --remove-learning
EOF
    exit 1
}

# Parse arguments
SPECIFIC_ADW_ID=""
CLEAN_ALL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -a|--age)
            AGE_DAYS="$2"
            shift 2
            ;;
        --all)
            CLEAN_ALL=true
            shift
            ;;
        --keep-learning)
            KEEP_LEARNING=true
            shift
            ;;
        --remove-learning)
            KEEP_LEARNING=false
            shift
            ;;
        --adw-id)
            SPECIFIC_ADW_ID="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            ;;
    esac
done

# Change to repo root
cd "$REPO_ROOT"

echo -e "${BLUE}=== ADW Test Artifacts Cleanup ===${NC}"
echo -e "Repository: ${REPO_ROOT}"
echo -e "Dry run: ${DRY_RUN}"
echo -e "Age threshold: ${AGE_DAYS} days"
echo -e "Keep learning logs: ${KEEP_LEARNING}"
echo ""

# Function to check if path is older than threshold
is_old_enough() {
    local path="$1"
    if [ "$CLEAN_ALL" = true ]; then
        return 0  # Clean everything
    fi

    if [ ! -e "$path" ]; then
        return 1  # Path doesn't exist
    fi

    # Get modification time in seconds since epoch
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        local mod_time=$(stat -f %m "$path")
    else
        # Linux
        local mod_time=$(stat -c %Y "$path")
    fi

    local current_time=$(date +%s)
    local age_seconds=$((current_time - mod_time))
    local threshold_seconds=$((AGE_DAYS * 86400))

    [ $age_seconds -gt $threshold_seconds ]
}

# Function to safely remove file/directory
safe_remove() {
    local path="$1"
    local description="$2"

    if [ ! -e "$path" ]; then
        return
    fi

    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}[DRY RUN]${NC} Would remove: ${description}"
        du -sh "$path" 2>/dev/null || echo "  (empty)"
    else
        echo -e "${GREEN}Removing:${NC} ${description}"
        rm -rf "$path"
    fi
}

# Function to remove git branch
remove_branch() {
    local branch_name="$1"

    if git show-ref --verify --quiet "refs/heads/$branch_name"; then
        if [ "$DRY_RUN" = true ]; then
            echo -e "${YELLOW}[DRY RUN]${NC} Would delete branch: ${branch_name}"
        else
            echo -e "${GREEN}Deleting branch:${NC} ${branch_name}"
            git branch -D "$branch_name" 2>/dev/null || true
        fi
    fi
}

# Get list of ADW IDs to clean
if [ -n "$SPECIFIC_ADW_ID" ]; then
    ADW_IDS=("$SPECIFIC_ADW_ID")
    echo -e "${BLUE}Cleaning specific ADW ID: ${SPECIFIC_ADW_ID}${NC}\n"
else
    # Get all ADW IDs from worktrees
    ADW_IDS=()

    # Check both trees/ and webhook-hub/runtime/trees/ locations
    for trees_dir in "trees" "webhook-hub/runtime/trees"; do
        if [ -d "$trees_dir" ]; then
            for worktree_path in "$trees_dir"/*; do
                if [ -d "$worktree_path" ]; then
                    adw_id=$(basename "$worktree_path")
                    if [[ ! " ${ADW_IDS[@]} " =~ " ${adw_id} " ]]; then
                        ADW_IDS+=("$adw_id")
                    fi
                fi
            done
        fi
    done

    # Also get ADW IDs from agents directory
    if [ -d "agents" ]; then
        for agent_path in agents/*; do
            if [ -d "$agent_path" ]; then
                adw_id=$(basename "$agent_path")
                # Check if it's a valid ADW ID (8 characters, alphanumeric)
                if [[ "$adw_id" =~ ^[a-z0-9]{8}$ ]]; then
                    if [[ ! " ${ADW_IDS[@]} " =~ " ${adw_id} " ]]; then
                        ADW_IDS+=("$adw_id")
                    fi
                fi
            fi
        done
    fi
fi

# Summary counters
TOTAL_WORKTREES=0
TOTAL_AGENTS=0
TOTAL_BRANCHES=0
TOTAL_LOGS=0
TOTAL_LEARNING=0

# Clean each ADW ID
for adw_id in "${ADW_IDS[@]}"; do
    echo -e "${BLUE}Processing ADW ID: ${adw_id}${NC}"

    # 1. Remove worktree (check both trees/ and webhook-hub/runtime/trees/)
    for worktree_path in "trees/$adw_id" "webhook-hub/runtime/trees/$adw_id"; do
        if [ -d "$worktree_path" ]; then
            if is_old_enough "$worktree_path"; then
                # First, remove from git worktree list
                if [ "$DRY_RUN" = false ]; then
                    git worktree remove "$worktree_path" --force 2>/dev/null || rm -rf "$worktree_path"
                else
                    echo -e "${YELLOW}[DRY RUN]${NC} Would remove worktree: $worktree_path"
                fi
                safe_remove "$worktree_path" "Worktree: $worktree_path"
                ((TOTAL_WORKTREES++))
            else
                echo -e "  Skipping worktree (too recent): $worktree_path"
            fi
        fi
    done

    # 2. Remove agent state (check both agents/ and webhook-hub/runtime/agents/)
    for agent_path in "agents/$adw_id" "webhook-hub/runtime/agents/$adw_id"; do
        if [ ! -d "$agent_path" ]; then
            continue
        fi
        if is_old_enough "$agent_path"; then
            safe_remove "$agent_path" "Agent state: $agent_path"
            ((TOTAL_AGENTS++))
        else
            echo -e "  Skipping agent state (too recent): $agent_path"
        fi
    done

    # 3. Remove git branch (look for branches with this ADW ID)
    for branch in $(git branch --list | grep "$adw_id" | sed 's/^[* ]*//'); do
        if [ -n "$branch" ]; then
            remove_branch "$branch"
            ((TOTAL_BRANCHES++))
        fi
    done

    # 4. Remove learning logs (optional)
    if [ "$KEEP_LEARNING" = false ]; then
        learning_file="adw/.tac/learning/execution_logs/${adw_id}.json"
        if [ -f "$learning_file" ]; then
            if is_old_enough "$learning_file"; then
                safe_remove "$learning_file" "Learning log: $learning_file"
                ((TOTAL_LEARNING++))
            else
                echo -e "  Skipping learning log (too recent): $learning_file"
            fi
        fi
    fi

    echo ""
done

# Clean orphaned session logs (logs that don't match any ADW ID)
for logs_base_dir in "logs" "webhook-hub/runtime/logs"; do
    if [ -d "$logs_base_dir" ]; then
        echo -e "${BLUE}Cleaning orphaned session logs in $logs_base_dir...${NC}"
        for log_dir in "$logs_base_dir"/*; do
        if [ -d "$log_dir" ]; then
            if is_old_enough "$log_dir"; then
                session_id=$(basename "$log_dir")
                # Check if this session ID belongs to any existing ADW
                found=false
                for adw_id in "${ADW_IDS[@]}"; do
                    if [ -d "agents/$adw_id" ]; then
                        if grep -q "$session_id" "agents/$adw_id"/*.jsonl 2>/dev/null; then
                            found=true
                            break
                        fi
                    fi
                done

                if [ "$found" = false ]; then
                    safe_remove "$log_dir" "Orphaned log: $log_dir"
                    ((TOTAL_LOGS++))
                fi
            fi
        fi
        done
    fi
done

# Summary
echo ""
echo -e "${BLUE}=== Cleanup Summary ===${NC}"
echo -e "Worktrees removed: ${TOTAL_WORKTREES}"
echo -e "Agent states removed: ${TOTAL_AGENTS}"
echo -e "Branches deleted: ${TOTAL_BRANCHES}"
echo -e "Session logs removed: ${TOTAL_LOGS}"
if [ "$KEEP_LEARNING" = false ]; then
    echo -e "Learning logs removed: ${TOTAL_LEARNING}"
else
    echo -e "Learning logs: ${GREEN}Preserved${NC}"
fi

if [ "$DRY_RUN" = true ]; then
    echo ""
    echo -e "${YELLOW}This was a dry run. No files were actually deleted.${NC}"
    echo -e "Run without --dry-run to perform the cleanup."
fi

echo ""
echo -e "${GREEN}Cleanup complete!${NC}"
