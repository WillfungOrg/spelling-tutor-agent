# Git Workflow Guide

## Handling Multiple Feature Branches

### Scenario: AI Creates Multiple Branches for Related Fixes

When working with AI assistants that create multiple feature branches, follow this workflow to combine fixes without losing work.

### Problem This Solves
- AI creates Branch A with Fix 1
- AI creates Branch B with Fix 2 (based on older code)
- You want both fixes combined without manual re-work

---

## Quick Commands

### Before Switching Branches

**Always check your current status:**
```bash
git status
git branch
```

**If you have uncommitted changes, stash them:**
```bash
git stash save "WIP: description of your work"
```

### Combining Two Feature Branches

#### Option 1: Merge Strategy (Recommended)

```bash
# 1. Ensure you're on the newer branch
git checkout <newer-branch>

# 2. Pull latest changes
git pull origin <newer-branch>

# 3. Merge the older branch
git merge <older-branch>

# 4. Resolve any conflicts (VS Code will show them)

# 5. After resolving conflicts, complete the merge
git add .
git commit -m "Merge <older-branch> into <newer-branch>"

# 6. Run tests
pytest tests/ -v

# 7. Push the combined result
git push origin <newer-branch>
```

#### Option 2: Create New Combined Branch (Safest)

```bash
# 1. Start from the newer branch
git checkout <newer-branch>

# 2. Create new branch for combined work
git checkout -b combined-<feature-name>

# 3. Merge the older branch
git merge <older-branch>

# 4. Resolve conflicts, test, and push
git add .
git commit -m "Combine <older-branch> and <newer-branch> fixes"
pytest tests/ -v
git push origin combined-<feature-name>
```

#### Option 3: Cherry-Pick Specific Commits

```bash
# 1. List commits from the other branch
git log <other-branch> --oneline

# 2. Switch to your target branch
git checkout <target-branch>

# 3. Cherry-pick specific commits
git cherry-pick <commit-hash>

# 4. Resolve any conflicts, test, and push
```

---

## Best Practices

### 1. Communication with AI

**Before AI creates a new branch:**
```markdown
User: "Do I have any local changes? Please check git status first."
AI: [checks git status]
User: "I have work on branch-A. Can you merge your changes into branch-A instead of creating branch-B?"
```

**When AI has already created a branch:**
```markdown
User: "I need to combine both fixes from branch-A and branch-B. Please guide me through merging them."
```

### 2. Use `git fetch` Instead of `git pull`

```bash
# Safer - see what's coming without changing your files
git fetch origin

# Review what changed
git log HEAD..origin/<branch> --oneline

# Decide: merge, rebase, or create new branch
```

### 3. Regularly Check Branch Status

```bash
# See all branches
git branch -a

# See branch relationships
git log --oneline --graph --all --decorate

# See uncommitted changes
git status
```

### 4. Use Stash for WIP

```bash
# Save your work before switching
git stash save "WIP: working on session.say() fix"

# List stashes
git stash list

# Apply stash later
git stash pop

# View stash contents
git stash show -p stash@{0}
```

---

## Common Workflows

### Workflow 1: AI Creates Second Branch While You Have Local Changes

**Situation:** You're on `branch-A`, AI pushes `branch-B`

```bash
# Option A: Merge branch-B into your branch-A
git fetch origin
git merge origin/branch-B
# Resolve conflicts, test, push

# Option B: Create new combined branch
git checkout -b combined-fix
git merge origin/branch-B
# Resolve conflicts, test, push
```

### Workflow 2: AI Creates Branch, You Want to Add More

**Situation:** AI pushed `branch-A`, you want to add more commits

```bash
# 1. Switch to the AI's branch
git checkout branch-A
git pull origin branch-A

# 2. Make your changes
# ... edit files ...

# 3. Commit and push
git add .
git commit -m "Add additional improvements to <feature>"
git push origin branch-A
```

### Workflow 3: Keep Multiple Branches Separate

**Situation:** You want to test each fix independently

```bash
# No merge needed - just work with branches separately
git checkout branch-A  # Test fix A
pytest tests/ -v

git checkout branch-B  # Test fix B
pytest tests/ -v

# Later, merge both into main separately via PRs
```

---

## Resolving Merge Conflicts

### Step-by-Step

1. **When merge conflict occurs:**
```bash
git merge <other-branch>
# Auto-merging file.py
# CONFLICT (content): Merge conflict in file.py
```

2. **Open conflicted files (VS Code will highlight them):**
```
<<<<<<< HEAD
Your current changes
=======
Incoming changes from other branch
>>>>>>> other-branch
```

3. **Resolve by choosing:**
   - Keep your version (delete incoming)
   - Keep incoming version (delete your version)
   - Combine both changes
   - Write new solution

4. **Complete the merge:**
```bash
git add <resolved-files>
git commit -m "Merge <other-branch> - resolved conflicts"
pytest tests/ -v  # Verify tests pass
git push origin <current-branch>
```

---

## Prevention Strategies

### Strategy 1: Single Branch Policy

When working with AI on related fixes:
```markdown
User: "Please work on the current branch I'm on, don't create new branches unless I explicitly ask."
```

### Strategy 2: Always Pull Before New Work

```bash
# Before starting any new work
git fetch origin
git pull origin main
git checkout -b new-feature-branch
```

### Strategy 3: Use Worktrees for Parallel Work

```bash
# Create worktree for parallel work (like ADW system)
git worktree add trees/feature-A feature-A
cd trees/feature-A
# Work here without affecting main repo
```

---

## Emergency Recovery

### If You Accidentally Lost Changes

```bash
# View reflog (history of all actions)
git reflog

# Find your lost commit
git reflog | grep "commit message"

# Restore it
git cherry-pick <commit-hash>

# Or reset to that point
git reset --hard <commit-hash>
```

### If Merge Went Wrong

```bash
# Abort the merge
git merge --abort

# Start over
git reset --hard HEAD
```

---

## Quick Reference

### Check Status
```bash
git status              # Current changes
git branch              # Current branch
git branch -a           # All branches
git log --oneline -5    # Recent commits
```

### Combining Branches
```bash
git merge <branch>      # Merge into current
git rebase <branch>     # Rebase current onto branch
git cherry-pick <hash>  # Copy single commit
```

### Safety
```bash
git stash               # Save current work
git fetch               # Get updates without changing files
git merge --abort       # Cancel merge
git reflog              # View all history
```

---

## When to Use Each Approach

| Scenario | Best Approach | Why |
|----------|--------------|-----|
| AI creates 2 related branches | **Option 2: New combined branch** | Keeps both originals safe |
| AI branch has fixes you want | **Option 1: Merge** | Clean, preserves history |
| Want specific commits only | **Option 3: Cherry-pick** | Fine-grained control |
| Testing different approaches | **Keep separate** | Independent testing |
| Quick fix on AI's branch | **Checkout and commit** | Direct and simple |

---

## TAC Integration

When using TAC workflows:

1. **Before /implement:**
```bash
git status  # Check current state
git stash   # Save any WIP
```

2. **After AI creates branch:**
```bash
git checkout <ai-branch>
git pull origin <ai-branch>
# Review changes before proceeding
```

3. **If combining multiple AI branches:**
- Use "Create New Combined Branch" approach
- Run full validation: `/review` and `/test`
- Update spec if needed

---

**Remember:** 2 minutes of git checking saves hours of re-implementation!
