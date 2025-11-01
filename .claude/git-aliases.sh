#!/bin/bash
# Git Aliases for Quick Access
# Run this to install: bash .claude/git-aliases.sh

echo "Installing git aliases..."

# Safety and status
git config --global alias.safe-check '!f() { \
    echo "=== Git Safety Check ==="; \
    echo "Current branch: $(git branch --show-current)"; \
    if [[ -n $(git status -s) ]]; then \
        echo "⚠️  Uncommitted changes:"; \
        git status -s; \
    else \
        echo "✓ No uncommitted changes"; \
    fi; \
    if [[ -n $(git log @{u}.. --oneline 2>/dev/null) ]]; then \
        echo "⚠️  Unpushed commits:"; \
        git log @{u}.. --oneline; \
    else \
        echo "✓ No unpushed commits"; \
    fi; \
    echo "All branches:"; \
    git branch -a; \
}; f'

git config --global alias.s-all '!git status && echo "" && echo "Recent commits:" && git log --oneline -5'

# Combining branches
git config --global alias.combine '!f() { \
    if [ $# -lt 1 ]; then \
        echo "Usage: git combine <branch-to-merge> [new-branch-name]"; \
        return 1; \
    fi; \
    branch_to_merge="$1"; \
    current_branch=$(git branch --show-current); \
    new_branch="${2:-combined-${current_branch}-and-${branch_to_merge}}"; \
    echo "Creating $new_branch and merging $branch_to_merge..."; \
    git fetch origin && \
    git checkout -b "$new_branch" && \
    git merge "$branch_to_merge"; \
}; f'

git config --global alias.merge-in '!f() { \
    if [ $# -lt 1 ]; then \
        echo "Usage: git merge-in <branch>"; \
        return 1; \
    fi; \
    echo "Merging $1 into $(git branch --show-current)..."; \
    git fetch origin && git merge "$1"; \
}; f'

# Preview
git config --global alias.preview '!f() { \
    if [ $# -lt 1 ]; then \
        echo "Usage: git preview <branch>"; \
        return 1; \
    fi; \
    current=$(git branch --show-current); \
    echo "=== Preview: $1 ==="; \
    git fetch origin >/dev/null 2>&1; \
    echo "Commits in $1 not in $current:"; \
    git log $current..$1 --oneline --decorate; \
    echo ""; \
    echo "Files changed:"; \
    git diff $current...$1 --stat; \
}; f'

# Save work (stash)
git config --global alias.save '!f() { \
    branch=$(git branch --show-current); \
    timestamp=$(date +"%Y-%m-%d_%H:%M:%S"); \
    msg="${1:-WIP on $branch}"; \
    git stash save "$msg - $timestamp"; \
    echo "✓ Saved: $msg"; \
}; f'

# List stashes
git config --global alias.stashes 'stash list'

# Undo last commit (keep changes)
git config --global alias.undo-commit 'reset --soft HEAD~1'

# Useful shortcuts
git config --global alias.br 'branch -a'
git config --global alias.co 'checkout'
git config --global alias.st 'status'
git config --global alias.cm 'commit -m'
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.visual 'log --oneline --graph --all --decorate'

# Show all aliases
git config --global alias.aliases '!git config --get-regexp ^alias\. | sed -e s/^alias\.// -e s/\ /\ =\ /'

echo ""
echo "✓ Git aliases installed!"
echo ""
echo "Available aliases:"
echo "  git safe-check         - Run safety check"
echo "  git s-all              - Show status and recent commits"
echo "  git combine <branch>   - Create new branch with merge"
echo "  git merge-in <branch>  - Merge into current"
echo "  git preview <branch>   - Preview changes"
echo "  git save [msg]         - Stash with message"
echo "  git stashes            - List stashed work"
echo "  git undo-commit        - Undo last commit (keep changes)"
echo ""
echo "Shortcuts:"
echo "  git br                 - List branches"
echo "  git co <branch>        - Checkout branch"
echo "  git st                 - Status"
echo "  git cm 'msg'           - Commit with message"
echo "  git visual             - Visual branch graph"
echo "  git aliases            - Show all aliases"
echo ""
echo "💡 To see all aliases: git aliases"
