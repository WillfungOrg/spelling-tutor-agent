"""Manual Session Logger - Automatically log valuable Claude Code sessions.

This module analyzes manual Claude sessions and intelligently decides whether
they're worth logging for learning purposes. It logs complex/valuable work
while skipping trivial tasks.
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
import hashlib

from adw_modules.meta_adw_types import (
    TaskAnalysis,
    ExecutionMetrics,
    ErrorRecord,
    LearningRecord,
)
from adw_modules.learning_extractor import (
    analyze_git_diffs,
    extract_commit_error_patterns,
    analyze_problem_solving_flow,
    generate_actionable_learnings,
)


def generate_session_id() -> str:
    """Generate a unique session ID for manual Claude sessions."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    random_part = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:8]
    return f"session-{timestamp}-{random_part}"


def analyze_git_history(since_minutes: int = 180, repo_path: Optional[Path] = None) -> Dict[str, Any]:
    """Analyze git history to extract session metrics.

    Args:
        since_minutes: How far back to look (default: 3 hours)
        repo_path: Repository path (default: current directory)

    Returns:
        Dict with session metrics
    """
    if repo_path is None:
        repo_path = Path.cwd()

    try:
        # Get commits from the last N minutes
        since_time = f"{since_minutes}.minutes.ago"
        cmd_log = ["git", "log", f"--since={since_time}", "--pretty=format:%H|%s|%ct", "--no-merges"]
        result_log = subprocess.run(cmd_log, cwd=repo_path, capture_output=True, text=True, timeout=10)

        commits = []
        if result_log.stdout:
            for line in result_log.stdout.strip().split('\n'):
                if line:
                    commit_hash, message, timestamp = line.split('|', 2)
                    commits.append({
                        "hash": commit_hash,
                        "message": message,
                        "timestamp": int(timestamp)
                    })

        if not commits:
            return {
                "commits": [],
                "files_changed": 0,
                "lines_added": 0,
                "lines_removed": 0,
                "duration_minutes": 0,
                "complexity_indicators": [],
            }

        # Get detailed stats for all commits
        commit_hashes = [c["hash"] for c in commits]
        cmd_diff = ["git", "diff", "--shortstat", f"{commit_hashes[-1]}^", commit_hashes[0]]
        result_diff = subprocess.run(cmd_diff, cwd=repo_path, capture_output=True, text=True, timeout=10)

        # Parse: "X files changed, Y insertions(+), Z deletions(-)"
        files_changed = 0
        lines_added = 0
        lines_removed = 0

        if result_diff.stdout:
            parts = result_diff.stdout.strip().split(',')
            for part in parts:
                if 'file' in part:
                    files_changed = int(part.split()[0])
                elif 'insertion' in part:
                    lines_added = int(part.split()[0])
                elif 'deletion' in part:
                    lines_removed = int(part.split()[0])

        # Get list of changed files
        cmd_files = ["git", "diff", "--name-only", f"{commit_hashes[-1]}^", commit_hashes[0]]
        result_files = subprocess.run(cmd_files, cwd=repo_path, capture_output=True, text=True, timeout=10)
        changed_files = [f.strip() for f in result_files.stdout.strip().split('\n') if f.strip()]

        # Calculate duration
        if len(commits) >= 2:
            duration_seconds = commits[0]["timestamp"] - commits[-1]["timestamp"]
            duration_minutes = duration_seconds / 60.0
        else:
            duration_minutes = 5.0  # Single commit, assume 5 minutes

        # Analyze complexity indicators
        complexity_indicators = []

        # Check for test files
        test_files = [f for f in changed_files if 'test' in f.lower()]
        if test_files:
            complexity_indicators.append("wrote_tests")

        # Check for new files (not just edits)
        cmd_new = ["git", "diff", "--diff-filter=A", "--name-only", f"{commit_hashes[-1]}^", commit_hashes[0]]
        result_new = subprocess.run(cmd_new, cwd=repo_path, capture_output=True, text=True, timeout=10)
        new_files = [f.strip() for f in result_new.stdout.strip().split('\n') if f.strip()]

        if len(new_files) >= 2:
            complexity_indicators.append("created_multiple_files")

        # Check for module/package work (multiple related files)
        unique_dirs = set(Path(f).parent for f in changed_files)
        if len(unique_dirs) >= 3:
            complexity_indicators.append("multi_module_changes")

        # Large change indicator
        if lines_added + lines_removed > 500:
            complexity_indicators.append("large_change")

        # Multiple commits (iterative development)
        if len(commits) >= 3:
            complexity_indicators.append("iterative_development")

        return {
            "commits": commits,
            "files_changed": files_changed,
            "changed_file_list": changed_files,
            "new_files": new_files,
            "lines_added": lines_added,
            "lines_removed": lines_removed,
            "duration_minutes": duration_minutes,
            "complexity_indicators": complexity_indicators,
        }

    except Exception as e:
        print(f"Warning: Could not analyze git history: {e}")
        return {
            "commits": [],
            "files_changed": 0,
            "lines_added": 0,
            "lines_removed": 0,
            "duration_minutes": 0,
            "complexity_indicators": [],
            "error": str(e)
        }


def calculate_complexity_score(git_analysis: Dict[str, Any]) -> float:
    """Calculate complexity score from git analysis.

    Returns:
        Complexity score from 1-10
    """
    score = 1.0

    # Files changed (max +3)
    files_changed = git_analysis.get("files_changed", 0)
    if files_changed >= 10:
        score += 3.0
    elif files_changed >= 5:
        score += 2.0
    elif files_changed >= 2:
        score += 1.0

    # Lines of code (max +2)
    total_lines = git_analysis.get("lines_added", 0) + git_analysis.get("lines_removed", 0)
    if total_lines >= 1000:
        score += 2.0
    elif total_lines >= 500:
        score += 1.5
    elif total_lines >= 200:
        score += 1.0

    # Complexity indicators (max +3)
    indicators = git_analysis.get("complexity_indicators", [])
    score += min(len(indicators) * 0.5, 3.0)

    # Duration (max +2)
    duration = git_analysis.get("duration_minutes", 0)
    if duration >= 120:  # 2+ hours
        score += 2.0
    elif duration >= 60:  # 1+ hour
        score += 1.0

    return min(score, 10.0)


def should_log_session(git_analysis: Dict[str, Any]) -> Tuple[bool, str]:
    """Decide if this session is worth logging for learning.

    Args:
        git_analysis: Git analysis data

    Returns:
        (should_log: bool, reason: str)
    """
    files_changed = git_analysis.get("files_changed", 0)
    lines_changed = git_analysis.get("lines_added", 0) + git_analysis.get("lines_removed", 0)
    duration = git_analysis.get("duration_minutes", 0)
    commits = git_analysis.get("commits", [])
    complexity_indicators = git_analysis.get("complexity_indicators", [])

    # Skip if no meaningful work
    if files_changed == 0:
        return (False, "No files changed")

    if len(commits) == 0:
        return (False, "No commits found")

    # Skip trivial changes
    if files_changed == 1 and lines_changed < 20 and duration < 10:
        return (False, "Trivial change: 1 file, <20 lines, <10 minutes")

    # Log if substantial work
    if files_changed >= 3:
        return (True, f"Substantial work: {files_changed} files changed")

    if lines_changed >= 200:
        return (True, f"Significant changes: {lines_changed} lines modified")

    if duration >= 30:
        return (True, f"Significant effort: {duration:.1f} minutes of work")

    if len(commits) >= 3:
        return (True, f"Iterative development: {len(commits)} commits")

    if len(complexity_indicators) >= 2:
        return (True, f"Complex work: {', '.join(complexity_indicators)}")

    # Check for test file creation (always valuable)
    changed_files = git_analysis.get("changed_file_list", [])
    test_files = [f for f in changed_files if 'test' in f.lower()]
    if test_files:
        return (True, f"Test development: {len(test_files)} test files")

    # Default: skip logging for minor work
    return (False, f"Minor work: {files_changed} files, {lines_changed} lines, {duration:.1f} min")


def infer_task_type(git_analysis: Dict[str, Any]) -> str:
    """Infer task type from commit messages and files changed."""
    commits = git_analysis.get("commits", [])
    if not commits:
        return "chore"

    # Analyze commit messages
    messages = " ".join([c["message"].lower() for c in commits])
    changed_files = git_analysis.get("changed_file_list", [])

    if any(keyword in messages for keyword in ["feat:", "feature", "add", "implement"]):
        return "feature"
    elif any(keyword in messages for keyword in ["fix:", "bug", "error", "issue"]):
        return "bug"
    elif any(keyword in messages for keyword in ["test:", "spec", "coverage"]):
        return "feature"  # Test development is feature work
    elif any(keyword in messages for keyword in ["refactor:", "cleanup", "improve"]):
        return "refactor"
    elif "test" in " ".join(changed_files).lower():
        return "feature"
    else:
        return "chore"


def extract_learnings_from_commits(git_analysis: Dict[str, Any], repo_path: Path) -> Dict[str, List[str]]:
    """Extract actionable learning insights using deep code analysis.

    Returns:
        Dict with key_learnings, what_worked_well, what_to_avoid, technical_patterns
    """
    commits = git_analysis.get("commits", [])

    if not commits:
        return {
            "key_learnings": [],
            "what_worked_well": [],
            "what_to_avoid": [],
            "technical_patterns": [],
        }

    # Deep analysis using learning_extractor
    diff_analysis = analyze_git_diffs(commits, repo_path)
    commit_errors = extract_commit_error_patterns(commits)
    flow_analysis = analyze_problem_solving_flow(commits)

    # Generate actionable learnings
    learnings = generate_actionable_learnings(
        git_analysis,
        diff_analysis,
        commit_errors,
        flow_analysis,
    )

    return learnings


def log_manual_session(
    task_description: Optional[str] = None,
    issue_number: Optional[str] = None,
    since_minutes: int = 180,
    repo_path: Optional[Path] = None,
    force: bool = False,
) -> Optional[str]:
    """Log a manual Claude Code session if it's worth learning from.

    Args:
        task_description: Optional description (if None, inferred from commits)
        issue_number: Optional GitHub issue number
        since_minutes: How far back to analyze git history (default: 3 hours)
        repo_path: Repository path (default: current directory)
        force: Force logging even if decision logic says skip

    Returns:
        Session ID if logged, None if skipped
    """
    if repo_path is None:
        repo_path = Path.cwd()

    # Analyze recent git history
    print(f"\nAnalyzing recent work (last {since_minutes} minutes)...")
    git_analysis = analyze_git_history(since_minutes, repo_path)

    # Decide if worth logging
    should_log, reason = should_log_session(git_analysis)

    if not should_log and not force:
        print(f"⏭️  Skipping log: {reason}")
        return None

    print(f"📝 Logging session: {reason}")

    # Generate session ID
    session_id = generate_session_id()

    # Infer task details
    task_type = infer_task_type(git_analysis)
    complexity_score = calculate_complexity_score(git_analysis)

    # Determine complexity level
    if complexity_score >= 8:
        complexity_level = "complex"
    elif complexity_score >= 5:
        complexity_level = "moderate"
    elif complexity_score >= 3:
        complexity_level = "simple"
    else:
        complexity_level = "simple"

    # Create task description if not provided
    if task_description is None:
        commits = git_analysis.get("commits", [])
        if commits:
            task_description = f"Manual session: {commits[0]['message']}"
        else:
            task_description = "Manual Claude Code session"

    # Build task analysis
    task_analysis = TaskAnalysis(
        task_type=task_type,
        complexity_score=complexity_score,
        complexity_level=complexity_level,
        validation_needs="thorough" if complexity_score >= 6 else "basic",
        key_requirements=[],
        estimated_effort_hours=git_analysis.get("duration_minutes", 0) / 60.0,
        has_ui_changes=False,  # Could be inferred from file patterns
        requires_e2e_tests="test" in " ".join(git_analysis.get("changed_file_list", [])).lower(),
    )

    # Build execution metrics
    execution_metrics = ExecutionMetrics(
        actual_duration_minutes=git_analysis.get("duration_minutes"),
        files_changed=git_analysis.get("files_changed"),
        lines_added=git_analysis.get("lines_added"),
        lines_removed=git_analysis.get("lines_removed"),
    )

    # Extract learning insights with deep analysis
    learnings = extract_learnings_from_commits(git_analysis, repo_path)

    # Build learning record
    record = LearningRecord(
        task_description=task_description,
        task_analysis=task_analysis,
        recommended_strategy=None,  # No recommendation for manual sessions
        selected_strategy="manual-claude-session",
        outcome="success",  # Assume success if committed
        execution_metrics=execution_metrics,
        execution_timestamp=datetime.now(),
        execution_start_time=datetime.fromtimestamp(git_analysis["commits"][-1]["timestamp"]) if git_analysis.get("commits") else None,
        execution_end_time=datetime.fromtimestamp(git_analysis["commits"][0]["timestamp"]) if git_analysis.get("commits") else None,
        session_id=session_id,
        issue_number=issue_number,
        trigger_type="manual-claude",
        key_learnings=learnings["key_learnings"],
        what_worked_well=learnings["what_worked_well"],
        what_to_avoid=learnings["what_to_avoid"],
        technical_patterns=learnings.get("technical_patterns", []),
    )

    # Store learning record
    learning_dir = repo_path / ".tac" / "learning"
    execution_logs_dir = learning_dir / "execution_logs"
    execution_logs_dir.mkdir(parents=True, exist_ok=True)

    log_file = execution_logs_dir / f"{session_id}.json"
    with open(log_file, 'w') as f:
        json.dump(record.model_dump(), f, indent=2, default=str)

    print(f"✅ Session logged: {session_id}")
    print(f"   Task: {task_description}")
    print(f"   Type: {task_type}, Complexity: {complexity_score:.1f}/10")
    print(f"   Files: {git_analysis.get('files_changed')}, Lines: {git_analysis.get('lines_added') + git_analysis.get('lines_removed')}")
    print(f"   Duration: {git_analysis.get('duration_minutes', 0):.1f} minutes")
    print(f"   Saved to: {log_file}")

    return session_id
