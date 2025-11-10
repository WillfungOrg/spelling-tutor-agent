#!/usr/bin/env -S uv run
# /// script
# dependencies = ["fastapi", "uvicorn", "python-dotenv", "claude-agent-sdk"]
# ///

"""
GitHub Webhook Trigger - AI Developer Workflow (ADW)

FastAPI webhook endpoint that receives GitHub issue events and triggers ADW workflows.
Responds immediately to meet GitHub's 10-second timeout by launching workflows
in the background. Supports both standard and isolated workflows.

Usage: uv run trigger_webhook.py

Environment Requirements:
- PORT: Server port (default: 8001)
- All workflow requirements (GITHUB_PAT, ANTHROPIC_API_KEY, etc.)
"""

import os
import subprocess
import sys
from typing import Optional
from fastapi import FastAPI, Request
from dotenv import load_dotenv
import uvicorn

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hub_modules.utils import make_adw_id, setup_logger, get_safe_subprocess_env
from hub_modules.github import make_issue_comment, ADW_BOT_IDENTIFIER
from hub_modules.workflow_ops import extract_adw_info_async, AVAILABLE_ADW_WORKFLOWS
from hub_modules.state import ADWState

# Load environment variables
load_dotenv()

# Configuration
PORT = int(os.getenv("PORT", "8001"))

# Dependent workflows that require existing worktrees
# These cannot be triggered directly via webhook
DEPENDENT_WORKFLOWS = [
    "adw_build_iso",
    "adw_test_iso",
    "adw_review_iso",
    "adw_document_iso",
    "adw_ship_iso",
]

# Label to workflow mapping
# Maps GitHub issue labels to ADW workflow commands
LABEL_TO_WORKFLOW = {
    # Planning
    "adw-plan": "adw_plan_iso",
    "adw-design": "adw_plan_iso",

    # Quick fixes
    "adw-patch": "adw_patch_iso",
    "adw-hotfix": "adw_patch_iso",

    # Implementation (dependent - requires existing plan)
    "adw-implement": "adw_build_iso",
    "adw-build": "adw_build_iso",

    # Testing (dependent)
    "adw-test": "adw_test_iso",
    "adw-e2e": "adw_test_e2e",

    # Review & Documentation (dependent)
    "adw-review": "adw_review_iso",
    "adw-document": "adw_document_iso",

    # Complete workflows
    "adw-sdlc": "adw_sdlc_iso",
    "adw-full": "adw_sdlc_iso",
    "adw-zte": "adw_sdlc_ZTE_iso",

    # Combined workflows
    "adw-plan-build": "adw_plan_build_iso",
    "adw-pbt": "adw_plan_build_test_iso",
    "adw-pbtr": "adw_plan_build_test_review_iso",

    # Meta strategy
    "adw-strategy": "meta_adw_strategy",
}

# Model selection labels
LABEL_TO_MODEL_SET = {
    "adw-heavy": "heavy",
    "adw-fast": "base",
}

# Create FastAPI app
app = FastAPI(
    title="ADW Webhook Trigger", description="GitHub webhook endpoint for ADW"
)

print(f"Starting ADW Webhook Trigger on port {PORT}")


def extract_workflow_from_labels(labels: list) -> tuple[Optional[str], Optional[str]]:
    """Extract ADW workflow and model_set from GitHub issue labels.

    Args:
        labels: List of label dicts from GitHub webhook payload

    Returns:
        Tuple of (workflow_command, model_set) or (None, None) if no ADW labels found
    """
    workflow = None
    model_set = "base"  # Default

    for label in labels:
        label_name = label.get("name", "").lower()

        # Check for workflow label
        if label_name in LABEL_TO_WORKFLOW and not workflow:
            workflow = LABEL_TO_WORKFLOW[label_name]

        # Check for model selection label
        if label_name in LABEL_TO_MODEL_SET:
            model_set = LABEL_TO_MODEL_SET[label_name]

    return workflow, model_set


def ensure_repo_ready(repo_full_name: str, repo_clone_url: str, logger) -> str:
    """Ensure target repository is cloned and has plugin installed.

    Args:
        repo_full_name: Full repo name (e.g., "owner/repo-name")
        repo_clone_url: Git clone URL for the repository
        logger: Logger instance for this operation

    Returns:
        Path to the cloned repository
    """
    # Get repo name from full name
    repo_name = repo_full_name.split("/")[-1]

    # Determine paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    webhook_hub_dir = os.path.dirname(script_dir)  # webhook-hub directory
    library_root = os.path.dirname(webhook_hub_dir)  # agentic-coding-library root

    # Check if this is the same repo where webhook is running
    current_repo_name = os.path.basename(library_root)

    if repo_name == current_repo_name:
        # Same repo - use the current working directory, no cloning needed
        logger.info(f"Issue is from same repository ({repo_name}), using current directory")
        logger.info(f"Target repository: {library_root}")
        return library_root

    # Different repo - clone as usual
    runtime_dir = os.path.join(webhook_hub_dir, "runtime")
    repos_dir = os.path.join(runtime_dir, "repos")
    os.makedirs(repos_dir, exist_ok=True)

    # Target repo path
    repo_path = os.path.join(repos_dir, repo_name)

    # Check if repo already exists
    if os.path.exists(repo_path):
        logger.info(f"Repository {repo_name} already cloned, pulling latest changes")
        try:
            # Pull latest changes
            subprocess.run(
                ["git", "pull"],
                cwd=repo_path,
                capture_output=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to pull latest changes: {e}")
    else:
        logger.info(f"Cloning repository {repo_full_name} to {repo_path}")
        try:
            # Clone the repository
            subprocess.run(
                ["git", "clone", repo_clone_url, repo_path],
                capture_output=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to clone repository: {e}")
            raise

    # Check if plugin exists in target repo
    plugin_path = os.path.join(repo_path, "tac-core-plugin")

    if not os.path.exists(plugin_path):
        logger.info(f"Installing tac-core-plugin in {repo_name}")
        # Copy plugin from library to target repo
        # library_root is the parent directory of webhook-hub (agentic-coding-library root)
        library_root = os.path.dirname(webhook_hub_dir)
        library_plugin = os.path.join(library_root, "tac-core-plugin")

        if os.path.exists(library_plugin):
            import shutil
            shutil.copytree(library_plugin, plugin_path)
            logger.info(f"Plugin installed in {repo_name}")
        else:
            logger.error(f"Plugin source not found at {library_plugin}")
            raise FileNotFoundError(f"Plugin source not found at {library_plugin}")
    else:
        logger.info(f"Plugin already exists in {repo_name}")

    # adw_modules are inside tac-core-plugin, no separate copy needed
    return repo_path


@app.post("/gh-webhook")
async def github_webhook(request: Request):
    """Handle GitHub webhook events from multiple repositories."""
    try:
        # Get event type from header
        event_type = request.headers.get("X-GitHub-Event", "")

        # Parse webhook payload
        payload = await request.json()

        # Extract event details
        action = payload.get("action", "")
        issue = payload.get("issue", {})
        issue_number = issue.get("number")

        # Extract repository information
        repository = payload.get("repository", {})
        repo_full_name = repository.get("full_name", "unknown/unknown")
        repo_clone_url = repository.get("clone_url", "")

        print(
            f"Received webhook: repo={repo_full_name}, event={event_type}, action={action}, issue_number={issue_number}"
        )

        workflow = None
        provided_adw_id = None
        model_set = None
        trigger_reason = ""
        content_to_check = ""

        # Check if this is an issue opened or labeled event
        if event_type == "issues" and action in ["opened", "labeled"] and issue_number:
            issue_body = issue.get("body", "")
            issue_labels = issue.get("labels", [])
            content_to_check = issue_body

            # Ignore issues from ADW bot to prevent loops
            if ADW_BOT_IDENTIFIER in issue_body:
                print(f"Ignoring ADW bot issue to prevent loop")
                workflow = None
            else:
                # First, check labels for ADW workflow
                workflow_from_label, model_from_label = extract_workflow_from_labels(issue_labels)
                if workflow_from_label:
                    workflow = workflow_from_label
                    model_set = model_from_label
                    label_names = [l.get("name") for l in issue_labels if l.get("name", "").startswith("adw-")]
                    trigger_reason = f"Issue with label(s): {', '.join(label_names)}"
                    print(f"Detected workflow from labels: {workflow}, model_set: {model_set}")

                # If no workflow from labels, check body for "adw_" text
                elif "adw_" in issue_body.lower():
                    # Use temporary ID for classification
                    temp_id = make_adw_id()
                    extraction_result = await extract_adw_info_async(issue_body, temp_id)
                    if extraction_result.has_workflow:
                        workflow = extraction_result.workflow_command
                        provided_adw_id = extraction_result.adw_id
                        model_set = extraction_result.model_set
                        trigger_reason = f"New issue with {workflow} workflow"

        # Check if this is an issue comment
        elif event_type == "issue_comment" and action == "created" and issue_number:
            comment = payload.get("comment", {})
            comment_body = comment.get("body", "")
            content_to_check = comment_body

            print(f"Comment body: '{comment_body}'")

            # Ignore comments from ADW bot to prevent loops
            if ADW_BOT_IDENTIFIER in comment_body:
                print(f"Ignoring ADW bot comment to prevent loop")
                workflow = None
            # Check if comment contains "adw_"
            elif "adw_" in comment_body.lower():
                # Use temporary ID for classification
                temp_id = make_adw_id()
                extraction_result = await extract_adw_info_async(comment_body, temp_id)
                if extraction_result.has_workflow:
                    workflow = extraction_result.workflow_command
                    provided_adw_id = extraction_result.adw_id
                    model_set = extraction_result.model_set
                    trigger_reason = f"Comment with {workflow} workflow"

        # Validate workflow constraints
        if workflow in DEPENDENT_WORKFLOWS:
            if not provided_adw_id:
                print(
                    f"{workflow} is a dependent workflow that requires an existing ADW ID"
                )
                print(f"Cannot trigger {workflow} directly via webhook without ADW ID")
                workflow = None
                # Post error comment to issue
                try:
                    make_issue_comment(
                        str(issue_number),
                        f"❌ Error: `{workflow}` is a dependent workflow that requires an existing ADW ID.\n\n"
                        f"To run this workflow, you must provide the ADW ID in your comment, for example:\n"
                        f"`{workflow} adw-12345678`\n\n"
                        f"The ADW ID should come from a previous workflow run (like `adw_plan_iso` or `adw_patch_iso`).",
                    )
                except Exception as e:
                    print(f"Failed to post error comment: {e}")

        if workflow:
            # Use provided ADW ID or generate a new one
            adw_id = provided_adw_id or make_adw_id()

            # If ADW ID was provided, update/create state file
            if provided_adw_id:
                # Try to load existing state first
                state = ADWState.load(provided_adw_id)
                if state:
                    # Update issue_number and model_set if state exists
                    state.update(issue_number=str(issue_number), model_set=model_set)
                else:
                    # Only create new state if it doesn't exist
                    state = ADWState(provided_adw_id)
                    state.update(
                        adw_id=provided_adw_id,
                        issue_number=str(issue_number),
                        model_set=model_set,
                    )
                state.save("webhook_trigger")
            else:
                # Create new state for newly generated ADW ID
                state = ADWState(adw_id)
                state.update(
                    adw_id=adw_id, issue_number=str(issue_number), model_set=model_set
                )
                state.save("webhook_trigger")

            # Set up logger
            logger = setup_logger(adw_id, "webhook_trigger")
            logger.info(
                f"Detected workflow: {workflow} from content: {content_to_check[:100]}..."
            )
            logger.info(f"Target repository: {repo_full_name}")
            if provided_adw_id:
                logger.info(f"Using provided ADW ID: {provided_adw_id}")

            # Ensure target repository is cloned and ready
            try:
                repo_path = ensure_repo_ready(repo_full_name, repo_clone_url, logger)
                logger.info(f"Repository ready at: {repo_path}")
            except Exception as e:
                logger.error(f"Failed to prepare repository: {e}")
                # Post error comment to issue
                try:
                    make_issue_comment(
                        str(issue_number),
                        f"❌ Error: Failed to prepare repository for workflow execution.\n\n"
                        f"Error: {str(e)}\n\n"
                        f"Please check the webhook server logs for details.",
                    )
                except Exception as comment_error:
                    logger.error(f"Failed to post error comment: {comment_error}")
                return {"status": "error", "message": "Failed to prepare repository"}

            # Post comment to issue about detected workflow
            try:
                make_issue_comment(
                    str(issue_number),
                    f"🤖 ADW Webhook: Detected `{workflow}` workflow request\n\n"
                    f"Repository: `{repo_full_name}`\n"
                    f"Starting workflow with ID: `{adw_id}`\n"
                    f"Workflow: `{workflow}` 🏗️\n"
                    f"Model Set: `{model_set}` ⚙️\n"
                    f"Reason: {trigger_reason}\n\n"
                    f"Logs will be available at: `agents/{adw_id}/{workflow}/`",
                )
            except Exception as e:
                logger.warning(f"Failed to post issue comment: {e}")

            # Build command to run the appropriate workflow
            # Use workflow from tac-core-plugin (single source of truth)
            plugin_workflows_dir = os.path.join(repo_path, "tac-core-plugin", "workflows")
            trigger_script = os.path.join(plugin_workflows_dir, f"{workflow}.py")

            cmd = ["uv", "run", trigger_script, str(issue_number), adw_id]

            print(f"Launching {workflow} for issue #{issue_number} in {repo_full_name}")
            print(f"Command: {' '.join(cmd)} (reason: {trigger_reason})")
            print(f"Working directory: {repo_path}")
            print(f"Workflow script: {trigger_script}")

            # Launch in background using Popen with filtered environment
            process = subprocess.Popen(
                cmd,
                cwd=repo_path,  # Run from target repo where tac-core-plugin is installed
                env=get_safe_subprocess_env(),  # Pass only required environment variables
                start_new_session=True,
            )

            print(
                f"Background process started for issue #{issue_number} with ADW ID: {adw_id}"
            )
            print(f"Logs will be written to: agents/{adw_id}/{workflow}/execution.log")

            # Return immediately
            return {
                "status": "accepted",
                "issue": issue_number,
                "adw_id": adw_id,
                "workflow": workflow,
                "message": f"ADW {workflow} triggered for issue #{issue_number}",
                "reason": trigger_reason,
                "logs": f"agents/{adw_id}/{workflow}/",
            }
        else:
            print(
                f"Ignoring webhook: event={event_type}, action={action}, issue_number={issue_number}"
            )
            return {
                "status": "ignored",
                "reason": f"Not a triggering event (event={event_type}, action={action})",
            }

    except Exception as e:
        print(f"Error processing webhook: {e}")
        # Always return 200 to GitHub to prevent retries
        return {"status": "error", "message": "Internal error processing webhook"}


@app.get("/health")
async def health():
    """Health check endpoint - runs comprehensive system health check."""
    try:
        # Run the health check script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Health check is in adw_tests, not adw_triggers
        health_check_script = os.path.join(
            os.path.dirname(script_dir), "adw_tests", "health_check.py"
        )

        # Run health check with timeout
        result = subprocess.run(
            ["uv", "run", health_check_script],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.path.dirname(script_dir),  # Run from adws directory
        )

        # Print the health check output for debugging
        print("=== Health Check Output ===")
        print(result.stdout)
        if result.stderr:
            print("=== Health Check Errors ===")
            print(result.stderr)

        # Parse the output - look for the overall status
        output_lines = result.stdout.strip().split("\n")
        is_healthy = result.returncode == 0

        # Extract key information from output
        warnings = []
        errors = []

        capturing_warnings = False
        capturing_errors = False

        for line in output_lines:
            if "⚠️  Warnings:" in line:
                capturing_warnings = True
                capturing_errors = False
                continue
            elif "❌ Errors:" in line:
                capturing_errors = True
                capturing_warnings = False
                continue
            elif "📝 Next Steps:" in line:
                break

            if capturing_warnings and line.strip().startswith("-"):
                warnings.append(line.strip()[2:])
            elif capturing_errors and line.strip().startswith("-"):
                errors.append(line.strip()[2:])

        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "service": "adw-webhook-trigger",
            "health_check": {
                "success": is_healthy,
                "warnings": warnings,
                "errors": errors,
                "details": "Run health_check.py directly for full report",
            },
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "unhealthy",
            "service": "adw-webhook-trigger",
            "error": "Health check timed out",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "adw-webhook-trigger",
            "error": f"Health check failed: {str(e)}",
        }


if __name__ == "__main__":
    print(f"Starting server on http://0.0.0.0:{PORT}")
    print(f"Webhook endpoint: POST /gh-webhook")
    print(f"Health check: GET /health")

    uvicorn.run(app, host="0.0.0.0", port=PORT)
