# Webhook Label Guide

Complete guide for using GitHub labels to trigger ADW workflows.

---

## ✅ Label Support is Now Active!

The webhook server now supports triggering workflows via GitHub labels. This is **cleaner and easier** than putting commands in issue bodies.

---

## 🏷️ How It Works

### Before (Old Way):
```
Create issue with body:
"Fix login bug

adw_plan_iso"
```

### Now (Label Way):
```
Create issue with:
Title: "Fix login bug"
Body: (whatever you want)
Labels: ["adw-plan"]  ← Triggers workflow automatically!
```

---

## 📋 Complete Label List

### Planning & Design

| Label | Workflow | Description |
|-------|----------|-------------|
| `adw-plan` | `adw_plan_iso` | Create implementation plan |
| `adw-design` | `adw_plan_iso` | Alias for plan |

**Example:**
```
Title: "Implement user authentication"
Labels: ["adw-plan"]
→ Creates implementation plan and posts to issue
```

### Quick Fixes

| Label | Workflow | Description |
|-------|----------|-------------|
| `adw-patch` | `adw_patch_iso` | Quick bug fix workflow |
| `adw-hotfix` | `adw_patch_iso` | Alias for patch |

**Example:**
```
Title: "Fix typo in error message"
Labels: ["adw-patch"]
→ Quick fix workflow (faster than full plan)
```

### Implementation (Requires Existing Plan)

| Label | Workflow | Description |
|-------|----------|-------------|
| `adw-implement` | `adw_build_iso` | Build from existing plan |
| `adw-build` | `adw_build_iso` | Alias for implement |

**⚠️ Note:** These are **dependent workflows** that require an existing ADW ID from a previous `adw-plan` or `adw-patch`.

**Example:**
```
Title: "Continue implementing auth feature"
Body: "adw_build_iso abc12345"  ← Need ADW ID
Labels: ["adw-implement"]
→ Builds from plan abc12345
```

### Testing (Requires Existing Plan)

| Label | Workflow | Description |
|-------|----------|-------------|
| `adw-test` | `adw_test_iso` | Run tests with auto-fix |
| `adw-e2e` | `adw_test_e2e` | Run E2E tests |

**Example:**
```
Title: "Test authentication feature"
Body: "adw_test_iso abc12345"
Labels: ["adw-test"]
→ Runs tests and fixes failures
```

### Review & Documentation (Requires Existing Plan)

| Label | Workflow | Description |
|-------|----------|-------------|
| `adw-review` | `adw_review_iso` | Review implementation |
| `adw-document` | `adw_document_iso` | Generate documentation |

**Example:**
```
Title: "Document auth system"
Body: "adw_document_iso abc12345"
Labels: ["adw-document"]
→ Generates comprehensive docs
```

### Complete Workflows (Recommended for Most Cases)

| Label | Workflow | Description |
|-------|----------|-------------|
| `adw-sdlc` | `adw_sdlc_iso` | **RECOMMENDED:** Full SDLC pipeline |
| `adw-full` | `adw_sdlc_iso` | Alias for sdlc |
| `adw-zte` | `adw_sdlc_ZTE_iso` | ⚠️ **Zero Touch Execution** (auto-merges!) |

**Full SDLC Pipeline:**
```
Plan → Build → Test → Review → Document → PR
```

**Example:**
```
Title: "Add dark mode support"
Labels: ["adw-sdlc"]
→ Complete end-to-end automation
```

**⚠️ ZTE Warning:**
```
Title: "Minor CSS tweak"
Labels: ["adw-zte"]
→ Completes SDLC AND auto-merges to main!
   Only use if you have comprehensive tests!
```

### Combined Workflows

| Label | Workflow | Description |
|-------|----------|-------------|
| `adw-plan-build` | `adw_plan_build_iso` | Plan + Build |
| `adw-pbt` | `adw_plan_build_test_iso` | Plan + Build + Test |
| `adw-pbtr` | `adw_plan_build_test_review_iso` | Plan + Build + Test + Review |

**Example:**
```
Title: "Quick feature iteration"
Labels: ["adw-pbt"]
→ Creates plan, builds, and tests
```

### Model Selection

| Label | Model | Description |
|-------|-------|-------------|
| `adw-heavy` | Opus | Use for complex tasks (expensive, smart) |
| `adw-fast` | Sonnet | Use for simple tasks (cheap, fast) [DEFAULT] |

**Combine with workflow labels:**
```
Title: "Refactor entire authentication system"
Labels: ["adw-sdlc", "adw-heavy"]
→ Uses Opus model for all steps
```

### Meta Strategy

| Label | Workflow | Description |
|-------|----------|-------------|
| `adw-strategy` | `meta_adw_strategy` | AI recommends best workflow |

**Example:**
```
Title: "Not sure how to approach this..."
Labels: ["adw-strategy"]
→ AI interviews you and recommends optimal workflow
```

---

## 🎯 Quick Reference - What Should I Use?

### New Feature
```
Labels: ["adw-sdlc"]
```
→ Full automation from planning to PR

### Bug Fix
```
Labels: ["adw-patch"]
```
→ Quick fix workflow

### Unsure What to Use?
```
Labels: ["adw-strategy"]
```
→ AI helps you decide

### Complex Refactoring
```
Labels: ["adw-sdlc", "adw-heavy"]
```
→ Full workflow with smart model

### Just Planning (No Implementation)
```
Labels: ["adw-plan"]
```
→ Creates plan only

---

## 🚀 Setting Up Labels in Your Repos

### Option 1: Per-Repo Setup (Manual)

1. Go to: `https://github.com/YOUR-ORG/YOUR-REPO/labels`
2. Click **"New label"** for each label below
3. Use the suggested colors for easy visual identification

### Option 2: Organization-Wide Setup (Recommended)

Create labels once, apply to all repos:

1. Create in one repo first (test repo)
2. Use GitHub CLI to copy to other repos:

```bash
# Export labels from test repo
gh label list --repo YOUR-ORG/test-repo --json name,description,color > labels.json

# Import to other repos
gh label create --repo YOUR-ORG/other-repo --file labels.json
```

### Option 3: Automated Setup Script

Create `scripts/setup_labels.sh`:

```bash
#!/bin/bash
# Setup ADW labels for all repos in organization

ORG="YOUR-ORG"

# Define labels
declare -A LABELS
LABELS["adw-plan"]="0366d6|Create implementation plan"
LABELS["adw-design"]="0366d6|Create implementation plan (alias)"
LABELS["adw-patch"]="d93f0b|Quick bug fix"
LABELS["adw-hotfix"]="d93f0b|Quick bug fix (alias)"
LABELS["adw-implement"]="0e8a16|Build from existing plan"
LABELS["adw-build"]="0e8a16|Build from existing plan (alias)"
LABELS["adw-test"]="fbca04|Run tests with auto-fix"
LABELS["adw-e2e"]="fbca04|Run E2E tests"
LABELS["adw-review"]="5319e7|Review implementation"
LABELS["adw-document"]="5319e7|Generate documentation"
LABELS["adw-sdlc"]="d73a4a|Full SDLC pipeline"
LABELS["adw-full"]="d73a4a|Full SDLC pipeline (alias)"
LABELS["adw-zte"]="b60205|Zero Touch Execution (auto-merge!)"
LABELS["adw-plan-build"]="1d76db|Plan + Build"
LABELS["adw-pbt"]="1d76db|Plan + Build + Test"
LABELS["adw-pbtr"]="1d76db|Plan + Build + Test + Review"
LABELS["adw-strategy"]="c5def5|AI recommends best workflow"
LABELS["adw-heavy"]="e99695|Use Opus model (expensive)"
LABELS["adw-fast"]="c2e0c6|Use Sonnet model (fast) [default]"

# Get all repos in org
REPOS=$(gh repo list $ORG --limit 1000 --json name -q '.[].name')

# Create labels in each repo
for repo in $REPOS; do
    echo "Setting up labels in $ORG/$repo..."

    for label in "${!LABELS[@]}"; do
        IFS='|' read -r color description <<< "${LABELS[$label]}"

        gh label create "$label" \
            --repo "$ORG/$repo" \
            --color "$color" \
            --description "$description" \
            --force 2>/dev/null || true
    done

    echo "✅ Labels created for $ORG/$repo"
done

echo "✅ All labels created across organization!"
```

Run with:
```bash
chmod +x scripts/setup_labels.sh
./scripts/setup_labels.sh
```

---

## 📝 Suggested Label Colors

For visual consistency across your organization:

| Color | Hex | Use For |
|-------|-----|---------|
| 🔵 Blue | `#0366d6` | Planning labels |
| 🟢 Green | `#0e8a16` | Implementation labels |
| 🟡 Yellow | `#fbca04` | Testing labels |
| 🟣 Purple | `#5319e7` | Review/Documentation labels |
| 🔴 Red | `#d73a4a` | Complete workflow labels |
| 🟠 Orange | `#d93f0b` | Quick fix labels |
| 🔷 Teal | `#1d76db` | Combined workflow labels |
| 🧠 Light Blue | `#c5def5` | Meta/Strategy labels |
| 💎 Pink | `#e99695` | Heavy model |
| ⚡ Light Green | `#c2e0c6` | Fast model |

---

## 🎯 Common Workflows

### Scenario 1: New Feature (Recommended)

**Create issue:**
```
Title: "Add password reset functionality"
Body: "Users should be able to reset their password via email"
Labels: ["adw-sdlc"]
```

**What happens:**
1. Webhook detects `adw-sdlc` label
2. Clones repo (if not already cloned)
3. Runs full SDLC: plan → build → test → review → document
4. Creates PR with complete implementation
5. Posts updates to issue

**Time:** 5-15 minutes depending on complexity

### Scenario 2: Quick Bug Fix

**Create issue:**
```
Title: "Fix validation error on signup form"
Body: "Email validation is case-sensitive but shouldn't be"
Labels: ["adw-patch"]
```

**What happens:**
1. Webhook detects `adw-patch` label
2. Runs quick patch workflow
3. Creates PR with fix
4. Posts result to issue

**Time:** 2-5 minutes

### Scenario 3: Complex Refactoring

**Create issue:**
```
Title: "Refactor authentication system to use JWT"
Body: "Current session-based auth needs to be replaced with JWT tokens"
Labels: ["adw-sdlc", "adw-heavy"]
```

**What happens:**
1. Webhook detects both labels
2. Uses Opus model (smarter) for complex task
3. Runs full SDLC with heavy model
4. Creates PR with comprehensive refactoring

**Time:** 10-30 minutes (longer but smarter)

### Scenario 4: Not Sure What to Use

**Create issue:**
```
Title: "Improve performance of dashboard"
Body: "Dashboard is slow when loading large datasets"
Labels: ["adw-strategy"]
```

**What happens:**
1. Webhook detects `adw-strategy` label
2. AI interviews you about the task (7 questions)
3. AI analyzes complexity and requirements
4. AI recommends optimal workflow with reasoning
5. You apply recommended label to proceed

**Time:** 2-3 minutes for recommendation

---

## 🔄 Label Priority

If an issue has multiple ADW labels, the webhook will:
1. Use the **first workflow label** found
2. Use the **model label** if present

**Example:**
```
Labels: ["adw-plan", "adw-sdlc", "adw-heavy"]
→ Uses: adw-plan (first workflow) + heavy model
```

**Recommendation:** Use only **ONE workflow label** per issue to avoid confusion.

---

## ⚙️ GitHub Webhook Configuration

**Important:** The webhook must listen for label events!

When setting up the webhook, select these events:
- ☑️ **Issues** (for issue creation)
- ☑️ **Issue comments** (for comment-based triggers)

The webhook will trigger on:
- Issue opened with label
- Label added to existing issue
- Issue comment with `adw_` command (fallback)

---

## 🧪 Testing the Labels

### Test 1: Simple Plan

1. Go to one of your existing issues (e.g., `spelling-tutor-agent #2`)
2. Click **"Labels"** on the right sidebar
3. Add label: `adw-plan`
4. Watch for webhook activity in logs: `tail -f /tmp/adw_logs/webhook.log`

### Test 2: Full SDLC

1. Create new issue:
   ```
   Title: "Test full SDLC workflow"
   Body: "Testing label-based triggering"
   ```
2. Before submitting, add label: `adw-sdlc`
3. Submit issue
4. Watch for bot comment and PR creation

### Test 3: Heavy Model

1. Create new issue:
   ```
   Title: "Complex algorithm optimization"
   Body: "Optimize sorting algorithm for large datasets"
   ```
2. Add labels: `adw-plan`, `adw-heavy`
3. Submit issue
4. Check bot comment mentions "Model Set: heavy"

---

## 🐛 Troubleshooting

### Label not triggering workflow

**Check:**
1. Label name is exactly correct (case-sensitive: `adw-plan` not `adw-Plan`)
2. Webhook is configured for "labeled" events
3. Check webhook logs: `tail -f /tmp/adw_logs/webhook.log`

### Wrong workflow triggered

**Check:**
1. Issue has only ONE workflow label
2. Remove extra workflow labels

### Model selection not working

**Check:**
1. Model label is correct: `adw-heavy` or `adw-fast`
2. Check bot comment for "Model Set:" confirmation

---

## 📚 Migration from Body-Based to Label-Based

### Old Way (Still Works)
```
Create issue with body: "adw_plan_iso"
```

### New Way (Recommended)
```
Create issue with label: "adw-plan"
```

**Both work!** The webhook checks:
1. Labels first (cleaner)
2. Issue body second (fallback)
3. Comments third (for manual triggering)

---

## ✅ Benefits of Label-Based Triggering

1. **Cleaner Issues** - No need for special syntax in body
2. **Visual Identification** - Color-coded labels make workflow type obvious
3. **Easy Discovery** - GitHub's label filter makes finding ADW issues easy
4. **Reusable** - Apply label to existing issue to re-trigger
5. **Organization-Wide** - Set up labels once, use everywhere

---

## 🎉 You're Ready to Use Labels!

**Next steps:**
1. Update your GitHub webhook URL (new one after restart):
   ```
   https://jews-upc-icons-petersburg.trycloudflare.com/gh-webhook
   ```
2. Create labels in your repos (use script above)
3. Test by adding `adw-plan` label to one of your existing issues
4. Watch the magic happen!

**New Webhook URL:**
```
https://jews-upc-icons-petersburg.trycloudflare.com/gh-webhook
```

**Secret (unchanged):**
```
b81beb2589279c8f11e139833a78136c476d659a9f63219af26d472021851962
```

---

**Last Updated:** 2025-11-06
**Webhook Status:** ✅ ACTIVE with label support
