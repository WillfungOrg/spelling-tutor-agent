"""Enhanced Learning Extraction - Deep analysis of code changes for actionable insights.

This module analyzes git diffs, error patterns, and code changes to extract
truly actionable learnings that help improve future deployments.
"""

import re
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict


def analyze_git_diffs(commits: List[Dict[str, Any]], repo_path: Path) -> Dict[str, Any]:
    """Analyze git diffs to understand actual code changes.

    Args:
        commits: List of commit dicts from git history
        repo_path: Repository path

    Returns:
        Dict with detailed change analysis
    """
    if not commits or len(commits) < 2:
        return {
            "errors_fixed": [],
            "schema_changes": [],
            "api_changes": [],
            "imports_added": [],
            "functions_modified": [],
            "error_handling_added": [],
        }

    # Get unified diff for all changes
    oldest_commit = commits[-1]["hash"]
    newest_commit = commits[0]["hash"]

    cmd_diff = ["git", "diff", f"{oldest_commit}^", newest_commit]
    result = subprocess.run(cmd_diff, cwd=repo_path, capture_output=True, text=True, timeout=30)

    if result.returncode != 0:
        return {"error": "Could not get git diff"}

    diff_text = result.stdout

    # Analyze the diff
    analysis = {
        "errors_fixed": extract_errors_from_diff(diff_text),
        "schema_changes": detect_schema_changes(diff_text),
        "api_changes": detect_api_changes(diff_text),
        "imports_added": extract_imports_added(diff_text),
        "functions_modified": extract_functions_modified(diff_text),
        "error_handling_added": detect_error_handling(diff_text),
        "type_fixes": detect_type_fixes(diff_text),
        "defensive_coding": detect_defensive_coding_patterns(diff_text),
    }

    return analysis


def extract_errors_from_diff(diff_text: str) -> List[Dict[str, str]]:
    """Extract error patterns that were fixed from diff.

    Looks for:
    - Removed lines with error-prone patterns
    - Added lines that fix those patterns
    - Comments mentioning errors
    """
    errors_fixed = []

    # Pattern: AttributeError fixes (accessing None)
    # Look for: if xyz is not None (added) or xyz is None check (added)
    none_check_pattern = r'\+.*(?:if|and|or)\s+(\w+)\s+is\s+(?:not\s+)?None'
    for match in re.finditer(none_check_pattern, diff_text):
        var_name = match.group(1)
        errors_fixed.append({
            "type": "AttributeError",
            "pattern": f"Added None check for '{var_name}'",
            "fix": f"Check if {var_name} is None before accessing attributes",
            "preventive": True,
        })

    # Pattern: Type errors (wrong type assumptions)
    # Look for type conversions or type checks being added
    type_conversion_pattern = r'\+.*(?:int|float|str|list|dict|bool)\(([^)]+)\)'
    for match in re.finditer(type_conversion_pattern, diff_text):
        errors_fixed.append({
            "type": "TypeError",
            "pattern": f"Added type conversion: {match.group(0)[1:].strip()}",
            "fix": "Explicitly convert types instead of assuming",
            "preventive": True,
        })

    # Pattern: Dictionary .get() instead of direct access
    dict_get_pattern = r'\+.*\.get\(["\'](\w+)["\']\)'
    for match in re.finditer(dict_get_pattern, diff_text):
        key = match.group(1)
        errors_fixed.append({
            "type": "KeyError",
            "pattern": f"Use .get('{key}') instead of ['{key}']",
            "fix": "Use dict.get() for optional keys to avoid KeyError",
            "preventive": True,
        })

    # Pattern: Try-except blocks added
    try_except_pattern = r'\+\s*try:\s*\n(.*?\n)+?\+\s*except\s+(\w+)'
    for match in re.finditer(try_except_pattern, diff_text):
        exception_type = match.group(2)
        errors_fixed.append({
            "type": exception_type,
            "pattern": f"Added try-except for {exception_type}",
            "fix": f"Wrap risky operations in try-except {exception_type}",
            "preventive": True,
        })

    return errors_fixed


def detect_schema_changes(diff_text: str) -> List[Dict[str, str]]:
    """Detect schema/model changes from diff.

    Looks for:
    - Field additions to Pydantic models
    - Optional[] type annotations
    - Field removals
    """
    schema_changes = []

    # Pattern: Optional field additions
    optional_field_pattern = r'\+\s*(\w+):\s*Optional\[([^\]]+)\]'
    for match in re.finditer(optional_field_pattern, diff_text):
        field_name = match.group(1)
        field_type = match.group(2)
        schema_changes.append({
            "type": "field_addition",
            "field": field_name,
            "field_type": f"Optional[{field_type}]",
            "learning": f"Made {field_name} Optional to support multiple use cases",
            "pattern": "Use Optional[] for fields that don't apply to all record types",
        })

    # Pattern: Required to Optional migration
    required_to_optional = r'-\s*(\w+):\s*([^=\n]+)\s*=\s*Field.*\n\+\s*\1:\s*Optional\['
    for match in re.finditer(required_to_optional, diff_text):
        field_name = match.group(1)
        schema_changes.append({
            "type": "optional_migration",
            "field": field_name,
            "learning": f"Migrated {field_name} from required to Optional",
            "pattern": "Backward compatibility: make new fields Optional, not required",
        })

    # Pattern: New fields with default values
    default_field_pattern = r'\+\s*(\w+):\s*([^=\n]+)\s*=\s*Field\(.*default'
    for match in re.finditer(default_field_pattern, diff_text):
        field_name = match.group(1)
        field_type = match.group(2)
        schema_changes.append({
            "type": "field_with_default",
            "field": field_name,
            "field_type": field_type,
            "learning": f"Added {field_name} with default value for backward compatibility",
            "pattern": "New schema fields should have defaults to avoid breaking existing code",
        })

    return schema_changes


def detect_api_changes(diff_text: str) -> List[Dict[str, str]]:
    """Detect API/function signature changes."""
    api_changes = []

    # Pattern: Function signature changes
    func_sig_pattern = r'-\s*def\s+(\w+)\((.*?)\):.*\n\+\s*def\s+\1\((.*?)\):'
    for match in re.finditer(func_sig_pattern, diff_text, re.MULTILINE):
        func_name = match.group(1)
        old_params = match.group(2)
        new_params = match.group(3)

        # Check what changed
        if "Optional" in new_params and "Optional" not in old_params:
            api_changes.append({
                "type": "parameter_optional",
                "function": func_name,
                "change": f"Made parameter Optional: {new_params}",
                "learning": f"Added Optional parameter to {func_name} for flexibility",
                "pattern": "Use Optional[] for parameters that have sensible defaults",
            })
        elif len(new_params) > len(old_params):
            api_changes.append({
                "type": "parameter_addition",
                "function": func_name,
                "change": f"Added parameter: {new_params}",
                "learning": f"Extended {func_name} with new parameter",
                "pattern": "Add new parameters with defaults to maintain backward compatibility",
            })

    # Pattern: Return type changes
    return_type_pattern = r'-\s*def\s+(\w+)\(.*?\)\s*->\s*(\w+):.*\n\+\s*def\s+\1\(.*?\)\s*->\s*(\w+):'
    for match in re.finditer(return_type_pattern, diff_text):
        func_name = match.group(1)
        old_return = match.group(2)
        new_return = match.group(3)

        if old_return != new_return:
            api_changes.append({
                "type": "return_type_change",
                "function": func_name,
                "old_return": old_return,
                "new_return": new_return,
                "learning": f"Changed {func_name} return type from {old_return} to {new_return}",
                "pattern": "Document return type changes to prevent downstream errors",
            })

    return api_changes


def extract_imports_added(diff_text: str) -> List[str]:
    """Extract new imports added during session."""
    imports = []

    # Pattern: New import statements
    import_pattern = r'\+\s*(?:from\s+[\w.]+\s+)?import\s+([\w, ]+)'
    for match in re.finditer(import_pattern, diff_text):
        import_names = match.group(1)
        imports.append(import_names.strip())

    return imports


def extract_functions_modified(diff_text: str) -> List[str]:
    """Extract functions that were modified."""
    functions = set()

    # Look for function definitions in changed sections
    func_pattern = r'@@.*@@\s+def\s+(\w+)\('
    for match in re.finditer(func_pattern, diff_text):
        functions.add(match.group(1))

    return list(functions)


def detect_error_handling(diff_text: str) -> List[Dict[str, str]]:
    """Detect error handling patterns added."""
    patterns = []

    # Pattern: Continue/skip on None
    skip_none_pattern = r'\+\s*if\s+(\w+)\s+is\s+None:\s*\n\+\s*continue'
    for match in re.finditer(skip_none_pattern, diff_text):
        var_name = match.group(1)
        patterns.append({
            "pattern": "skip_on_none",
            "code": f"if {var_name} is None: continue",
            "learning": f"Skip processing when {var_name} is None instead of crashing",
            "best_practice": "Gracefully handle missing data with skip logic",
        })

    # Pattern: Default value on None
    default_on_none_pattern = r'\+\s*(\w+)\s*=\s*\(.*\)\s*if\s+.*\s*else\s+None'
    for match in re.finditer(default_on_none_pattern, diff_text):
        var_name = match.group(1)
        patterns.append({
            "pattern": "default_on_none",
            "code": match.group(0)[1:].strip(),
            "learning": f"Use ternary operator to provide default for {var_name}",
            "best_practice": "Provide sensible defaults instead of None where possible",
        })

    return patterns


def detect_type_fixes(diff_text: str) -> List[Dict[str, str]]:
    """Detect type-related fixes."""
    fixes = []

    # Pattern: Changed .get() call to handle float vs dict
    # Example: avg_effort.get() -> (avg_effort / 60.0) if avg_effort else None
    dict_to_value_pattern = r'-\s*(\w+)\.get\(["\'](\w+)["\']\).*\n\+\s*(?:\()?(\w+)(?:\s*/\s*[\d.]+)?(?:\))?\s*if\s+\3\s+else\s+None'
    for match in re.finditer(dict_to_value_pattern, diff_text):
        var_name = match.group(1)
        fixes.append({
            "type": "type_assumption",
            "issue": f"Assumed {var_name} was dict, but it was a scalar value",
            "fix": f"Check return type before calling .get() on {var_name}",
            "learning": "Don't assume return types - check function signature or handle both cases",
        })

    return fixes


def detect_defensive_coding_patterns(diff_text: str) -> List[Dict[str, str]]:
    """Detect defensive coding patterns added."""
    patterns = []

    # Pattern: Early return on empty/None
    early_return_pattern = r'\+\s*if\s+not\s+(\w+):\s*\n\+\s*return'
    for match in re.finditer(early_return_pattern, diff_text):
        var_name = match.group(1)
        patterns.append({
            "pattern": "early_return",
            "code": f"if not {var_name}: return",
            "learning": "Use early returns to avoid processing invalid data",
            "best_practice": "Validate inputs early and return/skip if invalid",
        })

    # Pattern: Assertion or validation
    assert_pattern = r'\+\s*assert\s+(.*?),'
    for match in re.finditer(assert_pattern, diff_text):
        condition = match.group(1)
        patterns.append({
            "pattern": "assertion",
            "code": f"assert {condition}",
            "learning": "Add assertions to validate assumptions",
            "best_practice": "Use assertions in tests, explicit checks in production code",
        })

    return patterns


def extract_commit_error_patterns(commits: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Extract error patterns from commit message flow.

    Analyzes commit sequence to understand:
    - What broke (error messages in commits)
    - What was tried (fix attempts)
    - What worked (successful fix)
    """
    error_patterns = []

    # Look for fix commits that follow error patterns
    for i in range(len(commits) - 1):
        current = commits[i]
        previous = commits[i + 1] if i + 1 < len(commits) else None

        msg_lower = current["message"].lower()

        # Pattern: "fix: <error type>"
        if "fix:" in msg_lower:
            error_type = None
            error_desc = current["message"].split(":", 1)[1].strip() if ":" in current["message"] else current["message"]

            # Try to extract error type from message
            if "attributeerror" in msg_lower:
                error_type = "AttributeError"
            elif "typeerror" in msg_lower:
                error_type = "TypeError"
            elif "keyerror" in msg_lower:
                error_type = "KeyError"
            elif "nameerror" in msg_lower:
                error_type = "NameError"
            elif "none" in msg_lower and ("attribute" in msg_lower or "has no" in msg_lower):
                error_type = "AttributeError (NoneType)"

            if error_type:
                error_patterns.append({
                    "error_type": error_type,
                    "description": error_desc,
                    "fix_commit": current["hash"][:8],
                    "learning": f"Fixed {error_type}: {error_desc}",
                    "prevention": generate_prevention_tip(error_type, error_desc),
                })

    return error_patterns


def generate_prevention_tip(error_type: str, description: str) -> str:
    """Generate prevention tip based on error type."""
    tips = {
        "AttributeError": "Always check for None before accessing attributes: if obj is not None",
        "AttributeError (NoneType)": "Validate that objects are not None before accessing properties",
        "TypeError": "Verify data types match expected types, use explicit type conversions",
        "KeyError": "Use dict.get() instead of dict[] for optional keys",
        "NameError": "Ensure variables are defined before use, check imports",
    }

    return tips.get(error_type, "Add defensive checks and validation")


def analyze_problem_solving_flow(commits: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze the problem-solving approach from commit sequence.

    Returns:
        Dict with flow analysis including iterative refinement, error-fix cycles, etc.
    """
    if len(commits) < 2:
        return {"approach": "single_commit", "iterations": 0}

    # Categorize commits
    feature_commits = []
    fix_commits = []
    test_commits = []
    refactor_commits = []

    for commit in commits:
        msg_lower = commit["message"].lower()

        if any(kw in msg_lower for kw in ["fix:", "fixed", "resolve"]):
            fix_commits.append(commit)
        elif any(kw in msg_lower for kw in ["test:", "spec:", "testing"]):
            test_commits.append(commit)
        elif any(kw in msg_lower for kw in ["refactor:", "cleanup", "improve"]):
            refactor_commits.append(commit)
        elif any(kw in msg_lower for kw in ["feat:", "add", "implement", "create"]):
            feature_commits.append(commit)

    # Analyze flow
    total_commits = len(commits)
    fix_ratio = len(fix_commits) / total_commits if total_commits > 0 else 0

    if fix_ratio > 0.5:
        approach = "error_driven"
        insight = f"High fix ratio ({fix_ratio:.1%}): Many errors encountered and resolved"
    elif len(test_commits) > 0:
        approach = "test_driven"
        insight = f"TDD approach: {len(test_commits)} test commits found"
    elif len(refactor_commits) > len(feature_commits):
        approach = "refactor_driven"
        insight = "Iterative refinement: More refactoring than initial implementation"
    else:
        approach = "feature_driven"
        insight = "Direct implementation: Feature commits dominate"

    return {
        "approach": approach,
        "total_commits": total_commits,
        "feature_commits": len(feature_commits),
        "fix_commits": len(fix_commits),
        "test_commits": len(test_commits),
        "refactor_commits": len(refactor_commits),
        "fix_ratio": fix_ratio,
        "insight": insight,
        "iterations": len(fix_commits),
    }


def generate_actionable_learnings(
    git_analysis: Dict[str, Any],
    diff_analysis: Dict[str, Any],
    commit_errors: List[Dict[str, str]],
    flow_analysis: Dict[str, Any],
) -> Dict[str, List[str]]:
    """Generate actionable learnings from all analyses.

    Returns:
        Dict with key_learnings, what_worked_well, what_to_avoid, technical_patterns
    """
    key_learnings = []
    what_worked_well = []
    what_to_avoid = []
    technical_patterns = []

    # From commit errors
    for error in commit_errors:
        what_to_avoid.append(
            f"Avoid {error['error_type']}: {error['description']} - Prevention: {error['prevention']}"
        )

    # From diff analysis - errors fixed
    for error in diff_analysis.get("errors_fixed", []):
        if error.get("preventive"):
            what_worked_well.append(f"✓ {error['fix']}")
        else:
            what_to_avoid.append(f"✗ {error['pattern']} - Fix: {error['fix']}")

    # From schema changes
    for change in diff_analysis.get("schema_changes", []):
        key_learnings.append(change["learning"])
        technical_patterns.append(change["pattern"])

    # From API changes
    for change in diff_analysis.get("api_changes", []):
        key_learnings.append(change["learning"])
        if change.get("pattern"):
            technical_patterns.append(change["pattern"])

    # From error handling patterns
    for pattern in diff_analysis.get("error_handling_added", []):
        what_worked_well.append(f"✓ {pattern['learning']}")
        technical_patterns.append(pattern["best_practice"])

    # From type fixes
    for fix in diff_analysis.get("type_fixes", []):
        what_to_avoid.append(f"✗ {fix['issue']} - Fix: {fix['fix']}")
        key_learnings.append(fix["learning"])

    # From defensive coding
    for pattern in diff_analysis.get("defensive_coding", []):
        what_worked_well.append(f"✓ {pattern['learning']}")
        technical_patterns.append(pattern["best_practice"])

    # From flow analysis
    if flow_analysis["approach"] == "error_driven":
        key_learnings.append(
            f"Error-driven development: {flow_analysis['iterations']} iterations needed to resolve issues"
        )
        what_worked_well.append("✓ Persisted through multiple errors and found solutions iteratively")
    elif flow_analysis["approach"] == "test_driven":
        what_worked_well.append(f"✓ Test-driven approach: {flow_analysis['test_commits']} test commits")
        technical_patterns.append("Write tests alongside features for faster validation")

    # From complexity indicators
    if "iterative_development" in git_analysis.get("complexity_indicators", []):
        key_learnings.append(
            f"Complex task requiring {flow_analysis['total_commits']} commits - "
            f"break down similar tasks into smaller iterations"
        )

    if "wrote_tests" in git_analysis.get("complexity_indicators", []):
        what_worked_well.append("✓ Implemented tests alongside features for validation")

    if "created_multiple_files" in git_analysis.get("complexity_indicators", []):
        key_learnings.append(
            f"Multi-file implementation: {len(git_analysis.get('new_files', []))} new files created - "
            "plan file structure before implementation"
        )

    # Deduplicate and limit
    return {
        "key_learnings": list(dict.fromkeys(key_learnings))[:7],
        "what_worked_well": list(dict.fromkeys(what_worked_well))[:5],
        "what_to_avoid": list(dict.fromkeys(what_to_avoid))[:5],
        "technical_patterns": list(dict.fromkeys(technical_patterns))[:5],
    }
