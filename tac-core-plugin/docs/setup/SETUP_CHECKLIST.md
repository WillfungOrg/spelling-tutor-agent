# Agentic Coding Setup Checklist

**Purpose:** Quick guide to set up agentic coding infrastructure for any new project.

**Time Required:** 15-30 minutes (one-time per project)

---

## 📋 Quick Setup (New Project)

### ✅ Step 1: Copy Library to Project (2 min)

```bash
# Navigate to your new project
cd /path/to/your-new-project

# Copy the entire .claude/ directory
cp -r ~/agentic-coding-library/.claude .

# Flatten structure (move commands to root)
mv .claude/commands/core/* .claude/commands/
mv .claude/commands/workflow/* .claude/commands/
mv .claude/commands/advanced/* .claude/commands/
rmdir .claude/commands/{core,workflow,advanced}

# Verify
ls .claude/commands/
Expected result: .claude/commands/ contains 12-18 .md files

✅ Step 2: Write Project Context (10-15 min)
This is the ONLY file you write from scratch each time.

# Create project-context.md
touch .claude/project-context.md
Template to fill in:

# [Project Name] - Project Context

## Project Overview
**Name:** [Your project name]
**Purpose:** [What this project does in 1-2 sentences]
**Stage:** [MVP / Development / Production]

## Tech Stack
- **Language:** [Python / JavaScript / Go / Rust / etc.]
- **Framework:** [Django / React / FastAPI / etc.]
- **Database:** [PostgreSQL / MongoDB / etc.]
- **Key Libraries:** [List 3-5 main dependencies]

## Codebase Structure
your-project/
├── src/ # [What goes here]
├── tests/ # [What goes here]
├── config/ # [What goes here]
└── docs/ # [What goes here]


## Environment Variables
- `VAR_NAME` - [Purpose]
- `API_KEY` - [Purpose]

## Coding Conventions
- **Naming:** [camelCase / snake_case / PascalCase for what]
- **File Organization:** [One component per file, etc.]
- **Testing:** [Test framework and coverage target]
- **Linting:** [ESLint / Pylint / etc.]

## Development Workflow
1. Setup: [Command to install dependencies]
2. Run: [Command to start dev server]
3. Test: [Command to run tests]
4. Build: [Command to build for production]

## What AI Should Know
- **Always:** [Things AI should always do]
- **Never:** [Things AI should never do]
- **Ask First:** [Things that need human approval]

## Success Criteria
- [ ] [Key goal 1]
- [ ] [Key goal 2]
- [ ] [Key goal 3]
💡 Tip: Look at existing codebases for reference, or use TAC examples.

✅ Step 3: Customize Commands (5-10 min)
Most commands work as-is, but these need minor edits:

3a. Update generate_branch_name.md (if using)
Find this section (around line 20):

## Branch Naming Convention
- feature/* - New features
- bugfix/* - Bug fixes
- chore/* - Maintenance tasks
Customize if your team uses different prefixes (e.g., feat/, fix/, etc.)

3b. Update commit.md (if using)
Find this section (around line 15):

## Commit Message Format
<type>(<scope>): <subject>

Types: feat, fix, chore, docs, style, refactor, test
Customize if your team uses different commit style.

3c. Update test.md (if using advanced tier)
Find the test command (around line 30):

npm test
Replace with your test command:

Python: pytest or python -m pytest
Go: go test ./...
Rust: cargo test
etc.
✅ Step 4: Initialize Git & Commit (2 min)
# Initialize git (if not already)
git init

# Add .claude/ to version control
git add .claude/
git commit -m "chore: add agentic coding infrastructure"
Why commit .claude/?

✅ Share with team
✅ Version control your AI workflows
✅ Track improvements over time
✅ Step 5: Test It Works (3 min)
Ask Claude to use a command:

Hey Claude, I need to understand this codebase.
Please run /prime to analyze the project.
Expected: Claude reads project-context.md and analyzes your project.

🎯 Command Reference
Core Commands (Always Available)
Command	Purpose	When to Use
/prime	Understand codebase	Start of project / new feature
/feature	Plan new feature	Before building something new
/bug	Plan bug fix	When fixing bugs
/chore	Plan maintenance	Refactoring, dependencies, etc.
/implement	Execute plan	After planning with feature/bug/chore
/tools	List AI capabilities	When unsure what AI can do
Workflow Commands (If Tier 2 Installed)
Command	Purpose	When to Use
/classify_issue	Classify issue type	When starting new work
/generate_branch_name	Create branch name	Before creating branches
/commit	Generate commit message	Before committing
/install	Setup project	Initial setup / onboarding
/resolve_failed_test	Fix failing tests	When tests fail
/conditional_docs	Smart documentation	When unsure if docs needed
Advanced Commands (If Tier 3 Installed)
Command	Purpose	When to Use
/test	Run & validate tests	During development
/test_e2e	E2E testing	Before deployment
/pull_request	Generate PR description	Creating PRs
/review	Code review	Before merging
/document	Generate docs	Documenting APIs/features
/patch	Apply security patches	Security updates
🔄 Typical Workflow
Starting a New Feature
1. You: "I want to add user authentication"
2. You: "/classify_issue" → AI determines it's a feature
3. You: "/generate_branch_name" → AI suggests: feature/user-authentication
4. You: Create branch
5. You: "/feature" → AI creates detailed feature plan
6. You: "/implement" → AI executes the plan
7. You: "/test" → AI runs tests & validates
8. You: "/commit" → AI generates commit message
9. You: "/pull_request" → AI creates PR description
Fixing a Bug
1. You: "Users can't log in"
2. You: "/classify_issue" → AI determines it's a bug
3. You: "/generate_branch_name" → AI suggests: bugfix/login-failure
4. You: Create branch
5. You: "/bug" → AI creates bug fix plan (investigation + fix)
6. You: "/implement" → AI executes the fix
7. You: "/test" → AI validates tests pass
8. If tests fail: "/resolve_failed_test" → AI auto-fixes
9. You: "/commit" → AI generates commit message
10. You: "/pull_request" → AI creates PR description
📁 What to Commit to Git
✅ Always Commit
.claude/project-context.md - Project knowledge
.claude/commands/*.md - All command templates
Customized commands (after you edit them)
❌ Never Commit
API keys or secrets in any .claude/ files
Personal notes not relevant to team
Temporary test files
⚠️ Consider .gitignore for
.claude/specs/*.md - If feature specs contain sensitive info
.claude/meta-prompts/*.md - If prompts are personal workflow
Recommendation: Commit everything in .claude/ by default for team collaboration.

🔧 Troubleshooting
Issue: "Claude doesn't recognize /command"
Solution: Check file location

ls .claude/commands/
# Should show: prime.md, feature.md, bug.md, etc.
Issue: "Command doesn't match my tech stack"
Solution: Edit the command file directly

# Example: Update test command for Python
nano .claude/commands/test.md
# Find: npm test
# Replace with: pytest
Issue: "Too many commands, confusing"
Solution: Start with core only (6 commands)

# Remove workflow/advanced commands
rm .claude/commands/classify_issue.md
rm .claude/commands/generate_branch_name.md
# etc.

# Keep only:
# - prime.md
# - feature.md
# - bug.md
# - chore.md
# - implement.md
# - tools.md
Add back as you learn them.

📚 Resources
TAC Course: https://github.com/willfung28/tac-course
Your Library: ~/agentic-coding-library
Template-First Workflow: See your notes in Agentic-Coding/Quick-Refs/
🎯 Success Checklist
After setup, verify:

.claude/project-context.md exists and is filled out
At least 6 core commands in .claude/commands/
Claude recognizes /prime command
Git committed .claude/ directory
Team knows where to find command reference
Time spent: ~30 minutes
Time saved per project: Hours to days of AI back-and-forth

💡 Pro Tips
Update project-context.md as project evolves

Add new conventions
Document architectural decisions
Update file structure
Improve commands based on experience

If AI misses something, update the command
Version control shows evolution
Commands get better over time
Share learnings with team

Your .claude/ directory is team knowledge
Better commands = better AI results for everyone
Start simple, expand later

Begin with 6 core commands
Add workflow commands when comfortable
Add advanced commands for production projects
Commands work across languages

Same commands for Python, JS, Go, Rust
Only project-context.md changes
Universal development workflow
Ready to start? Follow Step 1! ✅

---

## 🤖 TAC Workflow Setup (Optional - For Zero-Touch Development)

### ✅ Step 6: Enable TAC Workflow (5-10 min)

TAC (Template-Driven Agentic Coding) enables you to create GitHub issues from mobile and have an agent complete them automatically.

**6a. Create GitHub Labels**

```bash
# Update repo name first!
REPO="your-username/your-repo-name"

gh label create "tac:pending" --color "fbca04" --description "TAC: Waiting to be processed" --repo $REPO
gh label create "tac:in-progress" --color "0052cc" --description "TAC: Currently being worked on" --repo $REPO
gh label create "tac:completed" --color "0e8a16" --description "TAC: Task completed" --repo $REPO
```

**6b. Update Trigger Script**

```bash
# Edit scripts/tac-local-trigger.sh
# Line 8: Update REPO variable
REPO="your-username/your-repo-name"
```

**6c. Test TAC Workflow**

```bash
# Should show "No pending TAC tasks found"
./scripts/tac-local-trigger.sh
```

### 📱 Using TAC Workflow

1. **From Mobile:** Create issue using TAC Task template
2. **From Dev Machine:** Run `./scripts/tac-local-trigger.sh`
3. **In Claude Desktop:** Process the issue
4. **Result:** PR created automatically

See `scripts/README.md` for full details.

