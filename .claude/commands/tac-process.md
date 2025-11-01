# TAC Process Issue

**Purpose:** Process a TAC issue from `.tac/current-issue.json` and complete it autonomously.

**When to use:** After running `./scripts/tac-local-trigger.sh`

---

## Your Task

You are a TAC (Template-Driven Agentic Coding) agent. Your job is to:
1. Read the issue from `.tac/current-issue.json`
2. Plan the work using the appropriate ADW template
3. Execute the plan
4. Create a PR
5. Update the issue label to `tac:completed`

---

## Step-by-Step Process

### Step 1: Read the Issue

Read the issue data:
```
.tac/current-issue.json
```

Parse out:
- `number`: The issue number
- `title`: The issue title
- `body`: Contains work type, description, criteria, context

### Step 2: Determine Work Type

From the issue body, extract the work type (should be first section):
- **feature**: Building something new
- **bug**: Fixing something broken
- **chore**: Maintenance, refactoring, dependencies

### Step 3: Create Feature Branch

Create a new branch for this work:
```bash
git checkout -b tac/issue-{number}/{slug}
```

Where `{slug}` is a kebab-case version of the task.

Example: `tac/issue-4/add-goodbye-world`

### Step 4: Plan with ADW

Use the appropriate ADW template from `.claude/adw/`:
- `example-feature.md` for features
- `example-bug.md` for bugs
- (Create chore template if needed)

Create a spec file:
```
.claude/specs/tac-issue-{number}-spec.md
```

### Step 5: Implement

Execute the plan from your spec:
- Create/modify files as needed
- Follow the acceptance criteria from the issue
- Keep it simple and focused

### Step 6: Test (if applicable)

If the project has tests, run them:
```bash
# Python
pytest

# JavaScript
npm test

# etc.
```

Fix any failures.

### Step 7: Commit

Create a descriptive commit:
```bash
git add .
git commit -m "feat: {brief description}

Implements #{issue_number}

{what was done}

🤖 Generated with TAC workflow"
```

### Step 8: Push and Create PR

```bash
git push -u origin tac/issue-{number}/{slug}
```

Then create PR:
```bash
gh pr create \
  --title "{issue title}" \
  --body "Closes #{issue_number}

## What Changed
{what you implemented}

## Testing
{how it was tested}

🤖 Generated with TAC workflow" \
  --label "tac:completed"
```

### Step 9: Update Issue

Update the issue label:
```bash
gh issue edit {issue_number} \
  --remove-label "tac:in-progress" \
  --add-label "tac:completed" \
  --repo willfung28/agentic-coding-library
```

Add a comment linking to the PR:
```bash
gh issue comment {issue_number} \
  --body "✅ Completed! See PR: {pr_url}" \
  --repo willfung28/agentic-coding-library
```

---

## Important Notes

- **Stay focused**: Only do what the issue asks for
- **Keep it simple**: Prefer simple solutions
- **Follow conventions**: Match the existing codebase style
- **Document as you go**: Add comments for complex logic
- **Fail gracefully**: If something is unclear, ask the user

---

## Example Workflow

```
User: Process the TAC issue from .tac/current-issue.json

You:
1. Read .tac/current-issue.json
2. Parse: Issue #4, feature, "Add goodbye world"
3. Create branch: tac/issue-4/add-goodbye-world
4. Plan using example-feature.md
5. Create examples/goodbye.py
6. Test it works
7. Commit with good message
8. Push and create PR
9. Update issue to tac:completed
10. Report success to user
```

---

## Start Now

Read `.tac/current-issue.json` and begin the process!
