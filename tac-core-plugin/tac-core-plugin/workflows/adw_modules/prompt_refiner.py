"""Self-Refine pattern for prompt improvement.

This module implements the Self-Refine pattern where prompts are iteratively
improved based on feedback from execution outcomes.

Pattern: FEEDBACK → GENERATE_SUGGESTIONS → APPLY → REFINE (repeat 3-5 iterations)
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


logger = logging.getLogger(__name__)


class PromptRefiner:
    """Implements Self-Refine pattern for continuous prompt improvement."""

    def __init__(self, repo_root: Path):
        """Initialize prompt refiner.

        Args:
            repo_root: Path to repository root
        """
        self.repo_root = repo_root
        self.prompts_dir = repo_root / ".tac" / "prompts"
        self.prompts_dir.mkdir(parents=True, exist_ok=True)

        self.refinement_history_file = self.prompts_dir / "refinement_history.json"

    def refine_prompt(
        self,
        prompt_id: str,
        current_prompt: str,
        feedback: Dict[str, Any],
        max_iterations: int = 3
    ) -> str:
        """Apply Self-Refine pattern to improve prompt.

        Args:
            prompt_id: Identifier for the prompt (e.g., "feature_planning")
            current_prompt: Current version of the prompt
            feedback: Feedback data from execution outcomes
            max_iterations: Max refinement iterations (default 3)

        Returns:
            Refined prompt text
        """
        # Load refinement history
        history = self._load_history(prompt_id)

        # Generate refinement suggestions based on feedback
        suggestions = self._generate_suggestions(feedback)

        if not suggestions:
            logger.info(f"No refinement suggestions for prompt {prompt_id}")
            return current_prompt  # No changes needed

        logger.info(f"Generated {len(suggestions)} refinement suggestions for {prompt_id}")

        # Apply refinements iteratively
        refined_prompt = current_prompt
        iterations = 0
        applied_suggestions = []

        while iterations < max_iterations and suggestions:
            # Apply top suggestion
            suggestion = suggestions[0]
            refined_prompt = self._apply_suggestion(refined_prompt, suggestion)

            # Record refinement
            applied_suggestions.append({
                "iteration": iterations + 1,
                "suggestion": suggestion,
                "timestamp": datetime.now().isoformat(),
            })

            iterations += 1
            suggestions = suggestions[1:]  # Move to next suggestion

        # Update history
        if prompt_id not in history.get("prompts", {}):
            history.setdefault("prompts", {})[prompt_id] = {
                "refinements": [],
                "version": 1
            }

        history["prompts"][prompt_id]["refinements"].extend(applied_suggestions)
        history["prompts"][prompt_id]["version"] += 1

        # Save updated history
        self._save_history(history)

        # Save refined prompt
        self._save_prompt_version(prompt_id, refined_prompt, history["prompts"][prompt_id]["version"])

        logger.info(
            f"Refined prompt {prompt_id}: applied {len(applied_suggestions)} suggestions "
            f"over {iterations} iterations"
        )

        return refined_prompt

    def _generate_suggestions(self, feedback: Dict[str, Any]) -> List[str]:
        """Generate refinement suggestions based on feedback.

        Feedback patterns → Prompt improvements:
        - Test failures → Add validation requirements
        - Review changes (logic) → Strengthen technical specs
        - Review changes (style) → Add style guidelines
        - Review changes (security) → Add security checklist
        - Deployment errors → Add deployment validation

        Args:
            feedback: Dict containing feedback data

        Returns:
            List of suggestion strings
        """
        suggestions = []

        # Test feedback
        test_failures = feedback.get("test_failures", [])
        if test_failures:
            if "auth" in test_failures:
                suggestions.append(
                    "Add explicit instruction: 'Include comprehensive authentication tests "
                    "covering login, logout, token validation, and permission checks.'"
                )
            if "api" in test_failures:
                suggestions.append(
                    "Add explicit instruction: 'Validate all API endpoints with tests for "
                    "success cases, error cases, and edge cases (empty data, invalid input).'"
                )
            if "database" in test_failures or "db" in test_failures:
                suggestions.append(
                    "Add explicit instruction: 'Test database operations including "
                    "transactions, rollbacks, and constraint validation.'"
                )

        # Review feedback
        review_changes = feedback.get("review_changes", [])
        if review_changes:
            if "logic" in review_changes:
                suggestions.append(
                    "Add section: '## Logic Verification\\n"
                    "Before implementation, trace through the logic flow and verify:\\n"
                    "- Edge cases are handled\\n"
                    "- Error conditions are covered\\n"
                    "- Business rules are correctly implemented'"
                )
            if "security" in review_changes:
                suggestions.append(
                    "Add section: '## Security Checklist\\n"
                    "- [ ] Input validation and sanitization\\n"
                    "- [ ] SQL injection prevention\\n"
                    "- [ ] XSS prevention\\n"
                    "- [ ] Authentication and authorization checks\\n"
                    "- [ ] Sensitive data protection'"
                )
            if "performance" in review_changes:
                suggestions.append(
                    "Add explicit instruction: 'Consider performance implications: "
                    "avoid N+1 queries, add database indexes where needed, "
                    "use caching for expensive operations.'"
                )
            if "testing" in review_changes:
                suggestions.append(
                    "Add explicit instruction: 'Write tests BEFORE implementation (TDD). "
                    "Ensure tests cover happy path, error cases, and edge cases.'"
                )
            if "refactor" in review_changes:
                suggestions.append(
                    "Add explicit instruction: 'Check for code duplication and extract "
                    "reusable functions/classes. Follow DRY principle.'"
                )
            if "style" in review_changes:
                suggestions.append(
                    "Add explicit instruction: 'Follow project coding conventions for "
                    "naming, formatting, and file organization. Run linter before committing.'"
                )

        # Deployment feedback
        if feedback.get("deployment_errors"):
            suggestions.append(
                "Add validation step: 'Before marking as complete, verify the change "
                "works in a production-like environment and check for environment-specific "
                "configuration requirements (env vars, secrets, external services).'"
            )

        # Low success rate (general)
        success_rate = feedback.get("success_rate", 1.0)
        if success_rate < 0.7:
            suggestions.append(
                "Add reminder: 'IMPORTANT: Read and understand existing code patterns "
                "before implementing. Follow established conventions in the codebase.'"
            )

        return suggestions

    def _apply_suggestion(self, prompt: str, suggestion: str) -> str:
        """Apply a suggestion to a prompt.

        Strategies:
        1. If suggestion starts with "Add section:", append to end
        2. If suggestion starts with "Add instruction:", insert after intro
        3. If suggestion starts with "Add reminder:", insert at top
        4. Otherwise, append to end

        Args:
            prompt: Current prompt text
            suggestion: Suggestion to apply

        Returns:
            Modified prompt text
        """
        if suggestion.startswith("Add section:"):
            # Extract section content
            section = suggestion.replace("Add section:", "").strip()
            return prompt + "\n\n" + section

        elif suggestion.startswith("Add explicit instruction:"):
            # Insert into instructions section
            instruction = suggestion.replace("Add explicit instruction:", "").strip()

            # Find "## Instructions" section
            if "## Instructions" in prompt:
                parts = prompt.split("## Instructions")
                before = parts[0]
                after = parts[1]

                # Insert at end of instructions section
                next_section = after.find("\n##")
                if next_section != -1:
                    instructions = after[:next_section]
                    rest = after[next_section:]
                    return before + "## Instructions" + instructions + f"\n- {instruction}\n" + rest
                else:
                    return before + "## Instructions" + after + f"\n- {instruction}\n"
            else:
                # No instructions section, create one
                return prompt + f"\n\n## Instructions\n\n- {instruction}\n"

        elif suggestion.startswith("Add reminder:"):
            # Insert at top (after title)
            reminder = suggestion.replace("Add reminder:", "").strip()

            # Find first heading
            lines = prompt.split("\n")
            for i, line in enumerate(lines):
                if line.startswith("# "):
                    # Insert after title
                    return "\n".join(lines[:i+1] + [f"\n**{reminder}**\n"] + lines[i+1:])

            # No title found, prepend
            return f"**{reminder}**\n\n" + prompt

        else:
            # Generic: append to end
            return prompt + "\n\n" + suggestion

    def _load_history(self, prompt_id: str) -> Dict[str, Any]:
        """Load refinement history.

        Args:
            prompt_id: Prompt identifier

        Returns:
            History dict
        """
        if not self.refinement_history_file.exists():
            return {"prompts": {}}

        try:
            with open(self.refinement_history_file) as f:
                data = json.load(f)

            if prompt_id not in data.get("prompts", {}):
                data.setdefault("prompts", {})[prompt_id] = {
                    "refinements": [],
                    "version": 1
                }

            return data
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Could not load refinement history: {e}")
            return {"prompts": {}}

    def _save_history(self, history: Dict[str, Any]) -> None:
        """Save refinement history.

        Args:
            history: History dict to save
        """
        try:
            with open(self.refinement_history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save refinement history: {e}")

    def _save_prompt_version(self, prompt_id: str, prompt: str, version: int) -> None:
        """Save a new version of a prompt.

        Args:
            prompt_id: Prompt identifier
            prompt: Prompt text
            version: Version number
        """
        # Save versioned file
        version_file = self.prompts_dir / f"{prompt_id}_v{version}.md"
        try:
            with open(version_file, 'w') as f:
                f.write(prompt)
            logger.debug(f"Saved prompt version: {version_file}")
        except Exception as e:
            logger.error(f"Failed to save prompt version: {e}")

        # Also save as latest
        latest_file = self.prompts_dir / f"{prompt_id}_latest.md"
        try:
            with open(latest_file, 'w') as f:
                f.write(prompt)
            logger.debug(f"Updated latest prompt: {latest_file}")
        except Exception as e:
            logger.error(f"Failed to save latest prompt: {e}")

    def get_refinement_stats(self, prompt_id: str) -> Dict[str, Any]:
        """Get refinement statistics for a prompt.

        Args:
            prompt_id: Prompt identifier

        Returns:
            Dict with refinement stats
        """
        history = self._load_history(prompt_id)

        if prompt_id not in history.get("prompts", {}):
            return {
                "total_refinements": 0,
                "current_version": 1,
                "last_refined": None,
            }

        prompt_history = history["prompts"][prompt_id]
        refinements = prompt_history.get("refinements", [])

        return {
            "total_refinements": len(refinements),
            "current_version": prompt_history.get("version", 1),
            "last_refined": refinements[-1]["timestamp"] if refinements else None,
            "recent_suggestions": [r["suggestion"][:100] + "..." for r in refinements[-3:]],
        }
