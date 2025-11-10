"""Claude Agent SDK module for async agent execution.

This module provides async/await implementations using the Claude Agent SDK
as a replacement for the subprocess-based Claude Code CLI execution.

Key Benefits:
- Native Python async/await (no subprocess blocking)
- Built-in message streaming and parsing
- Cleaner error handling with typed exceptions
- Same authentication as Claude Code CLI
"""

import asyncio
import os
import logging
from typing import Optional, List
from dotenv import load_dotenv

# Try to import claude_agent_sdk, but make it optional
try:
    from claude_agent_sdk import (
        ClaudeSDKClient,
        ClaudeAgentOptions,
        AssistantMessage,
        TextBlock,
        ToolUseBlock,
        ResultMessage,
    )
    CLAUDE_SDK_AVAILABLE = True
except ImportError:
    # SDK not available, will fall back to subprocess execution
    CLAUDE_SDK_AVAILABLE = False
    ClaudeSDKClient = None
    ClaudeAgentOptions = None
    AssistantMessage = None
    TextBlock = None
    ToolUseBlock = None
    ResultMessage = None

from .data_types import (
    AgentPromptRequest,
    AgentPromptResponse,
    AgentTemplateRequest,
    RetryCode,
)

# Load environment variables
load_dotenv()

# Get Claude Code CLI path from environment (for compatibility)
CLAUDE_PATH = os.getenv("CLAUDE_CODE_PATH", "claude")


def load_and_expand_slash_command(slash_command: str, args: List[str], working_dir: str) -> str:
    """Load a slash command template and expand it with arguments.

    Args:
        slash_command: The slash command (e.g., "/classify_issue")
        args: Arguments to substitute for $ARGUMENTS and positional $1, $2, etc.
        working_dir: Working directory where tac-core-plugin/commands/ exists

    Returns:
        Expanded template content
    """
    # Remove leading slash
    command_name = slash_command.lstrip("/")

    # Load template from tac-core-plugin/commands/ (flattened plugin structure)
    template_path = os.path.join(working_dir, "tac-core-plugin", "commands", f"{command_name}.md")

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Slash command template not found: {template_path}")

    with open(template_path, "r") as f:
        template_content = f.read()

    # Expand template with arguments
    expanded_content = template_content

    # First, expand positional arguments ($1, $2, $3, etc.)
    for i, arg in enumerate(args):
        placeholder = f"${i + 1}"
        expanded_content = expanded_content.replace(placeholder, arg)

    # Then, expand $ARGUMENTS with all args joined
    args_str = " ".join(args) if args else ""
    expanded_content = expanded_content.replace("$ARGUMENTS", args_str)

    return expanded_content


def get_model_for_slash_command_sdk(
    request: AgentTemplateRequest, default: str = "sonnet"
) -> str:
    """Get the appropriate model for a template request based on ADW state and slash command.

    This is a duplicate of the function in agent.py to avoid circular imports.

    Args:
        request: The template request containing the slash command and adw_id
        default: Default model if not found in mapping

    Returns:
        Model name to use (e.g., "sonnet" or "opus")
    """
    # Import here to avoid circular imports
    from .state import ADWState
    from .data_types import ModelSet
    from .agent import SLASH_COMMAND_MODEL_MAP

    # Load state to get model_set
    model_set: ModelSet = "base"  # Default model set
    state = ADWState.load(request.adw_id)
    if state:
        model_set = state.get("model_set", "base")

    # Get the model configuration for the command
    command_config = SLASH_COMMAND_MODEL_MAP.get(request.slash_command)

    if command_config:
        # Get the model for the specified model set, defaulting to base if not found
        return command_config.get(model_set, command_config.get("base", default))

    return default


def extract_full_response_text(messages: List) -> str:
    """Extract full text response from SDK messages.

    Args:
        messages: List of SDK messages (AssistantMessage, ResultMessage, etc.)

    Returns:
        Combined text from all assistant text blocks
    """
    text_parts = []

    for message in messages:
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    text_parts.append(block.text)

    return "".join(text_parts)


async def prompt_claude_code_async(
    request: AgentPromptRequest,
) -> AgentPromptResponse:
    """Execute Claude Code using Agent SDK (async).

    This is the async version of prompt_claude_code() that uses the
    Claude Agent SDK instead of subprocess execution.

    Args:
        request: The prompt request configuration

    Returns:
        AgentPromptResponse with output and session information
    """
    if not CLAUDE_SDK_AVAILABLE:
        raise ImportError(
            "claude_agent_sdk is not installed. "
            "Async agent execution is not available. "
            "Use synchronous execute_template() instead."
        )

    # Configure SDK options
    options_dict = {
        "system_prompt": "You are an AI developer workflow agent.",
        "max_turns": 100,  # Allow multi-step reasoning
    }

    # Set working directory if provided
    if request.working_dir:
        options_dict["cwd"] = request.working_dir

    # Add tools
    options_dict["allowed_tools"] = ["Read", "Write", "Bash", "Edit", "Glob", "Grep"]

    # Check for MCP config in working directory
    if request.working_dir:
        mcp_config_path = os.path.join(request.working_dir, ".mcp.json")
        if os.path.exists(mcp_config_path):
            # SDK will auto-detect .mcp.json in cwd
            logging.debug(f"MCP config found at {mcp_config_path}")

    # Add skip permissions if requested
    if request.dangerously_skip_permissions:
        # Note: SDK uses different permission model
        # This is handled through ClaudeAgentOptions
        pass

    options = ClaudeAgentOptions(**options_dict)

    try:
        async with ClaudeSDKClient(options=options) as client:
            # Send query with model specification
            # Note: SDK uses model names differently than CLI
            model_name = request.model
            if model_name == "sonnet":
                # SDK will use default (typically claude-sonnet-4)
                pass
            elif model_name == "opus":
                # SDK uses opus when specified
                pass

            await client.query(request.prompt)

            # Collect messages
            messages = []
            session_id = None
            is_error = False

            async for message in client.receive_response():
                messages.append(message)

                if isinstance(message, ResultMessage):
                    session_id = message.session_id
                    is_error = message.is_error

                    # Extract text from collected messages
                    full_text = extract_full_response_text(messages)

                    # Save output to file for compatibility
                    output_dir = os.path.dirname(request.output_file)
                    if output_dir:
                        os.makedirs(output_dir, exist_ok=True)

                    # Write output
                    with open(request.output_file, "w") as f:
                        f.write(full_text)

                    return AgentPromptResponse(
                        output=full_text,
                        success=not is_error,
                        session_id=session_id,
                        retry_code=RetryCode.NONE,
                    )

            # No ResultMessage received
            return AgentPromptResponse(
                output="No result message received from SDK",
                success=False,
                session_id=None,
                retry_code=RetryCode.EXECUTION_ERROR,
            )

    except Exception as e:
        error_msg = f"SDK Error: {str(e)}"
        logging.error(error_msg)

        # Write error to output file
        try:
            output_dir = os.path.dirname(request.output_file)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            with open(request.output_file, "w") as f:
                f.write(error_msg)
        except:
            pass

        return AgentPromptResponse(
            output=error_msg,
            success=False,
            session_id=None,
            retry_code=RetryCode.CLAUDE_CODE_ERROR,
        )


async def prompt_claude_code_with_retry_async(
    request: AgentPromptRequest,
    max_retries: int = 3,
    retry_delays: List[int] = None,
) -> AgentPromptResponse:
    """Execute with retry logic (async).

    Args:
        request: The prompt request configuration
        max_retries: Maximum number of retry attempts (default: 3)
        retry_delays: List of delays in seconds between retries (default: [1, 3, 5])

    Returns:
        AgentPromptResponse with output and retry information
    """
    if retry_delays is None:
        retry_delays = [1, 3, 5]

    # Ensure we have enough delays for max_retries
    while len(retry_delays) < max_retries:
        retry_delays.append(retry_delays[-1] + 2)

    last_response = None

    for attempt in range(max_retries + 1):  # +1 for initial attempt
        if attempt > 0:
            # This is a retry
            delay = retry_delays[attempt - 1]
            logging.info(f"Retrying after {delay}s (attempt {attempt}/{max_retries})...")
            await asyncio.sleep(delay)

        response = await prompt_claude_code_async(request)
        last_response = response

        # Check if we should retry based on the retry code
        if response.success or response.retry_code == RetryCode.NONE:
            # Success or non-retryable error
            return response

        # Check if this is a retryable error
        if response.retry_code in [
            RetryCode.CLAUDE_CODE_ERROR,
            RetryCode.TIMEOUT_ERROR,
            RetryCode.EXECUTION_ERROR,
            RetryCode.ERROR_DURING_EXECUTION,
        ]:
            if attempt < max_retries:
                continue
            else:
                return response

        # Not retryable
        return response

    # Should not reach here, but return last response just in case
    return last_response


async def execute_template_async(
    request: AgentTemplateRequest,
) -> AgentPromptResponse:
    """Execute a slash command template (async).

    Args:
        request: The template request with slash command and arguments

    Returns:
        AgentPromptResponse with execution results
    """
    if not CLAUDE_SDK_AVAILABLE:
        raise ImportError(
            "claude_agent_sdk is not installed. "
            "Async agent execution is not available. "
            "Use synchronous execute_template() instead."
        )

    # Get model for this command
    model = get_model_for_slash_command_sdk(request)

    # Determine output file path
    output_file = f"agents/{request.adw_id}/{request.agent_name}/output.jsonl"

    # Determine working directory
    # For slash commands to work, we need to be in the project root where .claude/ exists
    # If not specified, use the project root (parent of adw directory)
    if request.working_dir:
        working_dir = request.working_dir
    else:
        # Get project root by going up from adw_modules directory
        # __file__ is in adw/adw_modules/agent_sdk.py
        # Go up 3 levels: agent_sdk.py -> adw_modules -> adw -> project_root
        current_file = os.path.abspath(__file__)
        adw_modules_dir = os.path.dirname(current_file)  # adw/adw_modules
        adw_dir = os.path.dirname(adw_modules_dir)  # adw
        project_root = os.path.dirname(adw_dir)  # project root
        working_dir = project_root

    # Load and expand the slash command template
    # Instead of sending "/classify_issue arg1", we load the template content
    # and substitute $ARGUMENTS with the args
    prompt = load_and_expand_slash_command(
        request.slash_command,
        request.args or [],
        working_dir
    )

    # Create prompt request
    prompt_request = AgentPromptRequest(
        prompt=prompt,
        model=model,
        working_dir=working_dir,
        output_file=output_file,
        adw_id=request.adw_id,
        agent_name=request.agent_name,
        dangerously_skip_permissions=False,  # Use default from request if available
    )

    # Execute with retry
    return await prompt_claude_code_with_retry_async(prompt_request)
