# Github Issue Command Selection

Based on the `Github Issue` below, follow the `Instructions` to select the appropriate command to execute based on the `Command Mapping`.

## Instructions

- Based on the details in the `Github Issue`, select the appropriate command to execute.
- IMPORTANT: Respond exclusively with '/' followed by the command to execute based on the `Command Mapping` below.
- Use the command mapping to help you decide which command to respond with.
- Don't examine the codebase just focus on the `Github Issue` and the `Command Mapping` below to determine the appropriate command to execute.

## CRITICAL OUTPUT FORMAT

**YOU MUST RETURN ONLY THE SLASH COMMAND - NOTHING ELSE!**

Examples of CORRECT output:
- `/chore`
- `/bug`
- `/feature`
- `/patch`
- `0`

Examples of WRONG output (DO NOT DO THIS):
- "Based on my analysis, this is a `/chore`" ❌
- "I recommend `/feature` because..." ❌
- Any text before or after the command ❌
- Any markdown formatting or explanations ❌

**RETURN ONLY THE COMMAND ON A SINGLE LINE!**

## Command Mapping

- Respond with `/chore` if the issue is a chore.
- Respond with `/bug` if the issue is a bug.
- Respond with `/feature` if the issue is a feature.
- Respond with `/patch` if the issue is a patch.
- Respond with `0` if the issue isn't any of the above.

## Github Issue

$ARGUMENTS