"""
Test suite for SDLC documentation completeness.

This test validates that the Simple Task SDLC documentation is complete,
well-structured, and all referenced files exist.
"""

import os
from pathlib import Path


def test_sdlc_documentation_exists():
    """Test that the main SDLC documentation file exists."""
    docs_path = Path(__file__).parent.parent / "docs" / "SIMPLE_TASK_SDLC.md"
    assert docs_path.exists(), "docs/SIMPLE_TASK_SDLC.md does not exist"
    assert docs_path.is_file(), "docs/SIMPLE_TASK_SDLC.md is not a file"


def test_sdlc_documentation_not_empty():
    """Test that the SDLC documentation has content."""
    docs_path = Path(__file__).parent.parent / "docs" / "SIMPLE_TASK_SDLC.md"
    content = docs_path.read_text()
    assert len(content) > 0, "docs/SIMPLE_TASK_SDLC.md is empty"
    assert len(content) > 5000, "docs/SIMPLE_TASK_SDLC.md seems too short (< 5000 chars)"


def test_sdlc_documentation_has_required_sections():
    """Test that all required sections are present in the documentation."""
    docs_path = Path(__file__).parent.parent / "docs" / "SIMPLE_TASK_SDLC.md"
    content = docs_path.read_text()

    required_sections = [
        "# Simple Task SDLC Framework",
        "## Introduction",
        "## Process Overview",
        "## Stage 1: Planning",
        "## Stage 2: Implementation",
        "## Stage 3: Testing",
        "## Stage 4: Review",
        "## Stage 5: Deployment",
        "## Integration with ADW",
        "## Decision Guide",
        "## Task Type Templates",
        "## Examples",
        "## Quick Reference",
        "## Common Pitfalls",
    ]

    for section in required_sections:
        assert section in content, f"Required section '{section}' not found in SDLC documentation"


def test_sdlc_documentation_has_quality_gates():
    """Test that quality gates are defined for each stage."""
    docs_path = Path(__file__).parent.parent / "docs" / "SIMPLE_TASK_SDLC.md"
    content = docs_path.read_text()

    # Each stage should have a quality gate
    quality_gate_keywords = [
        "Quality Gate",
        "Pass Criteria",
        "Fail Actions",
    ]

    for keyword in quality_gate_keywords:
        assert keyword in content, f"Quality gate keyword '{keyword}' not found in documentation"


def test_bug_fix_template_exists():
    """Test that the bug fix template exists."""
    template_path = Path(__file__).parent.parent / "docs" / "templates" / "simple-bug-fix-template.md"
    assert template_path.exists(), "docs/templates/simple-bug-fix-template.md does not exist"
    assert template_path.is_file(), "Bug fix template is not a file"


def test_bug_fix_template_not_empty():
    """Test that the bug fix template has content."""
    template_path = Path(__file__).parent.parent / "docs" / "templates" / "simple-bug-fix-template.md"
    content = template_path.read_text()
    assert len(content) > 0, "Bug fix template is empty"
    assert len(content) > 1000, "Bug fix template seems too short"


def test_bug_fix_template_has_required_sections():
    """Test that the bug fix template has all required sections."""
    template_path = Path(__file__).parent.parent / "docs" / "templates" / "simple-bug-fix-template.md"
    content = template_path.read_text()

    required_sections = [
        "# Simple Bug Fix Template",
        "## Stage 1: Planning",
        "## Stage 2: Implementation",
        "## Stage 3: Testing",
        "## Stage 4: Review",
        "## Stage 5: Deployment",
        "### Problem Description",
        "### Reproduction Steps",
        "### Root Cause Analysis",
        "### Solution Approach",
        "### Acceptance Criteria",
    ]

    for section in required_sections:
        assert section in content, f"Required section '{section}' not found in bug fix template"


def test_feature_template_exists():
    """Test that the feature template exists."""
    template_path = Path(__file__).parent.parent / "docs" / "templates" / "simple-feature-template.md"
    assert template_path.exists(), "docs/templates/simple-feature-template.md does not exist"
    assert template_path.is_file(), "Feature template is not a file"


def test_feature_template_not_empty():
    """Test that the feature template has content."""
    template_path = Path(__file__).parent.parent / "docs" / "templates" / "simple-feature-template.md"
    content = template_path.read_text()
    assert len(content) > 0, "Feature template is empty"
    assert len(content) > 1000, "Feature template seems too short"


def test_feature_template_has_required_sections():
    """Test that the feature template has all required sections."""
    template_path = Path(__file__).parent.parent / "docs" / "templates" / "simple-feature-template.md"
    content = template_path.read_text()

    required_sections = [
        "# Simple Feature Template",
        "## Stage 1: Planning",
        "## Stage 2: Implementation",
        "## Stage 3: Testing",
        "## Stage 4: Review",
        "## Stage 5: Deployment",
        "### Goal",
        "### User Story",
        "### Solution Approach",
        "### Scope",
        "### Acceptance Criteria",
    ]

    for section in required_sections:
        assert section in content, f"Required section '{section}' not found in feature template"


def test_chore_template_exists():
    """Test that the chore template exists."""
    template_path = Path(__file__).parent.parent / "docs" / "templates" / "simple-chore-template.md"
    assert template_path.exists(), "docs/templates/simple-chore-template.md does not exist"
    assert template_path.is_file(), "Chore template is not a file"


def test_chore_template_not_empty():
    """Test that the chore template has content."""
    template_path = Path(__file__).parent.parent / "docs" / "templates" / "simple-chore-template.md"
    content = template_path.read_text()
    assert len(content) > 0, "Chore template is empty"
    assert len(content) > 1000, "Chore template seems too short"


def test_chore_template_has_required_sections():
    """Test that the chore template has all required sections."""
    template_path = Path(__file__).parent.parent / "docs" / "templates" / "simple-chore-template.md"
    content = template_path.read_text()

    required_sections = [
        "# Simple Chore Template",
        "## Stage 1: Planning",
        "## Stage 2: Implementation",
        "## Stage 3: Testing",
        "## Stage 4: Review",
        "## Stage 5: Deployment",
        "### Objective",
        "### Rationale",
        "### Scope",
        "### Success Criteria",
    ]

    for section in required_sections:
        assert section in content, f"Required section '{section}' not found in chore template"


def test_readme_links_to_sdlc_documentation():
    """Test that README.md links to the SDLC documentation."""
    readme_path = Path(__file__).parent.parent / "README.md"
    content = readme_path.read_text()

    assert "docs/SIMPLE_TASK_SDLC.md" in content, "README.md does not link to SDLC documentation"
    assert "Development Workflow" in content or "SDLC" in content, \
        "README.md does not mention SDLC or development workflow"


def test_adw_readme_references_sdlc_documentation():
    """Test that adw/README.md references the SDLC documentation."""
    adw_readme_path = Path(__file__).parent.parent / "adw" / "README.md"
    content = adw_readme_path.read_text()

    assert "docs/SIMPLE_TASK_SDLC.md" in content or "SIMPLE_TASK_SDLC" in content, \
        "adw/README.md does not reference SDLC documentation"


def test_templates_directory_exists():
    """Test that the templates directory exists."""
    templates_dir = Path(__file__).parent.parent / "docs" / "templates"
    assert templates_dir.exists(), "docs/templates/ directory does not exist"
    assert templates_dir.is_dir(), "docs/templates/ is not a directory"


def test_all_three_templates_exist():
    """Test that all three task type templates exist."""
    templates_dir = Path(__file__).parent.parent / "docs" / "templates"

    expected_templates = [
        "simple-bug-fix-template.md",
        "simple-feature-template.md",
        "simple-chore-template.md",
    ]

    for template_name in expected_templates:
        template_path = templates_dir / template_name
        assert template_path.exists(), f"Template {template_name} does not exist"


def test_sdlc_documentation_has_validation_commands():
    """Test that SDLC documentation includes validation commands."""
    docs_path = Path(__file__).parent.parent / "docs" / "SIMPLE_TASK_SDLC.md"
    content = docs_path.read_text()

    # Should include common validation commands
    validation_keywords = [
        "pytest",
        "bun tsc",
        "bun run build",
        "Validation Commands",
    ]

    for keyword in validation_keywords:
        assert keyword in content, f"Validation keyword '{keyword}' not found in documentation"


def test_sdlc_documentation_has_adw_integration():
    """Test that SDLC documentation explains ADW integration."""
    docs_path = Path(__file__).parent.parent / "docs" / "SIMPLE_TASK_SDLC.md"
    content = docs_path.read_text()

    # Should explain ADW workflows
    adw_keywords = [
        "adw_plan_iso",
        "adw_build_iso",
        "adw_test_iso",
        "adw_review_iso",
        "adw_sdlc_iso",
        "ADW Integration",
        "Automated",
        "Manual",
    ]

    for keyword in adw_keywords:
        assert keyword in content, f"ADW keyword '{keyword}' not found in documentation"


def test_sdlc_documentation_has_examples():
    """Test that SDLC documentation includes practical examples."""
    docs_path = Path(__file__).parent.parent / "docs" / "SIMPLE_TASK_SDLC.md"
    content = docs_path.read_text()

    # Should have example sections
    assert "## Examples" in content, "Examples section not found"
    assert "Example" in content, "No examples found in documentation"


def test_sdlc_documentation_has_decision_trees():
    """Test that SDLC documentation includes decision guidance."""
    docs_path = Path(__file__).parent.parent / "docs" / "SIMPLE_TASK_SDLC.md"
    content = docs_path.read_text()

    # Should help users decide which approach to use
    decision_keywords = [
        "Decision",
        "When to Use",
        "Should I",
    ]

    found_count = sum(1 for keyword in decision_keywords if keyword in content)
    assert found_count >= 1, "No decision guidance found in documentation"


def test_sdlc_documentation_word_count():
    """Test that SDLC documentation is comprehensive (minimum word count)."""
    docs_path = Path(__file__).parent.parent / "docs" / "SIMPLE_TASK_SDLC.md"
    content = docs_path.read_text()

    # Count words (rough estimate)
    word_count = len(content.split())

    # Should be substantial documentation (minimum 3000 words for comprehensive guide)
    assert word_count >= 3000, f"SDLC documentation seems incomplete (only {word_count} words, expected >= 3000)"


def test_templates_consistency():
    """Test that all templates follow consistent structure."""
    templates_dir = Path(__file__).parent.parent / "docs" / "templates"

    template_files = [
        "simple-bug-fix-template.md",
        "simple-feature-template.md",
        "simple-chore-template.md",
    ]

    # Each template should have all 5 stages
    required_stages = [
        "## Stage 1: Planning",
        "## Stage 2: Implementation",
        "## Stage 3: Testing",
        "## Stage 4: Review",
        "## Stage 5: Deployment",
    ]

    for template_file in template_files:
        template_path = templates_dir / template_file
        content = template_path.read_text()

        for stage in required_stages:
            assert stage in content, f"{template_file} missing {stage}"


def test_no_broken_internal_links():
    """Test that internal documentation links are valid."""
    docs_path = Path(__file__).parent.parent / "docs" / "SIMPLE_TASK_SDLC.md"
    content = docs_path.read_text()

    # Find markdown links to local files: [text](path)
    import re
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(link_pattern, content)

    base_dir = Path(__file__).parent.parent

    for link_text, link_path in matches:
        # Only check local file links (not URLs)
        if not link_path.startswith('http') and not link_path.startswith('#'):
            # Handle relative paths
            if link_path.startswith('.'):
                # Relative to docs directory
                full_path = (base_dir / "docs" / link_path.lstrip('./')).resolve()
            else:
                # Absolute from repo root
                full_path = (base_dir / link_path).resolve()

            # Check if target exists (allow both files and directories)
            if not full_path.exists():
                # Some links might be in format: .claude/commands/ (directory reference)
                # Only fail if it's clearly a file reference (.md extension)
                if link_path.endswith('.md'):
                    assert False, f"Broken link in SDLC docs: [{link_text}]({link_path}) -> {full_path} does not exist"
