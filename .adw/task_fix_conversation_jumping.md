# Fix Agent Conversation Jumping Issue

## Problem Description
The spelling tutor agent's conversation jumps between words during practice. While practicing spelling "butterfly", the agent talks about other words, then suddenly jumps back to butterfly saying "well done on getting correct spelling". This is caused by the LLM not having context about which word the child should be spelling.

## Root Cause
The agent's system instructions are static and set once during initialization (src/spelling_tutor/agent.py:57-63). These instructions don't include:
1. The current word being practiced
2. The current attempt count
3. Hints that have been provided
4. Expected spelling format

The LLM has NO KNOWLEDGE of which specific word (e.g., "butterfly") the child should be spelling, so it cannot properly guide the conversation.

## Required Changes

### 1. Add Dynamic Context Method to Agent Class
**File:** `src/spelling_tutor/agent.py`

Add a new method to generate dynamic instructions that include current state:

```python
def _get_dynamic_instructions(self) -> str:
    """Generate instructions with current word context."""
    base = f"""You are {self.child_name}'s spelling tutor.

CRITICAL CONTEXT:
"""

    if self.current_word and self.current_tutor:
        attempt_num = self.current_tutor.current_attempts + 1
        base += f"""- Current word to spell: {self.current_word.word.upper()}
- This is attempt #{attempt_num} of 3
- Correct spelling: {'-'.join(self.current_word.word.upper())}
"""

        # Add hint context if hints have been given
        if self.current_tutor.current_attempts > 0:
            hints_given = []
            if self.current_tutor.current_attempts >= 1:
                hints_given.append("phonics hint")
            if self.current_tutor.current_attempts >= 2:
                hints_given.append("letter-by-letter guidance")
            base += f"- Hints already provided: {', '.join(hints_given)}\n"
    else:
        base += "- No word is currently active\n"

    base += """
INSTRUCTIONS:
- Wait for the user to spell the current word
- ONLY call spell_word when the user provides their spelling attempt for the current word
- DO NOT call spell_word based on your own responses or when presenting a new word
- If the user says something unrelated to the current word, gently redirect them back to spelling the current word
- Be encouraging, patient, and keep focus on the current word
- After correct spelling, present the next word clearly
"""
    return base
```

### 2. Update Constructor to Use Dynamic Instructions
**File:** `src/spelling_tutor/agent.py`
**Location:** Lines 57-63

Change from static instructions to dynamic:

```python
# OLD:
super().__init__(
    instructions=f"""You are {self.child_name}'s spelling tutor.
    ONLY call the spell_word function when the user provides their spelling attempt.
    DO NOT call spell_word based on your own responses or when presenting a new word.
    Wait for the user to respond before calling any functions.
    Be encouraging and patient."""
)

# NEW:
super().__init__(
    instructions=self._get_dynamic_instructions()
)
```

### 3. Update Instructions After Each Word Change
**File:** `src/spelling_tutor/agent.py`
**Location:** After line 109 (when moving to next word)

Add instruction update after moving to next word:

```python
# Inside spell_word function, after self.current_word = next_word (line 109)
self.current_word = next_word
self.current_tutor = None

# ADD THIS:
# Update instructions with new word context
self.instructions = self._get_dynamic_instructions()
```

### 4. Update Instructions Before Each Greeting
**File:** `src/spelling_tutor/agent.py`
**Location:** Lines 159-168 (on_enter method)

Update instructions before greeting:

```python
async def on_enter(self):
    """Called when agent becomes active - like working examples."""
    logger.info("Spelling tutor agent session started")

    # ADD THIS: Update instructions with current word context
    self.instructions = self._get_dynamic_instructions()

    if self.current_word:
        greeting = f"Hi {self.child_name}! Let's practice spelling. Your word is: {self.current_word.word}. Please spell {self.current_word.word} for me."
    else:
        greeting = f"Hi {self.child_name}! It looks like we don't have any words to practice right now."

    await self.session.generate_reply(instructions=greeting)
```

### 5. Update Instructions After Processing Attempt
**File:** `src/spelling_tutor/agent.py`
**Location:** After line 98 (after updating tutor with result)

Add instruction update after attempt processing:

```python
# Inside spell_word function, after self.current_tutor = tutor (line 98)
self.current_tutor = tutor

# ADD THIS:
# Update instructions to reflect new attempt count
self.instructions = self._get_dynamic_instructions()
```

## Testing Requirements

Test the following scenarios:

1. **Focused conversation**: Child spells the current word correctly → Agent stays on task
2. **Off-topic handling**: Child says unrelated word → Agent redirects to current word
3. **Multiple attempts**: Child makes wrong attempts → Instructions reflect attempt count
4. **Word progression**: Completing a word → Instructions update with next word
5. **Hint progression**: Failed attempts → Instructions reflect hints given

## Expected Behavior After Fix

- Agent always knows which word child should be spelling
- Conversation stays focused on current word
- No jumping between words
- Clear transitions when moving to next word
- Attempt count and hints reflected in agent's awareness

## Success Criteria

- [ ] Agent maintains focus on current word throughout spelling attempts
- [ ] No conversation jumping between words
- [ ] Agent correctly redirects if child mentions other words
- [ ] Smooth transitions between words after successful spelling
- [ ] Instructions reflect current state (word, attempt, hints)

## Notes

- The existing state management in tutor_logic.py is correct and doesn't need changes
- This fix addresses only the LLM context awareness issue
- The spell_word function logic remains unchanged
- This builds on the previous fix from commit 0e9adc1 that prevented robotic responses
