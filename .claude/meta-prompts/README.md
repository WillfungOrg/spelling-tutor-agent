## Purpose
Multi-phase orchestration prompts for complex tasks.

## What Goes Here
- Multi-step implementation workflows
- Complex feature rollouts
- Migration plans
- Deployment orchestrations

## When to Use Meta-Prompts
- Task has 3+ distinct phases
- Phases have dependencies (Phase 2 needs Phase 1 output)
- Need validation between phases
- Complex enough to need orchestration

## Structure
```markdown
# Meta-Prompt: [Task Name]

## Phase 1: [Name]
- Objective
- Steps
- Validation
- Output

## Phase 2: [Name]
- Input from Phase 1
- Steps
- Validation
- Output
...

Example
See examples/meta-prompts/ for reference.