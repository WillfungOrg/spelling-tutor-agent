# Testing Guide: Conversation Jumping Fix

## What Was Fixed

The agent's conversation was jumping between words because the LLM didn't know which word the child should be spelling. This fix adds dynamic context to the agent's system instructions, so it always knows:
- The current word being practiced (e.g., "BUTTERFLY")
- The attempt number (1, 2, or 3)
- What hints have been given
- How to redirect if the child mentions other words

## How to Test the Fix

### Prerequisites
1. Start the LiveKit agent server:
   ```bash
   python src/spelling_tutor/agent_worker.py
   ```

2. Connect to the agent via the LiveKit client (voice interface)

### Test Scenarios

#### Test 1: Focused Spelling Practice (Main Fix)
**Goal:** Verify agent stays focused on current word

1. **Start session** - Agent says: "Hi Emma! Your word is: butterfly"
2. **Say the word correctly**: "b-u-t-t-e-r-f-l-y"
3. **Expected behavior:**
   - ✓ Agent recognizes this as spelling attempt for "butterfly"
   - ✓ Agent says "Excellent work! You spelled 'butterfly' perfectly!"
   - ✓ Agent moves to next word smoothly
   - ✗ NO jumping to other topics
   - ✗ NO confusion about which word you're spelling

#### Test 2: Off-Topic Handling
**Goal:** Verify agent redirects when child mentions other words

1. **Agent presents word**: "Your word is: butterfly"
2. **Say something off-topic**: "Can we spell elephant instead?"
3. **Expected behavior:**
   - ✓ Agent gently redirects: "Let's focus on 'butterfly' first"
   - ✓ Agent encourages: "Please spell butterfly for me"
   - ✗ NO jumping to discuss elephant
   - ✗ NO losing track of butterfly

#### Test 3: Multiple Attempts with Hints
**Goal:** Verify instructions update with attempt count

1. **Agent presents word**: "Your word is: butterfly"
2. **First attempt (wrong)**: "b-u-t-e-r-f-l-y"
3. **Expected behavior:**
   - ✓ Agent gives phonics hint
   - ✓ Agent encourages another try
   - ✓ Agent STILL knows current word is butterfly
4. **Second attempt (wrong)**: "b-u-t-t-e-r-f-y"
5. **Expected behavior:**
   - ✓ Agent gives letter-by-letter hint
   - ✓ Agent mentions this is the last try
   - ✓ Agent STILL focused on butterfly
6. **Third attempt (correct)**: "b-u-t-t-e-r-f-l-y"
7. **Expected behavior:**
   - ✓ Agent celebrates success
   - ✓ Agent moves to next word

#### Test 4: Word Progression
**Goal:** Verify instructions update when changing words

1. **Complete word 1**: Spell "butterfly" correctly
2. **Agent presents word 2**: "Next word is: cat"
3. **Expected behavior:**
   - ✓ Agent clearly announces new word
   - ✓ Agent asks child to spell "cat"
   - ✓ Agent no longer mentions "butterfly"
4. **Spell word 2**: "c-a-t"
5. **Expected behavior:**
   - ✓ Agent recognizes spelling for "cat" (not butterfly)
   - ✓ Agent celebrates and moves to word 3

#### Test 5: Edge Case - Saying Previous Word
**Goal:** Verify agent doesn't get confused by previous words

1. **Complete word 1**: Spell "butterfly" correctly
2. **Agent presents word 2**: "Next word is: cat"
3. **Say previous word**: "butterfly"
4. **Expected behavior:**
   - ✓ Agent recognizes this is NOT the current word
   - ✓ Agent redirects: "We already did butterfly! Now spell cat for me"
   - ✗ NO processing "butterfly" as if it's current word
   - ✗ NO jumping back to previous word

## What to Look For

### ✓ **Good Behaviors (Fix Working)**
- Agent always knows which word child should spell
- Smooth transitions between words
- Clear focus on one word at a time
- Appropriate redirection when child goes off-topic
- Consistent tracking of attempts (1, 2, 3)
- Hints progress appropriately

### ✗ **Bad Behaviors (Fix NOT Working)**
- Agent processes wrong word (e.g., processes "butterfly" when current word is "cat")
- Conversation jumps between words randomly
- Agent says "Well done!" when child hasn't spelled current word
- Agent loses track of which word is active
- Confusion about attempt numbers
- Repeating same hints

## Technical Verification

### Check Agent Logs
The agent logs should show:

```
INFO: Started new word: butterfly
INFO: Processing spelling attempt: 'butterfly' -> 'butterfly' for word 'butterfly'
```

**Look for:**
- Correct word name in logs
- Attempt processing matches current word
- No mismatches between what child says and what agent expects

### Verify Instructions Update
Add debug logging to see instructions:

```python
# In agent.py, after updating instructions
logger.debug(f"Updated instructions: {self.instructions[:200]}...")
```

**Expected output:**
```
Updated instructions: You are Emma's spelling tutor.

CRITICAL CONTEXT:
- Current word to spell: BUTTERFLY
- This is attempt #1 of 3
- Correct spelling: B-U-T-T-E-R-F-L-Y
...
```

## Success Criteria

The fix is successful if:

1. ✓ Agent maintains focus on current word throughout all attempts
2. ✓ No conversation jumping between words
3. ✓ Agent correctly redirects when child mentions other words
4. ✓ Smooth, clear transitions when moving to next word
5. ✓ Attempt count and hints correctly reflected in agent behavior
6. ✓ Child can complete full spelling session without confusion

## Regression Testing

Also verify the previous fix still works:

### Previous Issue: Robotic Auto-Responses
**What was fixed before:** Agent was calling `spell_word` on its own responses

**Test:** Agent should NOT process its own speech
1. Agent says: "Please spell butterfly"
2. **Expected:** Agent waits for child's response
3. **NOT Expected:** Agent immediately calls spell_word on the word "butterfly" from its own speech

This should still work correctly.

## Notes for Testing

- Test with multiple words in sequence (at least 3-4 words)
- Try both correct and incorrect spellings
- Test with different word difficulties (easy, medium, hard)
- Test session completion (after all words done)
- Use realistic child speech patterns (may include "um", "uh", pauses)

## Reporting Issues

If you find the conversation still jumping:

1. Note the exact words in the word list
2. Note what the child said
3. Note what the agent responded
4. Check agent logs for the session
5. Report with full details so we can investigate
