# AI Self-Improving Learning System - MVP Specification

**Created:** 2025-11-07
**Status:** Planning
**Complexity:** 7/10
**Estimated Effort:** 5-7 hours

---

## 🎯 Objective

Build a self-improving AI learning system that passively learns from test outcomes, code reviews, and deployment results across all projects to reduce mistakes over time through meta-learning and prompt refinement.

---

## 📊 Current State (50% Complete!)

### Existing Infrastructure

**1. Data Models (Complete)** - `adw/adw_modules/meta_adw_types.py:84-223`
- ✅ `LearningRecord` - Complete with all needed fields
- ✅ `TaskAnalysis` - Task characteristics
- ✅ `StrategyRecommendation` - Workflow recommendations
- ✅ `PatternDatabase` - Storage for learned patterns
- ✅ `DecisionWeights` - Adjustable matching weights
- ✅ `TemplateIndexEntry` - Template metadata with success rates

**2. Learning Loop Foundation (Partial)** - `adw/meta_strategy.py`
- ✅ `collect_feedback()` (line 489-532) - Basic feedback collection
- ✅ `update_pattern_database()` (line 534-596) - Pattern storage
- ✅ `retrain_weights()` (line 597-673) - Weight adjustment
- ❌ **Missing:** Test/review/deployment feedback integration
- ❌ **Missing:** Cross-project aggregation
- ❌ **Missing:** Prompt refinement

**3. Decision Engine (Complete)** - `adw/decision_engine.py`
- ✅ `load_learning_data()` (line 83-114) - Load patterns and weights
- ✅ `match_patterns()` (line 116-190) - Pattern matching
- ✅ `rank_workflows()` (line 192-283) - Workflow selection

**4. Storage Structure (Initialized)** - `.tac/learning/`
- ✅ `pattern_database.json` - Empty, ready to use
- ✅ `decision_weights.json` - Initialized with defaults
- ✅ `execution_logs/` - One example log exists

**5. Integration Points (Available)**
- ✅ `adw_test_iso.py:91-102` - Test result parsing
- ✅ `logs/<session-id>/chat.json` - Full execution logs
- ✅ `agents/<adw-id>/adw_state.json` - Workflow state

### What's Missing (50% to Complete)

1. ❌ **Test Feedback Integration** - Extract actual test results
2. ❌ **Review Feedback Capture** - Analyze PR reviews and code changes
3. ❌ **Deployment Feedback** - Track deployment outcomes
4. ❌ **Cross-Project Learning** - Centralized knowledge sharing
5. ❌ **Prompt Refinement Engine** - Self-improving prompts

---

## 🎯 MVP Scope

### In Scope - 5 Core Components

#### Component 1: Test Feedback Integration
**Purpose:** Capture test results and patterns from ADW test executions

**Functionality:**
- Read test results from `adw_test_iso.py` executions
- Parse pass/fail counts, specific test failures
- Identify patterns in failures (e.g., always fails auth tests)
- Store in LearningRecord.success_metrics

**Success Criteria:**
- ✅ Captures test pass/fail counts for every test execution
- ✅ Identifies recurring failure patterns
- ✅ Data flows into pattern database

#### Component 2: Review Feedback Capture
**Purpose:** Learn from human code review feedback

**Functionality:**
- Fetch PR associated with issue (GitHub API)
- Get review comments and approval/changes_requested status
- Analyze diff between AI-generated code and final merged code
- Categorize changes: logic fixes, style, refactoring, bug fixes
- Store insights in LearningRecord.problems_encountered

**Success Criteria:**
- ✅ Captures PR review status (approved/changes_requested)
- ✅ Identifies what changed between AI code and final code
- ✅ Categorizes types of changes made by humans
- ✅ Feeds patterns back to prompt refinement

#### Component 3: Deployment Feedback Integration
**Purpose:** Track deployment success and post-deployment outcomes

**Functionality:**
- Check deployment status (GitHub Actions, manual confirmation, or labels)
- Track deployment success/failure
- Monitor post-deployment error rates (if available)
- Detect rollbacks or reverts
- Store in LearningRecord.success_metrics

**Success Criteria:**
- ✅ Tracks deployment success/failure for each ADW execution
- ✅ (Nice-to-have) Captures post-deployment error rate changes
- ✅ Correlates deployments with code quality

#### Component 4: Cross-Project Learning Aggregation
**Purpose:** Share learnings across all projects in organization

**Functionality:**
- Central storage at `~/agentic-coding-library/.tac/learning/global/`
- Push learnings from individual projects to central database
- Pull aggregated learnings when making decisions
- Merge patterns with similar characteristics
- Maintain global success rates and decision weights

**Success Criteria:**
- ✅ Project A's learnings available to Project B
- ✅ Global pattern database grows over time
- ✅ Global decision weights improve based on all projects
- ✅ Privacy: Share patterns, not code/secrets

#### Component 5: Prompt Refinement Engine
**Purpose:** Automatically improve slash command prompts based on failures

**Functionality:**
- Analyze failure patterns (common mistakes)
- Generate prompt improvements using Self-Refine pattern
- Iterate 3-5 times on improvements (PromptWizard approach)
- Apply refinements to CLAUDE.md as "Learned Patterns"
- Generate custom validation checklists from common mistakes

**Success Criteria:**
- ✅ Identifies failure patterns (e.g., "Always forgets to add tests")
- ✅ Generates specific prompt refinements
- ✅ Appends learnings to CLAUDE.md
- ✅ Creates project-specific validation checklists
- ✅ AI makes fewer of the same mistakes over time

### Out of Scope (Phase 2+)

- ❌ Real-time monitoring dashboards
- ❌ Advanced ML models for pattern recognition
- ❌ User-facing feedback UI
- ❌ Integration with external APM tools (DataDog, New Relic)
- ❌ Multi-tenant isolation (privacy already handled)
- ❌ Automatic rollback based on error rates
- ❌ A/B testing of different strategies

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     ADW Workflow Execution                       │
│  (adw_sdlc_iso.py, adw_plan_build_test_iso.py, etc.)           │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Feedback Collection                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Test Results │  │ PR Reviews   │  │ Deployment   │          │
│  │ Feedback     │  │ Feedback     │  │ Feedback     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│              Learning Record Creation                            │
│  (LearningRecord with complete success_metrics)                 │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│           Local Pattern Database Update                          │
│  (.tac/learning/pattern_database.json)                          │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│     Cross-Project Aggregation (push to global)                  │
│  (~/agentic-coding-library/.tac/learning/global/)               │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│         Pattern Analysis & Prompt Refinement                     │
│  (Every 10+ patterns, analyze failures → refine prompts)        │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│            Apply Improvements                                    │
│  • Update CLAUDE.md with learned patterns                       │
│  • Update decision weights                                       │
│  • Generate validation checklists                               │
└─────────────────────────────────────────────────────────────────┘
```

### Storage Structure

```
~/agentic-coding-library/.tac/learning/
├── global/                                    # NEW - Cross-project
│   ├── global_pattern_database.json         # Aggregated patterns
│   ├── global_decision_weights.json         # Aggregated weights
│   └── project_contributions/
│       ├── agentic-coding-library.json
│       ├── project-a.json
│       └── project-b.json
├── pattern_database.json                     # EXISTING - Local patterns
├── decision_weights.json                     # EXISTING - Local weights
└── execution_logs/                           # EXISTING - Execution history
    └── 2025-11-03T23-39-42.364704-issue-9.json

<project-root>/.tac/learning/
├── pattern_database.json                     # Project-specific patterns
├── decision_weights.json                     # Project-specific weights
└── execution_logs/                           # Project execution logs

CLAUDE.md
└── "Learned Patterns" section                # NEW - Appended automatically
    ├── Common mistakes to avoid
    ├── Successful patterns
    └── Project-specific validations
```

### Data Flow

**1. Execution Phase:**
```python
# ADW workflow runs (e.g., adw_sdlc_iso.py)
workflow_result = execute_workflow(issue_number, adw_id)

# Feedback collected immediately after
feedback = FeedbackCollector().collect_all(adw_id, issue_number)
# Returns: {
#   "tests_passed": 45,
#   "tests_failed": 2,
#   "test_failure_patterns": ["auth_test", "validation_test"],
#   "review_status": "approved",
#   "human_changes_made": ["added error handling", "fixed typo"],
#   "deployed": true,
#   "deployment_success": true,
#   "error_rate_change": -0.02  # 2% reduction in errors
# }
```

**2. Learning Phase:**
```python
# Create LearningRecord
learning_record = LearningRecord(
    task_description=issue.title,
    task_analysis=task_analysis,
    recommended_strategy=recommendation,
    selected_strategy=selected_workflow,
    outcome="success",  # Based on tests + review + deployment
    success_metrics=feedback,
    problems_encountered=extract_problems(feedback),
    false_fix_detected=check_false_fix(issue_number),
)

# Update local pattern database
update_pattern_database(learning_record)

# Push to global learning
CrossProjectLearningStore().push_learnings(project_id, learning_record)
```

**3. Improvement Phase (every 10+ patterns):**
```python
# Analyze patterns
failure_patterns = PromptRefiner().analyze_failures(pattern_database)
# Returns: [
#   {type: "test_failures", pattern: "always forgets auth tests", count: 8},
#   {type: "review_changes", pattern: "missing error handling", count: 6}
# ]

# Generate refinements
refinements = PromptRefiner().generate_prompt_refinements(failure_patterns)
# Returns: {
#   "/implement": "Always include: 1) comprehensive error handling, 2) auth tests for protected endpoints",
#   "/test": "Verify auth tests exist for all protected routes"
# }

# Apply to CLAUDE.md
PromptRefiner().apply_refinements(refinements)
```

---

## 🔧 Implementation Details

### Component 1: Test Feedback Integration

**File:** `adw/adw_modules/learning_feedback.py` (NEW)

```python
class FeedbackCollector:
    """Collects feedback from test results, reviews, and deployments."""

    def collect_test_feedback(self, adw_id: str) -> Dict[str, Any]:
        """Extract test feedback from adw_test_iso execution.

        Returns:
            {
                "tests_passed": int,
                "tests_failed": int,
                "test_failure_patterns": List[str],  # Which tests failed
                "test_coverage": float,  # If available
            }
        """
        # 1. Find latest log for this adw_id
        log_dir = Path("logs")
        # Search for chat.json files containing this adw_id

        # 2. Parse test results from logs/<session-id>/chat.json
        # Look for /test command output
        # Use existing parse_test_results() from adw_test_iso.py

        # 3. Identify patterns
        failed_test_names = [test.name for test in test_results if not test.passed]
        patterns = self._categorize_failures(failed_test_names)

        return {
            "tests_passed": passed_count,
            "tests_failed": failed_count,
            "test_failure_patterns": patterns,
        }

    def _categorize_failures(self, test_names: List[str]) -> List[str]:
        """Categorize test failures by type."""
        categories = []
        for name in test_names:
            if "auth" in name.lower():
                categories.append("authentication")
            elif "valid" in name.lower():
                categories.append("validation")
            # ... more categories
        return list(set(categories))
```

**Integration Point:** Call from `meta_strategy.py:collect_feedback()`

### Component 2: Review Feedback Capture

**File:** Extend `adw/adw_modules/github.py`

```python
def get_pr_for_issue(issue_number: int, repo_path: str) -> Optional[Dict]:
    """Get PR associated with issue.

    Args:
        issue_number: GitHub issue number
        repo_path: Repository path (owner/repo)

    Returns:
        PR data dict or None if no PR found
    """
    # Search for PRs that reference this issue
    # GitHub API: GET /repos/{owner}/{repo}/issues/{issue_number}/timeline
    # Filter for "cross-referenced" events with PR

def get_pr_reviews(pr_number: int, repo_path: str) -> List[Dict]:
    """Get all reviews for a PR.

    Returns:
        List of review dicts with state, comments, etc.
    """
    # GitHub API: GET /repos/{owner}/{repo}/pulls/{pr_number}/reviews

def analyze_pr_diff(pr_number: int, repo_path: str) -> Dict[str, Any]:
    """Analyze what changed between AI code and merged code.

    Returns:
        {
            "total_changes": int,  # Lines changed by reviewers
            "change_categories": {
                "logic_fixes": int,
                "style_changes": int,
                "added_tests": int,
                "error_handling": int,
            },
            "significant_changes": List[str],  # Descriptions
        }
    """
    # Get PR diff
    # Analyze patterns in changes
    # Categorize by type
```

**File:** `adw/adw_modules/learning_feedback.py` (extend)

```python
def collect_review_feedback(self, issue_number: int) -> Dict[str, Any]:
    """Extract feedback from GitHub PR reviews."""
    pr = get_pr_for_issue(issue_number, self.repo_path)
    if not pr:
        return {"review_status": "no_pr"}

    reviews = get_pr_reviews(pr["number"], self.repo_path)
    diff_analysis = analyze_pr_diff(pr["number"], self.repo_path)

    # Determine overall status
    status = "approved"
    if any(r["state"] == "CHANGES_REQUESTED" for r in reviews):
        status = "changes_requested"

    return {
        "review_status": status,
        "review_count": len(reviews),
        "human_changes_made": diff_analysis["significant_changes"],
        "change_categories": diff_analysis["change_categories"],
    }
```

### Component 3: Deployment Feedback

**File:** `adw/adw_modules/deployment_tracker.py` (NEW)

```python
class DeploymentTracker:
    """Tracks deployment outcomes for learning."""

    def check_deployment_status(self, adw_id: str, issue_number: int) -> Dict:
        """Check if code was deployed and outcome.

        Strategies (in order of preference):
        1. Check for "deployed" label on issue/PR
        2. Check GitHub Actions workflow status
        3. Check for deployment-related PR comments
        4. Return unknown if none found

        Returns:
            {
                "deployed": bool,
                "deployment_success": bool,
                "deployment_method": str,  # "github_actions", "manual", "unknown"
            }
        """
        # Strategy 1: Check labels
        issue = fetch_issue(str(issue_number), self.repo_path)
        if any(label.name.lower() == "deployed" for label in issue.labels):
            return {
                "deployed": True,
                "deployment_success": True,  # Assume success if labeled
                "deployment_method": "manual_label"
            }

        # Strategy 2: Check GitHub Actions
        # (if applicable - depends on project setup)

        # Default: unknown
        return {"deployed": False, "deployment_success": False, "deployment_method": "unknown"}

    def get_post_deployment_metrics(self, adw_id: str, hours_after: int = 24) -> Optional[Dict]:
        """Get error rates after deployment (if available).

        For MVP: Returns None (future integration with APM tools)
        """
        # Future: Integrate with Sentry, DataDog, etc.
        return None
```

### Component 4: Cross-Project Learning

**File:** `adw/adw_modules/cross_project_learning.py` (NEW)

```python
class CrossProjectLearningStore:
    """Centralized learning database across all projects."""

    def __init__(self, central_db_path: Optional[Path] = None):
        if central_db_path is None:
            # Default to agentic-coding-library repo
            central_db_path = Path.home() / "agentic-coding-library" / ".tac" / "learning" / "global"

        self.central_db_path = central_db_path
        self.central_db_path.mkdir(parents=True, exist_ok=True)

        self.global_patterns_path = central_db_path / "global_pattern_database.json"
        self.global_weights_path = central_db_path / "global_decision_weights.json"
        self.contributions_dir = central_db_path / "project_contributions"
        self.contributions_dir.mkdir(exist_ok=True)

    def push_learnings(self, project_id: str, learning_record: LearningRecord):
        """Push project learnings to central database.

        Args:
            project_id: Unique project identifier (repo name)
            learning_record: LearningRecord to add to global database
        """
        # 1. Save to project contributions
        project_file = self.contributions_dir / f"{project_id}.json"
        contributions = []
        if project_file.exists():
            with open(project_file) as f:
                contributions = json.load(f)

        contributions.append(learning_record.model_dump(mode='json'))

        with open(project_file, 'w') as f:
            json.dump(contributions, f, indent=2)

        # 2. Update global pattern database
        self._update_global_patterns(learning_record)

        # 3. Trigger global weight retraining (if threshold met)
        self._check_global_retraining()

    def pull_learnings(self, project_id: str) -> Dict:
        """Get aggregated learnings from all projects.

        Returns:
            {
                "global_patterns": List[Pattern],
                "global_weights": DecisionWeights,
                "total_executions": int,
                "global_success_rate": float,
            }
        """
        if not self.global_patterns_path.exists():
            return {"global_patterns": [], "total_executions": 0}

        with open(self.global_patterns_path) as f:
            global_db = json.load(f)

        with open(self.global_weights_path) as f:
            global_weights = json.load(f)

        return {
            "global_patterns": global_db.get("patterns", []),
            "global_weights": global_weights,
            "total_executions": global_db.get("total_patterns", 0),
            "global_success_rate": self._calculate_global_success_rate(global_db),
        }

    def _update_global_patterns(self, learning_record: LearningRecord):
        """Merge new pattern into global database."""
        # Load existing
        if self.global_patterns_path.exists():
            with open(self.global_patterns_path) as f:
                global_db = json.load(f)
        else:
            global_db = {"patterns": [], "version": "1.0", "total_patterns": 0}

        # Add new pattern
        pattern = {
            "task_type": learning_record.task_analysis.task_type,
            "complexity_level": learning_record.task_analysis.complexity_level,
            "recommended_workflow": learning_record.recommended_strategy.workflow_name,
            "selected_workflow": learning_record.selected_strategy,
            "outcome": learning_record.outcome,
            "success_metrics": learning_record.success_metrics,
            "timestamp": learning_record.execution_timestamp.isoformat(),
        }

        global_db["patterns"].append(pattern)
        global_db["total_patterns"] = len(global_db["patterns"])
        global_db["last_updated"] = datetime.utcnow().isoformat()

        # Save
        with open(self.global_patterns_path, 'w') as f:
            json.dump(global_db, f, indent=2)
```

### Component 5: Prompt Refinement Engine

**File:** `adw/adw_modules/prompt_refiner.py` (NEW)

```python
class PromptRefiner:
    """Self-Refine pattern for improving slash command prompts."""

    def analyze_failures(self, pattern_database: PatternDatabase) -> List[Dict]:
        """Identify patterns where AI consistently fails.

        Returns:
            List of failure patterns with suggestions
        """
        failures = []
        patterns = pattern_database.patterns

        # Group by failure type
        test_failures = {}
        review_changes = {}

        for pattern in patterns:
            if pattern.get("outcome") != "success":
                # Analyze why it failed
                problems = pattern.get("problems_encountered", [])
                for problem in problems:
                    # Categorize
                    if "test" in problem.lower():
                        test_failures[problem] = test_failures.get(problem, 0) + 1
                    elif "review" in problem.lower():
                        review_changes[problem] = review_changes.get(problem, 0) + 1

        # Identify patterns (>= 3 occurrences)
        for problem, count in test_failures.items():
            if count >= 3:
                failures.append({
                    "type": "test_failures",
                    "pattern": problem,
                    "count": count,
                    "severity": "high" if count >= 5 else "medium"
                })

        for problem, count in review_changes.items():
            if count >= 3:
                failures.append({
                    "type": "review_changes",
                    "pattern": problem,
                    "count": count,
                    "severity": "high" if count >= 5 else "medium"
                })

        return failures

    def generate_prompt_refinements(self, failure_patterns: List[Dict]) -> Dict[str, str]:
        """Generate improved prompt content using Self-Refine pattern.

        Uses iterative FEEDBACK → REFINE loop (3-5 iterations)

        Returns:
            Dict mapping command names to refined prompt sections
        """
        refinements = {}

        for pattern in failure_patterns:
            # Determine which command needs refinement
            if pattern["type"] == "test_failures":
                command = "/test"
                refinement = self._generate_test_refinement(pattern)
            elif pattern["type"] == "review_changes":
                command = "/implement"
                refinement = self._generate_implementation_refinement(pattern)
            else:
                continue

            if command not in refinements:
                refinements[command] = []
            refinements[command].append(refinement)

        # Consolidate refinements per command
        consolidated = {}
        for cmd, refs in refinements.items():
            consolidated[cmd] = "\n".join(refs)

        return consolidated

    def _generate_test_refinement(self, pattern: Dict) -> str:
        """Generate refinement for test-related failures."""
        problem = pattern["pattern"]
        count = pattern["count"]

        # Simple rule-based refinement (can be enhanced with LLM later)
        if "auth" in problem.lower():
            return f"- Always include authentication tests for protected endpoints (failed {count}x previously)"
        elif "validation" in problem.lower():
            return f"- Always test input validation edge cases (failed {count}x previously)"
        else:
            return f"- Address: {problem} (occurred {count}x)"

    def apply_refinements(self, refinements: Dict[str, str]):
        """Apply prompt refinements to CLAUDE.md.

        Appends learned patterns to CLAUDE.md
        """
        claude_md_path = Path("CLAUDE.md")

        # Read current CLAUDE.md
        with open(claude_md_path) as f:
            content = f.read()

        # Check if "Learned Patterns" section exists
        if "## Learned Patterns" not in content:
            content += "\n\n---\n\n## Learned Patterns\n\n"
            content += "*This section is automatically updated by the AI learning system.*\n\n"

        # Append new refinements
        timestamp = datetime.utcnow().strftime("%Y-%m-%d")
        content += f"\n### Refinements Applied - {timestamp}\n\n"

        for command, refinement in refinements.items():
            content += f"**{command}:**\n{refinement}\n\n"

        # Write back
        with open(claude_md_path, 'w') as f:
            f.write(content)

    def update_validation_checklists(self, patterns: List[Dict]):
        """Generate custom validation checklists from learnings."""
        checklist_path = Path("tac-core-plugin/validation-checklists/learned-validations.md")
        checklist_path.parent.mkdir(parents=True, exist_ok=True)

        # Group patterns by success/failure
        successful = [p for p in patterns if p.get("success")]
        failed = [p for p in patterns if not p.get("success")]

        checklist_content = "# Learned Validation Checklist\n\n"
        checklist_content += "*Auto-generated from AI learning system*\n\n"

        # Always do (from successful patterns)
        checklist_content += "## ✅ Always Do (Successful Patterns)\n\n"
        # ... extract from successful patterns

        # Never do (from failed patterns)
        checklist_content += "## ❌ Common Mistakes to Avoid\n\n"
        # ... extract from failed patterns

        with open(checklist_path, 'w') as f:
            f.write(checklist_content)
```

---

## ✅ Success Criteria

### Functional Requirements

1. **Test Feedback:**
   - ✅ Captures test pass/fail counts for 100% of test executions
   - ✅ Identifies recurring failure patterns
   - ✅ Data flows into pattern database within 1 minute of test completion

2. **Review Feedback:**
   - ✅ Captures PR review status for 100% of merged PRs
   - ✅ Categorizes types of human changes with >80% accuracy
   - ✅ Identifies patterns in reviewer feedback

3. **Deployment Feedback:**
   - ✅ Tracks deployment success/failure for 100% of deployments
   - ✅ Correlates deployment outcomes with code quality metrics

4. **Cross-Project Learning:**
   - ✅ Learnings from Project A available in Project B within 1 minute
   - ✅ Global pattern database grows with each execution
   - ✅ No secrets or sensitive data leaked across projects

5. **Prompt Refinement:**
   - ✅ Generates refinements after 10+ patterns collected
   - ✅ Refinements address actual recurring failures
   - ✅ CLAUDE.md updated automatically with learned patterns

### Performance Metrics

**Baseline (Before Learning):**
- Success rate: ~70% (assumed from current Meta-ADW)
- Test failure rate: ~20%
- Review changes required: ~40% of PRs
- Deployment failures: ~10%

**Target (After 50 Executions with Learning):**
- ✅ Success rate increases to >85%
- ✅ Test failure rate decreases to <10%
- ✅ Review changes required decreases to <20%
- ✅ Deployment failures decrease to <5%
- ✅ Same failure type occurs <3 times before being learned

### Quality Metrics

- ✅ Learning system has <5% overhead on execution time
- ✅ Pattern database corruption rate: 0%
- ✅ Cross-project data leakage: 0 incidents
- ✅ Prompt refinements are human-readable and actionable

---

## 🧪 Validation Strategy

### Unit Tests

**File:** `adw/tests/test_learning_system.py` (NEW)

```python
def test_feedback_collector_test_results():
    """Test feedback collection from test results."""
    # Given: Mock adw_test_iso execution with known results
    # When: collect_test_feedback() is called
    # Then: Correct pass/fail counts and patterns extracted

def test_feedback_collector_pr_reviews():
    """Test feedback collection from PR reviews."""
    # Given: Mock GitHub PR with reviews
    # When: collect_review_feedback() is called
    # Then: Review status and changes correctly captured

def test_deployment_tracker():
    """Test deployment tracking."""
    # Given: Mock deployment status
    # When: check_deployment_status() is called
    # Then: Correct deployment outcome captured

def test_cross_project_push_pull():
    """Test cross-project learning."""
    # Given: Two mock projects
    # When: Project A pushes learning, Project B pulls
    # Then: Learning available in Project B

def test_pattern_database_update():
    """Test pattern database updates correctly."""
    # Given: Mock learning record
    # When: update_pattern_database() is called
    # Then: Pattern added to database with correct fields

def test_prompt_refinement_generation():
    """Test prompt refinement generates improvements."""
    # Given: Mock failure patterns
    # When: generate_prompt_refinements() is called
    # Then: Refinements generated and are actionable

def test_weight_retraining():
    """Test decision weight retraining."""
    # Given: 10+ patterns with varying success rates
    # When: retrain_weights() is called
    # Then: Weights adjusted appropriately
```

### Integration Tests

```python
def test_complete_learning_loop():
    """Test end-to-end learning loop."""
    # Given: Mock ADW execution from start to finish
    # When: Learning system processes execution
    # Then:
    #   - Feedback collected from all sources
    #   - Learning record created
    #   - Pattern database updated
    #   - Global database updated
    #   - Prompt refinements generated (if threshold met)

def test_learning_improves_decisions():
    """Test that learning actually improves future decisions."""
    # Given: Pattern database with successful patterns for specific task type
    # When: Decision engine recommends workflow for similar task
    # Then: Recommendation matches successful pattern
```

### Manual Validation

1. **Enable learning for test issue:**
   ```bash
   cd adw/
   ENABLE_LEARNING=true uv run meta_strategy.py 999  # Test issue
   ```

2. **Verify learning files created:**
   ```bash
   # Check local learning
   cat .tac/learning/pattern_database.json

   # Check global learning
   cat ~/agentic-coding-library/.tac/learning/global/global_pattern_database.json

   # Check CLAUDE.md updated
   tail -50 CLAUDE.md | grep "Learned Patterns"
   ```

3. **Run 10 test executions and verify improvement:**
   - Track success rate over 10 executions
   - Verify pattern database grows
   - Verify weights adjust
   - Verify prompt refinements generated after 10th execution

---

## 🔒 Security & Privacy

### Privacy Considerations

**What Gets Shared Across Projects:**
- ✅ Task characteristics (type, complexity)
- ✅ Workflow recommendations and outcomes
- ✅ Success/failure patterns (aggregated)
- ✅ Generic failure categories

**What NEVER Gets Shared:**
- ❌ Actual code content
- ❌ Secrets, API keys, credentials
- ❌ Company/client names
- ❌ Specific file paths or repo URLs
- ❌ GitHub issue descriptions (unless explicitly generic)

### Security Measures

1. **Data Sanitization:**
   - Strip sensitive data before cross-project push
   - Validate all inputs to learning system
   - No eval() or code execution from learned patterns

2. **Access Control:**
   - Global learning database only writable by owner
   - Projects can only read global patterns, not raw data
   - Audit log of all cross-project pushes

3. **Rollback Protection:**
   - Feature flag to enable/disable learning
   - Backup pattern database before updates
   - Validate pattern database schema before writes

---

## 📦 Feature Flags

**Environment Variables:**

```bash
# Enable/disable learning system (default: false)
ENABLE_LEARNING=true

# Enable/disable cross-project sharing (default: true if learning enabled)
ENABLE_CROSS_PROJECT_LEARNING=true

# Minimum patterns before prompt refinement (default: 10)
MIN_PATTERNS_FOR_REFINEMENT=10

# Verbose logging for learning system (default: false)
LEARNING_DEBUG=true
```

**Configuration File:** `.tac/learning/config.json`

```json
{
  "enabled": true,
  "cross_project_enabled": true,
  "min_patterns_for_refinement": 10,
  "learning_rate": 0.1,
  "backup_before_update": true,
  "max_pattern_age_days": 90
}
```

---

## 📅 Implementation Timeline

### Phase 1: Core Infrastructure (2-3 hours)
- [ ] Component 1: Test Feedback Integration (1 hour)
- [ ] Component 2: Review Feedback Capture (1 hour)
- [ ] Component 3: Deployment Feedback (1 hour)

### Phase 2: Learning & Improvement (2-3 hours)
- [ ] Component 4: Cross-Project Learning (1 hour)
- [ ] Component 5: Prompt Refinement Engine (1.5 hours)
- [ ] Integration with meta_strategy.py (30 min)

### Phase 3: Testing & Validation (1 hour)
- [ ] Unit tests for all components (30 min)
- [ ] Integration test for complete loop (15 min)
- [ ] Manual validation with test issue (15 min)

### Phase 4: Documentation (30 min)
- [ ] Create docs/AI_LEARNING_SYSTEM.md
- [ ] Update CLAUDE.md with learning system info
- [ ] Add inline code comments

**Total: 5-7 hours**

---

## 🚀 Rollout Strategy

### Stage 1: Local Testing (Week 1)
- Enable learning on agentic-coding-library repo only
- Run 10-20 test executions
- Validate all components working
- Fix any bugs found

### Stage 2: Limited Rollout (Week 2)
- Enable on 1-2 additional test projects
- Monitor cross-project learning
- Validate no data leakage
- Tune thresholds based on results

### Stage 3: Full Rollout (Week 3+)
- Enable for all projects
- Monitor global pattern database growth
- Track success rate improvements
- Iterate on prompt refinements

---

## 📊 Monitoring & Metrics

### What to Monitor

**Learning System Health:**
- Pattern database growth rate (should increase steadily)
- Global pattern database size
- Number of projects contributing
- Prompt refinement frequency

**AI Improvement Metrics:**
- Success rate trend (should increase)
- Test failure rate trend (should decrease)
- Review change rate trend (should decrease)
- Deployment failure rate trend (should decrease)

**System Performance:**
- Learning overhead per execution (<5% target)
- Pattern database query time (<100ms target)
- Cross-project push latency (<1s target)

### Dashboards (Future)

```bash
# Quick status check
python adw/learning_status.py

# Output:
# Learning System Status
# =====================
# Total Patterns: 47
# Global Patterns: 156
# Success Rate: 82% (↑ from 70%)
# Last Refinement: 2025-11-06
# Projects Contributing: 3
```

---

## 🔄 Iteration & Improvement

### After MVP (Phase 2)

**High Priority:**
1. Real-time APM integration for deployment metrics
2. Advanced pattern recognition (ML-based)
3. A/B testing of strategies
4. User feedback collection ("Was this helpful?")

**Medium Priority:**
5. Dashboard for visualizing learning
6. Slack/Discord notifications of improvements
7. Export learning reports
8. Import learnings from external sources

**Low Priority:**
9. Multi-model comparison
10. Custom learning strategies per project
11. Learning system API for external tools

---

## 📚 References

**Research:**
- Self-Refine: Iterative Refinement with Self-Feedback (2023)
- PromptWizard: Feedback-driven self-evolving prompts (Microsoft, 2025)
- SICA: Self-Improving Coding Agent (ICLR 2025)

**Implementation Patterns:**
- FEEDBACK → REFINE → FEEDBACK loop
- Monte Carlo sampling for prompt optimization
- Cross-project knowledge aggregation

**Existing Code:**
- `adw/meta_strategy.py` - Meta-ADW orchestration
- `adw/decision_engine.py` - Pattern matching and decisions
- `adw/adw_modules/meta_adw_types.py` - Data models

---

## ✅ Next Steps

1. **Review this spec** - Ensure alignment with vision
2. **Create implementation plan** - Use `/feature` to break down tasks
3. **Begin implementation** - Start with Component 1 (Test Feedback)
4. **Iterate** - Build → Test → Refine for each component
5. **Deploy** - Enable learning and monitor improvements

---

**Last Updated:** 2025-11-07
**Status:** Ready for Implementation
**Approval Required:** Yes (modifies ADW workflow behavior)
