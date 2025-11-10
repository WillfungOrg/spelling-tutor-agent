#!/bin/bash

# TAC Local Trigger - Pulls latest GitHub issues and processes them
# Usage: ./scripts/tac-local-trigger.sh
# NOTE: Update REPO variable when copying to new project

set -e

# ⚠️ CUSTOMIZE THIS: Update with your repo name when copying to new project
REPO="willfung28/agentic-coding-library"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🤖 TAC Local Trigger"
echo "===================="
echo ""
echo "🔍 Checking for pending TAC tasks in $REPO..."
echo ""

# Get all open issues with tac:pending label
ISSUES=$(gh issue list --repo "$REPO" --label "tac:pending" --json number,title,body,labels --limit 10)

# Check if there are any issues
ISSUE_COUNT=$(echo "$ISSUES" | jq 'length')

if [ "$ISSUE_COUNT" -eq 0 ]; then
  echo "✅ No pending TAC tasks found."
  echo ""
  echo "💡 To create a new TAC task:"
  echo "   Visit: https://github.com/$REPO/issues/new/choose"
  echo "   Or from CLI: gh issue create --repo $REPO --label tac:pending"
  exit 0
fi

# Show issues
echo "📋 Found $ISSUE_COUNT pending task(s):"
echo ""
echo "$ISSUES" | jq -r '.[] | "  #\(.number): \(.title)"'
echo ""

# Let user pick which issue to process
read -p "Enter issue number to process (or 'q' to quit): " ISSUE_NUM

if [ "$ISSUE_NUM" = "q" ] || [ -z "$ISSUE_NUM" ]; then
  echo "Cancelled."
  exit 0
fi

# Get the specific issue details
echo ""
echo "📥 Fetching issue #$ISSUE_NUM details..."
ISSUE_DATA=$(gh issue view "$ISSUE_NUM" --repo "$REPO" --json number,title,body,labels)

# Extract work type from body (since it's in the form data)
WORK_TYPE=$(echo "$ISSUE_DATA" | jq -r '.body' | grep -A1 "Work Type" | tail -1 | xargs || echo "feature")

# Save issue details to temp file for the agent to read
ISSUE_FILE="$PROJECT_ROOT/.tac/current-issue.json"
mkdir -p "$PROJECT_ROOT/.tac"
echo "$ISSUE_DATA" > "$ISSUE_FILE"

# Also save a human-readable version
echo "$ISSUE_DATA" | jq '.' > "$PROJECT_ROOT/.tac/current-issue-readable.json"

# Update issue label to in-progress
echo "🏷️  Updating issue status to 'in-progress'..."
gh issue edit "$ISSUE_NUM" --repo "$REPO" --remove-label "tac:pending" --add-label "tac:in-progress"

echo ""
echo "✅ Issue #$ISSUE_NUM is ready for processing!"
echo ""
echo "📁 Issue data saved to: .tac/current-issue.json"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Open Claude Desktop (if not already open)"
echo ""
echo "2. Run this command in Claude Desktop:"
echo ""
echo "   Process the TAC issue from .tac/current-issue.json"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 Tip: The agent will:"
echo "   - Read the issue details"
echo "   - Create a branch"
echo "   - Implement the changes"
echo "   - Run tests"
echo "   - Create a PR"
echo "   - Update the issue to 'tac:completed'"
echo ""
