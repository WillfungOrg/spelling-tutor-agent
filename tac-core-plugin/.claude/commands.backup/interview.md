# Meta-ADW User Interview

**Purpose:** Gather information about the task to recommend optimal strategy.

**When to use:** First step in Meta-ADW workflow to understand user intent and task requirements.

---

## Your Task

Conduct an interview with the user to understand their task. Ask the following questions and gather structured responses.

## Interview Questions

Based on the task description provided, ask the user these 7 key questions. For each question, provide context and examples to help them answer accurately.

### Question 1: Task Type
**Ask:** "What type of task is this?"

**Options:**
- `feature` - Building something new
- `bug` - Fixing something broken
- `chore` - Maintenance, refactoring, dependencies
- `investigation` - Exploring/debugging without immediate fix
- `patch` - Quick hotfix
- `refactor` - Code improvement without functional changes

**Example:** "Adding user authentication would be a `feature`. Fixing a null pointer exception would be a `bug`."

### Question 2: Complexity Level
**Ask:** "How would you rate the complexity of this task?"

**Options:**
- `simple` - Straightforward, single file, < 2 hours
- `moderate` - Few files, some thought required, 2-6 hours
- `complex` - Many files, careful planning needed, 6-16 hours
- `very_complex` - Cross-cutting, high risk, > 16 hours

**Example:** "Changing button text is `simple`. Adding OAuth integration is `complex`."

### Question 3: User Interaction Layer
**Ask:** "What parts of the system does this task involve?"

**Options:**
- `UI` - Frontend/user interface changes
- `backend` - Server/API changes
- `full-stack` - Both frontend and backend
- `infrastructure` - DevOps, deployment, config
- `data` - Database schema, migrations
- `none` - No user-facing changes

**Example:** "Adding a login form is `UI`. Creating an authentication API is `backend`. End-to-end auth flow is `full-stack`."

### Question 4: Testing Requirements
**Ask:** "What types of tests are needed for this task?"

**Options:**
- `unit` - Unit tests only
- `integration` - Integration tests needed
- `e2e` - End-to-end/browser tests needed
- `all` - Comprehensive testing at all levels
- `manual` - Manual testing sufficient
- `none` - No tests needed (rare)

**Example:** "Adding a utility function needs `unit` tests. A new user workflow needs `e2e` tests."

### Question 5: Validation Needs
**Ask:** "How critical is validation for this task?"

**Options:**
- `basic` - Standard validation (tests pass)
- `thorough` - Comprehensive validation (tests + code review)
- `critical` - Mission-critical (tests + review + manual QA + monitoring)
- `l5_closed_loop` - TAC L5: Closed-loop feedback with real logs
- `l6_specialized` - TAC L6: Specialized validation agents
- `l7_zero_touch` - TAC L7: Zero-touch execution with full automation

**Example:** "Internal tool update is `basic`. Payment processing is `critical`. Production incident fix might need `l5_closed_loop`."

### Question 6: Timeline
**Ask:** "What's the desired timeline for this task?"

**Options:**
- `quick-patch` - Need it done ASAP, minimal process
- `normal` - Standard development timeline
- `comprehensive` - Take time to do it right, full process

**Example:** "Fixing a production bug blocking users is `quick-patch`. Adding a new feature for next sprint is `normal`."

### Question 7: Novelty
**Ask:** "Is this a standard task or something novel/unusual?"

**Options:**
- `standard` - Similar tasks have been done before
- `novel` - First time doing something like this
- `unique` - Completely custom scenario

**Example:** "Adding another CRUD endpoint is `standard`. Integrating a new third-party service is `novel`. Building a custom ML pipeline is `unique`."

---

## Output Format

After gathering responses, output a JSON structure:

```json
{
  "task_description": "<original task description>",
  "task_type": "<feature|bug|chore|investigation|patch|refactor>",
  "complexity_level": "<simple|moderate|complex|very_complex>",
  "user_interaction_layer": "<UI|backend|full-stack|infrastructure|data|none>",
  "testing_requirements": "<unit|integration|e2e|all|manual|none>",
  "validation_needs": "<basic|thorough|critical|l5_closed_loop|l6_specialized|l7_zero_touch>",
  "timeline": "<quick-patch|normal|comprehensive>",
  "novelty": "<standard|novel|unique>",
  "additional_context": "<any additional information gathered>"
}
```

---

## Examples

### Example 1: Simple Bug Fix
```json
{
  "task_description": "Fix typo in error message",
  "task_type": "bug",
  "complexity_level": "simple",
  "user_interaction_layer": "UI",
  "testing_requirements": "unit",
  "validation_needs": "basic",
  "timeline": "quick-patch",
  "novelty": "standard",
  "additional_context": "Low risk, cosmetic fix"
}
```

### Example 2: Complex Feature
```json
{
  "task_description": "Add user authentication with OAuth",
  "task_type": "feature",
  "complexity_level": "complex",
  "user_interaction_layer": "full-stack",
  "testing_requirements": "all",
  "validation_needs": "critical",
  "timeline": "comprehensive",
  "novelty": "novel",
  "additional_context": "Security-critical, affects all users, requires external OAuth provider integration"
}
```

### Example 3: Moderate Chore
```json
{
  "task_description": "Upgrade database library to latest version",
  "task_type": "chore",
  "complexity_level": "moderate",
  "user_interaction_layer": "backend",
  "testing_requirements": "integration",
  "validation_needs": "thorough",
  "timeline": "normal",
  "novelty": "standard",
  "additional_context": "Need to check for breaking changes and update queries"
}
```

---

## Instructions

**IMPORTANT: This is a programmatic interview. Do NOT ask questions interactively.**

1. Read the task description below
2. Analyze the task across all 7 dimensions
3. Make an informed assessment for each field based on the task description
4. Output ONLY valid JSON according to the Output Format above
5. **DO NOT** include any explanatory text before or after the JSON
6. **DO NOT** ask questions or wait for user input
7. The JSON must be parseable by `json.loads()` in Python

## Task Description

$1

---

## Your Response

**CRITICAL:** Your entire response must be ONLY the JSON object below. Start your response with `{` and end with `}`. Do not include markdown code fences, explanatory text, or any other characters.

Example of correct output:
```
{"task_description":"Example task","task_type":"feature","complexity_level":"moderate","user_interaction_layer":"full-stack","testing_requirements":"integration","validation_needs":"thorough","timeline":"normal","novelty":"standard","additional_context":""}
```

Now analyze the task and output your JSON:
