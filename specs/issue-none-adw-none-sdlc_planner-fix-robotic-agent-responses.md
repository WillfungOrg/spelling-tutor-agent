# Bug: Agent Delivers Robotic Responses Despite Child-Friendly Code Implementation

## Metadata
issue_number: `none`
adw_id: `none`
issue_json: `Manual bug report - LiveKit agent paraphrasing child-friendly responses`

## Bug Description

The spelling tutor voice agent is delivering robotic, repetitive responses despite having comprehensive child-friendly response variations implemented in the code.

**Expected Behavior:**
- Agent should deliver varied, enthusiastic responses like "Woohoo! You got 'cat' right!", "Yay! Perfect spelling!", "Boom! You nailed it!"
- Each interaction should feel fresh and engaging for 6-10 year old children
- Responses should use the exact text returned by the `spell_word()` function which includes 12+ variations per scenario

**Actual Behavior:**
- Agent delivers robotic, formal responses like "Excellent work, Emma! You spelled 'cat' perfectly!"
- Responses are repetitive and sound the same across multiple words
- Child-friendly exclamations (Woohoo, Yay, Boom) are not being spoken
- The agent feels more like a formal teacher than an enthusiastic learning companion

**User Report:**
"I don't feel any changes toward the agent. I have pulled the latest branch into local and restarted the agent with `python -m spelling_tutor.agent_worker console`"

## Problem Statement

The LiveKit Agents framework's LLM layer is **paraphrasing** the function tool return values instead of delivering them verbatim. When the `spell_word()` function returns child-friendly text like "Woohoo! You got 'cat' right!", the LLM interprets this as "information about what to say" rather than "exact text to speak", and reformulates it based on the agent's instructions to be "encouraging and patient."

This creates a disconnect between the carefully crafted child-friendly responses in the code and what the child actually hears.

## Solution Statement

Implement a **direct text-to-speech bypass** that circumvents LLM reformulation entirely. Instead of returning text from function tools and relying on the LLM to deliver it, we will:

1. Use LiveKit's `session.say()` method to speak responses directly to the child
2. Modify the `spell_word()` function to call `session.say()` with the child-friendly text before returning
3. Return a minimal acknowledgment (or empty string) from the function to prevent LLM from generating additional response
4. Lower LLM temperature to 0.1 to reduce creative reformulation for any remaining LLM-generated text

This approach ensures that the exact child-friendly text is spoken without any LLM intermediation.

## Steps to Reproduce

1. Start the agent in console mode:
   ```bash
   python -m spelling_tutor.agent_worker console
   ```

2. Type a correct spelling attempt for the first word (e.g., "mushrooms")

3. Observe the agent's response

4. Expected: "Woohoo! You got 'mushrooms' right, Emma! Ready for another one? Let's spell 'broccoli'!"

5. Actual: "Excellent work, Emma! You spelled 'mushrooms' perfectly! Now let's try the next word: 'broccoli'. Please spell it for me."

6. Notice the lack of variety, enthusiasm, and child-friendly language despite code having 12+ response variations

## Root Cause Analysis

### Architecture Flow

**Current (Broken) Flow:**
```
spell_word() returns "Woohoo! You got 'cat' right!"
    ↓
Agent LLM receives function return value
    ↓
LLM instructions: "Be encouraging and patient"
    ↓
LLM interprets: "I should celebrate their success"
    ↓
LLM reformulates: "Excellent work, Emma! You spelled 'cat' perfectly!"
    ↓
TTS speaks the reformulated (robotic) response
```

**Root Causes:**

1. **LLM Reformulation**: LiveKit's Agent framework treats function tool returns as **semantic information** not **exact speech text**. The LLM has discretion to reformulate based on agent instructions.

2. **Instruction Ambiguity**: Current instructions say "Be encouraging and patient" and "deliver it EXACTLY as written" - these are contradictory. The LLM prioritizes the personality instruction over the verbatim instruction.

3. **No Direct TTS Path**: The codebase doesn't use direct TTS methods that bypass LLM interpretation.

4. **High Temperature**: LLM temperature is set to 0.7, encouraging creative reformulation rather than faithful reproduction.

### Evidence

1. **Test Script Confirms Code is Correct**:
   - `test_child_friendly.py` shows 8 unique positive feedback variations
   - Code has "Woohoo", "Yay", "Boom" in `agent.py` lines 106, 116, 117, 129
   - `random.choice()` is used 7 times in `agent.py`

2. **User Confirmation**:
   - User pulled latest branch with commit `798cf51` (child-friendly responses)
   - User restarted agent in console mode
   - User still hears robotic responses

3. **Architecture Analysis**:
   - `agent_worker.py:119-147` creates `AgentSession` with LLM
   - `agent.py:58-69` sets agent instructions that guide LLM behavior
   - `agent.py:67` function tools return text that LLM can reformulate
   - No `session.say()` calls found in codebase (grep confirms)

## Relevant Files

Use these files to fix the bug:

### Core Files to Modify

- **`src/spelling_tutor/agent.py`** (lines 58-250)
  - Contains the `SpellingTutorAgent` class with `spell_word()` function tool
  - Currently returns child-friendly text that gets paraphrased by LLM
  - Need to add `session.say()` calls to bypass LLM reformulation
  - Contains all the child-friendly response variations (12 patterns for success, 6 for hints, 6 for failure recovery)

- **`src/spelling_tutor/agent_worker.py`** (lines 119-147)
  - Creates the `AgentSession` with LLM configuration
  - Currently sets `temperature=0.7` which encourages creative reformulation
  - Need to lower temperature to 0.1 for more faithful reproduction

- **`src/spelling_tutor/tutor_logic.py`** (lines 1-200)
  - Contains `SpellingTutor` class with phonics hint generation
  - Has positive feedback with 24 variations (lines 32-50)
  - This file is working correctly and doesn't need changes

### Test Files to Create/Modify

- **`tests/test_agent_responses.py`** (NEW FILE)
  - Integration test that verifies actual agent spoken responses
  - Must test in console mode or with mock LiveKit session
  - Should validate that child-friendly text is actually spoken, not paraphrased

- **`test_child_friendly.py`** (EXISTING - UPDATE)
  - Currently only tests code structure (random.choice, keywords)
  - Need to add integration test that runs actual agent and captures spoken output

### Reference Documentation

- **`docs/livekit_agents_framework.md`**
  - LiveKit Agents 1.2.14 framework documentation
  - Reference for proper session.say() usage patterns

- **`docs/livekit_plugins.md`** (lines 85-100)
  - Shows `session.generate_reply()` pattern
  - Need to research if `session.say()` exists or alternative direct TTS method

- **`specs/child-friendly-responses-spec.md`**
  - Original specification for child-friendly responses
  - Documents the 12 success patterns, 6 hint patterns, 6 failure patterns

### New Files

#### `tests/test_agent_integration.py`
- Integration test that starts agent in test mode
- Sends spelling attempts to agent
- Captures actual TTS output (or LLM-generated text before TTS)
- Asserts that child-friendly keywords appear in spoken responses
- Validates variety across multiple attempts

## Step by Step Tasks

### Task 1: Research LiveKit Session Direct TTS Methods

- Read LiveKit Agents documentation to find if `session.say()` or equivalent exists
- Check if `AgentSession` has methods to speak text directly without LLM
- Review `livekit.agents.AgentSession` API for direct TTS methods
- Search codebase examples for patterns of bypassing LLM for specific responses
- Document findings: What's the proper way to speak text directly in LiveKit Agents 1.2.14+?

**Expected Findings:**
- `session.say(text)` or `await session.speak(text)` method exists
- OR need to manually use TTS and publish audio track
- OR need to use `generate_reply()` with very specific instructions

### Task 2: Implement Direct TTS in spell_word() Function

**File: `src/spelling_tutor/agent.py`**

Modify the `spell_word()` function tool to speak responses directly:

- Store reference to `session` in `SpellingTutorAgent.__init__()` (it's available via `self.session`)
- In `spell_word()`, before returning, call direct TTS method to speak the response
- Options:
  - Option A: `await self.session.say(response)` if method exists
  - Option B: Manually use TTS to generate and publish audio
  - Option C: Use `generate_reply()` but with empty instructions so it just speaks the function return
- After speaking directly, return empty string or minimal acknowledgment to prevent LLM from adding more
- Test each response path (correct, hint, failure) to ensure all use direct TTS

**Key Changes:**
- Line 125: After `return random.choice(responses)` → call direct TTS first
- Line 133: After `return random.choice(completions)` → call direct TTS first
- Line 160: After `return random.choice(hint_deliveries)` → call direct TTS first
- Line 187: After `return random.choice(recoveries)` → call direct TTS first
- Line 244: After `greeting = random.choice(greetings)` → already uses generate_reply, keep as-is

### Task 3: Lower LLM Temperature for Faithful Reproduction

**File: `src/spelling_tutor/agent_worker.py`**

Reduce LLM temperature to minimize creative reformulation:

- Line 130: Change `temperature=0.7` to `temperature=0.1`
- Add comment explaining why: "Low temperature to minimize paraphrasing of function responses"
- This ensures that if LLM still generates any text, it's more faithful to function returns

### Task 4: Update Agent Instructions for Clarity

**File: `src/spelling_tutor/agent.py`**

Simplify agent instructions now that we're using direct TTS:

- Lines 59-68: Simplify instructions since function now speaks directly
- Remove "CRITICAL: deliver it EXACTLY as written" (no longer relevant)
- Add: "When spell_word is called, it will speak directly to the child. Do not repeat or paraphrase what it says."
- Keep: "Wait for the user to respond before calling any functions."

### Task 5: Create Integration Test for Actual Spoken Responses

**New File: `tests/test_agent_integration.py`**

Create an integration test that validates actual agent behavior:

```python
"""
Integration test for agent responses.
Tests that child-friendly responses are actually delivered, not paraphrased.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from spelling_tutor.agent import SpellingTutorAgent

@pytest.mark.asyncio
async def test_agent_delivers_child_friendly_responses():
    """Test that agent speaks child-friendly text, not robotic paraphrases."""

    # Mock LiveKit session and capture what's spoken
    spoken_texts = []

    async def mock_say(text):
        spoken_texts.append(text)

    # Create agent with mocked session
    agent = SpellingTutorAgent(child_id=1, word_list_name='week1')
    agent.session = Mock()
    agent.session.say = AsyncMock(side_effect=mock_say)

    # Mock RunContext
    ctx = Mock()

    # Test correct spelling response
    response = await agent.spell_word(ctx, 'mushrooms')

    # Assert child-friendly keywords appear in spoken text
    spoken = ' '.join(spoken_texts)
    child_friendly_words = ['Woohoo', 'Yay', 'Boom', 'Amazing', 'Yes!', 'Sweet']
    assert any(word in spoken for word in child_friendly_words), \
        f"Expected child-friendly words, got: {spoken}"

    # Assert NOT robotic phrases
    robotic_phrases = ['Excellent work', 'spelled perfectly', 'Please spell']
    assert not any(phrase in spoken for phrase in robotic_phrases), \
        f"Found robotic phrase in: {spoken}"

@pytest.mark.asyncio
async def test_response_variety_across_multiple_words():
    """Test that responses vary across multiple correct spellings."""

    spoken_texts = []

    async def mock_say(text):
        spoken_texts.append(text)

    agent = SpellingTutorAgent(child_id=1, word_list_name='week1')
    agent.session = Mock()
    agent.session.say = AsyncMock(side_effect=mock_say)

    ctx = Mock()

    # Get first 3 words correct
    for i in range(3):
        word = agent.current_word.word
        await agent.spell_word(ctx, word)

    # Check for variety (should have different responses)
    unique_responses = set(spoken_texts)
    assert len(unique_responses) >= 2, \
        f"Expected variety in responses, got same response {len(unique_responses)} times"
```

### Task 6: Update Existing Test Script

**File: `test_child_friendly.py`**

Add a note to the test script explaining what it validates:

- Add comment at top: "This script validates code structure only. For actual spoken response testing, run: pytest tests/test_agent_integration.py"
- Add a 4th test section that checks for `session.say` calls in agent.py
- Update final output to recommend running integration test

### Task 7: Manual Console Testing

After implementing fix, perform manual testing:

1. Start agent: `python -m spelling_tutor.agent_worker console`
2. Type correct spelling for 5 words in a row
3. Listen/observe for varied, enthusiastic responses
4. Verify you hear "Woohoo!", "Yay!", "Boom!" at least once
5. Verify responses don't all sound identical
6. Test hint scenarios (intentionally misspell) to verify hint variety
7. Document sample responses in testing notes

### Task 8: Run All Validation Commands

Execute validation commands to ensure fix works with zero regressions:

- Run unit tests: `pytest tests/ -v`
- Run integration test: `pytest tests/test_agent_integration.py -v`
- Run child-friendly test: `python test_child_friendly.py`
- Run console test manually and verify child-friendly responses
- Check for any errors or warnings in agent logs

## Validation Commands

Execute every command to validate the bug is fixed with zero regressions.

### Before Fix (Reproduce Bug)
```bash
# Start agent and reproduce bug
python -m spelling_tutor.agent_worker console
# Type correct spelling and observe robotic response
# Expected: "Excellent work, Emma! You spelled 'mushrooms' perfectly!"
```

### After Fix (Validate Solution)
```bash
# 1. Run unit tests (existing tests should still pass)
pytest tests/ -v

# 2. Run integration test (new test validates spoken responses)
pytest tests/test_agent_integration.py -v

# 3. Run child-friendly code structure test
python test_child_friendly.py

# 4. Manual console test - verify child-friendly responses
python -m spelling_tutor.agent_worker console
# Type correct spellings for 5 words
# Expected: Hear varied responses with "Woohoo!", "Yay!", "Boom!"
# Expected: Responses should feel enthusiastic and varied
# NOT expected: Robotic "Excellent work" repetition

# 5. Check agent logs for errors
# (Logs appear in terminal when running console mode)
# Should see no errors related to TTS or session.say()

# 6. Test hint scenarios
python -m spelling_tutor.agent_worker console
# Type incorrect spelling to trigger hint
# Expected: Hear varied hint deliveries like "Ooh, let me help!"
# NOT expected: Formal "Not quite! Let me help."

# 7. Test failure recovery
python -m spelling_tutor.agent_worker console
# Type incorrect spelling 3 times
# Expected: Hear warm failure recovery like "You tried so hard!"
# NOT expected: Formal "That's okay, the correct spelling is..."
```

### Regression Testing
```bash
# Ensure existing functionality still works
pytest tests/test_tutor_logic.py -v  # Phonics hints still work
pytest tests/test_database.py -v      # Database operations still work
pytest tests/test_word_manager.py -v  # Word management still works

# Type checking (if applicable)
# mypy src/spelling_tutor/agent.py

# No build step needed (Python project)
```

## Notes

### Key Insights

1. **LiveKit's LLM Layer is Not a Pass-Through**: Function tool returns are semantic information, not verbatim speech scripts. The LLM actively interprets and reformulates them.

2. **Temperature Matters**: Even with "EXACTLY as written" instructions, temperature=0.7 encourages creativity. Lower temperature helps but may not fully solve the issue.

3. **Direct TTS is the Solution**: The only reliable way to ensure exact text is spoken is to bypass the LLM layer entirely for responses that must be verbatim.

4. **Agent Instructions are LLM Personality**: Instructions like "Be encouraging and patient" shape how the LLM interprets function returns. They don't guarantee verbatim delivery.

### Alternative Solutions Considered

**Option A: Stronger Instructions (TRIED - FAILED)**
- Added "CRITICAL: deliver EXACTLY as written" to instructions
- Result: LLM still paraphrased because temperature was high and LLM prioritized personality over verbatim

**Option B: Return JSON with "speak_verbatim" flag (REJECTED)**
- Too complex, still relies on LLM to honor the flag
- No guarantee LLM follows the flag instruction

**Option C: Disable LLM entirely (REJECTED)**
- Would lose natural conversation flow for greetings and edge cases
- Too drastic, removes LLM benefits

**Option D: Direct TTS (SELECTED)**
- Most reliable: completely bypasses LLM reformulation
- Preserves LLM for non-critical interactions (greetings, error handling)
- Surgical fix: only affects response delivery, not logic

### Testing Strategy

The original `test_child_friendly.py` script was well-intentioned but insufficient:
- ✅ It validated code structure (keywords, random.choice usage)
- ❌ It didn't test actual runtime behavior (what LLM actually speaks)

The new integration test (`test_agent_integration.py`) fills this gap by:
- Mocking LiveKit session
- Capturing what's actually spoken via `session.say()`
- Asserting child-friendly keywords appear in spoken text
- Asserting robotic phrases do NOT appear

### Performance Considerations

- Direct TTS bypasses LLM processing, potentially reducing latency by 100-300ms
- Lower temperature (0.1 vs 0.7) may slightly reduce LLM processing time
- No additional API calls introduced (TTS was already being called)

### Maintainability

- This fix makes response generation more explicit and predictable
- Future developers will clearly see `session.say()` calls and understand exact text is spoken
- Less "magic" happening in the LLM black box
- Easier to debug response issues (check function returns, not LLM behavior)

### Future Enhancements

If this pattern works well, consider:
1. Creating a helper method `speak_directly(text)` to centralize direct TTS logic
2. Adding logging: "🗣️ Speaking directly: {text[:50]}..."
3. Measuring response latency before/after to quantify improvement
4. Applying same pattern to phonics hints if variety issues appear there
