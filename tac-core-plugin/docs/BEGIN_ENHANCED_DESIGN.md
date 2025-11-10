# Enhanced /begin Design - Collaborative Discovery

## Vision

Transform `/begin` from a simple task router into an intelligent brainstorming partner that:

1. **Collaboratively discovers** user objectives through conversation
2. **Provides ideas and suggestions** to help crystallize thinking
3. **Identifies knowledge gaps** proactively using integrated `/knowledge_gap_check`
4. **Searches codebase** for relevant existing documents and patterns
5. **Fetches external docs** via MCP when needed
6. **Gathers context first** before recommending any implementation approach

## Enhanced Flow

### Phase 0: Setup Check (Existing)
- Check if "Project-Specific Context" exists in CLAUDE.md
- If missing → Setup Mode (interview + append)
- If exists → Continue to Phase 1

---

### Phase 1: Collaborative Discovery (NEW)

**Goal:** Understand what the user wants to achieve, even if they don't have a complete picture yet.

#### Step 1.1: Open-Ended Exploration
Ask: *"What would you like to work on? Tell me your ideas, even if they're not fully formed yet."*

Listen for:
- **Objectives** - What they want to achieve
- **Intent** - Why they want to do it
- **Constraints** - Limitations or requirements
- **Uncertainty** - What they're unsure about
- **Scope** - How big is this (feature, bug, refactor, etc.)

#### Step 1.2: Active Brainstorming
Based on their initial response, provide:
- **Clarifying questions** - Help them think through the problem
- **Ideas and suggestions** - "Have you considered...?"
- **Trade-offs** - "This approach has benefits X but trade-offs Y"
- **Alternatives** - "Another way to achieve this would be..."
- **Scope refinement** - "Should we tackle all of this, or start with...?"

**Example:**
```
User: "I want to add authentication"

AI: "Great! Let me help you think through this:

Authentication is a broad topic. A few questions to help us focus:

1. **User Identity**:
   - Are users logging in with email/password?
   - Social logins (Google, GitHub)?
   - SSO for enterprise?

2. **Scope**:
   - Just login/logout? Or also:
     - User registration
     - Password reset
     - Email verification
     - Role-based access control

3. **Integration**:
   - I can check your codebase for existing auth patterns
   - Are you using any auth services already? (Auth0, Clerk, etc.)

Tell me more about what you envision, and I'll help refine it!"
```

#### Step 1.3: Objective Crystallization
Once the conversation reaches clarity, summarize:

```markdown
## 🎯 What We're Building

**Objective:** [Clear statement of what we're doing]

**Why:** [The reason/problem being solved]

**Scope:**
- In scope: [Specific features/changes]
- Out of scope: [What we're NOT doing now]

**Success looks like:** [Measurable outcomes]

Does this capture what you want? Any adjustments?
```

Get user confirmation before proceeding.

---

### Phase 2: Knowledge Gap Analysis (NEW - Integrated)

**Goal:** Identify and fill ALL knowledge gaps before planning or implementation.

#### Step 2.1: Search Codebase for Context

**Automatically check:**

1. **Related specifications:**
   ```bash
   Glob pattern: .claude/specs/*.md
   # Look for related work
   ```

2. **Related code patterns:**
   ```bash
   # Search for keywords related to the task
   Grep pattern: [key terms from objective]
   # Find existing implementations
   ```

3. **Configuration files:**
   ```bash
   # Check for relevant config
   Read: .env.example, config files, package.json dependencies
   ```

4. **Existing tests:**
   ```bash
   # Find test patterns
   Grep pattern: test|spec related to task
   ```

5. **Recent similar work:**
   ```bash
   git log --oneline --all -30 --grep="[keywords]"
   # See if similar work was done recently
   ```

Present findings:
```markdown
## 📚 Existing Context I Found

### In Your Codebase:
- ✅ Found: [List relevant files/patterns found]
- ℹ️ Relevant specs: [Link to related specs]
- ℹ️ Similar code: [Point to existing patterns]
- ℹ️ Tests: [Existing test patterns to follow]

### Missing from Codebase:
- ❌ Not found: [What doesn't exist yet]
```

#### Step 2.2: Identify External Knowledge Gaps

Run integrated `/knowledge_gap_check` logic:

**Check:**
1. **Framework/Library Versions**
   - What libraries/frameworks are needed?
   - Are they in package.json/pyproject.toml?
   - Is AI training data current for these versions?

2. **External APIs/Services**
   - Are there external dependencies?
   - Do we need API documentation?

3. **Domain Knowledge**
   - Are there domain-specific concepts?
   - Are there compliance/security requirements?

**Present gaps:**
```markdown
## ❓ Knowledge Gaps Identified

### What I Know:
- ✅ [List what AI is confident about]
- ✅ [Versions it knows]

### What I Need to Know:
1. **[Gap 1]** - [Why it matters]
   - Can get from: [MCP docs / web search / user]

2. **[Gap 2]** - [Why it matters]
   - Can get from: [source]

### Risk if We Skip:
- ⚠️ [What could go wrong without this knowledge]
- ⚠️ [Potential rework needed]
```

#### Step 2.3: MCP Integration for Documentation

**Check available MCP resources:**
```bash
# List available MCP servers
ListMcpResourcesTool
```

**If relevant docs available via MCP:**
```markdown
## 📖 I can fetch official documentation:

Available via MCP:
- [Library/Framework name] official docs
- [API service] documentation

Should I fetch these now? This will ensure I'm working with current, accurate information.
```

If user approves, fetch docs:
```bash
# Example: Get React docs
ReadMcpResourceTool server="chrome" uri="https://react.dev/reference/..."
```

#### Step 2.4: Web Search Permission

**If gaps require web search:**
```markdown
## 🌐 Additional Research Needed

I recommend searching for:
1. [Topic 1] - Latest best practices
2. [Topic 2] - Current API documentation
3. [Topic 3] - Security considerations

May I do web searches for these topics? This ensures I'm not using outdated patterns.
```

If approved, use WebSearch or WebFetch tools.

---

### Phase 3: Context Gathering & Validation (NEW)

**Goal:** Ensure we have everything needed before proceeding.

#### Step 3.1: Fill the Gaps

For each identified gap:
1. **If in codebase** → Read and summarize relevant content
2. **If external docs needed** → Fetch via MCP or web search (with permission)
3. **If domain knowledge** → Ask user to provide or confirm understanding
4. **If configuration** → Verify environment setup requirements

#### Step 3.2: Context Validation

Present complete context to user:

```markdown
## ✅ Context Gathered - Ready to Proceed

### What I Now Know:

**Codebase Context:**
- [Summary of relevant code patterns found]
- [Existing similar implementations]
- [Test patterns to follow]

**External Context:**
- [Framework/library documentation reviewed]
- [API documentation gathered]
- [Best practices identified]

**Domain Context:**
- [Domain-specific requirements understood]
- [Constraints and requirements noted]

### Confidence Level: [High/Medium/Low]

**Still Missing:** [List any remaining gaps, if any]

Do we have enough context to proceed with planning?
```

Get user confirmation before moving forward.

---

### Phase 4: Task Analysis (Enhanced)

**Now with full context, analyze the task properly.**

#### Step 4.1: Classify Task Type
- Feature / Bug / Chore / Refactor / Investigation / Documentation
- Complexity: 1-10 scale
- Estimated effort

#### Step 4.2: Identify Constraints
- Technical constraints from codebase
- Architectural patterns to follow
- Testing requirements
- Performance requirements

#### Step 4.3: Risk Assessment
- What could go wrong?
- What are the unknowns?
- What validation is needed?

---

### Phase 5: Workflow Recommendation (Enhanced)

**Recommend optimal workflow based on complete context.**

```markdown
## 🎯 Recommended Workflow

**Task Type:** [Classification]
**Complexity:** [1-10] - [Reasoning]
**Estimated Time:** [Planning: X min, Implementation: Y min]

**Best Approach:** [Manual Commands / ADW Automated / Hybrid]

**Why This Approach:**
- [Reason 1 based on task characteristics]
- [Reason 2 based on available context]
- [Reason 3 based on complexity and risks]

## 📋 Detailed Next Steps

### Phase 1: Specification
[Exact steps with commands]

### Phase 2: Implementation
[Exact steps with commands]

### Phase 3: Validation
[Exact steps with commands]

### Phase 4: Integration
[Exact steps with commands]

## 🔍 Decision Factors

I recommended this workflow because:
1. **Context Availability**: [We have/don't have X]
2. **Complexity**: [Task is simple/moderate/complex because...]
3. **Risk Level**: [Low/Medium/High risk due to...]
4. **Validation Strategy**: [How we'll ensure success]

## ⚡ Alternative Approaches

If you prefer a different workflow:
- **[Alternative 1]**: [Description + when to use]
- **[Alternative 2]**: [Description + when to use]

Ready to proceed? Or would you like to adjust the plan?
```

---

## Key Differences from Current /begin

### Current /begin:
1. Check setup
2. Ask "What do you want to work on?"
3. Classify task
4. Recommend workflow
5. Done

### Enhanced /begin:
1. Check setup
2. **Collaborative discovery** - Brainstorm with user, provide ideas
3. **Search codebase** - Find all relevant existing context
4. **Identify knowledge gaps** - Integrated `/knowledge_gap_check`
5. **Fetch external docs** - MCP integration for official documentation
6. **Gather context** - Fill all gaps before proceeding
7. **Validate readiness** - Confirm we have everything needed
8. **Analyze task** - With full context, proper classification
9. **Recommend workflow** - Informed by complete picture
10. **Provide detailed plan** - Step-by-step with reasoning

---

## Benefits

### For Users:
- ✅ Never miss critical context
- ✅ Get ideas and suggestions when unsure
- ✅ Confidence that AI understands the task
- ✅ Avoid rework from missing knowledge
- ✅ Clear, informed recommendations

### For AI:
- ✅ Complete context before planning
- ✅ Access to latest documentation
- ✅ Reduced hallucination risk
- ✅ Better workflow recommendations
- ✅ Higher success rate

---

## Example End-to-End Flow

### User starts:
```
/begin
```

### AI (Phase 1 - Discovery):
```
What would you like to work on? Tell me your ideas, even if they're not fully formed yet.
```

### User:
```
I want to add some kind of caching to make the app faster
```

### AI (Phase 1 - Brainstorming):
```
Great idea! Let me help you think through this:

Caching can mean several things:

1. **HTTP Response Caching**
   - Cache API responses at the client level
   - Reduces repeated network calls
   - Tools: React Query, SWR, Apollo Client

2. **Server-Side Caching**
   - Cache database queries (Redis, Memcached)
   - Cache computed results
   - Reduces database load

3. **Static Asset Caching**
   - Browser caching headers
   - CDN caching
   - Build-time pre-rendering

Questions to help us focus:
- What's slow right now? (specific pages/features)
- Have you measured performance? (what metrics?)
- Where do you think the bottleneck is? (API calls? Database? Rendering?)

Tell me more about what you're experiencing!
```

### User:
```
The dashboard page is slow. It makes like 5 API calls on load and each one takes 2-3 seconds.
Users complain it takes forever to load.
```

### AI (Phase 1 - Crystallization):
```
## 🎯 What We're Building

**Objective:** Implement client-side API response caching for dashboard to reduce repeated API calls

**Why:** Dashboard makes 5 API calls (2-3s each) on every load, causing poor user experience

**Scope:**
- In scope:
  - Client-side caching for dashboard API calls
  - Cache invalidation strategy
  - Stale-while-revalidate pattern
- Out of scope (for now):
  - Server-side caching
  - Other pages beyond dashboard
  - Database query optimization

**Success looks like:**
- Dashboard loads in <1 second on return visits
- Fresh data still shown when needed
- Reduced server load from repeated calls

Does this capture what you want?
```

### User:
```
Yes exactly!
```

### AI (Phase 2 - Knowledge Gap Analysis):
```
## 📚 Existing Context I Found

### In Your Codebase:
- ✅ Found: React Query already installed in package.json
- ✅ Found: Existing API client in `src/api/client.ts`
- ✅ Found: Dashboard component at `src/pages/Dashboard.tsx`
- ✅ Found: Test pattern in `src/tests/` using Jest + React Testing Library

### Missing from Codebase:
- ❌ No React Query configuration yet
- ❌ No caching strategy documented

## ❓ Knowledge Gaps Identified

### What I Know:
- ✅ React Query (you have v5.28.0 installed)
- ✅ Your React setup and patterns
- ✅ General caching strategies

### What I Need to Know:
1. **React Query v5 Latest Features** - (Released after my training cutoff)
   - Can get from: Official React Query docs via MCP or web search

2. **Your Current API Call Pattern**
   - Can get from: Reading Dashboard.tsx and API client code

### 🌐 Additional Research Recommended

I recommend getting the latest React Query v5 documentation to ensure I use current best practices.

May I:
1. Read your Dashboard.tsx and API client code
2. Fetch React Query v5 official docs (via web search or MCP if available)

This ensures I recommend patterns that work with your specific version.
```

### User:
```
Yes go ahead
```

### AI (Phase 3 - Context Gathering):
```
[Reads Dashboard.tsx]
[Reads API client code]
[Fetches React Query v5 docs via WebFetch]

## ✅ Context Gathered - Ready to Proceed

### What I Now Know:

**Codebase Context:**
- Dashboard makes 5 separate `useEffect` + fetch calls
- No query library currently in use (raw fetch calls)
- API client has auth token handling
- Tests use mock fetch responses

**External Context:**
- React Query v5 docs reviewed
- Latest patterns: useQuery, useSuspenseQuery, queryClient
- Recommended stale time: 5 minutes for dashboards
- Best practice: QueryClientProvider at app root

**Domain Context:**
- Dashboard shows: user stats, recent activity, notifications, metrics, alerts
- Data updates every few minutes (not real-time critical)
- Users refresh dashboard frequently

### Confidence Level: High

**Still Missing:** None - we have complete context!

Ready to proceed with planning.
```

### AI (Phase 4-5 - Analysis & Recommendation):
```
## 🎯 Recommended Workflow

**Task Type:** Feature (Performance Optimization)
**Complexity:** 4/10 - Straightforward refactor with established patterns
**Estimated Time:** Planning: 10 min, Implementation: 45-60 min

**Best Approach:** Manual Commands (Spec-First)

**Why This Approach:**
- Refactoring existing code (benefits from careful planning)
- Need to update multiple call sites
- Testing strategy important (can't break dashboard)
- No GitHub issue (exploratory improvement)

## 📋 Detailed Next Steps

### Phase 1: Specification
```
/spec
```
- Define caching strategy
- Specify cache times for each API call
- Define invalidation triggers
- List migration steps from raw fetch to React Query

### Phase 2: Implementation Plan
```
/feature
```
- Generate step-by-step implementation plan
- Break down: QueryClient setup, migrate each hook, add tests

### Phase 3: Execute
```
/implement
```
- Set up QueryClientProvider
- Replace fetch calls with useQuery
- Configure cache times
- Add loading states

### Phase 4: Validation
```
/test
```
- Run existing tests (ensure no regressions)
- Add new tests for caching behavior
- Auto-fix any failures

### Phase 5: Review
```
/review
```
- Verify against spec
- Check performance improvement
- Validate cache invalidation works

### Phase 6: Ship
```
/commit
/pull_request
```

## 🔍 Decision Factors

I recommended manual workflow because:
1. **Context Availability**: We have complete picture (codebase + docs + patterns)
2. **Complexity**: Moderate refactor requiring careful migration of 5 call sites
3. **Risk Level**: Medium (could break dashboard if not careful)
4. **Validation Strategy**: Existing tests must pass + new cache tests

## ⚡ Alternative Approaches

If you create a GitHub issue for tracking:
- **ADW SDLC**: `uv run adw/adw_sdlc_iso.py <issue-number>` for automated execution

Ready to start with `/spec`?
```

---

## Implementation Considerations

### Performance
- Context gathering is front-loaded but saves time later
- Web searches are async and optional (ask permission first)
- MCP fetches are cached

### User Experience
- Conversational and collaborative
- User always in control (permissions for searches)
- Clear progress through phases
- Can skip phases if context is complete

### Flexibility
- Can abort early if user just wants quick answer
- Can deep-dive if complex task
- Adapts to user's certainty level

---

## Success Metrics

A successful enhanced `/begin` session:

✅ User feels heard and understood
✅ User gets helpful suggestions and ideas
✅ All knowledge gaps identified and addressed
✅ Complete context gathered before planning
✅ User confident in recommended workflow
✅ No surprises or missing info during implementation
✅ Time: 5-10 minutes for complex tasks (vs 30+ minutes of rework)

---

## Next Steps for Implementation

1. Update `tac-core-plugin/commands/begin.md` with new phases
2. Integrate `/knowledge_gap_check` logic inline
3. Add MCP resource checking
4. Add codebase search automation
5. Test with various task types
6. Document examples
