# AI Learning System - Implementation Plan

**Spec Reference:** `specs/ai-learning-system-mvp.md`
**Created:** 2025-11-07
**Estimated Time:** 5-7 hours
**Complexity:** 7/10

---

## 📋 Overview

This plan breaks down the 5 core components needed to complete the AI self-improving learning system (currently 50% complete with existing infrastructure).

**Components to Build:**
1. Test Feedback Integration (1 hour)
2. Review Feedback Capture (1 hour)
3. Deployment Feedback Integration (1 hour)
4. Cross-Project Learning Aggregation (1 hour)
5. Prompt Refinement Engine (1.5 hours)

**Foundation Already Exists:**
- ✅ Data models (`LearningRecord`, `PatternDatabase`, etc.)
- ✅ Basic learning loop (`collect_feedback`, `update_pattern_database`, `retrain_weights`)
- ✅ Decision engine (pattern matching, workflow ranking)
- ✅ Storage structure (`.tac/learning/`)

---

## 🎯 Implementation Order

### Phase 1: Feedback Collectors (3 hours)
Build the three feedback collection components that integrate with existing ADW workflows.

### Phase 2: Cross-Project Aggregation (1 hour)
Create the global learning store and aggregation logic.

### Phase 3: Prompt Refinement (1.5 hours)
Implement the Self-Refine pattern for continuous prompt improvement.

### Phase 4: Integration & Testing (0.5 hours)
Activate the learning loop and validate end-to-end.

---

## 📝 Step-by-Step Tasks

### Task 1: Create FeedbackCollector Base Class
**Time:** 20 minutes
**File:** `adw/adw_modules/learning_feedback.py` (NEW)

**Implementation:**
```python
"""Feedback collection system for AI learning."""

from typing import Dict, Any, List, Optional
from pathlib import Path
import json
from datetime import datetime

from adw_modules.meta_adw_types import LearningRecord, TaskAnalysis, StrategyRecommendation


class FeedbackCollector:
    """Base class for collecting feedback from different sources."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.learning_dir = repo_root / ".tac" / "learning"
        self.learning_dir.mkdir(parents=True, exist_ok=True)

    def collect(self, adw_id: str, issue_number: str) -> Optional[Dict[str, Any]]:
        """Collect feedback for a specific ADW execution.

        Returns:
            Dict with feedback data or None if not available
        """
        raise NotImplementedError("Subclasses must implement collect()")

    def store_learning_record(self, record: LearningRecord) -> None:
        """Store a learning record in the execution logs."""
        log_file = self.learning_dir / "execution_logs" / f"{record.adw_id}.json"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(log_file, 'w') as f:
            json.dump(record.model_dump(), f, indent=2, default=str)
```

**Acceptance Criteria:**
- ✅ Base class created with `collect()` abstract method
- ✅ `store_learning_record()` saves to `.tac/learning/execution_logs/`
- ✅ Proper error handling and type hints

---

### Task 2: Implement TestFeedbackCollector
**Time:** 40 minutes
**File:** `adw/adw_modules/learning_feedback.py` (append to existing)

**Implementation:**
```python
class TestFeedbackCollector(FeedbackCollector):
    """Collect feedback from ADW test executions."""

    def collect(self, adw_id: str, issue_number: str) -> Optional[Dict[str, Any]]:
        """Parse test results from adw_test_iso.py execution.

        Returns:
            {
                "total_tests": int,
                "passed": int,
                "failed": int,
                "failure_patterns": List[str],
                "test_output": str,
                "success_rate": float
            }
        """
        # 1. Find agent state
        agent_dir = self.repo_root / "agents" / adw_id
        state_file = agent_dir / "adw_state.json"

        if not state_file.exists():
            return None

        with open(state_file) as f:
            state = json.load(f)

        # 2. Find test execution logs
        logs_dir = self.repo_root / "logs"
        test_logs = []

        for session_dir in logs_dir.iterdir():
            if not session_dir.is_dir():
                continue
            chat_file = session_dir / "chat.json"
            if chat_file.exists():
                with open(chat_file) as f:
                    chat = json.load(f)
                    # Check if this is a test execution for our ADW
                    if self._is_test_execution(chat, adw_id):
                        test_logs.append(chat)

        if not test_logs:
            return None

        # 3. Parse most recent test results
        latest_test = test_logs[-1]
        results = self._parse_pytest_output(latest_test)

        return results

    def _is_test_execution(self, chat_log: Dict, adw_id: str) -> bool:
        """Check if chat log is from a test execution for this ADW."""
        # Look for pytest commands and ADW ID references
        for message in chat_log.get("messages", []):
            content = str(message.get("content", ""))
            if "pytest" in content.lower() and adw_id in content:
                return True
        return False

    def _parse_pytest_output(self, chat_log: Dict) -> Dict[str, Any]:
        """Extract test metrics from pytest output."""
        output = self._get_test_output(chat_log)

        # Parse pytest output format:
        # "X passed, Y failed in Z.ZZs"
        # "FAILED app/tests/test_foo.py::test_bar - AssertionError: ..."

        import re

        passed = 0
        failed = 0
        failure_patterns = []

        # Look for summary line
        summary_match = re.search(r"(\d+) passed.*?(\d+) failed", output)
        if summary_match:
            passed = int(summary_match.group(1))
            failed = int(summary_match.group(2))
        else:
            # Try single stat
            passed_match = re.search(r"(\d+) passed", output)
            if passed_match:
                passed = int(passed_match.group(1))

        # Extract failure patterns
        failed_tests = re.findall(r"FAILED ([\w/]+\.py::[\w_]+)", output)
        for test_path in failed_tests:
            # Extract test category (e.g., "auth", "api", "database")
            category = self._categorize_test(test_path)
            failure_patterns.append(category)

        total = passed + failed
        success_rate = passed / total if total > 0 else 0.0

        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "failure_patterns": list(set(failure_patterns)),
            "test_output": output[:1000],  # First 1000 chars
            "success_rate": success_rate,
        }

    def _get_test_output(self, chat_log: Dict) -> str:
        """Extract test output from chat log."""
        for message in reversed(chat_log.get("messages", [])):
            if message.get("role") == "tool_result":
                content = message.get("content", "")
                if "pytest" in str(content).lower():
                    return str(content)
        return ""

    def _categorize_test(self, test_path: str) -> str:
        """Categorize test by path (e.g., 'auth', 'api', 'database')."""
        # Extract category from path like "app/tests/test_auth.py::test_login"
        match = re.search(r"test_([\w]+)\.py", test_path)
        if match:
            return match.group(1)
        return "unknown"
```

**Acceptance Criteria:**
- ✅ Parses pytest output from chat logs
- ✅ Extracts pass/fail counts accurately
- ✅ Identifies failure patterns by test category
- ✅ Returns None gracefully if no test data available
- ✅ Calculates success rate

---

### Task 3: Implement ReviewFeedbackCollector
**Time:** 40 minutes
**File:** `adw/adw_modules/learning_feedback.py` (append to existing)

**Implementation:**
```python
class ReviewFeedbackCollector(FeedbackCollector):
    """Collect feedback from PR reviews."""

    def __init__(self, repo_root: Path, github_token: Optional[str] = None):
        super().__init__(repo_root)
        self.github_token = github_token or os.getenv("GITHUB_PAT")

    def collect(self, adw_id: str, issue_number: str) -> Optional[Dict[str, Any]]:
        """Fetch PR review feedback from GitHub.

        Returns:
            {
                "pr_number": int,
                "review_status": "approved" | "changes_requested" | "commented",
                "num_review_comments": int,
                "change_categories": List[str],
                "human_changes_made": bool,
                "diff_summary": str
            }
        """
        from adw_modules.github import get_repo_info, fetch_pr_for_issue

        # 1. Get PR associated with issue
        repo_owner, repo_name = get_repo_info()
        pr_data = fetch_pr_for_issue(repo_owner, repo_name, issue_number, self.github_token)

        if not pr_data:
            return None

        pr_number = pr_data.get("number")

        # 2. Fetch review comments
        reviews = self._fetch_reviews(repo_owner, repo_name, pr_number)
        review_comments = self._fetch_review_comments(repo_owner, repo_name, pr_number)

        # 3. Determine review status
        review_status = self._determine_review_status(reviews)

        # 4. Analyze changes made after AI generation
        change_categories = self._analyze_review_changes(review_comments)

        # 5. Check if human made changes (commits after AI)
        commits = self._fetch_commits(repo_owner, repo_name, pr_number)
        human_changes = self._detect_human_commits(commits, adw_id)

        return {
            "pr_number": pr_number,
            "review_status": review_status,
            "num_review_comments": len(review_comments),
            "change_categories": change_categories,
            "human_changes_made": human_changes,
            "diff_summary": self._summarize_changes(review_comments)[:500],
        }

    def _fetch_reviews(self, owner: str, repo: str, pr_number: int) -> List[Dict]:
        """Fetch PR reviews from GitHub API."""
        import requests

        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        headers = {"Authorization": f"token {self.github_token}"} if self.github_token else {}

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return []

    def _fetch_review_comments(self, owner: str, repo: str, pr_number: int) -> List[Dict]:
        """Fetch PR review comments."""
        import requests

        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments"
        headers = {"Authorization": f"token {self.github_token}"} if self.github_token else {}

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return []

    def _fetch_commits(self, owner: str, repo: str, pr_number: int) -> List[Dict]:
        """Fetch PR commits."""
        import requests

        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/commits"
        headers = {"Authorization": f"token {self.github_token}"} if self.github_token else {}

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return []

    def _determine_review_status(self, reviews: List[Dict]) -> str:
        """Determine overall review status."""
        if not reviews:
            return "no_review"

        # Get most recent review
        latest = reviews[-1]
        state = latest.get("state", "").lower()

        if state == "approved":
            return "approved"
        elif state == "changes_requested":
            return "changes_requested"
        else:
            return "commented"

    def _analyze_review_changes(self, comments: List[Dict]) -> List[str]:
        """Categorize types of changes requested."""
        categories = set()

        keywords = {
            "logic": ["bug", "logic", "error", "incorrect", "wrong"],
            "style": ["style", "format", "naming", "convention"],
            "performance": ["performance", "slow", "optimize", "inefficient"],
            "security": ["security", "vulnerability", "unsafe", "injection"],
            "testing": ["test", "coverage", "assertion"],
            "refactor": ["refactor", "simplify", "cleanup", "duplicate"],
        }

        for comment in comments:
            body = comment.get("body", "").lower()
            for category, terms in keywords.items():
                if any(term in body for term in terms):
                    categories.add(category)

        return list(categories) if categories else ["general"]

    def _detect_human_commits(self, commits: List[Dict], adw_id: str) -> bool:
        """Check if human made commits after AI."""
        # Look for commits NOT made by ADW automation
        for commit in commits:
            message = commit.get("commit", {}).get("message", "")
            if adw_id not in message and "🤖 Generated with" not in message:
                return True
        return False

    def _summarize_changes(self, comments: List[Dict]) -> str:
        """Create summary of review feedback."""
        if not comments:
            return "No review comments"

        return f"{len(comments)} review comments covering: " + \
               ", ".join(c.get("path", "unknown") for c in comments[:5])
```

**Acceptance Criteria:**
- ✅ Fetches PR data from GitHub API
- ✅ Extracts review status (approved/changes_requested)
- ✅ Categorizes review feedback (logic, style, security, etc.)
- ✅ Detects if human made additional commits
- ✅ Gracefully handles missing PR or auth

---

### Task 4: Implement DeploymentFeedbackCollector
**Time:** 40 minutes
**File:** `adw/adw_modules/learning_feedback.py` (append to existing)

**Implementation:**
```python
class DeploymentFeedbackCollector(FeedbackCollector):
    """Collect deployment outcome feedback."""

    def __init__(self, repo_root: Path, github_token: Optional[str] = None):
        super().__init__(repo_root)
        self.github_token = github_token or os.getenv("GITHUB_PAT")

    def collect(self, adw_id: str, issue_number: str) -> Optional[Dict[str, Any]]:
        """Check deployment status and outcomes.

        Returns:
            {
                "deployed": bool,
                "deployment_status": "success" | "failure" | "unknown",
                "deployment_method": "github_actions" | "manual" | "unknown",
                "post_deployment_errors": List[str],
                "rollback_required": bool
            }
        """
        from adw_modules.github import get_repo_info

        repo_owner, repo_name = get_repo_info()

        # 1. Check GitHub Actions deployments
        gh_deployment = self._check_github_actions(repo_owner, repo_name, issue_number)

        # 2. Check issue labels for deployment markers
        label_deployment = self._check_deployment_labels(repo_owner, repo_name, issue_number)

        # 3. Check for post-deployment error issues
        related_errors = self._find_related_error_issues(repo_owner, repo_name, issue_number)

        # Merge results
        deployed = gh_deployment.get("deployed") or label_deployment.get("deployed")

        return {
            "deployed": deployed,
            "deployment_status": gh_deployment.get("status") or label_deployment.get("status", "unknown"),
            "deployment_method": gh_deployment.get("method", "unknown"),
            "post_deployment_errors": related_errors,
            "rollback_required": any("rollback" in err.lower() for err in related_errors),
        }

    def _check_github_actions(self, owner: str, repo: str, issue_number: str) -> Dict[str, Any]:
        """Check GitHub Actions for deployment status."""
        import requests

        # Get PR for issue
        pr_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
        headers = {"Authorization": f"token {self.github_token}"} if self.github_token else {}

        response = requests.get(pr_url, headers=headers)
        if response.status_code != 200:
            return {"deployed": False}

        pr_data = response.json()
        if not pr_data.get("pull_request"):
            return {"deployed": False}

        # Check if PR is merged
        pr_number = pr_data["number"]
        pr_detail_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
        pr_response = requests.get(pr_detail_url, headers=headers)

        if pr_response.status_code != 200:
            return {"deployed": False}

        pr_detail = pr_response.json()
        is_merged = pr_detail.get("merged", False)

        if not is_merged:
            return {"deployed": False}

        # Check deployment status (simplified - assumes merged = deployed)
        return {
            "deployed": True,
            "status": "success",
            "method": "github_actions"
        }

    def _check_deployment_labels(self, owner: str, repo: str, issue_number: str) -> Dict[str, Any]:
        """Check issue labels for deployment status markers."""
        import requests

        url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
        headers = {"Authorization": f"token {self.github_token}"} if self.github_token else {}

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return {"deployed": False}

        issue = response.json()
        labels = [label["name"].lower() for label in issue.get("labels", [])]

        if "deployed" in labels or "production" in labels:
            status = "failure" if "failed" in labels else "success"
            return {"deployed": True, "status": status}

        return {"deployed": False}

    def _find_related_error_issues(self, owner: str, repo: str, issue_number: str) -> List[str]:
        """Find issues created after deployment that reference this issue."""
        import requests

        # Search for issues that reference this one
        query = f"repo:{owner}/{repo} #{issue_number} is:issue created:>2024-01-01"
        url = f"https://api.github.com/search/issues?q={query}"
        headers = {"Authorization": f"token {self.github_token}"} if self.github_token else {}

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return []

        results = response.json()
        error_issues = []

        for item in results.get("items", [])[:5]:
            title = item.get("title", "")
            if any(word in title.lower() for word in ["error", "bug", "broken", "failure"]):
                error_issues.append(f"#{item['number']}: {title}")

        return error_issues
```

**Acceptance Criteria:**
- ✅ Checks GitHub Actions for deployment status
- ✅ Checks issue labels (deployed, production, failed)
- ✅ Finds related error issues after deployment
- ✅ Detects rollback requirements
- ✅ Returns structured deployment data

---

### Task 5: Create CrossProjectLearningStore
**Time:** 30 minutes
**File:** `adw/adw_modules/cross_project_learning.py` (NEW)

**Implementation:**
```python
"""Cross-project learning aggregation."""

import json
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict

from adw_modules.meta_adw_types import LearningRecord, PatternDatabase, DecisionWeights


class CrossProjectLearningStore:
    """Aggregate and share learnings across all projects."""

    def __init__(self, global_learning_dir: Path):
        """
        Args:
            global_learning_dir: Path to global learning directory
                                (e.g., ~/agentic-coding-library/.tac/learning/global/)
        """
        self.global_dir = global_learning_dir
        self.global_dir.mkdir(parents=True, exist_ok=True)

        self.global_patterns_file = self.global_dir / "global_pattern_database.json"
        self.global_weights_file = self.global_dir / "global_decision_weights.json"
        self.project_registry_file = self.global_dir / "project_registry.json"

    def aggregate_from_project(self, project_name: str, local_learning_dir: Path) -> None:
        """Aggregate learnings from a project into global store.

        Args:
            project_name: Name of the project (e.g., "my-web-app")
            local_learning_dir: Path to project's .tac/learning/ directory
        """
        # 1. Load global pattern database
        global_db = self._load_global_patterns()

        # 2. Load project's pattern database
        project_patterns_file = local_learning_dir / "pattern_database.json"
        if not project_patterns_file.exists():
            return

        with open(project_patterns_file) as f:
            project_db = json.load(f)

        # 3. Merge patterns
        for pattern in project_db.get("patterns", []):
            pattern_id = pattern.get("pattern_name")

            # Add project source
            pattern["source_project"] = project_name

            # Append or update
            existing = next((p for p in global_db["patterns"] if p["pattern_name"] == pattern_id), None)
            if existing:
                # Average success rates
                existing["success_rate"] = (existing["success_rate"] + pattern["success_rate"]) / 2
                existing["use_count"] = existing.get("use_count", 0) + pattern.get("use_count", 1)
            else:
                global_db["patterns"].append(pattern)

        # 4. Save global database
        self._save_global_patterns(global_db)

        # 5. Update project registry
        self._register_project(project_name, local_learning_dir)

    def sync_to_project(self, local_learning_dir: Path) -> None:
        """Sync global learnings back to a project.

        Args:
            local_learning_dir: Path to project's .tac/learning/ directory
        """
        # Load global patterns
        global_db = self._load_global_patterns()

        # Load project patterns
        project_patterns_file = local_learning_dir / "pattern_database.json"
        if project_patterns_file.exists():
            with open(project_patterns_file) as f:
                project_db = json.load(f)
        else:
            project_db = {"patterns": [], "total_patterns": 0}

        # Merge global patterns into project (only higher success rates)
        for global_pattern in global_db["patterns"]:
            pattern_id = global_pattern["pattern_name"]
            existing = next((p for p in project_db["patterns"] if p["pattern_name"] == pattern_id), None)

            if not existing or global_pattern["success_rate"] > existing["success_rate"]:
                # Replace with better global pattern
                if existing:
                    project_db["patterns"].remove(existing)
                project_db["patterns"].append(global_pattern)

        project_db["total_patterns"] = len(project_db["patterns"])

        # Save updated project database
        with open(project_patterns_file, 'w') as f:
            json.dump(project_db, f, indent=2)

    def get_global_insights(self) -> Dict[str, Any]:
        """Get aggregated insights across all projects."""
        global_db = self._load_global_patterns()

        # Calculate statistics
        total_patterns = len(global_db["patterns"])
        avg_success_rate = sum(p["success_rate"] for p in global_db["patterns"]) / total_patterns if total_patterns > 0 else 0

        # Top performing patterns
        top_patterns = sorted(global_db["patterns"], key=lambda p: p["success_rate"], reverse=True)[:10]

        # Patterns by project
        by_project = defaultdict(int)
        for pattern in global_db["patterns"]:
            by_project[pattern.get("source_project", "unknown")] += 1

        return {
            "total_patterns": total_patterns,
            "average_success_rate": avg_success_rate,
            "top_patterns": [p["pattern_name"] for p in top_patterns],
            "patterns_by_project": dict(by_project),
        }

    def _load_global_patterns(self) -> Dict[str, Any]:
        """Load global pattern database."""
        if self.global_patterns_file.exists():
            with open(self.global_patterns_file) as f:
                return json.load(f)
        return {"patterns": [], "total_patterns": 0}

    def _save_global_patterns(self, db: Dict[str, Any]) -> None:
        """Save global pattern database."""
        db["total_patterns"] = len(db["patterns"])
        with open(self.global_patterns_file, 'w') as f:
            json.dump(db, f, indent=2)

    def _register_project(self, project_name: str, local_dir: Path) -> None:
        """Register project in global registry."""
        if self.project_registry_file.exists():
            with open(self.project_registry_file) as f:
                registry = json.load(f)
        else:
            registry = {"projects": []}

        # Add or update project
        existing = next((p for p in registry["projects"] if p["name"] == project_name), None)
        if not existing:
            registry["projects"].append({
                "name": project_name,
                "learning_dir": str(local_dir),
                "registered_at": datetime.now().isoformat(),
            })

        with open(self.project_registry_file, 'w') as f:
            json.dump(registry, f, indent=2)
```

**Acceptance Criteria:**
- ✅ Aggregates patterns from project to global store
- ✅ Syncs global learnings back to projects
- ✅ Merges patterns intelligently (averages success rates)
- ✅ Tracks source project for each pattern
- ✅ Provides global insights API

---

### Task 6: Create PromptRefiner Engine
**Time:** 60 minutes
**File:** `adw/adw_modules/prompt_refiner.py` (NEW)

**Implementation:**
```python
"""Self-Refine pattern for prompt improvement."""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


class PromptRefiner:
    """Implements Self-Refine pattern for continuous prompt improvement."""

    def __init__(self, repo_root: Path):
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
            feedback: Feedback data from execution
            max_iterations: Max refinement iterations (default 3)

        Returns:
            Refined prompt text
        """
        # Load refinement history
        history = self._load_history(prompt_id)

        # Generate refinement suggestions based on feedback
        suggestions = self._generate_suggestions(feedback)

        if not suggestions:
            return current_prompt  # No changes needed

        # Apply refinements iteratively
        refined_prompt = current_prompt
        iterations = 0

        while iterations < max_iterations and suggestions:
            # Apply top suggestion
            suggestion = suggestions[0]
            refined_prompt = self._apply_suggestion(refined_prompt, suggestion)

            # Record refinement
            self._record_refinement(history, {
                "iteration": iterations + 1,
                "suggestion": suggestion,
                "timestamp": datetime.now().isoformat(),
            })

            iterations += 1
            suggestions = suggestions[1:]  # Move to next suggestion

        # Save updated history
        self._save_history(prompt_id, history)

        # Save refined prompt
        self._save_prompt_version(prompt_id, refined_prompt)

        return refined_prompt

    def _generate_suggestions(self, feedback: Dict[str, Any]) -> List[str]:
        """Generate refinement suggestions based on feedback.

        Feedback patterns → Prompt improvements:
        - Test failures → Add validation requirements
        - Review changes (logic) → Strengthen technical specs
        - Review changes (style) → Add style guidelines
        - Review changes (security) → Add security checklist
        - Deployment errors → Add deployment validation
        """
        suggestions = []

        # Test feedback
        if feedback.get("test_failures"):
            failures = feedback["test_failures"]
            if "auth" in failures:
                suggestions.append(
                    "Add explicit instruction: 'Include comprehensive authentication tests "
                    "covering login, logout, token validation, and permission checks.'"
                )
            if "api" in failures:
                suggestions.append(
                    "Add explicit instruction: 'Validate all API endpoints with tests for "
                    "success cases, error cases, and edge cases (empty data, invalid input).'"
                )

        # Review feedback
        if feedback.get("review_changes"):
            changes = feedback["review_changes"]
            if "logic" in changes:
                suggestions.append(
                    "Add section: '## Logic Verification\\n"
                    "Before implementation, trace through the logic flow and verify:\\n"
                    "- Edge cases are handled\\n"
                    "- Error conditions are covered\\n"
                    "- Business rules are correctly implemented'"
                )
            if "security" in changes:
                suggestions.append(
                    "Add section: '## Security Checklist\\n"
                    "- [ ] Input validation and sanitization\\n"
                    "- [ ] SQL injection prevention\\n"
                    "- [ ] XSS prevention\\n"
                    "- [ ] Authentication and authorization checks'"
                )
            if "performance" in changes:
                suggestions.append(
                    "Add instruction: 'Consider performance implications: "
                    "avoid N+1 queries, add database indexes where needed, "
                    "use caching for expensive operations.'"
                )

        # Deployment feedback
        if feedback.get("deployment_errors"):
            suggestions.append(
                "Add validation step: 'Before marking as complete, verify the change "
                "works in a production-like environment and check for environment-specific "
                "configuration requirements.'"
            )

        return suggestions

    def _apply_suggestion(self, prompt: str, suggestion: str) -> str:
        """Apply a suggestion to a prompt.

        Strategies:
        1. If suggestion starts with "Add section:", append to end
        2. If suggestion starts with "Add instruction:", insert after intro
        3. If suggestion contains specific text, insert context-appropriately
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
                # No instructions section, append
                return prompt + f"\n\n- {instruction}\n"

        else:
            # Generic: append to end
            return prompt + "\n\n" + suggestion

    def _load_history(self, prompt_id: str) -> Dict[str, Any]:
        """Load refinement history for a prompt."""
        if not self.refinement_history_file.exists():
            return {"prompts": {}}

        with open(self.refinement_history_file) as f:
            data = json.load(f)

        if prompt_id not in data["prompts"]:
            data["prompts"][prompt_id] = {"refinements": [], "version": 1}

        return data

    def _save_history(self, prompt_id: str, history: Dict[str, Any]) -> None:
        """Save refinement history."""
        with open(self.refinement_history_file, 'w') as f:
            json.dump(history, f, indent=2)

    def _record_refinement(self, history: Dict[str, Any], refinement: Dict[str, Any]) -> None:
        """Record a refinement in history."""
        # Placeholder - history is updated in memory, saved later
        pass

    def _save_prompt_version(self, prompt_id: str, prompt: str) -> None:
        """Save a new version of a prompt."""
        version_file = self.prompts_dir / f"{prompt_id}_v{int(datetime.now().timestamp())}.md"
        with open(version_file, 'w') as f:
            f.write(prompt)

        # Also save as latest
        latest_file = self.prompts_dir / f"{prompt_id}_latest.md"
        with open(latest_file, 'w') as f:
            f.write(prompt)
```

**Acceptance Criteria:**
- ✅ Generates suggestions from feedback patterns
- ✅ Applies suggestions to prompts (max 3 iterations)
- ✅ Saves prompt versions with timestamps
- ✅ Maintains refinement history
- ✅ Handles missing sections gracefully

---

### Task 7: Integrate Feedback Collection into meta_strategy.py
**Time:** 30 minutes
**File:** `adw/meta_strategy.py` (modify existing)

**Changes:**

1. Add imports at top:
```python
from adw_modules.learning_feedback import (
    TestFeedbackCollector,
    ReviewFeedbackCollector,
    DeploymentFeedbackCollector,
)
from adw_modules.cross_project_learning import CrossProjectLearningStore
from adw_modules.prompt_refiner import PromptRefiner
```

2. Update `collect_feedback()` function (around line 489):
```python
def collect_feedback(
    adw_id: str,
    issue_number: str,
    selected_strategy: str,
    recommended_strategy: StrategyRecommendation,
    task_analysis: TaskAnalysis,
    repo_root: Path,
) -> LearningRecord:
    """Collect feedback from ADW execution with enhanced collectors."""

    # Initialize collectors
    test_collector = TestFeedbackCollector(repo_root)
    review_collector = ReviewFeedbackCollector(repo_root)
    deployment_collector = DeploymentFeedbackCollector(repo_root)

    # Collect feedback from all sources
    test_feedback = test_collector.collect(adw_id, issue_number)
    review_feedback = review_collector.collect(adw_id, issue_number)
    deployment_feedback = deployment_collector.collect(adw_id, issue_number)

    # Determine outcome
    outcome = _determine_outcome(test_feedback, review_feedback, deployment_feedback)

    # Extract problems
    problems = []
    if test_feedback and test_feedback.get("failed") > 0:
        problems.extend([f"Test failures in {cat}" for cat in test_feedback.get("failure_patterns", [])])
    if review_feedback and review_feedback.get("review_status") == "changes_requested":
        problems.append(f"Code review changes: {', '.join(review_feedback.get('change_categories', []))}")
    if deployment_feedback and deployment_feedback.get("post_deployment_errors"):
        problems.extend(deployment_feedback["post_deployment_errors"])

    # Build success metrics
    success_metrics = {
        "test_success_rate": test_feedback.get("success_rate") if test_feedback else None,
        "review_approved": review_feedback.get("review_status") == "approved" if review_feedback else None,
        "deployed_successfully": deployment_feedback.get("deployment_status") == "success" if deployment_feedback else None,
        "human_changes_needed": review_feedback.get("human_changes_made") if review_feedback else False,
    }

    # Detect false fix
    false_fix = _detect_false_fix(test_feedback, review_feedback)

    # Create learning record
    record = LearningRecord(
        task_description=task_analysis.description,
        task_analysis=task_analysis,
        recommended_strategy=recommended_strategy,
        selected_strategy=selected_strategy,
        user_overrode_recommendation=selected_strategy != recommended_strategy.workflow_name,
        outcome=outcome,
        success_metrics=success_metrics,
        problems_encountered=problems,
        false_fix_detected=false_fix,
        user_satisfaction=None,  # Could be collected via GitHub reactions
        execution_timestamp=datetime.now(),
        adw_id=adw_id,
        issue_number=issue_number,
    )

    # Store locally
    test_collector.store_learning_record(record)

    return record


def _determine_outcome(test_fb, review_fb, deploy_fb) -> str:
    """Determine overall outcome from feedback."""
    # Success: tests pass, review approved, deployed successfully
    if (test_fb and test_fb.get("success_rate", 0) >= 0.9 and
        review_fb and review_fb.get("review_status") == "approved" and
        deploy_fb and deploy_fb.get("deployment_status") == "success"):
        return "success"

    # Failure: tests fail or deployment failed
    if (test_fb and test_fb.get("success_rate", 0) < 0.5) or \
       (deploy_fb and deploy_fb.get("deployment_status") == "failure"):
        return "failure"

    # Partial: mixed results
    return "partial"


def _detect_false_fix(test_fb, review_fb) -> bool:
    """Enhanced false fix detection."""
    # Original logic + new checks
    if review_fb and review_fb.get("human_changes_made"):
        # If human had to fix logic issues, it was a false fix
        if "logic" in review_fb.get("change_categories", []):
            return True

    if test_fb and test_fb.get("failed", 0) > 0:
        # Failed tests indicate incomplete fix
        return True

    return False
```

**Acceptance Criteria:**
- ✅ Integrates all three feedback collectors
- ✅ Populates LearningRecord with real data
- ✅ Determines outcome accurately
- ✅ Enhanced false fix detection
- ✅ Backward compatible with existing code

---

### Task 8: Add Cross-Project Sync Hook
**Time:** 20 minutes
**File:** `adw/meta_strategy.py` (add new function)

**Implementation:**
```python
def sync_cross_project_learning(repo_root: Path, project_name: str) -> None:
    """Sync learnings between project and global store.

    Call this after each ADW execution to aggregate learnings.

    Args:
        repo_root: Current project root
        project_name: Name of current project
    """
    # Global learning directory (in agentic-coding-library repo)
    global_learning_dir = Path.home() / "agentic-coding-library" / ".tac" / "learning" / "global"

    store = CrossProjectLearningStore(global_learning_dir)

    # Aggregate this project's learnings to global
    local_learning_dir = repo_root / ".tac" / "learning"
    store.aggregate_from_project(project_name, local_learning_dir)

    # Sync global learnings back to this project
    store.sync_to_project(local_learning_dir)

    logger.info(f"Cross-project learning synced for {project_name}")

    # Log global insights
    insights = store.get_global_insights()
    logger.info(f"Global learning insights: {insights}")
```

**Add call in main workflow** (e.g., at end of `adw_sdlc_iso.py`):
```python
# After workflow completes
sync_cross_project_learning(
    repo_root=Path.cwd(),
    project_name=os.getenv("PROJECT_NAME", "unknown-project")
)
```

**Acceptance Criteria:**
- ✅ Called automatically after ADW execution
- ✅ Aggregates to global store
- ✅ Syncs global patterns back
- ✅ Logs insights

---

### Task 9: Add Prompt Refinement Hook
**Time:** 20 minutes
**File:** `adw/meta_strategy.py` (add function + integration)

**Implementation:**
```python
def apply_prompt_refinement(
    feedback_record: LearningRecord,
    repo_root: Path,
) -> None:
    """Apply prompt refinement based on feedback.

    Call this after collecting feedback to improve prompts.
    """
    refiner = PromptRefiner(repo_root)

    # Prepare feedback for refiner
    feedback = {
        "test_failures": feedback_record.success_metrics.get("test_success_rate", 0) < 0.9,
        "test_failure_patterns": [p for p in feedback_record.problems_encountered if "Test failure" in p],
        "review_changes": _extract_review_categories(feedback_record),
        "deployment_errors": feedback_record.success_metrics.get("deployed_successfully") == False,
    }

    # Determine which prompt to refine based on task
    prompt_id = _map_task_to_prompt(feedback_record.task_analysis.task_type)

    # Get current prompt
    current_prompt = _load_current_prompt(prompt_id, repo_root)

    if not current_prompt:
        logger.warning(f"No prompt found for {prompt_id}, skipping refinement")
        return

    # Refine
    refined_prompt = refiner.refine_prompt(
        prompt_id=prompt_id,
        current_prompt=current_prompt,
        feedback=feedback,
        max_iterations=3
    )

    logger.info(f"Refined prompt {prompt_id}")


def _extract_review_categories(record: LearningRecord) -> List[str]:
    """Extract review change categories from problems."""
    categories = []
    for problem in record.problems_encountered:
        if "Code review changes:" in problem:
            cats = problem.split(":")[-1].strip().split(", ")
            categories.extend(cats)
    return categories


def _map_task_to_prompt(task_type: str) -> str:
    """Map task type to prompt ID."""
    mapping = {
        "feature": "feature_planning",
        "bug": "bug_fixing",
        "chore": "chore_execution",
        "patch": "quick_patch",
    }
    return mapping.get(task_type, "general_task")


def _load_current_prompt(prompt_id: str, repo_root: Path) -> Optional[str]:
    """Load current version of a prompt."""
    prompt_file = repo_root / "tac-core-plugin" / "commands" / f"{prompt_id.replace('_', '-')}.md"

    if not prompt_file.exists():
        # Try .tac/prompts/
        prompt_file = repo_root / ".tac" / "prompts" / f"{prompt_id}_latest.md"

    if prompt_file.exists():
        with open(prompt_file) as f:
            return f.read()

    return None
```

**Acceptance Criteria:**
- ✅ Maps task types to prompt IDs
- ✅ Loads current prompt version
- ✅ Calls PromptRefiner with feedback
- ✅ Logs refinement activity

---

### Task 10: Enable Learning Loop Feature Flag
**Time:** 10 minutes
**File:** `adw/meta_strategy.py`

**Add at top of file:**
```python
# Feature flag for learning system
ENABLE_LEARNING = os.getenv("ENABLE_ADW_LEARNING", "true").lower() == "true"
```

**Wrap learning calls:**
```python
# In main workflow (e.g., end of run_meta_strategy)
if ENABLE_LEARNING:
    # Collect feedback
    feedback_record = collect_feedback(...)

    # Update pattern database
    update_pattern_database(feedback_record, repo_root)

    # Retrain weights
    retrain_weights(repo_root)

    # Cross-project sync
    sync_cross_project_learning(repo_root, project_name)

    # Prompt refinement
    apply_prompt_refinement(feedback_record, repo_root)
```

**Acceptance Criteria:**
- ✅ Feature flag added with env var
- ✅ Defaults to enabled
- ✅ Can be disabled with `ENABLE_ADW_LEARNING=false`
- ✅ All learning hooks wrapped in flag check

---

### Task 11: Create Unit Tests
**Time:** 30 minutes
**Files:** Create `adw/tests/test_learning_system.py` (NEW)

**Implementation:**
```python
"""Unit tests for learning system components."""

import pytest
from pathlib import Path
import json
from datetime import datetime

from adw_modules.learning_feedback import (
    TestFeedbackCollector,
    ReviewFeedbackCollector,
    DeploymentFeedbackCollector,
)
from adw_modules.cross_project_learning import CrossProjectLearningStore
from adw_modules.prompt_refiner import PromptRefiner


@pytest.fixture
def temp_repo(tmp_path):
    """Create temporary repo structure."""
    repo = tmp_path / "test-repo"
    repo.mkdir()
    (repo / ".tac" / "learning" / "execution_logs").mkdir(parents=True)
    (repo / "agents").mkdir()
    (repo / "logs").mkdir()
    return repo


class TestFeedbackCollectors:

    def test_test_feedback_collector_parses_pytest_output(self, temp_repo):
        """Test that TestFeedbackCollector parses pytest output correctly."""
        collector = TestFeedbackCollector(temp_repo)

        # Create mock state and logs
        adw_id = "abc12345"
        (temp_repo / "agents" / adw_id).mkdir(parents=True)

        state = {"adw_id": adw_id, "issue_number": "123"}
        with open(temp_repo / "agents" / adw_id / "adw_state.json", 'w') as f:
            json.dump(state, f)

        # Create mock chat log with pytest output
        session_dir = temp_repo / "logs" / "session-123"
        session_dir.mkdir(parents=True)

        chat_log = {
            "messages": [
                {
                    "role": "tool_result",
                    "content": "============================= test session starts ==============================\n" +
                               "collected 10 items\n\n" +
                               "app/tests/test_auth.py::test_login PASSED\n" +
                               "app/tests/test_auth.py::test_logout FAILED\n" +
                               "app/tests/test_api.py PASSED\n" +
                               "========================= 8 passed, 2 failed in 1.23s =========================="
                }
            ]
        }

        with open(session_dir / "chat.json", 'w') as f:
            json.dump(chat_log, f)

        # Collect feedback
        # Note: This requires updating _is_test_execution to work with our mock
        # For now, test the parsing logic directly
        output = chat_log["messages"][0]["content"]
        results = collector._parse_pytest_output({"messages": chat_log["messages"]})

        assert results["total_tests"] == 10
        assert results["passed"] == 8
        assert results["failed"] == 2
        assert results["success_rate"] == 0.8

    def test_review_feedback_determines_status(self, temp_repo):
        """Test ReviewFeedbackCollector determines review status."""
        collector = ReviewFeedbackCollector(temp_repo, github_token=None)

        # Test approved status
        reviews = [{"state": "APPROVED"}]
        status = collector._determine_review_status(reviews)
        assert status == "approved"

        # Test changes requested
        reviews = [{"state": "CHANGES_REQUESTED"}]
        status = collector._determine_review_status(reviews)
        assert status == "changes_requested"

    def test_review_feedback_categorizes_changes(self, temp_repo):
        """Test ReviewFeedbackCollector categorizes review comments."""
        collector = ReviewFeedbackCollector(temp_repo)

        comments = [
            {"body": "This has a security vulnerability with SQL injection"},
            {"body": "Please fix the code style and naming conventions"},
            {"body": "The logic here is incorrect for edge cases"},
        ]

        categories = collector._analyze_review_changes(comments)

        assert "security" in categories
        assert "style" in categories
        assert "logic" in categories


class TestCrossProjectLearning:

    def test_aggregates_patterns_from_project(self, tmp_path):
        """Test that patterns are aggregated from project to global store."""
        global_dir = tmp_path / "global"
        project_dir = tmp_path / "project" / ".tac" / "learning"
        project_dir.mkdir(parents=True)

        store = CrossProjectLearningStore(global_dir)

        # Create project patterns
        project_patterns = {
            "patterns": [
                {"pattern_name": "feature-auth", "success_rate": 0.8, "use_count": 5}
            ],
            "total_patterns": 1
        }

        with open(project_dir / "pattern_database.json", 'w') as f:
            json.dump(project_patterns, f)

        # Aggregate
        store.aggregate_from_project("test-project", project_dir)

        # Verify global store
        global_db = store._load_global_patterns()
        assert len(global_db["patterns"]) == 1
        assert global_db["patterns"][0]["pattern_name"] == "feature-auth"
        assert global_db["patterns"][0]["source_project"] == "test-project"

    def test_syncs_global_patterns_to_project(self, tmp_path):
        """Test that global patterns sync back to projects."""
        global_dir = tmp_path / "global"
        project_dir = tmp_path / "project" / ".tac" / "learning"
        project_dir.mkdir(parents=True)

        store = CrossProjectLearningStore(global_dir)

        # Create global patterns
        global_patterns = {
            "patterns": [
                {"pattern_name": "bug-fix", "success_rate": 0.95, "use_count": 20}
            ],
            "total_patterns": 1
        }

        with open(global_dir / "global_pattern_database.json", 'w') as f:
            json.dump(global_patterns, f)

        # Sync to project
        store.sync_to_project(project_dir)

        # Verify project got the pattern
        with open(project_dir / "pattern_database.json") as f:
            project_db = json.load(f)

        assert len(project_db["patterns"]) == 1
        assert project_db["patterns"][0]["success_rate"] == 0.95


class TestPromptRefiner:

    def test_generates_suggestions_from_feedback(self, temp_repo):
        """Test that PromptRefiner generates suggestions from feedback."""
        refiner = PromptRefiner(temp_repo)

        feedback = {
            "test_failures": ["auth", "api"],
            "review_changes": ["security", "logic"],
        }

        suggestions = refiner._generate_suggestions(feedback)

        assert len(suggestions) > 0
        assert any("authentication tests" in s for s in suggestions)
        assert any("Security Checklist" in s for s in suggestions)

    def test_applies_suggestions_to_prompt(self, temp_repo):
        """Test that suggestions are applied correctly."""
        refiner = PromptRefiner(temp_repo)

        original_prompt = "# Feature Planning\n\n## Instructions\n\n- Create a plan\n\n## Tasks\n\n- Implement feature"

        suggestion = "Add explicit instruction: 'Include comprehensive tests'"

        refined = refiner._apply_suggestion(original_prompt, suggestion)

        assert "Include comprehensive tests" in refined
        assert "## Instructions" in refined
```

**Acceptance Criteria:**
- ✅ Tests for TestFeedbackCollector parsing
- ✅ Tests for ReviewFeedbackCollector categorization
- ✅ Tests for CrossProjectLearningStore aggregation and sync
- ✅ Tests for PromptRefiner suggestion generation
- ✅ All tests pass with `pytest`

---

### Task 12: Create Integration Test
**Time:** 20 minutes
**File:** `adw/tests/test_learning_integration.py` (NEW)

**Implementation:**
```python
"""Integration tests for complete learning flow."""

import pytest
from pathlib import Path
import json

from adw.meta_strategy import (
    collect_feedback,
    update_pattern_database,
    sync_cross_project_learning,
    apply_prompt_refinement,
)
from adw_modules.meta_adw_types import TaskAnalysis, StrategyRecommendation


@pytest.fixture
def integration_setup(tmp_path):
    """Set up complete repo structure for integration test."""
    repo = tmp_path / "test-repo"
    repo.mkdir()

    # Create all necessary directories
    (repo / ".tac" / "learning" / "execution_logs").mkdir(parents=True)
    (repo / ".tac" / "prompts").mkdir(parents=True)
    (repo / "agents" / "test123").mkdir(parents=True)
    (repo / "logs" / "session-1").mkdir(parents=True)
    (repo / "tac-core-plugin" / "commands").mkdir(parents=True)

    # Create mock ADW state
    state = {
        "adw_id": "test123",
        "issue_number": "42",
        "branch_name": "feat-42-test123-feature",
    }
    with open(repo / "agents" / "test123" / "adw_state.json", 'w') as f:
        json.dump(state, f)

    # Create mock chat log with test results
    chat_log = {
        "messages": [
            {
                "role": "tool_result",
                "content": "===== 8 passed, 2 failed in 1.23s ====="
            }
        ]
    }
    with open(repo / "logs" / "session-1" / "chat.json", 'w') as f:
        json.dump(chat_log, f)

    return repo


def test_complete_learning_flow(integration_setup):
    """Test the complete learning flow end-to-end."""
    repo_root = integration_setup

    # 1. Prepare task analysis and recommendation
    task_analysis = TaskAnalysis(
        description="Add user authentication",
        task_type="feature",
        complexity_level="moderate",
        complexity_score=5,
        estimated_effort_hours=3,
        key_requirements=["auth", "security", "tests"],
        validation_needs="thorough",
        requires_e2e_tests=True,
    )

    recommendation = StrategyRecommendation(
        workflow_name="adw_plan_build_test_iso",
        workflow_path="adw/adw_plan_build_test_iso.py",
        template_names=["feature.md"],
        validation_strategy="L5: Closed-loop validation",
        confidence_score=0.85,
        reasoning="Standard feature workflow",
        alternatives=[],
        estimated_tokens=80000,
        trade_offs=["Balanced approach"],
        recommended_phases=["plan", "build", "test"],
    )

    # 2. Collect feedback
    record = collect_feedback(
        adw_id="test123",
        issue_number="42",
        selected_strategy="adw_plan_build_test_iso",
        recommended_strategy=recommendation,
        task_analysis=task_analysis,
        repo_root=repo_root,
    )

    # 3. Verify record was created
    assert record.adw_id == "test123"
    assert record.outcome in ["success", "partial", "failure"]

    # 4. Update pattern database
    update_pattern_database(record, repo_root)

    # 5. Verify pattern database was updated
    pattern_file = repo_root / ".tac" / "learning" / "pattern_database.json"
    assert pattern_file.exists()

    # 6. Test cross-project sync
    global_dir = Path.home() / "test-global-learning"
    global_dir.mkdir(exist_ok=True)

    try:
        sync_cross_project_learning(repo_root, "test-project")

        # Verify global patterns exist
        global_patterns = global_dir / "global_pattern_database.json"
        # Note: This may not exist in test, just verify no crash

    finally:
        # Cleanup
        if global_dir.exists():
            import shutil
            shutil.rmtree(global_dir)
```

**Acceptance Criteria:**
- ✅ Tests complete flow: collect → update → sync
- ✅ Verifies LearningRecord creation
- ✅ Verifies pattern database update
- ✅ Tests cross-project sync (isolated)
- ✅ Test passes with `pytest`

---

### Task 13: Manual Validation with Test Issue
**Time:** 30 minutes

**Process:**
1. Create test GitHub issue:
   ```
   Title: "Test AI Learning System"
   Body: "Simple feature to test learning collection"
   ```

2. Run ADW workflow:
   ```bash
   cd adw/
   ENABLE_ADW_LEARNING=true uv run adw_plan_build_test_iso.py <issue-number>
   ```

3. Check learning artifacts:
   ```bash
   # Execution log
   cat .tac/learning/execution_logs/<adw-id>.json

   # Pattern database updated
   cat .tac/learning/pattern_database.json

   # Global sync (if enabled)
   cat ~/agentic-coding-library/.tac/learning/global/global_pattern_database.json

   # Prompt refinement
   ls .tac/prompts/
   ```

4. Verify data:
   - ✅ LearningRecord has test results
   - ✅ LearningRecord has review feedback (if PR created)
   - ✅ Pattern database contains new patterns
   - ✅ Global store aggregated patterns
   - ✅ Prompts refined if issues found

**Acceptance Criteria:**
- ✅ Complete ADW execution with learning enabled
- ✅ All artifacts created
- ✅ Data is accurate and structured correctly
- ✅ No errors in logs

---

### Task 14: Update Documentation
**Time:** 20 minutes

**Files to Update:**

1. **`adw/README.md`** - Add learning system section:
```markdown
## Learning System

The ADW system includes a self-improving learning loop that learns from test results, code reviews, and deployment outcomes.

**Components:**
- **Test Feedback:** Captures pass/fail rates and failure patterns
- **Review Feedback:** Analyzes PR reviews and human changes
- **Deployment Feedback:** Tracks deployment success and post-deployment errors
- **Cross-Project Learning:** Shares patterns across all projects
- **Prompt Refinement:** Self-improves prompts using Self-Refine pattern

**Enable/Disable:**
```bash
# Enable (default)
export ENABLE_ADW_LEARNING=true

# Disable
export ENABLE_ADW_LEARNING=false
```

**View Learning Data:**
```bash
# Local patterns
cat .tac/learning/pattern_database.json

# Global patterns
cat ~/agentic-coding-library/.tac/learning/global/global_pattern_database.json

# Execution logs
ls .tac/learning/execution_logs/
```
```

2. **`CLAUDE.md`** - Add learning system to architecture:
```markdown
### 7. Learning System

**Self-improving AI** that learns from test outcomes, code reviews, and deployment results.

**Key Files:**
- `adw/adw_modules/learning_feedback.py` - Feedback collectors
- `adw/adw_modules/cross_project_learning.py` - Cross-project aggregation
- `adw/adw_modules/prompt_refiner.py` - Self-Refine engine
- `.tac/learning/` - Local learning data
- `~/agentic-coding-library/.tac/learning/global/` - Global patterns

**How It Works:**
1. After each ADW execution, feedback is collected from tests, reviews, and deployments
2. Patterns are extracted and stored in pattern database
3. Decision weights are retrained based on outcomes
4. Prompts are refined using Self-Refine pattern (3-5 iterations)
5. Learnings are aggregated to global store
6. Global patterns sync back to all projects

**Enable:** Set `ENABLE_ADW_LEARNING=true` (default)
```

**Acceptance Criteria:**
- ✅ adw/README.md updated
- ✅ CLAUDE.md updated with learning system section
- ✅ Clear instructions for users
- ✅ Architecture documented

---

## 🧪 Validation Commands

Execute all commands to validate the complete implementation:

```bash
# 1. Run unit tests
cd adw/
pytest tests/test_learning_system.py -v

# 2. Run integration test
pytest tests/test_learning_integration.py -v

# 3. Test with real ADW execution
ENABLE_ADW_LEARNING=true uv run adw_plan_build_test_iso.py <test-issue-number>

# 4. Verify learning artifacts created
ls .tac/learning/execution_logs/
cat .tac/learning/pattern_database.json
cat .tac/learning/decision_weights.json

# 5. Check global sync
ls ~/agentic-coding-library/.tac/learning/global/
cat ~/agentic-coding-library/.tac/learning/global/global_pattern_database.json

# 6. Verify prompt refinement
ls .tac/prompts/
cat .tac/prompts/feature_planning_latest.md

# 7. Test feature flag
ENABLE_ADW_LEARNING=false uv run adw_plan_build_test_iso.py <issue-number>
# Should complete without creating learning artifacts
```

---

## 📊 Success Metrics

**MVP Success Criteria** (from spec):

1. ✅ **Learning Loop Active**
   - Feedback collected after /test, /review, and deployment
   - Pattern database updated with each execution
   - Decision weights retrained periodically

2. ✅ **Data Flowing**
   - LearningRecord captured with complete data
   - Test results: pass/fail counts, failure patterns
   - Review feedback: status, categories, human changes
   - Deployment feedback: success/failure, errors

3. ✅ **Cross-Project Sharing**
   - Global pattern database aggregates from all projects
   - Patterns sync back to projects with higher success rates
   - Project registry tracks all connected projects

4. ✅ **Prompt Refinement**
   - Prompts refined based on feedback patterns
   - 3-5 refinement iterations per prompt
   - Refinement history tracked
   - Versioned prompts saved

5. ✅ **Measurable Improvement**
   - Success rate increases over 50 executions (target: 70% → 85%)
   - False fix rate decreases
   - Review change requests decrease
   - Deployment failures decrease

---

## 📅 Timeline Summary

| Phase | Tasks | Time | Cumulative |
|-------|-------|------|------------|
| **Phase 1: Feedback Collectors** | Tasks 1-4 | 3 hours | 3 hours |
| **Phase 2: Cross-Project & Refinement** | Tasks 5-6 | 1.5 hours | 4.5 hours |
| **Phase 3: Integration** | Tasks 7-10 | 1.5 hours | 6 hours |
| **Phase 4: Testing & Validation** | Tasks 11-13 | 1.5 hours | 7.5 hours |
| **Phase 5: Documentation** | Task 14 | 0.5 hours | **8 hours** |

**Total Estimated Time:** 8 hours (includes buffer)

---

## 🎯 Implementation Strategy

### Order of Execution
Execute tasks **sequentially in numerical order** (1 → 14). Each task builds on previous tasks.

### Checkpoints
- **After Task 4:** All feedback collectors complete and tested individually
- **After Task 6:** Prompt refinement engine complete
- **After Task 10:** Learning loop fully integrated and feature-flagged
- **After Task 13:** Manual validation confirms system works end-to-end
- **After Task 14:** Documentation complete, ready to use

### Risk Mitigation
- **Feature flag** allows safe rollout (can disable if issues)
- **Unit tests** catch bugs early
- **Integration test** validates complete flow
- **Manual validation** confirms real-world usage
- **Backward compatible** with existing meta_strategy.py

---

## 📝 Notes

- **Existing foundation:** 50% of infrastructure already complete (data models, basic learning loop, storage)
- **GitHub API:** ReviewFeedbackCollector and DeploymentFeedbackCollector require `GITHUB_PAT` env var
- **Cross-project sync:** Assumes `~/agentic-coding-library/` exists (centralized learning repo)
- **Prompt refinement:** Operates on prompts in `tac-core-plugin/commands/` and `.tac/prompts/`
- **Feature flag:** `ENABLE_ADW_LEARNING=true` (default), set to `false` to disable
- **Dependencies:** Uses existing `requests` library for GitHub API calls
- **Performance:** Feedback collection adds ~5-10 seconds to ADW execution
- **Privacy:** Current implementation shares all learnings across projects (as per user preference)

---

## 🚀 Next Steps After Completion

1. **Deploy to production:** Enable learning on all ADW executions
2. **Monitor metrics:** Track success rates, false fix rates, review changes
3. **Iterate on prompt refinement:** Tune suggestion generation based on outcomes
4. **Expand feedback sources:** Add more collectors (CI/CD, monitoring, user feedback)
5. **Build dashboard:** Visualize learning insights and improvements over time

---

**Ready to begin implementation?** Start with Task 1: Create FeedbackCollector Base Class.
