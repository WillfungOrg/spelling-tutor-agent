#!/bin/bash
# Setup ADW labels for all repos in organization

ORG="WillfungOrg"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Setting up ADW labels for $ORG"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo "   Install with: brew install gh"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub CLI."
    echo "   Run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI authenticated"
echo ""

# Get all repos in org
echo "🔍 Fetching repositories from $ORG..."
REPOS=$(gh repo list $ORG --limit 1000 --json name -q '.[].name' 2>/dev/null)

if [ -z "$REPOS" ]; then
    echo "❌ No repositories found or unable to access $ORG"
    echo "   Make sure you have access to the organization"
    exit 1
fi

REPO_COUNT=$(echo "$REPOS" | wc -l | tr -d ' ')
echo "✅ Found $REPO_COUNT repositories"
echo ""

# Function to create a label
create_label() {
    local repo=$1
    local name=$2
    local color=$3
    local description=$4

    gh label create "$name" \
        --repo "$ORG/$repo" \
        --color "$color" \
        --description "$description" \
        --force 2>/dev/null || true
}

# Create labels in each repo
for repo in $REPOS; do
    echo "📦 Setting up labels in $ORG/$repo..."

    # Planning
    create_label "$repo" "adw-plan" "0366d6" "Create implementation plan"
    create_label "$repo" "adw-design" "0366d6" "Create implementation plan (alias)"

    # Quick fixes
    create_label "$repo" "adw-patch" "d93f0b" "Quick bug fix"
    create_label "$repo" "adw-hotfix" "d93f0b" "Quick bug fix (alias)"

    # Implementation (dependent)
    create_label "$repo" "adw-implement" "0e8a16" "Build from existing plan"
    create_label "$repo" "adw-build" "0e8a16" "Build from existing plan (alias)"

    # Testing (dependent)
    create_label "$repo" "adw-test" "fbca04" "Run tests with auto-fix"
    create_label "$repo" "adw-e2e" "fbca04" "Run E2E tests"

    # Review & Documentation (dependent)
    create_label "$repo" "adw-review" "5319e7" "Review implementation"
    create_label "$repo" "adw-document" "5319e7" "Generate documentation"

    # Complete workflows
    create_label "$repo" "adw-sdlc" "d73a4a" "Full SDLC pipeline"
    create_label "$repo" "adw-full" "d73a4a" "Full SDLC pipeline (alias)"
    create_label "$repo" "adw-zte" "b60205" "Zero Touch Execution (auto-merge!)"

    # Combined workflows
    create_label "$repo" "adw-plan-build" "1d76db" "Plan + Build"
    create_label "$repo" "adw-pbt" "1d76db" "Plan + Build + Test"
    create_label "$repo" "adw-pbtr" "1d76db" "Plan + Build + Test + Review"

    # Meta strategy
    create_label "$repo" "adw-strategy" "c5def5" "AI recommends best workflow"

    # Model selection
    create_label "$repo" "adw-heavy" "e99695" "Use Opus model (expensive)"
    create_label "$repo" "adw-fast" "c2e0c6" "Use Sonnet model (fast) [default]"

    echo "   ✅ 19 labels created"
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ All labels created across organization!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Created 19 labels in $REPO_COUNT repositories"
echo ""
echo "🎯 Next steps:"
echo "   1. Go to any issue in your org repos"
echo "   2. Add label 'adw-plan' to trigger workflow"
echo "   3. Watch webhook logs: tail -f /tmp/adw_logs/webhook.log"
echo ""
echo "📚 View labels in repo:"
echo "   https://github.com/$ORG/spelling-tutor-agent/labels"
echo ""
