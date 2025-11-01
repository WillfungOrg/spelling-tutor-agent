# TAC Framework - Quick Start Guide

**5-Minute Guide to Using TAC in Your Projects**

---

## What is TAC?

**TAC = The Agentic Coder Framework**

A set of 5 principles that make AI coding more effective:
1. **Spec-First** - Plan before coding
2. **Knowledge Gap Pre-Fill** - Give AI what it needs upfront
3. **Agent Perspective** - Structure for AI, not humans
4. **Closed-Loop Validation** - Automated testing
5. **Template Engineering** - Reusable patterns

---

## Quick Workflow

### Starting New Work

```bash
# Step 1: Check what AI needs to know
/knowledge_gap_check

# Step 2: Create specification
/spec

# Step 3: Begin implementation
/feature   # for new features
/bug       # for bug fixes
/chore     # for maintenance

# Step 4: Execute the plan
/implement
```

### During Work

```bash
# Run tests frequently
/test

# Review against spec
/review
```

### Before Completion

```bash
# Final validation
/review

# Create pull request
/pull_request
```

---

## The 5 Principles (30-Second Version)

### 1. Spec-First Development
**Rule:** Write spec before code
**Why:** Prevents confusion and rework
**Command:** `/spec`

### 2. Knowledge Gap Pre-Fill
**Rule:** Tell AI what it needs to know upfront
**Why:** Prevents outdated solutions
**Command:** `/knowledge_gap_check`

### 3. Agent Perspective
**Rule:** Be explicit, not implicit
**Why:** AI can't infer like humans
**File:** `.claude/project-context.md`

### 4. Closed-Loop Validation
**Rule:** Automate validation
**Why:** Catch errors before review
**File:** `.claude/validation-checklists/`

### 5. Template Engineering
**Rule:** Reuse successful patterns
**Why:** Consistency and speed
**Location:** All commands and templates

---

## Essential Files

### Must Have
- `.claude/project-context.md` - Your project details
- `.claude/TAC-PRINCIPLES.md` - The framework (reference)

### Commands You'll Use
- `/knowledge_gap_check` - Before starting
- `/spec` - Creating specifications
- `/feature`, `/bug`, `/chore` - Implementation
- `/review` - Validation

### Templates
- `templates/spec-template.md` - For specs
- `templates/project-context template.md` - For setup
- `.claude/validation-checklists/` - For quality

---

## Common Scenarios

### Scenario 1: Adding a New Feature

```markdown
User: "Add OAuth authentication"

Step 1: /knowledge_gap_check
→ AI identifies: Need OAuth provider choice, library preference

Step 2: Clarify
User: "Use Google OAuth, Auth0 library"

Step 3: /spec
→ AI creates detailed specification

Step 4: /feature
→ AI creates implementation plan

Step 5: /implement
→ AI builds the feature

Step 6: /test
→ AI validates it works

Step 7: /review
→ AI checks spec compliance

Step 8: /pull_request
→ Ready to merge!
```

### Scenario 2: Fixing a Bug

```markdown
User: "Login is slow"

Step 1: /knowledge_gap_check
→ AI asks: How slow? Target speed?

Step 2: Clarify
User: "Currently 2s, want <500ms"

Step 3: /spec
→ AI creates bug fix spec with performance target

Step 4: /bug
→ AI creates fix plan

Step 5: /implement
→ AI fixes and optimizes

Step 6: /test
→ AI validates performance

Step 7: /review
→ AI checks regression tests

Done! Bug fixed with validation.
```

### Scenario 3: Updating Dependencies

```markdown
User: "Update React to latest"

Step 1: /knowledge_gap_check
→ AI identifies breaking changes

Step 2: /spec
→ AI creates migration spec

Step 3: /chore
→ AI creates update plan

Step 4: /implement
→ AI updates and fixes breaks

Step 5: /test
→ AI ensures nothing broke

Step 6: /review
→ AI validates checklist

Safe update complete!
```

---

## Quick Reference Card

### Before ANY Work
```
✓ Read .claude/project-context.md
✓ Run /knowledge_gap_check if uncertain
✓ Create spec with /spec
```

### During Work
```
✓ Follow the spec phases
✓ Run validation commands after each phase
✓ Update spec if requirements change
```

### Before Completion
```
✓ All tests passing
✓ Validation checklist complete
✓ Definition of done met
✓ Ready for /pull_request
```

---

## Success Metrics

You're doing TAC right when:
- ✅ Specs are created before code
- ✅ Knowledge gaps identified upfront
- ✅ Tests written and passing
- ✅ Validation automated
- ✅ Less rework and debugging

You're NOT doing TAC when:
- ❌ Code first, spec later (or never)
- ❌ Assuming AI has current knowledge
- ❌ Manual validation only
- ❌ Unclear success criteria
- ❌ Lots of back-and-forth clarifications

---

## Tips for Success

### Tip 1: Update project-context.md
Keep it current with:
- Latest framework versions
- New conventions
- Common knowledge gaps
- Updated commands

### Tip 2: Customize Checklists
Modify `.claude/validation-checklists/` for:
- Your tech stack
- Your quality standards
- Your team workflow

### Tip 3: Build Spec Library
Save good specs in `.claude/specs/` as examples for future work.

### Tip 4: Start Small
Don't use all features at once:
1. Week 1: Just use /knowledge_gap_check
2. Week 2: Add /spec
3. Week 3: Add validation checklists
4. Week 4: Full TAC workflow

### Tip 5: Measure Improvements
Track:
- Time from issue to PR
- Number of review iterations
- Test coverage
- Bug escape rate

---

## Common Mistakes

### Mistake 1: Skipping Spec
**Problem:** Jump straight to coding
**Fix:** Always `/spec` first, even for "quick" fixes

### Mistake 2: Vague Specs
**Problem:** "Make it better" objectives
**Fix:** Specific, measurable success criteria

### Mistake 3: Ignoring Knowledge Gaps
**Problem:** AI uses outdated patterns
**Fix:** `/knowledge_gap_check` before work

### Mistake 4: Manual Validation
**Problem:** "Looks good" without tests
**Fix:** Run validation checklist

### Mistake 5: Template Fatigue
**Problem:** Templates feel like overhead
**Fix:** Remember: 10 min spec saves hours of rework

---

## Getting Help

### Questions About TAC
- Read: `.claude/TAC-PRINCIPLES.md`
- Examples: Your Obsidian notes (Build-01)

### Questions About Commands
- List: `ls .claude/commands/`
- Read: `.claude/commands/[name].md`

### Questions About Setup
- Guide: `SETUP_CHECKLIST.md`
- Template: `TEMPLATE_SETUP.md`

---

## Next Steps

1. **Read TAC Principles** (10 min)
   ```bash
   cat .claude/TAC-PRINCIPLES.md
   ```

2. **Set Up project-context.md** (15 min)
   ```bash
   cp templates/project-context\ template.md .claude/project-context.md
   # Fill in your project details
   ```

3. **Try One Workflow** (30 min)
   - Pick a small feature
   - Use /knowledge_gap_check → /spec → /feature → /implement
   - See the difference

4. **Refine and Repeat**
   - What worked?
   - What needs adjustment?
   - Update templates/checklists

---

## Remember

**TAC is not about perfection, it's about:**
- ✅ Better results with less effort
- ✅ Fewer surprises
- ✅ Automated quality
- ✅ Reusable patterns
- ✅ Happier coding

**The secret:** 10 minutes of planning saves hours of debugging.

---

**Ready?** Try `/knowledge_gap_check` on your next task!

**Full Guide:** `.claude/TAC-PRINCIPLES.md`
**Implementation:** `.claude/TAC-IMPROVEMENTS-SUMMARY.md`
