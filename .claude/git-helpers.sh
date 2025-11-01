#!/bin/bash
# Git Helper Scripts for AI-Assisted Development
# Source this file: source .claude/git-helpers.sh

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# SAFETY CHECK - Run before switching branches
# ============================================================================
git-safe-check() {
    echo -e "${BLUE}=== Git Safety Check ===${NC}"

    # Check current branch
    current_branch=$(git branch --show-current)
    echo -e "${GREEN}Current branch:${NC} $current_branch"

    # Check for uncommitted changes
    if [[ -n $(git status -s) ]]; then
        echo -e "${YELLOW}⚠️  You have uncommitted changes:${NC}"
        git status -s
        echo -e "${YELLOW}💡 Tip: Run 'git-save' to stash them safely${NC}"
        return 1
    else
        echo -e "${GREEN}✓ No uncommitted changes${NC}"
    fi

    # Check for unpushed commits
    if [[ -n $(git log @{u}.. --oneline 2>/dev/null) ]]; then
        echo -e "${YELLOW}⚠️  You have unpushed commits:${NC}"
        git log @{u}.. --oneline
        echo -e "${YELLOW}💡 Tip: Run 'git push' or 'git-save' first${NC}"
    else
        echo -e "${GREEN}✓ No unpushed commits${NC}"
    fi

    # List all branches
    echo -e "\n${BLUE}All branches:${NC}"
    git branch -a

    echo -e "\n${GREEN}✓ Safety check complete${NC}"
}

# ============================================================================
# SAVE WORK - Stash with descriptive message
# ============================================================================
git-save() {
    if [[ -z $(git status -s) ]]; then
        echo -e "${GREEN}✓ No changes to save${NC}"
        return 0
    fi

    current_branch=$(git branch --show-current)
    timestamp=$(date +"%Y-%m-%d_%H:%M:%S")
    message="${1:-WIP on $current_branch}"

    git stash save "$message - $timestamp"
    echo -e "${GREEN}✓ Saved: $message${NC}"
    echo -e "${YELLOW}💡 Restore with: git stash pop${NC}"
}

# ============================================================================
# COMBINE BRANCHES - Merge two branches safely
# ============================================================================
git-combine() {
    if [ $# -lt 1 ]; then
        echo -e "${RED}Usage: git-combine <branch-to-merge-in> [new-branch-name]${NC}"
        echo -e "${YELLOW}Example: git-combine feature-A combined-fix${NC}"
        return 1
    fi

    branch_to_merge="$1"
    current_branch=$(git branch --show-current)

    # Determine new branch name
    if [ -n "$2" ]; then
        new_branch="$2"
    else
        new_branch="combined-${current_branch}-and-${branch_to_merge}"
    fi

    echo -e "${BLUE}=== Combining Branches ===${NC}"
    echo -e "${GREEN}Current branch:${NC} $current_branch"
    echo -e "${GREEN}Merging in:${NC} $branch_to_merge"
    echo -e "${GREEN}New branch:${NC} $new_branch"

    # Safety check
    if [[ -n $(git status -s) ]]; then
        echo -e "${RED}✗ You have uncommitted changes. Stash or commit first.${NC}"
        return 1
    fi

    # Fetch latest
    echo -e "\n${BLUE}Fetching latest changes...${NC}"
    git fetch origin

    # Create new branch
    echo -e "\n${BLUE}Creating new branch...${NC}"
    git checkout -b "$new_branch"

    # Merge
    echo -e "\n${BLUE}Merging $branch_to_merge...${NC}"
    if git merge "$branch_to_merge"; then
        echo -e "${GREEN}✓ Merge successful${NC}"
        echo -e "${YELLOW}💡 Next steps:${NC}"
        echo -e "  1. Run tests: pytest tests/ -v"
        echo -e "  2. Push: git push origin $new_branch"
    else
        echo -e "${RED}✗ Merge conflicts detected${NC}"
        echo -e "${YELLOW}💡 Resolve conflicts in the files above, then:${NC}"
        echo -e "  1. git add <resolved-files>"
        echo -e "  2. git commit -m 'Merge $branch_to_merge into $new_branch'"
        echo -e "  3. pytest tests/ -v"
        echo -e "  4. git push origin $new_branch"
    fi
}

# ============================================================================
# MERGE INTO CURRENT - Merge another branch into current (no new branch)
# ============================================================================
git-merge-in() {
    if [ $# -lt 1 ]; then
        echo -e "${RED}Usage: git-merge-in <branch-to-merge>${NC}"
        echo -e "${YELLOW}Example: git-merge-in feature-A${NC}"
        return 1
    fi

    branch_to_merge="$1"
    current_branch=$(git branch --show-current)

    echo -e "${BLUE}=== Merging into Current Branch ===${NC}"
    echo -e "${GREEN}Current branch:${NC} $current_branch"
    echo -e "${GREEN}Merging in:${NC} $branch_to_merge"

    # Safety check
    if [[ -n $(git status -s) ]]; then
        echo -e "${RED}✗ You have uncommitted changes. Stash or commit first.${NC}"
        return 1
    fi

    # Fetch latest
    echo -e "\n${BLUE}Fetching latest changes...${NC}"
    git fetch origin

    # Merge
    echo -e "\n${BLUE}Merging...${NC}"
    if git merge "$branch_to_merge"; then
        echo -e "${GREEN}✓ Merge successful${NC}"
        echo -e "${YELLOW}💡 Next steps:${NC}"
        echo -e "  1. Run tests: pytest tests/ -v"
        echo -e "  2. Push: git push origin $current_branch"
    else
        echo -e "${RED}✗ Merge conflicts detected${NC}"
        echo -e "${YELLOW}💡 To abort: git merge --abort${NC}"
    fi
}

# ============================================================================
# FETCH AND PREVIEW - See what's in another branch before merging
# ============================================================================
git-preview() {
    if [ $# -lt 1 ]; then
        echo -e "${RED}Usage: git-preview <branch-name>${NC}"
        echo -e "${YELLOW}Example: git-preview origin/feature-A${NC}"
        return 1
    fi

    branch="$1"
    current_branch=$(git branch --show-current)

    echo -e "${BLUE}=== Preview: $branch ===${NC}"

    # Fetch latest
    git fetch origin >/dev/null 2>&1

    # Show commits
    echo -e "\n${GREEN}Commits in $branch not in $current_branch:${NC}"
    git log $current_branch..$branch --oneline --decorate

    # Show file changes
    echo -e "\n${GREEN}Files changed:${NC}"
    git diff $current_branch...$branch --stat

    echo -e "\n${YELLOW}💡 To see full diff: git diff $current_branch...$branch${NC}"
    echo -e "${YELLOW}💡 To merge: git-merge-in $branch${NC}"
}

# ============================================================================
# LIST STASHES - Show all saved work
# ============================================================================
git-list-stashes() {
    echo -e "${BLUE}=== Saved Work (Stashes) ===${NC}"

    if [[ -z $(git stash list) ]]; then
        echo -e "${GREEN}No stashes found${NC}"
        return 0
    fi

    git stash list

    echo -e "\n${YELLOW}💡 To view stash: git stash show -p stash@{0}${NC}"
    echo -e "${YELLOW}💡 To restore stash: git stash pop${NC}"
    echo -e "${YELLOW}💡 To restore specific: git stash apply stash@{0}${NC}"
}

# ============================================================================
# EMERGENCY UNDO - Abort merge or reset to last commit
# ============================================================================
git-undo() {
    echo -e "${BLUE}=== Emergency Undo Options ===${NC}"
    echo -e "${YELLOW}Choose an option:${NC}"
    echo -e "  1) Abort current merge"
    echo -e "  2) Discard uncommitted changes"
    echo -e "  3) Undo last commit (keep changes)"
    echo -e "  4) Show reflog (find lost commits)"
    echo -e "  5) Cancel"

    read -p "Enter choice [1-5]: " choice

    case $choice in
        1)
            git merge --abort
            echo -e "${GREEN}✓ Merge aborted${NC}"
            ;;
        2)
            read -p "⚠️  This will discard ALL uncommitted changes. Continue? (yes/no): " confirm
            if [ "$confirm" = "yes" ]; then
                git reset --hard HEAD
                echo -e "${GREEN}✓ Changes discarded${NC}"
            else
                echo -e "${YELLOW}Cancelled${NC}"
            fi
            ;;
        3)
            git reset --soft HEAD~1
            echo -e "${GREEN}✓ Last commit undone (changes kept)${NC}"
            ;;
        4)
            git reflog
            echo -e "\n${YELLOW}💡 To restore: git cherry-pick <commit-hash>${NC}"
            ;;
        5)
            echo -e "${YELLOW}Cancelled${NC}"
            ;;
        *)
            echo -e "${RED}Invalid choice${NC}"
            ;;
    esac
}

# ============================================================================
# QUICK STATUS - Show everything at a glance
# ============================================================================
git-status-all() {
    echo -e "${BLUE}=== Complete Git Status ===${NC}"

    # Current branch
    current_branch=$(git branch --show-current)
    echo -e "\n${GREEN}Current Branch:${NC} $current_branch"

    # Uncommitted changes
    if [[ -n $(git status -s) ]]; then
        echo -e "\n${YELLOW}Uncommitted Changes:${NC}"
        git status -s
    else
        echo -e "\n${GREEN}✓ No uncommitted changes${NC}"
    fi

    # Unpushed commits
    if [[ -n $(git log @{u}.. --oneline 2>/dev/null) ]]; then
        echo -e "\n${YELLOW}Unpushed Commits:${NC}"
        git log @{u}.. --oneline
    else
        echo -e "\n${GREEN}✓ No unpushed commits${NC}"
    fi

    # Recent commits
    echo -e "\n${GREEN}Recent Commits:${NC}"
    git log --oneline -5

    # All branches
    echo -e "\n${GREEN}All Branches:${NC}"
    git branch -a

    # Stashes
    if [[ -n $(git stash list) ]]; then
        echo -e "\n${YELLOW}Stashed Work:${NC}"
        git stash list
    fi
}

# ============================================================================
# HELP - Show all available commands
# ============================================================================
git-helpers() {
    echo -e "${BLUE}=== Git Helper Commands ===${NC}"
    echo -e ""
    echo -e "${GREEN}Safety & Status:${NC}"
    echo -e "  git-safe-check        Check status before switching branches"
    echo -e "  git-status-all        Show complete git status"
    echo -e "  git-save [msg]        Stash changes with descriptive message"
    echo -e "  git-list-stashes      Show all stashed work"
    echo -e ""
    echo -e "${GREEN}Combining Branches:${NC}"
    echo -e "  git-combine <branch> [new-name]   Create new branch with merge"
    echo -e "  git-merge-in <branch>             Merge into current branch"
    echo -e "  git-preview <branch>              Preview changes before merge"
    echo -e ""
    echo -e "${GREEN}Emergency:${NC}"
    echo -e "  git-undo              Interactive undo menu"
    echo -e ""
    echo -e "${YELLOW}💡 Tip: Run 'git-safe-check' before any branch operation${NC}"
}

# ============================================================================
# INSTALLATION MESSAGE
# ============================================================================
echo -e "${GREEN}✓ Git helpers loaded!${NC}"
echo -e "${YELLOW}💡 Type 'git-helpers' to see all available commands${NC}"
