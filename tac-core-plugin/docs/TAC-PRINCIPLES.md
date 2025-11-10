# TAC Framework Principles

**TAC = The Agentic Coder Framework**

This document codifies the core principles that make agentic coding effective. These principles are derived from validated TAC lessons and real-world implementation experience.

---

## Core Principle 1: Spec-First Development

**Principle:** Always write specifications before writing code.

### Why It Matters
- Clarifies thinking before implementation
- Enables autonomous AI execution
- Serves as the single source of truth
- Prevents scope creep and confusion
- Makes validation objective

### How to Apply
1. **Before any feature/bug/chore:** Create a spec document
2. **Spec contains:**
   - Clear objective
   - Success criteria
   - Requirements (functional & non-functional)
   - Technical approach
   - Out of scope items
3. **All work validates against the spec**
4. **Spec is the contract** between human and AI

### When to Skip
- Trivial changes (typos, formatting)
- Exploratory prototypes (document findings after)
- Emergency hotfixes (document spec retroactively)

### Command Support
- `/spec` - Generate new specification
- `/feature`, `/bug`, `/chore` - Reference existing specs

---

## Core Principle 2: Knowledge Gap Pre-Fill

**Principle:** Identify and fill AI knowledge gaps BEFORE starting work.

### Why It Matters
- AI training data has cutoff dates
- Prevents outdated-knowledge work
- Saves hours of wrong-direction implementation
- Enables accurate technical decisions

### How to Apply
1. **Ask AI upfront:** "What knowledge gaps exist for this task?"
2. **Common gaps:**
   - Latest framework versions
   - New API patterns
   - Project-specific conventions
   - External dependencies
3. **Fill gaps before implementation:**
   - Use MCP servers (Archon for official docs)
   - Provide repository links
   - Share relevant documentation
   - Reference CLAUDE.md

### Example Flow
```
User: "Implement OAuth2 authentication"
AI: "Knowledge gaps: Latest OAuth2 library for [your stack], your auth flow preferences"
User: [Connects to library docs via MCP]
AI: [Now implements with current patterns]
```

### Command Support
- `/knowledge_gap_check` - Explicit gap identification
- `/prime` - Includes knowledge gap analysis

---

## Core Principle 3: Agent Perspective

**Principle:** Structure everything for AI consumption, not human convenience.

### Why It Matters
- AI can't "figure things out" like humans
- Explicit is better than implicit
- Clear context = better results
- Reduces back-and-forth clarifications

### How to Apply
1. **Explicit context:** Don't assume AI knows project details
2. **Structured formats:** Use consistent markdown sections
3. **Clear instructions:** "Do X then Y" not "Maybe consider X"
4. **Success criteria:** Objective, measurable outcomes
5. **AI-executable specs:** Include validation commands

### Examples
**Bad (Human-centric):**
```markdown
Make the login faster
```

**Good (Agent-centric):**
```markdown
## Objective
Reduce login API response time from 800ms to <300ms

## Success Criteria
- `/test` shows login_test.py passes
- Lighthouse performance score >90
- No new errors in logs

## Technical Approach
1. Add Redis caching for user lookups
2. Optimize database queries (add indexes)
3. Implement request batching
```

### Command Support
- All commands use agent-centric formatting
- Templates provide structure for AI consumption

---

## Core Principle 4: Closed-Loop Validation

**Principle:** Every task must include automated validation before completion.

### Why It Matters
- Catches errors before human review
- Enables autonomous execution
- Provides objective success metrics
- Reduces manual QA burden

### How to Apply
1. **Every spec defines validation:**
   - Unit tests to run
   - Integration tests to pass
   - E2E scenarios to verify
   - Performance benchmarks to meet
2. **Validation is executable:**
   - `npm test` or `pytest`
   - `npm run lint`
   - `npm run e2e`
   - Custom validation scripts
3. **AI auto-resolves failures:**
   - Reads test output
   - Identifies root cause
   - Fixes and re-validates
   - Loops until passing

### Validation Levels
- **L1 - Unit:** Individual function/component tests
- **L2 - Integration:** Component interaction tests
- **L3 - E2E:** Full user workflow tests
- **L4 - Performance:** Load, speed, resource tests

### Command Support
- `/test` - Run unit/integration tests with auto-fix
- `/test_e2e` - Run E2E tests with auto-fix
- `/resolve_failed_test` - Auto-fix test failures
- `/review` - Validation against spec

---

## Core Principle 5: Template Engineering

**Principle:** Reusable patterns and workflows accelerate development.

### Why It Matters
- Don't repeat planning work
- Encode best practices once
- Consistent quality across projects
- Faster onboarding for new team members

### How to Apply
1. **Spec templates:** Feature, bug, chore patterns
2. **Command templates:** Workflow automation
3. **ADW templates:** Multi-phase orchestration
4. **Validation checklists:** Reusable quality gates

### Template Hierarchy
```
.claude/
├── commands/           # Workflow templates
├── specs/              # Specification templates
├── validation-checklists/  # Validation templates
└── meta-prompts/      # Multi-phase orchestration
```

### Creating Templates
1. **Identify pattern:** Repeated workflow
2. **Extract structure:** Common sections
3. **Parameterize:** Project-specific values
4. **Validate:** Use in real projects
5. **Refine:** Improve based on feedback

### Command Support
- All commands are templates themselves
- `/feature`, `/bug`, `/chore` use spec templates
- ADW workflows are orchestration templates

---

## Integration with ADW (AI Developer Workflow)

TAC principles integrate seamlessly with ADW:

### TAC Principle → ADW Phase Mapping

| TAC Principle | ADW Phase | How It's Applied |
|--------------|-----------|------------------|
| Spec-First | `adw_plan_iso.py` | Creates specification before implementation |
| Knowledge Gap | `adw_plan_iso.py` | Checks for docs/context needed |
| Agent Perspective | All phases | Structured state files, explicit instructions |
| Closed-Loop Validation | `adw_test_iso.py`, `adw_review_iso.py` | Auto-test and auto-fix loops |
| Template Engineering | Orchestrators | Composable workflow templates |

### ADW Enhances TAC With:
- **Isolation:** Git worktrees prevent conflicts
- **Concurrency:** Up to 15 parallel workflows
- **State Management:** Persistent ADWState tracking
- **Auto-Ship:** Optional zero-touch deployment

---

## Success Patterns from Real Projects

### Pattern 1: Multi-Modal Search Strategy
**From:** Build-01 (Obsidian RAG MCP)

**Principle Applied:** Don't replace tools, combine them

**Result:**
- Semantic search for concepts
- Direct file access for exact matches
- Graph search for relationships
- AI chooses best method per query

### Pattern 2: Credential Verification Step
**From:** Build-01 (Wrong database error)

**Principle Applied:** Closed-loop validation includes setup

**Result:**
- Add environment verification before implementation
- Catch configuration errors early
- Saves debugging time

### Pattern 3: Spec-Driven MCP Development
**From:** Build-01 (Built MCP server without coding)

**Principle Applied:** Spec-first + Agent perspective

**Result:**
- Non-coder built production system
- Clear spec enabled autonomous implementation
- 1-2 hours from problem to solution

---

## Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Code-First Development
**Problem:** Starting implementation before spec

**Why it fails:**
- Unclear scope leads to scope creep
- No objective success criteria
- Difficult to validate completion
- AI makes assumptions without guidance

**Fix:** Always create spec first, even for small tasks

### ❌ Anti-Pattern 2: Skipping Knowledge Gap Check
**Problem:** Assuming AI has current knowledge

**Why it fails:**
- Uses outdated patterns/APIs
- Wrong library versions
- Deprecated approaches

**Fix:** Explicitly ask "What knowledge gaps exist?" before work

### ❌ Anti-Pattern 3: Manual Validation Only
**Problem:** Relying on human QA instead of automated tests

**Why it fails:**
- Breaks autonomous execution
- Slows down iteration
- Inconsistent quality
- Scales poorly

**Fix:** Define executable validation in spec

### ❌ Anti-Pattern 4: Implicit Context
**Problem:** Assuming AI "understands" project context

**Why it fails:**
- AI can't infer unstated conventions
- Leads to incorrect assumptions
- Requires repeated clarifications

**Fix:** Use `CLAUDE.md` and explicit specs

### ❌ Anti-Pattern 5: One-Off Solutions
**Problem:** Solving same problem differently each time

**Why it fails:**
- Wastes time re-planning
- Inconsistent quality
- Knowledge not captured

**Fix:** Create templates for repeated workflows

---

## Quick Reference: When to Use What

### Starting New Work
1. `/knowledge_gap_check` - Identify what AI needs
2. `/spec` - Create specification
3. `/generate_branch_name` - Create semantic branch
4. `/feature` or `/bug` or `/chore` - Begin implementation

### During Implementation
1. `/implement` - Execute the plan
2. `/test` - Validate with auto-fix
3. `/review` - Check against spec

### Before Completion
1. `/test_e2e` - Full workflow validation
2. `/document` - Generate documentation
3. `/commit` - Create semantic commit
4. `/pull_request` - Generate PR description

### For Complex Workflows
1. Use ADW orchestrators:
   - `adw_plan_build_test_iso.py` - Standard flow
   - `adw_sdlc_iso.py` - Complete SDLC
   - `adw_sdlc_zte_iso.py` - Zero-touch execution

---

## Measuring Success

### Project-Level Metrics
- **Time from issue to PR:** Should decrease over time
- **First-time success rate:** Percentage of PRs merged without revisions
- **Test coverage:** Should stay >80%
- **Documentation coverage:** All public APIs documented

### Process-Level Metrics
- **Spec creation time:** Faster with practice
- **Knowledge gaps identified:** More upfront = fewer mid-work blocks
- **Auto-resolution rate:** Percentage of test failures fixed autonomously
- **Template reuse:** Higher reuse = faster execution

### Quality Metrics
- **Bug escape rate:** Bugs found in production vs testing
- **Rework percentage:** Code changed after initial implementation
- **Review iteration count:** Revisions needed before merge

---

## Learning Resources

### Internal References
- **TAC Lessons:** Your Obsidian vault (`Learning-Cycles/Agentic-Coding/`)
- **Build Notes:** Real-world validations of principles
- **Command Examples:** `.claude/commands/` directory
- **ADW Architecture:** `adw/README.md`

### External Resources
- TAC Course Repository: [Your course notes]
- Claude Code Documentation: https://docs.claude.com/claude-code
- GitHub Workflows: `.github/workflows/`

---

## Contributing to TAC

This framework improves through use. When you discover:

### New Patterns
1. Document in build notes
2. Extract to atomic note
3. Add to this principles doc
4. Create template if repeatable

### Anti-Patterns
1. Document what went wrong
2. Identify which principle was violated
3. Add to anti-patterns section
4. Update templates to prevent

### Process Improvements
1. Measure before/after metrics
2. Validate in multiple projects
3. Update relevant commands
4. Share learnings

---

## Conclusion

TAC is not about replacing developers—it's about **amplifying development**.

**The human provides:**
- Problem definition
- Strategic direction
- Quality standards
- Final validation

**The AI provides:**
- Implementation speed
- Pattern recognition
- Tireless iteration
- Consistent quality

**Together, the result is:**
- Faster delivery
- Higher quality
- Better documentation
- More leverage

Follow these 5 principles, and you'll build production systems faster than you thought possible.

---

**Version:** 1.0
**Last Updated:** 2025-11-01
**Validated Through:** Build-01 (Obsidian RAG MCP), ADW Implementation
**Status:** Production-Ready
