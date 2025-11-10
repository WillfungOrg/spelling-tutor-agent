#!/bin/bash
# Cleanup script for webhook server repos/ directory
#
# Usage:
#   ./scripts/cleanup_repos.sh [--dry-run] [--days N]
#
# Options:
#   --dry-run    Show what would be deleted without deleting
#   --days N     Keep repos modified in last N days (default: 30)

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LIBRARY_ROOT="$(dirname "$SCRIPT_DIR")"
REPOS_DIR="$LIBRARY_ROOT/webhook-hub/runtime/repos"

# Default: keep repos modified in last 30 days
DAYS=30
DRY_RUN=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --days)
            DAYS="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--dry-run] [--days N]"
            exit 1
            ;;
    esac
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Webhook Repos Cleanup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ ! -d "$REPOS_DIR" ]; then
    echo "✅ No repos/ directory found. Nothing to clean."
    exit 0
fi

echo "📁 Repos directory: $REPOS_DIR"
echo "📅 Keep repos modified in last $DAYS days"
[ "$DRY_RUN" = true ] && echo "🔍 DRY RUN MODE - No files will be deleted"
echo ""

# Calculate current size
CURRENT_SIZE=$(du -sh "$REPOS_DIR" 2>/dev/null | cut -f1)
echo "💾 Current size: $CURRENT_SIZE"
echo ""

# Find old worktrees in each repo
echo "🔍 Scanning for old worktrees..."
echo ""

WORKTREES_REMOVED=0
WORKTREES_SIZE=0

for REPO_PATH in "$REPOS_DIR"/*; do
    if [ ! -d "$REPO_PATH" ]; then
        continue
    fi

    REPO_NAME=$(basename "$REPO_PATH")

    # Check for worktrees
    TREES_DIR="$REPO_PATH/trees"
    if [ -d "$TREES_DIR" ]; then
        for WORKTREE in "$TREES_DIR"/*; do
            if [ ! -d "$WORKTREE" ]; then
                continue
            fi

            # Check last modified time
            if [ -d "$WORKTREE/.git" ]; then
                MODIFIED=$(stat -f "%Sm" -t "%Y-%m-%d" "$WORKTREE/.git" 2>/dev/null || echo "unknown")
                DAYS_OLD=$(( ($(date +%s) - $(stat -f "%m" "$WORKTREE/.git" 2>/dev/null || echo 0)) / 86400 ))

                if [ "$DAYS_OLD" -gt "$DAYS" ]; then
                    WORKTREE_NAME=$(basename "$WORKTREE")
                    WORKTREE_SIZE=$(du -sh "$WORKTREE" 2>/dev/null | cut -f1)

                    echo "  🗑️  $REPO_NAME/trees/$WORKTREE_NAME"
                    echo "      Last modified: $MODIFIED ($DAYS_OLD days ago)"
                    echo "      Size: $WORKTREE_SIZE"

                    if [ "$DRY_RUN" = false ]; then
                        # Remove worktree properly
                        cd "$REPO_PATH"
                        git worktree remove "trees/$WORKTREE_NAME" --force 2>/dev/null || rm -rf "$WORKTREE"
                        echo "      ✅ Removed"
                    else
                        echo "      [Would remove]"
                    fi

                    WORKTREES_REMOVED=$((WORKTREES_REMOVED + 1))
                    echo ""
                fi
            fi
        done
    fi
done

# Find repos that haven't been accessed in N days
echo "🔍 Scanning for inactive repos..."
echo ""

REPOS_REMOVED=0

for REPO_PATH in "$REPOS_DIR"/*; do
    if [ ! -d "$REPO_PATH" ]; then
        continue
    fi

    REPO_NAME=$(basename "$REPO_PATH")

    # Check last modified time of .git directory
    if [ -d "$REPO_PATH/.git" ]; then
        MODIFIED=$(stat -f "%Sm" -t "%Y-%m-%d" "$REPO_PATH/.git" 2>/dev/null || echo "unknown")
        DAYS_OLD=$(( ($(date +%s) - $(stat -f "%m" "$REPO_PATH/.git" 2>/dev/null || echo 0)) / 86400 ))

        if [ "$DAYS_OLD" -gt "$DAYS" ]; then
            REPO_SIZE=$(du -sh "$REPO_PATH" 2>/dev/null | cut -f1)

            echo "  🗑️  $REPO_NAME"
            echo "      Last modified: $MODIFIED ($DAYS_OLD days ago)"
            echo "      Size: $REPO_SIZE"

            if [ "$DRY_RUN" = false ]; then
                rm -rf "$REPO_PATH"
                echo "      ✅ Removed"
            else
                echo "      [Would remove]"
            fi

            REPOS_REMOVED=$((REPOS_REMOVED + 1))
            echo ""
        fi
    fi
done

# Calculate new size
if [ "$DRY_RUN" = false ] && [ -d "$REPOS_DIR" ]; then
    NEW_SIZE=$(du -sh "$REPOS_DIR" 2>/dev/null | cut -f1)
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Cleanup Summary"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "💾 Size before: $CURRENT_SIZE"
    echo "💾 Size after:  $NEW_SIZE"
    echo "🗑️  Worktrees removed: $WORKTREES_REMOVED"
    echo "🗑️  Repos removed: $REPOS_REMOVED"
else
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Dry Run Summary"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🗑️  Would remove $WORKTREES_REMOVED worktrees"
    echo "🗑️  Would remove $REPOS_REMOVED repos"
    echo ""
    echo "Run without --dry-run to actually delete"
fi
echo ""
