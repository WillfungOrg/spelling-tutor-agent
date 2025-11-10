"""Feedback collection system for AI learning.

This module provides collectors for gathering feedback from different sources:
- Test executions (pytest results)
- Code reviews (GitHub PR reviews)
- Deployments (GitHub Actions, labels)

All collectors inherit from FeedbackCollector base class.
"""

import os
import re
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from adw_modules.meta_adw_types import LearningRecord, TaskAnalysis, StrategyRecommendation


logger = logging.getLogger(__name__)


class FeedbackCollector:
    """Base class for collecting feedback from different sources."""

    def __init__(self, repo_root: Path):
        """Initialize feedback collector.

        Args:
            repo_root: Path to repository root
        """
        self.repo_root = repo_root
        self.learning_dir = repo_root / ".tac" / "learning"
        self.learning_dir.mkdir(parents=True, exist_ok=True)

    def collect(self, adw_id: str, issue_number: str) -> Optional[Dict[str, Any]]:
        """Collect feedback for a specific ADW execution.

        Args:
            adw_id: ADW execution ID (e.g., "abc12345")
            issue_number: GitHub issue number

        Returns:
            Dict with feedback data or None if not available
        """
        raise NotImplementedError("Subclasses must implement collect()")

    def store_learning_record(self, record: LearningRecord) -> None:
        """Store a learning record in the execution logs.

        Args:
            record: LearningRecord to store
        """
        log_dir = self.learning_dir / "execution_logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / f"{record.adw_id}.json"

        with open(log_file, 'w') as f:
            json.dump(record.model_dump(), f, indent=2, default=str)

        logger.info(f"Stored learning record for ADW {record.adw_id} at {log_file}")


class TestFeedbackCollector(FeedbackCollector):
    """Collect feedback from ADW test executions."""

    def collect(self, adw_id: str, issue_number: str) -> Optional[Dict[str, Any]]:
        """Parse test results from adw_test_iso.py execution.

        Args:
            adw_id: ADW execution ID
            issue_number: GitHub issue number

        Returns:
            {
                "total_tests": int,
                "passed": int,
                "failed": int,
                "failure_patterns": List[str],
                "test_output": str,
                "success_rate": float
            }
            or None if no test data available
        """
        # 1. Find agent state
        agent_dir = self.repo_root / "agents" / adw_id
        state_file = agent_dir / "adw_state.json"

        if not state_file.exists():
            logger.warning(f"No state file found for ADW {adw_id}")
            return None

        with open(state_file) as f:
            state = json.load(f)

        # 2. Find test execution logs
        logs_dir = self.repo_root / "logs"
        if not logs_dir.exists():
            logger.warning(f"No logs directory found at {logs_dir}")
            return None

        test_logs = []

        for session_dir in logs_dir.iterdir():
            if not session_dir.is_dir():
                continue
            chat_file = session_dir / "chat.json"
            if chat_file.exists():
                try:
                    with open(chat_file) as f:
                        chat = json.load(f)
                        # Check if this is a test execution for our ADW
                        if self._is_test_execution(chat, adw_id):
                            test_logs.append(chat)
                except (json.JSONDecodeError, Exception) as e:
                    logger.debug(f"Could not parse {chat_file}: {e}")
                    continue

        if not test_logs:
            logger.info(f"No test execution logs found for ADW {adw_id}")
            return None

        # 3. Parse most recent test results
        latest_test = test_logs[-1]
        results = self._parse_pytest_output(latest_test)

        logger.info(f"Collected test feedback for ADW {adw_id}: {results.get('total_tests', 0)} tests, "
                   f"{results.get('success_rate', 0):.1%} success rate")

        return results

    def _is_test_execution(self, chat_log: Dict, adw_id: str) -> bool:
        """Check if chat log is from a test execution for this ADW.

        Args:
            chat_log: Chat log JSON data
            adw_id: ADW execution ID to match

        Returns:
            True if this is a test execution for the ADW
        """
        # Look for pytest-related content in messages
        has_pytest_command = False
        has_adw_reference = False

        for message in chat_log.get("messages", []):
            content = str(message.get("content", ""))
            if "pytest" in content.lower() or "test session starts" in content.lower():
                has_pytest_command = True
            if adw_id in content:
                has_adw_reference = True

        # Accept if we have pytest content (even without explicit ADW reference)
        # since we're already filtering by ADW directory
        return has_pytest_command

    def _parse_pytest_output(self, chat_log: Dict) -> Dict[str, Any]:
        """Extract test metrics from pytest output.

        Args:
            chat_log: Chat log containing pytest execution

        Returns:
            Dict with test metrics
        """
        output = self._get_test_output(chat_log)

        # Parse pytest output format:
        # "X passed, Y failed in Z.ZZs"
        # "FAILED app/tests/test_foo.py::test_bar - AssertionError: ..."

        passed = 0
        failed = 0
        failure_patterns = []

        # Look for summary line - use re.DOTALL to match across newlines
        summary_match = re.search(r"(\d+) passed[,\s]+(\d+) failed", output, re.DOTALL)
        if summary_match:
            passed = int(summary_match.group(1))
            failed = int(summary_match.group(2))
        else:
            # Try single stats
            passed_match = re.search(r"(\d+) passed", output)
            if passed_match:
                passed = int(passed_match.group(1))

            failed_match = re.search(r"(\d+) failed", output)
            if failed_match:
                failed = int(failed_match.group(1))

        # Extract failure patterns - handle both formats:
        # Format 1: "FAILED app/tests/test_foo.py::test_bar"
        # Format 2: "app/tests/test_foo.py::test_bar FAILED"
        failed_tests = re.findall(r"FAILED ([\w/]+\.py::[\w_]+)", output)
        if not failed_tests:
            # Try reverse format
            failed_tests = re.findall(r"([\w/]+\.py::[\w_]+) FAILED", output)

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
            "failure_patterns": list(set(failure_patterns)),  # Unique categories
            "test_output": output[:1000],  # First 1000 chars
            "success_rate": success_rate,
        }

    def _get_test_output(self, chat_log: Dict) -> str:
        """Extract test output from chat log.

        Args:
            chat_log: Chat log JSON

        Returns:
            Test output string
        """
        for message in reversed(chat_log.get("messages", [])):
            if message.get("role") == "tool_result":
                content = str(message.get("content", ""))
                # Look for pytest output indicators
                if any(indicator in content.lower() for indicator in [
                    "pytest", "test session starts", "passed", "failed", "collected"
                ]):
                    return content
        return ""

    def _categorize_test(self, test_path: str) -> str:
        """Categorize test by path (e.g., 'auth', 'api', 'database').

        Args:
            test_path: Test path like "app/tests/test_auth.py::test_login"

        Returns:
            Category string
        """
        # Extract category from path like "app/tests/test_auth.py::test_login"
        match = re.search(r"test_([\w]+)\.py", test_path)
        if match:
            return match.group(1)
        return "unknown"


class ReviewFeedbackCollector(FeedbackCollector):
    """Collect feedback from PR reviews."""

    def __init__(self, repo_root: Path, github_token: Optional[str] = None):
        """Initialize review feedback collector.

        Args:
            repo_root: Path to repository root
            github_token: GitHub personal access token (optional, reads from GITHUB_PAT env var)
        """
        super().__init__(repo_root)
        self.github_token = github_token or os.getenv("GITHUB_PAT")

    def collect(self, adw_id: str, issue_number: str) -> Optional[Dict[str, Any]]:
        """Fetch PR review feedback from GitHub.

        Args:
            adw_id: ADW execution ID
            issue_number: GitHub issue number

        Returns:
            {
                "pr_number": int,
                "review_status": "approved" | "changes_requested" | "commented" | "no_review",
                "num_review_comments": int,
                "change_categories": List[str],
                "human_changes_made": bool,
                "diff_summary": str
            }
            or None if no PR data available
        """
        try:
            from adw_modules.github import get_repo_info, fetch_pr_for_issue
        except ImportError:
            logger.warning("Could not import github module, skipping review feedback")
            return None

        # 1. Get PR associated with issue
        try:
            repo_owner, repo_name = get_repo_info()
        except Exception as e:
            logger.warning(f"Could not get repo info: {e}")
            return None

        pr_data = fetch_pr_for_issue(repo_owner, repo_name, issue_number, self.github_token)

        if not pr_data:
            logger.info(f"No PR found for issue {issue_number}")
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

        result = {
            "pr_number": pr_number,
            "review_status": review_status,
            "num_review_comments": len(review_comments),
            "change_categories": change_categories,
            "human_changes_made": human_changes,
            "diff_summary": self._summarize_changes(review_comments)[:500],
        }

        logger.info(f"Collected review feedback for issue {issue_number}: "
                   f"status={review_status}, comments={len(review_comments)}")

        return result

    def _fetch_reviews(self, owner: str, repo: str, pr_number: int) -> List[Dict]:
        """Fetch PR reviews from GitHub API.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number

        Returns:
            List of review objects
        """
        import requests

        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        headers = {"Authorization": f"token {self.github_token}"} if self.github_token else {}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.warning(f"Failed to fetch reviews: {e}")

        return []

    def _fetch_review_comments(self, owner: str, repo: str, pr_number: int) -> List[Dict]:
        """Fetch PR review comments.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number

        Returns:
            List of review comment objects
        """
        import requests

        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments"
        headers = {"Authorization": f"token {self.github_token}"} if self.github_token else {}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.warning(f"Failed to fetch review comments: {e}")

        return []

    def _fetch_commits(self, owner: str, repo: str, pr_number: int) -> List[Dict]:
        """Fetch PR commits.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number

        Returns:
            List of commit objects
        """
        import requests

        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/commits"
        headers = {"Authorization": f"token {self.github_token}"} if self.github_token else {}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.warning(f"Failed to fetch commits: {e}")

        return []

    def _determine_review_status(self, reviews: List[Dict]) -> str:
        """Determine overall review status.

        Args:
            reviews: List of review objects from GitHub

        Returns:
            "approved" | "changes_requested" | "commented" | "no_review"
        """
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
        """Categorize types of changes requested.

        Args:
            comments: List of review comment objects

        Returns:
            List of category strings (e.g., ["logic", "security", "style"])
        """
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
        """Check if human made commits after AI.

        Args:
            commits: List of commit objects
            adw_id: ADW execution ID to identify AI commits

        Returns:
            True if human commits detected
        """
        # Look for commits NOT made by ADW automation
        for commit in commits:
            message = commit.get("commit", {}).get("message", "")
            # AI commits contain ADW ID or automation marker
            if adw_id not in message and "🤖 Generated with" not in message:
                return True
        return False

    def _summarize_changes(self, comments: List[Dict]) -> str:
        """Create summary of review feedback.

        Args:
            comments: List of review comment objects

        Returns:
            Summary string
        """
        if not comments:
            return "No review comments"

        paths = [c.get("path", "unknown") for c in comments[:5]]
        return f"{len(comments)} review comments covering: {', '.join(paths)}"


class DeploymentFeedbackCollector(FeedbackCollector):
    """Collect deployment outcome feedback."""

    def __init__(self, repo_root: Path, github_token: Optional[str] = None):
        """Initialize deployment feedback collector.

        Args:
            repo_root: Path to repository root
            github_token: GitHub personal access token (optional, reads from GITHUB_PAT env var)
        """
        super().__init__(repo_root)
        self.github_token = github_token or os.getenv("GITHUB_PAT")

    def collect(self, adw_id: str, issue_number: str) -> Optional[Dict[str, Any]]:
        """Check deployment status and outcomes.

        Args:
            adw_id: ADW execution ID
            issue_number: GitHub issue number

        Returns:
            {
                "deployed": bool,
                "deployment_status": "success" | "failure" | "unknown",
                "deployment_method": "github_actions" | "manual" | "unknown",
                "post_deployment_errors": List[str],
                "rollback_required": bool
            }
            or None if no deployment data available
        """
        try:
            from adw_modules.github import get_repo_info
        except ImportError:
            logger.warning("Could not import github module, skipping deployment feedback")
            return None

        try:
            repo_owner, repo_name = get_repo_info()
        except Exception as e:
            logger.warning(f"Could not get repo info: {e}")
            return None

        # 1. Check GitHub Actions deployments
        gh_deployment = self._check_github_actions(repo_owner, repo_name, issue_number)

        # 2. Check issue labels for deployment markers
        label_deployment = self._check_deployment_labels(repo_owner, repo_name, issue_number)

        # 3. Check for post-deployment error issues
        related_errors = self._find_related_error_issues(repo_owner, repo_name, issue_number)

        # Merge results
        deployed = gh_deployment.get("deployed") or label_deployment.get("deployed")

        result = {
            "deployed": deployed,
            "deployment_status": gh_deployment.get("status") or label_deployment.get("status", "unknown"),
            "deployment_method": gh_deployment.get("method", "unknown"),
            "post_deployment_errors": related_errors,
            "rollback_required": any("rollback" in err.lower() for err in related_errors),
        }

        logger.info(f"Collected deployment feedback for issue {issue_number}: "
                   f"deployed={deployed}, status={result['deployment_status']}")

        return result

    def _check_github_actions(self, owner: str, repo: str, issue_number: str) -> Dict[str, Any]:
        """Check GitHub Actions for deployment status.

        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: GitHub issue number

        Returns:
            Dict with deployment info
        """
        import requests

        # Get PR for issue
        pr_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
        headers = {"Authorization": f"token {self.github_token}"} if self.github_token else {}

        try:
            response = requests.get(pr_url, headers=headers, timeout=10)
            if response.status_code != 200:
                return {"deployed": False}

            pr_data = response.json()
            if not pr_data.get("pull_request"):
                return {"deployed": False}

            # Check if PR is merged
            pr_number = pr_data["number"]
            pr_detail_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
            pr_response = requests.get(pr_detail_url, headers=headers, timeout=10)

            if pr_response.status_code != 200:
                return {"deployed": False}

            pr_detail = pr_response.json()
            is_merged = pr_detail.get("merged", False)

            if not is_merged:
                return {"deployed": False}

            # Simplified: assumes merged = deployed
            # TODO: Could check actual GitHub Actions workflow status here
            return {
                "deployed": True,
                "status": "success",
                "method": "github_actions"
            }

        except Exception as e:
            logger.warning(f"Failed to check GitHub Actions: {e}")
            return {"deployed": False}

    def _check_deployment_labels(self, owner: str, repo: str, issue_number: str) -> Dict[str, Any]:
        """Check issue labels for deployment status markers.

        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: GitHub issue number

        Returns:
            Dict with deployment info from labels
        """
        import requests

        url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
        headers = {"Authorization": f"token {self.github_token}"} if self.github_token else {}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return {"deployed": False}

            issue = response.json()
            labels = [label["name"].lower() for label in issue.get("labels", [])]

            if "deployed" in labels or "production" in labels:
                status = "failure" if "failed" in labels else "success"
                return {"deployed": True, "status": status}

        except Exception as e:
            logger.warning(f"Failed to check deployment labels: {e}")

        return {"deployed": False}

    def _find_related_error_issues(self, owner: str, repo: str, issue_number: str) -> List[str]:
        """Find issues created after deployment that reference this issue.

        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: GitHub issue number

        Returns:
            List of error issue descriptions
        """
        import requests

        # Search for issues that reference this one
        query = f"repo:{owner}/{repo} #{issue_number} is:issue created:>2024-01-01"
        url = f"https://api.github.com/search/issues?q={query}"
        headers = {"Authorization": f"token {self.github_token}"} if self.github_token else {}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return []

            results = response.json()
            error_issues = []

            for item in results.get("items", [])[:5]:
                title = item.get("title", "")
                if any(word in title.lower() for word in ["error", "bug", "broken", "failure"]):
                    error_issues.append(f"#{item['number']}: {title}")

            return error_issues

        except Exception as e:
            logger.warning(f"Failed to find related error issues: {e}")
            return []
