"""
TAC Integration Module

This module bridges TAC (The Agentic Coder) principles with ADW workflows.
It provides utilities for:
- Knowledge gap identification
- Spec-first validation
- Closed-loop validation
- Agent-perspective transformations

TAC Principles Implemented:
1. Spec-First Development
2. Knowledge Gap Pre-Fill
3. Agent Perspective
4. Closed-Loop Validation
5. Template Engineering
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
import subprocess

from .data_types import IssueData, PlanSpec


@dataclass
class KnowledgeGap:
    """Represents a knowledge gap that needs filling before work"""
    category: str  # "framework", "project", "external", "domain"
    description: str
    impact: str  # "critical", "high", "medium", "low"
    how_to_fill: str
    required: bool = True


@dataclass
class ValidationResult:
    """Result of a validation check"""
    passed: bool
    checklist_type: str  # "feature", "bug", "chore"
    completed_items: List[str]
    failed_items: List[str]
    warnings: List[str]


class TACIntegration:
    """
    Integrates TAC principles into ADW workflows.

    This class provides methods to enforce TAC best practices
    throughout the ADW lifecycle.
    """

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.claude_dir = self.project_root / ".claude"
        self.specs_dir = self.claude_dir / "specs"
        self.validation_dir = self.claude_dir / "validation-checklists"

    # =================================================================
    # Principle 1: Spec-First Development
    # =================================================================

    def ensure_spec_exists(self, issue_data: IssueData) -> Tuple[bool, Optional[Path]]:
        """
        Verify that a spec exists for the given issue.

        Returns:
            (spec_exists, spec_path)
        """
        issue_type = self._classify_issue_type(issue_data)
        potential_specs = [
            self.specs_dir / f"{issue_type}-{issue_data.number}.md",
            self.specs_dir / f"{issue_type}-{self._slugify(issue_data.title)}.md",
        ]

        for spec_path in potential_specs:
            if spec_path.exists():
                return True, spec_path

        return False, None

    def validate_spec_ai_executable(self, spec_path: Path) -> Dict[str, bool]:
        """
        Validate that a spec is AI-executable according to TAC principles.

        Checks for:
        - Explicit context
        - Clear objective
        - Success criteria
        - Validation commands
        - Phase breakdown
        - No ambiguity
        """
        if not spec_path.exists():
            return {"valid": False, "reason": "Spec file not found"}

        with open(spec_path, 'r') as f:
            content = f.read()

        checks = {
            "has_objective": "## Objective" in content or "# Objective" in content,
            "has_success_criteria": "## Success Criteria" in content or "success criteria" in content.lower(),
            "has_validation": "```bash" in content or "validation" in content.lower(),
            "has_phases": "## Phase" in content or "### Phase" in content or "## Implementation Plan" in content,
            "has_context": "## Context" in content or "## Background" in content,
        }

        checks["valid"] = all(checks.values())
        return checks

    # =================================================================
    # Principle 2: Knowledge Gap Pre-Fill
    # =================================================================

    def identify_knowledge_gaps(self, issue_data: IssueData) -> List[KnowledgeGap]:
        """
        Identify potential knowledge gaps based on issue content.

        This is a heuristic-based approach. For more sophisticated gap detection,
        use the /knowledge_gap_check command directly.
        """
        gaps = []

        # Check for framework/library mentions
        common_frameworks = [
            "react", "vue", "angular", "next.js", "fastapi", "django",
            "express", "flask", "rails", "spring"
        ]

        issue_text = f"{issue_data.title} {issue_data.body}".lower()

        for framework in common_frameworks:
            if framework in issue_text:
                gaps.append(KnowledgeGap(
                    category="framework",
                    description=f"Latest {framework} patterns and best practices",
                    impact="high",
                    how_to_fill=f"Connect to official {framework} docs via MCP (Archon)",
                    required=True
                ))

        # Check for project context
        project_context_path = self.claude_dir / "CLAUDE.md"
        if not project_context_path.exists():
            gaps.append(KnowledgeGap(
                category="project",
                description="Project context file missing",
                impact="critical",
                how_to_fill='Create CLAUDE.md "Project-Specific Context" section with project details',
                required=True
            ))

        # Check for API mentions
        if any(keyword in issue_text for keyword in ["api", "endpoint", "integration"]):
            gaps.append(KnowledgeGap(
                category="external",
                description="External API documentation and authentication patterns",
                impact="medium",
                how_to_fill="Provide API documentation or connect to API docs via MCP",
                required=False
            ))

        return gaps

    def load_project_context(self) -> Optional[Dict]:
        """
        Load project context from CLAUDE.md "Project-Specific Context" section

        Returns structured data if available, None otherwise.
        """
        context_path = self.claude_dir / "CLAUDE.md"

        if not context_path.exists():
            return None

        # For now, return simple dict indicating it exists
        # In future, could parse markdown into structured data
        return {
            "path": str(context_path),
            "exists": True
        }

    # =================================================================
    # Principle 3: Agent Perspective
    # =================================================================

    def transform_to_agent_perspective(self, human_request: str) -> str:
        """
        Transform human-centric request to agent-centric specification.

        Converts vague requests into structured, actionable specs.
        """
        # This is a simplified version. In practice, this would be done
        # by the AI agent itself using the /spec command.

        template = f"""# Task Specification (Agent Perspective)

## Objective
{human_request}

## Context Required
- Project: [From CLAUDE.md "Project-Specific Context" section]
- Tech Stack: [From CLAUDE.md]
- Related Work: [Check git log for similar work]

## Success Criteria (AI: Make these measurable)
- [ ] [Criterion 1 - must be testable]
- [ ] [Criterion 2 - must be testable]
- [ ] [Criterion 3 - must be testable]

## Validation Commands (AI: Specify exact commands)
```bash
# Tests that must pass
npm test

# Additional validation
[specific command here]
```

## Implementation Phases (AI: Break into concrete steps)
### Phase 1: [Name]
1. [Specific action with validation]

### Phase 2: [Name]
1. [Specific action with validation]
"""
        return template

    # =================================================================
    # Principle 4: Closed-Loop Validation
    # =================================================================

    def get_validation_checklist(self, issue_type: str) -> Optional[Path]:
        """
        Get the appropriate validation checklist for issue type.

        Args:
            issue_type: "feature", "bug", or "chore"

        Returns:
            Path to validation checklist file
        """
        checklist_map = {
            "feature": "feature-validation.md",
            "bug": "bug-validation.md",
            "chore": "chore-validation.md",
        }

        checklist_name = checklist_map.get(issue_type)
        if not checklist_name:
            return None

        checklist_path = self.validation_dir / checklist_name
        return checklist_path if checklist_path.exists() else None

    def validate_against_checklist(
        self,
        issue_type: str,
        working_dir: Optional[Path] = None
    ) -> ValidationResult:
        """
        Validate work against the appropriate checklist.

        Runs automated validation commands from the checklist.
        This is a simplified version - in practice, the AI agent
        would work through the checklist interactively.
        """
        cwd = working_dir or self.project_root

        # Common validation commands
        validation_commands = {
            "lint": ["npm", "run", "lint"],
            "test": ["npm", "test"],
            "build": ["npm", "run", "build"],
            "type-check": ["npm", "run", "type-check"],
        }

        completed = []
        failed = []
        warnings = []

        for check_name, command in validation_commands.items():
            try:
                result = subprocess.run(
                    command,
                    cwd=str(cwd),
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )

                if result.returncode == 0:
                    completed.append(f"{check_name}: passed")
                else:
                    failed.append(f"{check_name}: failed")

            except subprocess.TimeoutExpired:
                warnings.append(f"{check_name}: timeout")
            except FileNotFoundError:
                warnings.append(f"{check_name}: command not found")
            except Exception as e:
                warnings.append(f"{check_name}: error - {str(e)}")

        return ValidationResult(
            passed=len(failed) == 0,
            checklist_type=issue_type,
            completed_items=completed,
            failed_items=failed,
            warnings=warnings
        )

    # =================================================================
    # Principle 5: Template Engineering
    # =================================================================

    def get_spec_template(self, issue_type: str) -> Optional[str]:
        """
        Get the appropriate spec template for issue type.

        Templates are loaded from the /spec command documentation.
        """
        # In practice, these would be separate template files
        # For now, return indicator that template should come from /spec command
        template_map = {
            "feature": "Use /spec command with feature template",
            "bug": "Use /spec command with bug template",
            "chore": "Use /spec command with chore template",
        }

        return template_map.get(issue_type)

    def get_adw_workflow_for_issue(self, issue_data: IssueData) -> str:
        """
        Recommend appropriate ADW workflow based on issue characteristics.

        Maps TAC principles to ADW orchestrators.
        """
        issue_type = self._classify_issue_type(issue_data)

        # Map issue types to ADW workflows
        workflow_map = {
            "feature": "adw_plan_build_test_review_iso.py",  # Full validation
            "bug": "adw_plan_build_test_iso.py",  # Quick fix + test
            "chore": "adw_plan_build_iso.py",  # Minimal validation
        }

        # Check for zero-touch flag
        body_lower = issue_data.body.lower()
        if "zero-touch" in body_lower or "auto-ship" in body_lower:
            return "adw_sdlc_zte_iso.py"

        # Check for priority/urgency
        if any(label in ["urgent", "hotfix", "critical"] for label in issue_data.labels):
            return "adw_patch_iso.py"

        return workflow_map.get(issue_type, "adw_plan_build_test_review_iso.py")

    # =================================================================
    # Integration with ADW Workflows
    # =================================================================

    def enhance_plan_spec_with_tac(self, plan_spec: PlanSpec) -> PlanSpec:
        """
        Enhance an ADW PlanSpec with TAC principles.

        Adds:
        - Knowledge gap check results
        - Validation checklist reference
        - Agent-perspective formatting
        """
        # Add knowledge gap info to plan
        gaps = self.identify_knowledge_gaps(IssueData(
            number=0,  # Placeholder
            title=plan_spec.objective,
            body=plan_spec.approach or "",
            labels=[]
        ))

        # Add to plan notes or approach
        if gaps:
            gap_section = "\n\n## Knowledge Gaps to Address\n"
            for gap in gaps:
                gap_section += f"- [{gap.category}] {gap.description}\n"
                gap_section += f"  - How to fill: {gap.how_to_fill}\n"

            plan_spec.approach = (plan_spec.approach or "") + gap_section

        return plan_spec

    # =================================================================
    # Helper Methods
    # =================================================================

    def _classify_issue_type(self, issue_data: IssueData) -> str:
        """
        Classify issue as feature, bug, or chore.
        """
        # Check labels first
        for label in issue_data.labels:
            label_lower = label.lower()
            if any(kw in label_lower for kw in ["feature", "enhancement", "feat"]):
                return "feature"
            if any(kw in label_lower for kw in ["bug", "fix", "defect"]):
                return "bug"
            if any(kw in label_lower for kw in ["chore", "refactor", "maintenance"]):
                return "chore"

        # Check title
        title_lower = issue_data.title.lower()
        if title_lower.startswith(("feat:", "feature:")):
            return "feature"
        if title_lower.startswith(("fix:", "bug:")):
            return "bug"
        if title_lower.startswith(("chore:", "refactor:")):
            return "chore"

        # Default to feature
        return "feature"

    def _slugify(self, text: str) -> str:
        """Convert text to slug format"""
        return text.lower().replace(" ", "-").replace("_", "-")[:50]


# =================================================================
# Convenience Functions for ADW Workflows
# =================================================================

def apply_tac_to_plan(
    issue_data: IssueData,
    plan_spec: PlanSpec,
    project_root: Path
) -> Tuple[PlanSpec, List[KnowledgeGap]]:
    """
    Apply TAC principles to an ADW planning phase.

    Returns:
        (enhanced_plan_spec, knowledge_gaps)
    """
    tac = TACIntegration(project_root)

    # Identify knowledge gaps
    gaps = tac.identify_knowledge_gaps(issue_data)

    # Enhance plan with TAC principles
    enhanced_plan = tac.enhance_plan_spec_with_tac(plan_spec)

    return enhanced_plan, gaps


def apply_tac_to_test(
    issue_type: str,
    project_root: Path,
    working_dir: Optional[Path] = None
) -> ValidationResult:
    """
    Apply TAC validation principles to ADW testing phase.

    Returns:
        ValidationResult with pass/fail status
    """
    tac = TACIntegration(project_root)
    return tac.validate_against_checklist(issue_type, working_dir)


def apply_tac_to_review(
    issue_type: str,
    project_root: Path
) -> Optional[Path]:
    """
    Get TAC validation checklist for ADW review phase.

    Returns:
        Path to appropriate checklist
    """
    tac = TACIntegration(project_root)
    return tac.get_validation_checklist(issue_type)


def select_adw_workflow_with_tac(issue_data: IssueData, project_root: Path) -> str:
    """
    Select appropriate ADW workflow using TAC principles.

    Returns:
        Name of ADW workflow script to use
    """
    tac = TACIntegration(project_root)
    return tac.get_adw_workflow_for_issue(issue_data)
