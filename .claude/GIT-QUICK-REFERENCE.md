# Git Quick Reference Card

## 🚨 BEFORE ANYTHING - Safety First!

```bash
git-safe-check    # or: git safe-check
```

---

## 🎯 Most Common Scenarios

### AI Created Two Branches - I Want Both Fixes

```bash
# Option A: Create new combined branch (SAFEST)
git-combine <other-branch> combined-fixes

# Option B: Merge into current branch
git-merge-in <other-branch>
```

### See What's in Another Branch Before Merging

```bash
git-preview <branch-name>
```

### Save My Work Before Switching Branches

```bash
git-save "What I was working on"
```

### Get My Saved Work Back

```bash
git stash pop
```

---

## 🆘 Emergency Commands

```bash
git-undo                  # Interactive menu
git merge --abort         # Cancel merge
git reset --hard HEAD     # Discard all changes (DANGER!)
git reflog                # Find lost commits
```

---

## 📋 Status Commands

```bash
git-status-all           # Everything at once
git status               # Uncommitted changes
git branch -a            # All branches
git log --oneline -5     # Recent commits
git-list-stashes         # Saved work
```

---

## 🔧 Your Specific Workflow

### When I Tell You About a New Branch:

```bash
# 1. Check your status FIRST
git-safe-check

# 2. Preview what I added
git-preview origin/<my-branch>

# 3. Decide: combine or keep separate

# 4a. If combining:
git-combine origin/<my-branch> combined-fix

# 4b. If merging into yours:
git-merge-in origin/<my-branch>

# 5. Resolve conflicts (if any) in VS Code

# 6. Test
pytest tests/ -v

# 7. Push
git push origin <your-branch>
```

---

## 💡 Pro Tips

1. **Always `git-safe-check` before switching branches**
2. **Use `git-preview` before merging**
3. **Create new combined branch instead of merging directly**
4. **Stash (`git-save`) instead of committing WIP**
5. **Test after every merge: `pytest tests/ -v`**

---

## 📱 Cheat Sheet

| What I Want | Command |
|-------------|---------|
| Check if safe to switch | `git-safe-check` |
| Save my work | `git-save "message"` |
| See what's in branch X | `git-preview X` |
| Merge X into current | `git-merge-in X` |
| Create new combined branch | `git-combine X combined` |
| List all my saved work | `git-list-stashes` |
| Get saved work back | `git stash pop` |
| Undo last commit | `git reset --soft HEAD~1` |
| Cancel merge | `git merge --abort` |
| See everything | `git-status-all` |

---

## 🎨 Colors in Output

- 🟢 **Green**: Safe/Success
- 🟡 **Yellow**: Warning/Info
- 🔴 **Red**: Error/Danger
- 🔵 **Blue**: Headers

---

## 📚 Full Documentation

- **Complete Guide**: `.claude/GIT-WORKFLOW.md`
- **Setup Instructions**: `.claude/SETUP-GIT-HELPERS.md`
- **All Commands**: `git-helpers` (shows list)

---

## ⚡ Quick Setup

```bash
# Install git aliases globally
bash .claude/git-aliases.sh

# Load helpers in current session
source .claude/git-helpers.sh

# Auto-load in every new terminal
echo 'source ~/.git-helpers.sh' >> ~/.zshrc
cp .claude/git-helpers.sh ~/.git-helpers.sh
source ~/.zshrc
```

---

**Print this and keep it visible! 📌**
