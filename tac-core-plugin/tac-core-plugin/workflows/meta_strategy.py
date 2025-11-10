#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "python-dotenv",
#   "pydantic",
# ]
# ///
"""Meta-ADW Strategy Orchestrator.

Main entry point for Meta-ADW system. Interviews users, analyzes tasks,
recommends optimal workflow strategy, and executes selected workflow.

Usage:
    uv run adw/meta_strategy.py <issue-number> [--adw-id <id>] [--model-set <base|heavy>]

Example:
    uv run adw/meta_strategy.py 123
    uv run adw/meta_strategy.py 123 --model-set heavy
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from adw_modules.agent import execute_template
from adw_modules.data_types import GitHubIssue, ModelSet, AgentTemplateRequest
from adw_modules.github import fetch_issue, get_repo_url, extract_repo_path
from adw_modules.meta_adw_types import (
    TaskAnalysis,
    StrategyRecommendation,
    LearningRecord,
)
from decision_engine import DecisionEngine
from adw_modules.learning_feedback import (
    TestFeedbackCollector,
    ReviewFeedbackCollector,
    DeploymentFeedbackCollector,
)
from adw_modules.cross_project_learning import CrossProjectLearningStore
from adw_modules.prompt_refiner import PromptRefiner

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Feature flag for learning system
ENABLE_LEARNING = os.getenv("ENABLE_ADW_LEARNING", "true").lower() == "true"


class MetaStrategyOrchestrator:
    """Orchestrates the Meta-ADW workflow."""

    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize orchestrator.

        Args:
            repo_root: Path to repository root. Defaults to current directory.
        """
        self.repo_root = repo_root or Path.cwd()
        self.decision_engine = DecisionEngine(repo_root=self.repo_root)
        self.execution_log_dir = self.repo_root / ".tac" / "learning" / "execution_logs"
        self.execution_log_dir.mkdir(parents=True, exist_ok=True)

    def fetch_issue(self, issue_number: int) -> GitHubIssue:
        """Fetch GitHub issue details.

        Args:
            issue_number: GitHub issue number

        Returns:
            GitHubIssue object with issue details

        Raises:
            Exception: If issue fetch fails
        """
        logger.info(f"Fetching GitHub issue #{issue_number}...")
        try:
            # Get repo path from environment
            repo_url = get_repo_url()
            repo_path = extract_repo_path(repo_url)

            issue = fetch_issue(str(issue_number), repo_path)
            logger.info(f"Fetched issue: {issue.title}")
            return issue
        except Exception as e:
            logger.error(f"Failed to fetch issue #{issue_number}: {e}")
            raise

    def analyze_issue_directly(self, issue: GitHubIssue) -> TaskAnalysis:
        """Analyze GitHub issue directly without CLI templates.

        This is a simplified version that analyzes the issue based on keywords
        and patterns rather than using interactive templates.

        Args:
            issue: GitHubIssue object

        Returns:
            TaskAnalysis object
        """
        logger.info("Analyzing issue directly (simplified analysis)...")

        # Combine title and body for analysis
        text = f"{issue.title} {issue.body or ''}".lower()

        # Determine task type from labels and keywords
        task_type = "feature"
        if any(label.name.lower() in ["bug", "fix"] for label in issue.labels):
            task_type = "bug"
        elif any(label.name.lower() in ["chore", "maintenance", "deps"] for label in issue.labels):
            task_type = "chore"
        elif "bug" in text or "fix" in text or "error" in text:
            task_type = "bug"
        elif "chore" in text or "refactor" in text or "upgrade" in text:
            task_type = "chore"

        # Estimate complexity based on issue description length and keywords
        complexity_indicators = 0
        if len(text) > 500:
            complexity_indicators += 2
        elif len(text) > 200:
            complexity_indicators += 1

        complex_keywords = ["authentication", "security", "migration", "integration",
                          "oauth", "api", "database", "performance", "scalability"]
        complexity_indicators += sum(1 for kw in complex_keywords if kw in text)

        if complexity_indicators >= 5:
            complexity_level = "complex"
            complexity_score = 8.0
        elif complexity_indicators >= 3:
            complexity_level = "moderate"
            complexity_score = 5.5
        else:
            complexity_level = "simple"
            complexity_score = 3.0

        # Determine validation needs
        validation_needs = "thorough"
        if any(kw in text for kw in ["security", "auth", "payment", "critical"]):
            validation_needs = "critical"
        elif complexity_level == "simple":
            validation_needs = "basic"

        # Check for UI changes
        has_ui_changes = any(kw in text for kw in ["ui", "frontend", "button", "form", "page", "component", "display", "user interface"])

        # Check for E2E test needs
        requires_e2e_tests = has_ui_changes or "workflow" in text or "user" in text

        # Extract requirements from description
        key_requirements = [issue.title]
        if issue.body:
            # Simple extraction: look for bullet points or numbered lists
            lines = issue.body.split('\n')
            for line in lines:
                if line.strip().startswith(('-', '*', '•')) or (len(line) > 0 and line[0].isdigit() and '.' in line[:3]):
                    req = line.strip().lstrip('-*•0123456789. ')
                    if len(req) > 10 and len(req) < 200:
                        key_requirements.append(req)

        # Limit to 5 requirements
        key_requirements = key_requirements[:5]

        # Estimate effort
        if complexity_level == "complex":
            estimated_effort_hours = 12.0
        elif complexity_level == "moderate":
            estimated_effort_hours = 6.0
        else:
            estimated_effort_hours = 2.0

        # Identify risk factors
        risk_factors = []
        if validation_needs == "critical":
            risk_factors.append("High-impact changes requiring careful validation")
        if "database" in text or "migration" in text:
            risk_factors.append("Database changes - data integrity risk")
        if "breaking" in text:
            risk_factors.append("Breaking changes - backward compatibility risk")

        # External dependencies
        external_dependencies = []
        if "api" in text or "integration" in text:
            external_dependencies.append("External API/service")
        if "oauth" in text or "auth" in text:
            external_dependencies.append("Authentication provider")

        # Model set recommendation
        recommended_model_set = "heavy" if complexity_level == "complex" else "base"

        task_analysis = TaskAnalysis(
            task_type=task_type,
            complexity_score=complexity_score,
            complexity_level=complexity_level,
            validation_needs=validation_needs,
            key_requirements=key_requirements,
            estimated_effort_hours=estimated_effort_hours,
            risk_factors=risk_factors if risk_factors else ["Standard development risks"],
            has_ui_changes=has_ui_changes,
            requires_e2e_tests=requires_e2e_tests,
            external_dependencies=external_dependencies,
            recommended_model_set=recommended_model_set,
        )

        logger.info(
            f"Analysis complete: {task_analysis.complexity_level} "
            f"(score: {task_analysis.complexity_score:.1f})"
        )
        return task_analysis

    def conduct_interview_legacy(self, issue: GitHubIssue) -> Dict[str, Any]:
        """Conduct user interview about the task.

        Args:
            issue: GitHub issue details

        Returns:
            Dictionary with interview responses

        Raises:
            Exception: If interview fails
        """
        logger.info("Conducting user interview...")

        # Prepare interview prompt with issue context
        interview_prompt = f"""
Task Description: {issue.title}

{issue.body or 'No additional description provided'}

Please analyze this task and provide structured answers to the interview questions.
        """.strip()

        try:
            # Execute interview template
            request = AgentTemplateRequest(
                agent_name="strategist",
                slash_command="/strategy/interview",
                args=[interview_prompt],
                adw_id="meta_adw",
                model="sonnet",
                working_dir=str(self.repo_root),
            )
            response = execute_template(request)

            # Debug: Log response details
            logger.info(f"Interview response success: {response.success}")
            logger.info(f"Interview response output length: {len(response.output)}")
            if not response.success or not response.output.strip():
                logger.error(f"Interview failed. Full response: {response}")
                raise Exception(f"Interview execution failed: {response.output}")

            # Extract JSON from response (handle markdown code fences)
            output = response.output.strip()
            if output.startswith("```json"):
                output = output.split("```json", 1)[1].split("```")[0].strip()
            elif output.startswith("```"):
                output = output.split("```", 2)[1].strip()

            # Find JSON object boundaries
            start = output.find('{')
            end = output.rfind('}') + 1
            if start != -1 and end > start:
                output = output[start:end]

            # Parse JSON response
            interview_data = json.loads(output)
            logger.info(f"Interview completed: {interview_data.get('task_type', 'unknown')} task")
            return interview_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse interview response as JSON: {e}")
            raise
        except Exception as e:
            logger.error(f"Interview failed: {e}")
            raise

    def analyze_task(self, interview_data: Dict[str, Any]) -> TaskAnalysis:
        """Analyze task complexity and requirements.

        Args:
            interview_data: Dictionary with interview responses

        Returns:
            TaskAnalysis object

        Raises:
            Exception: If analysis fails
        """
        logger.info("Analyzing task complexity...")

        try:
            # Execute analyze template with interview results
            interview_json = json.dumps(interview_data, indent=2)
            request = AgentTemplateRequest(
                agent_name="strategist",
                slash_command="/strategy/analyze",
                args=[interview_json],
                adw_id="meta_adw",
                model="sonnet",
                working_dir=str(self.repo_root),
            )
            response = execute_template(request)

            # Extract JSON from response (handle markdown code fences)
            output = response.output.strip()
            if output.startswith("```json"):
                output = output.split("```json", 1)[1].split("```")[0].strip()
            elif output.startswith("```"):
                output = output.split("```", 2)[1].strip()

            # Find JSON object boundaries
            start = output.find('{')
            end = output.rfind('}') + 1
            if start != -1 and end > start:
                output = output[start:end]

            # Parse JSON response
            analysis_data = json.loads(output)
            task_analysis = TaskAnalysis.model_validate(analysis_data)

            logger.info(
                f"Analysis complete: {task_analysis.complexity_level} "
                f"(score: {task_analysis.complexity_score:.1f})"
            )
            return task_analysis

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse analysis response as JSON: {e}")
            raise
        except Exception as e:
            logger.error(f"Task analysis failed: {e}")
            raise

    def get_recommendation(self, task_analysis: TaskAnalysis) -> StrategyRecommendation:
        """Get workflow strategy recommendation.

        Args:
            task_analysis: TaskAnalysis object

        Returns:
            StrategyRecommendation object

        Raises:
            Exception: If recommendation fails
        """
        logger.info("Generating strategy recommendation...")

        try:
            # Use decision engine to generate recommendation
            recommendation = self.decision_engine.recommend_strategy(task_analysis)

            logger.info(
                f"Recommendation: {recommendation.workflow_name} "
                f"(confidence: {recommendation.confidence_score:.2f})"
            )
            return recommendation

        except Exception as e:
            logger.error(f"Recommendation failed: {e}")
            raise

    def display_recommendation(self, recommendation: StrategyRecommendation) -> None:
        """Display recommendation to user.

        Args:
            recommendation: StrategyRecommendation object
        """
        print("\n" + "="*80)
        print("META-ADW STRATEGY RECOMMENDATION")
        print("="*80)
        print(f"\nPrimary Recommendation: {recommendation.workflow_name}")
        print(f"Confidence: {recommendation.confidence_score:.1%}")
        print(f"\nReasoning: {recommendation.reasoning}")
        print(f"\nValidation Strategy: {recommendation.validation_strategy}")
        print(f"\nEstimated Tokens: {recommendation.estimated_tokens:,}")

        if recommendation.recommended_phases:
            print(f"\nPhases: {' → '.join(recommendation.recommended_phases)}")

        if recommendation.trade_offs:
            print("\nTrade-offs:")
            for trade_off in recommendation.trade_offs:
                print(f"  • {trade_off}")

        if recommendation.alternatives:
            print("\nAlternative Options:")
            for i, alt in enumerate(recommendation.alternatives, 1):
                workflow = alt.get("workflow_name", alt.get("workflow", "unknown"))
                confidence = alt.get("confidence", 0.0)
                reasoning = alt.get("reasoning", "No reasoning provided")
                print(f"  {i}. {workflow} (confidence: {confidence:.1%})")
                print(f"     {reasoning}")

        print("\n" + "="*80)

    def prompt_user_confirmation(self, recommendation: StrategyRecommendation) -> str:
        """Prompt user to confirm or override recommendation.

        Args:
            recommendation: StrategyRecommendation object

        Returns:
            Selected workflow name
        """
        print("\nOptions:")
        print(f"  1. Use recommended workflow: {recommendation.workflow_name}")

        if recommendation.alternatives:
            for i, alt in enumerate(recommendation.alternatives, 2):
                workflow = alt.get("workflow_name", alt.get("workflow", "unknown"))
                print(f"  {i}. Use alternative: {workflow}")

        print("  0. Cancel")

        while True:
            try:
                choice = input("\nSelect option (default: 1): ").strip()
                if not choice:
                    choice = "1"

                choice_num = int(choice)

                if choice_num == 0:
                    logger.info("User cancelled execution")
                    return ""
                elif choice_num == 1:
                    return recommendation.workflow_name
                elif 2 <= choice_num <= len(recommendation.alternatives) + 1:
                    alt = recommendation.alternatives[choice_num - 2]
                    workflow = alt.get("workflow_name", alt.get("workflow"))
                    logger.info(f"User selected alternative: {workflow}")
                    return workflow
                else:
                    print(f"Invalid choice. Please enter 0-{len(recommendation.alternatives) + 1}")
            except ValueError:
                print("Invalid input. Please enter a number.")
            except (KeyboardInterrupt, EOFError):
                print("\nCancelled by user")
                return ""

    def log_execution(
        self,
        issue_number: int,
        interview_data: Dict[str, Any],
        task_analysis: TaskAnalysis,
        recommendation: StrategyRecommendation,
        selected_workflow: str,
        outcome: str,
        error: Optional[str] = None,
    ) -> Path:
        """Log execution details for learning system.

        Args:
            issue_number: GitHub issue number
            interview_data: Interview responses
            task_analysis: Task analysis result
            recommendation: Strategy recommendation
            selected_workflow: Workflow selected by user
            outcome: "success", "failure", or "cancelled"
            error: Error message if outcome is "failure"

        Returns:
            Path to execution log file
        """
        timestamp = datetime.utcnow().isoformat()
        log_file = self.execution_log_dir / f"{timestamp.replace(':', '-')}-issue-{issue_number}.json"

        log_data = {
            "timestamp": timestamp,
            "issue_number": issue_number,
            "interview_responses": interview_data,
            "task_analysis": task_analysis.model_dump(mode='json'),
            "recommendation": recommendation.model_dump(mode='json'),
            "selected_workflow": selected_workflow,
            "outcome": outcome,
            "error": error,
        }

        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)

        logger.info(f"Execution logged to {log_file}")
        return log_file

    def collect_feedback(
        self,
        adw_id: str,
        issue_number: int,
        workflow_name: str,
        task_analysis: TaskAnalysis,
        recommendation: StrategyRecommendation,
        start_time: datetime,
    ) -> LearningRecord:
        """Collect comprehensive feedback from all sources.

        Args:
            adw_id: ADW execution ID
            issue_number: GitHub issue number
            workflow_name: Workflow that was executed
            task_analysis: Task analysis performed
            recommendation: Strategy recommendation made
            start_time: When workflow started

        Returns:
            LearningRecord with comprehensive feedback
        """
        if not ENABLE_LEARNING:
            logger.info("Learning disabled, skipping feedback collection")
            return None

        logger.info("Collecting comprehensive execution feedback...")

        # Initialize collectors
        test_collector = TestFeedbackCollector(self.repo_root)
        review_collector = ReviewFeedbackCollector(self.repo_root)
        deployment_collector = DeploymentFeedbackCollector(self.repo_root)

        # Collect feedback from all sources
        test_feedback = test_collector.collect(adw_id, str(issue_number))
        review_feedback = review_collector.collect(adw_id, str(issue_number))
        deployment_feedback = deployment_collector.collect(adw_id, str(issue_number))

        # Determine outcome
        outcome = self._determine_outcome(test_feedback, review_feedback, deployment_feedback)

        # Extract problems
        problems = []
        if test_feedback and test_feedback.get("failed", 0) > 0:
            problems.extend([
                f"Test failures in {cat}" for cat in test_feedback.get("failure_patterns", [])
            ])
        if review_feedback and review_feedback.get("review_status") == "changes_requested":
            categories = ', '.join(review_feedback.get('change_categories', []))
            problems.append(f"Code review changes: {categories}")
        if deployment_feedback and deployment_feedback.get("post_deployment_errors"):
            problems.extend(deployment_feedback["post_deployment_errors"])

        # Build success metrics
        success_metrics = {
            "test_success_rate": test_feedback.get("success_rate") if test_feedback else None,
            "review_approved": review_feedback.get("review_status") == "approved" if review_feedback else None,
            "deployed_successfully": deployment_feedback.get("deployment_status") == "success" if deployment_feedback else None,
            "human_changes_needed": review_feedback.get("human_changes_made") if review_feedback else False,
            "execution_time_minutes": (datetime.utcnow() - start_time).total_seconds() / 60,
        }

        # Detect false fix
        false_fix = self._detect_false_fix(test_feedback, review_feedback)

        # Create learning record
        record = LearningRecord(
            task_description=task_analysis.description,
            task_analysis=task_analysis,
            recommended_strategy=recommendation,
            selected_strategy=workflow_name,
            user_overrode_recommendation=workflow_name != recommendation.workflow_name,
            outcome=outcome,
            success_metrics=success_metrics,
            problems_encountered=problems,
            false_fix_detected=false_fix,
            user_satisfaction=None,  # Could be collected via GitHub reactions
            execution_timestamp=datetime.utcnow(),
            adw_id=adw_id,
            issue_number=str(issue_number),
        )

        # Store locally
        test_collector.store_learning_record(record)

        logger.info(f"Feedback collected: outcome={outcome}, problems={len(problems)}")

        return record

    def _determine_outcome(
        self,
        test_fb: Optional[Dict],
        review_fb: Optional[Dict],
        deploy_fb: Optional[Dict]
    ) -> str:
        """Determine overall outcome from feedback.

        Args:
            test_fb: Test feedback dict
            review_fb: Review feedback dict
            deploy_fb: Deployment feedback dict

        Returns:
            "success" | "partial" | "failure" | "unknown"
        """
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
        if test_fb or review_fb or deploy_fb:
            return "partial"

        return "unknown"

    def _detect_false_fix(
        self,
        test_fb: Optional[Dict],
        review_fb: Optional[Dict]
    ) -> bool:
        """Enhanced false fix detection.

        Args:
            test_fb: Test feedback dict
            review_fb: Review feedback dict

        Returns:
            True if false fix detected
        """
        # If human had to fix logic issues, it was a false fix
        if review_fb and review_fb.get("human_changes_made"):
            if "logic" in review_fb.get("change_categories", []):
                return True

        # Failed tests indicate incomplete fix
        if test_fb and test_fb.get("failed", 0) > 0:
            return True

        return False

    def update_pattern_database(
        self,
        task_analysis: TaskAnalysis,
        recommendation: StrategyRecommendation,
        selected_workflow: str,
        feedback: Dict[str, Any],
    ) -> None:
        """Update pattern database with execution results.

        Args:
            task_analysis: Task analysis
            recommendation: Strategy recommendation
            selected_workflow: Workflow that was executed
            feedback: Execution feedback
        """
        logger.info("Updating pattern database...")

        pattern_db_path = self.repo_root / ".tac" / "learning" / "pattern_database.json"

        try:
            # Load existing database
            if pattern_db_path.exists():
                with open(pattern_db_path, 'r') as f:
                    db = json.load(f)
            else:
                db = {
                    "patterns": [],
                    "version": "1.0",
                    "last_updated": "",
                    "total_patterns": 0,
                }

            # Create pattern record
            pattern = {
                "task_type": task_analysis.task_type,
                "complexity_score": task_analysis.complexity_score,
                "complexity_level": task_analysis.complexity_level,
                "validation_needs": task_analysis.validation_needs,
                "has_ui_changes": task_analysis.has_ui_changes,
                "requires_e2e_tests": task_analysis.requires_e2e_tests,
                "recommended_workflow": recommendation.workflow_name,
                "selected_workflow": selected_workflow,
                "confidence_score": recommendation.confidence_score,
                "execution_time_minutes": feedback.get("execution_time_minutes", 0),
                "is_false_fix": feedback.get("is_false_fix", False),
                "success": not feedback.get("is_false_fix", False) and feedback.get("issue_state") == "closed",
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Add to patterns
            db["patterns"].append(pattern)
            db["total_patterns"] = len(db["patterns"])
            db["last_updated"] = datetime.utcnow().isoformat()

            # Save updated database
            with open(pattern_db_path, 'w') as f:
                json.dump(db, f, indent=2)

            logger.info(f"Pattern database updated: {db['total_patterns']} total patterns")

        except Exception as e:
            logger.error(f"Failed to update pattern database: {e}")

    def retrain_weights(self) -> None:
        """Retrain decision weights based on accumulated patterns.

        Analyzes pattern database and adjusts weights to improve recommendations.
        Only retrains after minimum number of executions (default: 10).
        """
        logger.info("Checking if weight retraining is needed...")

        pattern_db_path = self.repo_root / ".tac" / "learning" / "pattern_database.json"
        weights_path = self.repo_root / ".tac" / "learning" / "decision_weights.json"

        try:
            # Load pattern database
            if not pattern_db_path.exists():
                logger.info("No pattern database yet, skipping retraining")
                return

            with open(pattern_db_path, 'r') as f:
                db = json.load(f)

            patterns = db.get("patterns", [])
            if len(patterns) < 10:
                logger.info(f"Only {len(patterns)} patterns, need 10+ for retraining")
                return

            # Load current weights
            if weights_path.exists():
                with open(weights_path, 'r') as f:
                    weights_data = json.load(f)
            else:
                weights_data = {
                    "version": "1.0",
                    "weights": {
                        "template_match": 0.4,
                        "complexity_match": 0.3,
                        "validation_depth": 0.3,
                    },
                    "learning_rate": 0.1,
                }

            # Analyze success patterns
            successful_patterns = [p for p in patterns if p.get("success", False)]
            success_rate = len(successful_patterns) / len(patterns) if patterns else 0

            logger.info(f"Success rate: {success_rate:.1%} ({len(successful_patterns)}/{len(patterns)})")

            # Simple weight adjustment based on success rate
            # In production, would use more sophisticated analysis
            learning_rate = weights_data.get("learning_rate", 0.1)

            if success_rate < 0.7:
                # Adjust weights to prioritize historical success more
                weights_data["weights"]["template_match"] += learning_rate * 0.1
                weights_data["weights"]["complexity_match"] -= learning_rate * 0.05
                weights_data["weights"]["validation_depth"] -= learning_rate * 0.05
                logger.info("Adjusted weights to prioritize template matching")
            elif success_rate > 0.9:
                # System working well, no changes needed
                logger.info("High success rate, weights unchanged")
            else:
                # Moderate success, minor adjustments
                logger.info("Moderate success rate, keeping current weights")

            # Normalize weights to sum to 1.0
            total = sum(weights_data["weights"].values())
            for key in weights_data["weights"]:
                weights_data["weights"][key] /= total

            # Save updated weights
            weights_data["last_retrained"] = datetime.utcnow().isoformat()
            with open(weights_path, 'w') as f:
                json.dump(weights_data, f, indent=2)

            logger.info(f"Weights retrained: {weights_data['weights']}")

        except Exception as e:
            logger.error(f"Failed to retrain weights: {e}")

    def sync_cross_project_learning(self, project_name: Optional[str] = None) -> None:
        """Sync learnings between project and global store.

        Call this after each ADW execution to aggregate learnings.

        Args:
            project_name: Name of current project (defaults to repo name from env)
        """
        if not ENABLE_LEARNING:
            return

        # Get project name
        if not project_name:
            repo_url = get_repo_url()
            project_name = repo_url.split("/")[-1].replace(".git", "")

        # Global learning directory (in agentic-coding-library repo)
        global_learning_dir = Path.home() / "agentic-coding-library" / ".tac" / "learning" / "global"

        try:
            store = CrossProjectLearningStore(global_learning_dir)

            # Aggregate this project's learnings to global
            local_learning_dir = self.repo_root / ".tac" / "learning"
            store.aggregate_from_project(project_name, local_learning_dir)

            # Sync global learnings back to this project
            store.sync_to_project(local_learning_dir)

            logger.info(f"Cross-project learning synced for {project_name}")

            # Log global insights
            insights = store.get_global_insights()
            logger.info(
                f"Global insights: {insights['total_patterns']} patterns, "
                f"{insights['average_success_rate']:.1%} avg success rate, "
                f"{insights['total_projects']} projects"
            )

        except Exception as e:
            logger.warning(f"Failed to sync cross-project learning: {e}")

    def apply_prompt_refinement(
        self,
        feedback_record: LearningRecord,
    ) -> None:
        """Apply prompt refinement based on feedback.

        Call this after collecting feedback to improve prompts.

        Args:
            feedback_record: LearningRecord with execution feedback
        """
        if not ENABLE_LEARNING or not feedback_record:
            return

        try:
            refiner = PromptRefiner(self.repo_root)

            # Prepare feedback for refiner
            feedback = {
                "test_failures": [
                    p.split("Test failures in ")[-1]
                    for p in feedback_record.problems_encountered
                    if "Test failures in" in p
                ],
                "review_changes": self._extract_review_categories(feedback_record),
                "deployment_errors": feedback_record.success_metrics.get("deployed_successfully") == False,
                "success_rate": feedback_record.success_metrics.get("test_success_rate", 1.0),
            }

            # Determine which prompt to refine based on task
            prompt_id = self._map_task_to_prompt(feedback_record.task_analysis.task_type)

            # Get current prompt
            current_prompt = self._load_current_prompt(prompt_id)

            if not current_prompt:
                logger.debug(f"No prompt found for {prompt_id}, skipping refinement")
                return

            # Refine
            refined_prompt = refiner.refine_prompt(
                prompt_id=prompt_id,
                current_prompt=current_prompt,
                feedback=feedback,
                max_iterations=3
            )

            logger.info(f"Refined prompt {prompt_id}")

        except Exception as e:
            logger.warning(f"Failed to apply prompt refinement: {e}")

    def _extract_review_categories(self, record: LearningRecord) -> List[str]:
        """Extract review change categories from problems.

        Args:
            record: LearningRecord

        Returns:
            List of category strings
        """
        categories = []
        for problem in record.problems_encountered:
            if "Code review changes:" in problem:
                cats = problem.split(":")[-1].strip().split(", ")
                categories.extend(cats)
        return categories

    def _map_task_to_prompt(self, task_type: str) -> str:
        """Map task type to prompt ID.

        Args:
            task_type: Task type from TaskAnalysis

        Returns:
            Prompt identifier string
        """
        mapping = {
            "feature": "feature_planning",
            "bug": "bug_fixing",
            "chore": "chore_execution",
            "patch": "quick_patch",
        }
        return mapping.get(task_type, "general_task")

    def _load_current_prompt(self, prompt_id: str) -> Optional[str]:
        """Load current version of a prompt.

        Args:
            prompt_id: Prompt identifier

        Returns:
            Prompt text or None if not found
        """
        # Try tac-core-plugin/commands/ first
        prompt_file = self.repo_root / "tac-core-plugin" / "commands" / f"{prompt_id.replace('_', '-')}.md"

        if not prompt_file.exists():
            # Try .tac/prompts/
            prompt_file = self.repo_root / ".tac" / "prompts" / f"{prompt_id}_latest.md"

        if prompt_file.exists():
            try:
                with open(prompt_file) as f:
                    return f.read()
            except Exception as e:
                logger.debug(f"Could not read prompt file: {e}")

        return None

    def execute_workflow(
        self,
        workflow_name: str,
        issue_number: int,
        model_set: ModelSet,
        adw_id: Optional[str] = None,
    ) -> bool:
        """Execute selected workflow.

        Args:
            workflow_name: Name of ADW workflow to execute
            issue_number: GitHub issue number
            model_set: Model set to use
            adw_id: Optional ADW ID for dependent workflows

        Returns:
            True if execution succeeded, False otherwise
        """
        logger.info(f"Executing workflow: {workflow_name}")

        # Map workflow names to scripts
        workflow_scripts = {
            "adw_patch_iso": "adw_patch_iso.py",
            "adw_plan_build_iso": "adw_plan_build_iso.py",
            "adw_plan_build_test_iso": "adw_plan_build_test_iso.py",
            "adw_sdlc_iso": "adw_sdlc_iso.py",
            "adw_plan_build_test_review_iso": "adw_plan_build_test_review_iso.py",
        }

        script_name = workflow_scripts.get(workflow_name)
        if not script_name:
            logger.error(f"Unknown workflow: {workflow_name}")
            return False

        # Build command
        script_path = self.repo_root / "adw" / script_name
        if not script_path.exists():
            logger.error(f"Workflow script not found: {script_path}")
            return False

        # For now, just log that we would execute it
        # In production, we would actually execute the workflow
        logger.info(f"Would execute: uv run {script_path} {issue_number} --model-set {model_set}")
        logger.info("Note: Actual workflow execution not implemented in MVP")

        return True

    def run(
        self,
        issue_number: int,
        adw_id: Optional[str] = None,
        model_set: ModelSet = "base",
    ) -> int:
        """Run complete Meta-ADW workflow.

        Args:
            issue_number: GitHub issue number
            adw_id: Optional ADW ID for dependent workflows
            model_set: Model set to use

        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        logger.info(f"Starting Meta-ADW for issue #{issue_number}")

        task_analysis = None
        recommendation = None
        selected_workflow = None
        start_time = datetime.utcnow()

        try:
            # Step 1: Fetch issue
            issue = self.fetch_issue(issue_number)

            # Step 2: Analyze issue directly (simplified - no CLI templates)
            task_analysis = self.analyze_issue_directly(issue)

            # Create interview_data for logging (synthesized from issue)
            interview_data = {
                "task_description": issue.title,
                "task_type": task_analysis.task_type,
                "complexity_level": task_analysis.complexity_level,
                "validation_needs": task_analysis.validation_needs,
                "analysis_method": "direct_issue_analysis"
            }

            # Step 3: Get recommendation from decision engine
            recommendation = self.get_recommendation(task_analysis)

            # Step 5: Display and confirm
            self.display_recommendation(recommendation)
            selected_workflow = self.prompt_user_confirmation(recommendation)

            if not selected_workflow:
                self.log_execution(
                    issue_number=issue_number,
                    interview_data=interview_data or {},
                    task_analysis=task_analysis,
                    recommendation=recommendation,
                    selected_workflow="",
                    outcome="cancelled",
                )
                logger.info("Execution cancelled by user")
                return 1

            # Step 6: Execute workflow
            success = self.execute_workflow(
                workflow_name=selected_workflow,
                issue_number=issue_number,
                model_set=model_set,
                adw_id=adw_id,
            )

            # Step 7: Collect feedback (learning system)
            feedback = self.collect_feedback(
                issue_number=issue_number,
                workflow_name=selected_workflow,
                start_time=start_time,
            )

            # Step 8: Update pattern database (learning system)
            self.update_pattern_database(
                task_analysis=task_analysis,
                recommendation=recommendation,
                selected_workflow=selected_workflow,
                feedback=feedback,
            )

            # Step 9: Retrain weights if needed (learning system)
            self.retrain_weights()

            # Step 10: Log execution
            outcome = "success" if success else "failure"
            self.log_execution(
                issue_number=issue_number,
                interview_data=interview_data or {},
                task_analysis=task_analysis,
                recommendation=recommendation,
                selected_workflow=selected_workflow,
                outcome=outcome,
            )

            if success:
                logger.info("Meta-ADW execution completed successfully")
                return 0
            else:
                logger.error("Workflow execution failed")
                return 1

        except Exception as e:
            logger.error(f"Meta-ADW execution failed: {e}", exc_info=True)

            # Log failure
            if interview_data and task_analysis and recommendation:
                self.log_execution(
                    issue_number=issue_number,
                    interview_data=interview_data,
                    task_analysis=task_analysis,
                    recommendation=recommendation,
                    selected_workflow=selected_workflow or "",
                    outcome="failure",
                    error=str(e),
                )

            return 1


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Meta-ADW Strategy Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run adw/meta_strategy.py 123
  uv run adw/meta_strategy.py 123 --model-set heavy
        """,
    )

    parser.add_argument(
        "issue_number",
        type=int,
        help="GitHub issue number",
    )

    parser.add_argument(
        "--adw-id",
        type=str,
        help="ADW ID for dependent workflows (optional)",
    )

    parser.add_argument(
        "--model-set",
        type=str,
        choices=["base", "heavy"],
        default="base",
        help="Model set to use (default: base)",
    )

    args = parser.parse_args()

    # Run orchestrator
    orchestrator = MetaStrategyOrchestrator()
    return orchestrator.run(
        issue_number=args.issue_number,
        adw_id=args.adw_id,
        model_set=args.model_set,  # Already validated by argparse choices
    )


if __name__ == "__main__":
    sys.exit(main())
