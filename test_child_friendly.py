#!/usr/bin/env python3
"""
Test script to verify child-friendly responses are working.
Run this to see if the variety and enthusiasm is present.

NOTE: This script validates code structure only.
For actual spoken response testing, run: pytest tests/test_agent_integration.py -v
"""

import random
from spelling_tutor.tutor_logic import SpellingTutor

def test_positive_feedback():
    """Test that positive feedback has variety."""
    print("=" * 60)
    print("TEST 1: Positive Feedback Variety")
    print("=" * 60)

    tutor = SpellingTutor('cat', 'easy', 'CVC')
    feedbacks = []

    for i in range(10):
        correct, feedback = tutor.check_spelling('cat')
        feedbacks.append(feedback)

    unique = set(feedbacks)
    print(f"\n✓ Generated {len(unique)} unique responses out of 10 attempts")
    print("\nSample responses:")
    for i, fb in enumerate(list(unique)[:5]):
        print(f"  {i+1}. {fb}")

    # Check for child-friendly words
    all_feedback = " ".join(feedbacks)
    child_words = ['amazing', 'awesome', 'great', 'super', 'love', 'proud']
    found = [w for w in child_words if w in all_feedback.lower()]
    print(f"\n✓ Found child-friendly words: {', '.join(found)}")

    return len(unique) >= 5  # Should have at least 5 variations

def test_hint_variety():
    """Test that hints have variety."""
    print("\n" + "=" * 60)
    print("TEST 2: Hint Variety")
    print("=" * 60)

    tutor = SpellingTutor('dog', 'easy', 'CVC')
    hints_attempt_1 = []
    hints_attempt_2 = []

    for i in range(5):
        tutor_test = SpellingTutor('dog', 'easy', 'CVC')
        hints_attempt_1.append(tutor_test.get_phonics_hint(1))
        hints_attempt_2.append(tutor_test.get_phonics_hint(2))

    unique_1 = set(hints_attempt_1)
    unique_2 = set(hints_attempt_2)

    print(f"\n✓ Attempt 1 hints: {len(unique_1)} unique variations")
    print("Sample:")
    for hint in list(unique_1)[:2]:
        print(f"  - {hint}")

    print(f"\n✓ Attempt 2 hints: {len(unique_2)} unique variations")
    print("Sample:")
    for hint in list(unique_2)[:2]:
        print(f"  - {hint}")

    return len(unique_1) >= 2 and len(unique_2) >= 2

def test_agent_responses():
    """Test that agent.py has varied responses defined."""
    print("\n" + "=" * 60)
    print("TEST 3: Agent Response Templates")
    print("=" * 60)

    with open('src/spelling_tutor/agent.py', 'r') as f:
        content = f.read()

    # Check for child-friendly words
    child_words = ['Woohoo', 'Yay', 'Boom', 'Amazing']
    found = [w for w in child_words if w in content]

    print(f"\n✓ Found {len(found)} child-friendly exclamations in agent.py:")
    for word in found:
        print(f"  - {word}")

    # Check for random.choice usage
    random_choices = content.count('random.choice')
    print(f"\n✓ Agent uses random.choice {random_choices} times (for variety)")

    # Check for session.say() calls (direct TTS)
    has_session_say = 'session.say(' in content
    session_say_count = content.count('await self.session.say(')
    print(f"\n✓ Uses session.say() for direct TTS: {has_session_say}")
    print(f"  - Found {session_say_count} direct TTS calls")

    if not has_session_say:
        print("\n⚠ WARNING: The agent might paraphrase responses!")
        print("  Not using session.say() to bypass LLM reformulation.")

    return len(found) >= 3 and random_choices >= 5 and has_session_say

if __name__ == '__main__':
    print("\n🧪 Testing Child-Friendly Response System\n")

    results = []
    results.append(("Positive Feedback Variety", test_positive_feedback()))
    results.append(("Hint Variety", test_hint_variety()))
    results.append(("Agent Response Templates", test_agent_responses()))

    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests PASSED!")
        print("\nThe child-friendly responses are properly implemented.")
        print("Code structure validates correctly.")
        print("\n📋 Next Steps:")
        print("1. Run integration tests: pytest tests/test_agent_integration.py -v")
        print("2. Test manually: python -m spelling_tutor.agent_worker console")
        print("\nExpected child-friendly responses:")
        print('  - "Woohoo! You got \'cat\' right!"')
        print('  - "Yay! Perfect spelling!"')
        print('  - "Boom! You nailed it!"')
    else:
        print("❌ Some tests FAILED")
        print("Review the output above for details.")
    print("=" * 60 + "\n")
