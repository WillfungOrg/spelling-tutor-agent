# Git Helpers Setup Guide

## Quick Setup (2 minutes)

### Option 1: Auto-load git helpers in every terminal session

**For Zsh (macOS default):**
```bash
# Add to your ~/.zshrc
echo 'source ~/.git-helpers.sh' >> ~/.zshrc

# Copy the helpers to your home directory
cp .claude/git-helpers.sh ~/.git-helpers.sh

# Reload your shell
source ~/.zshrc
```

**For Bash:**
```bash
# Add to your ~/.bashrc or ~/.bash_profile
echo 'source ~/.git-helpers.sh' >> ~/.bash_profile

# Copy the helpers to your home directory
cp .claude/git-helpers.sh ~/.git-helpers.sh

# Reload your shell
source ~/.bash_profile
```

### Option 2: Install git aliases (works in any terminal)

```bash
# Run the installation script
bash .claude/git-aliases.sh
```

This installs global git aliases that work in any repository.

### Option 3: Load manually when needed

```bash
# In this repository only
source .claude/git-helpers.sh
```

---

## What You Get

### Shell Functions (from git-helpers.sh)

When sourced, you get these commands:

**Safety & Status:**
- `git-safe-check` - Check before switching branches
- `git-status-all` - Complete git status overview
- `git-save [message]` - Stash with descriptive message
- `git-list-stashes` - Show all stashed work

**Combining Branches:**
- `git-combine <branch> [new-name]` - Create new branch with merge
- `git-merge-in <branch>` - Merge into current branch
- `git-preview <branch>` - See changes before merging

**Emergency:**
- `git-undo` - Interactive undo menu

**Help:**
- `git-helpers` - Show all available commands

### Git Aliases (from git-aliases.sh)

After running the install script, you get:

**Safety & Status:**
- `git safe-check` - Safety check
- `git s-all` - Status + recent commits
- `git stashes` - List stashes

**Combining:**
- `git combine <branch>` - Create new branch with merge
- `git merge-in <branch>` - Merge into current
- `git preview <branch>` - Preview changes
- `git save [msg]` - Stash with message

**Shortcuts:**
- `git br` - List branches
- `git co <branch>` - Checkout
- `git st` - Status
- `git cm 'msg'` - Commit
- `git visual` - Visual graph
- `git aliases` - Show all

---

## Typical Workflow

### Before Switching Branches

```bash
# Check if it's safe to switch
git-safe-check

# If you have changes, save them
git-save "Working on session.say() fix"
```

### Combining Two AI Branches

```bash
# Preview what's in the other branch
git-preview origin/feature-B

# Create new combined branch
git-combine origin/feature-B combined-fix

# Or merge into current
git-merge-in origin/feature-B

# After resolving conflicts (if any)
pytest tests/ -v
git push origin <branch-name>
```

### Emergency Recovery

```bash
# Interactive undo menu
git-undo

# Or abort merge directly
git merge --abort
```

---

## Real Example: Your Recent Situation

```bash
# You were on: claude/session-start-011CUgo6cu6jWaLVMqhAwz6k
# I pushed: claude/improve-agent-responses-011CUh3v6zijDdDeSfrRDdLm

# Step 1: Check status
git-safe-check

# Step 2: Preview the new branch
git-preview origin/claude/improve-agent-responses-011CUh3v6zijDdDeSfrRDdLm

# Step 3: Combine both
git-combine origin/claude/improve-agent-responses-011CUh3v6zijDdDeSfrRDdLm combined-fixes

# Step 4: Resolve conflicts, test, push
# (VS Code will show conflicts)
git add .
git commit -m "Merge session.say() with dynamic instructions"
pytest tests/ -v
git push origin combined-fixes
```

---

## Customization

### Add Your Own Helpers

Edit `.claude/git-helpers.sh` and add functions:

```bash
# Your custom function
my-git-helper() {
    echo "My custom git helper"
    # your commands here
}
```

### Add Your Own Aliases

```bash
git config --global alias.my-alias 'status -s'
```

---

## Troubleshooting

### "Command not found"

If `git-safe-check` says "command not found":

```bash
# Make sure it's sourced
source .claude/git-helpers.sh

# Or use git aliases instead
bash .claude/git-aliases.sh
git safe-check
```

### "Permission denied"

```bash
chmod +x .claude/git-helpers.sh
chmod +x .claude/git-aliases.sh
```

### Shell functions not working

Make sure you **source** the file (not execute it):

```bash
# Wrong (executes in subshell)
bash .claude/git-helpers.sh

# Correct (loads into current shell)
source .claude/git-helpers.sh
```

---

## Which Should I Use?

| Feature | Shell Functions | Git Aliases |
|---------|----------------|-------------|
| **Colorized output** | ✅ Yes | ❌ Limited |
| **Interactive prompts** | ✅ Yes | ❌ No |
| **Works anywhere** | ❌ Must source first | ✅ Global |
| **More features** | ✅ Full featured | ⚠️  Basic |
| **Installation** | Copy to ~ + source | Run install script |

**Recommendation:**
- **Install both!**
- Use **shell functions** (`git-*`) for interactive work in this repo
- Use **git aliases** (`git *`) for quick commands in any repo

---

## Quick Test

After setup, try:

```bash
# Test shell functions
git-safe-check

# Test git aliases
git safe-check

# If both work, you're all set! ✅
```

---

## Next Steps

1. **Setup now** (choose Option 1 or 2 above)
2. **Try it**: `git-safe-check` or `git safe-check`
3. **Read**: `.claude/GIT-WORKFLOW.md` for detailed workflows
4. **Customize**: Add your own helpers as you discover patterns

---

**Remember:** `git-safe-check` before any branch operation!
