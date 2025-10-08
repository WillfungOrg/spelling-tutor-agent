#!/usr/bin/env python3
"""
Director script for running iterative code development with AI assistance.
"""

import yaml
import subprocess
import sys
import json
import os
from typing import Dict, Any, Tuple


def load_config(yaml_file: str) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    with open(yaml_file, 'r') as f:
        config = yaml.safe_load(f)
    return config


def run_iteration(config: Dict[str, Any], iteration_num: int) -> Tuple[bool, str]:
    """
    Run a single iteration with the coder and execute tests.

    Returns:
        Tuple of (success: bool, output: str)
    """
    print(f"\n=== Iteration {iteration_num} ===")

    # Prepare coder command
    coder_cmd = ["claude-code"]

    # Add context files
    if "context_editable" in config:
        for file_path in config["context_editable"]:
            coder_cmd.append(file_path)

    if "context_read_only" in config:
        for file_path in config["context_read_only"]:
            coder_cmd.extend(["--read", file_path])

    # Add the prompt
    prompt = config.get("prompt", "")
    if "current_feedback" in config:
        prompt += f"\n\nPrevious iteration feedback: {config['current_feedback']}"

    print("Running coder...")

    try:
        # Run coder
        coder_result = subprocess.run(
            coder_cmd,
            input=prompt,
            text=True,
            capture_output=True,
            timeout=300  # 5 minute timeout
        )

        print(f"Coder exit code: {coder_result.returncode}")
        if coder_result.stdout:
            print("Coder stdout:", coder_result.stdout[:500] + ("..." if len(coder_result.stdout) > 500 else ""))
        if coder_result.stderr:
            print("Coder stderr:", coder_result.stderr[:500] + ("..." if len(coder_result.stderr) > 500 else ""))

    except subprocess.TimeoutExpired:
        print("Coder timed out")
        return False, "Coder execution timed out"
    except Exception as e:
        print(f"Error running coder: {e}")
        return False, f"Error running coder: {e}"

    # Run execution command
    execution_cmd = config.get("execution_command", "")
    if not execution_cmd:
        print("No execution command specified")
        return False, "No execution command specified"

    print(f"Running execution command: {execution_cmd}")

    try:
        # Run tests/execution command
        exec_result = subprocess.run(
            execution_cmd.split(),
            text=True,
            capture_output=True,
            timeout=120  # 2 minute timeout
        )

        success = exec_result.returncode == 0
        output = f"Exit code: {exec_result.returncode}\n"
        output += f"STDOUT:\n{exec_result.stdout}\n"
        output += f"STDERR:\n{exec_result.stderr}"

        print(f"Execution exit code: {exec_result.returncode}")
        print("Execution output:")
        print(output[:1000] + ("..." if len(output) > 1000 else ""))

        return success, output

    except subprocess.TimeoutExpired:
        print("Execution command timed out")
        return False, "Execution command timed out"
    except Exception as e:
        print(f"Error running execution command: {e}")
        return False, f"Error running execution command: {e}"


def evaluate_results(config: Dict[str, Any], iteration_num: int, success: bool, output: str) -> Tuple[bool, str]:
    """
    Evaluate the results and determine if we should continue.

    Returns:
        Tuple of (should_continue: bool, feedback: str)
    """
    evaluator_model = config.get("evaluator_model", "gpt-4o")

    if success:
        print("✅ Iteration succeeded!")
        return False, "Tests passed successfully"

    print("❌ Iteration failed, getting feedback...")

    # For now, provide simple feedback based on output analysis
    # In a full implementation, this would call the evaluator model API

    feedback = "Tests failed. "

    if "ImportError" in output:
        feedback += "Fix import errors. "
    if "AttributeError" in output:
        feedback += "Fix attribute errors - check method names and object types. "
    if "NameError" in output:
        feedback += "Fix undefined variables or functions. "
    if "SyntaxError" in output:
        feedback += "Fix syntax errors. "
    if "ModuleNotFoundError" in output:
        feedback += "Fix missing module imports. "
    if "TypeError" in output:
        feedback += "Fix type-related errors - check function signatures and arguments. "

    # Check if we've reached max iterations
    max_iterations = config.get("max_iterations", 5)
    if iteration_num >= max_iterations:
        feedback += "Maximum iterations reached."
        return False, feedback

    feedback += "Review the error output and fix the issues."
    return True, feedback


def main():
    """Main director execution function."""
    if len(sys.argv) != 2:
        print("Usage: python run_director.py <config.yaml>")
        sys.exit(1)

    yaml_file = sys.argv[1]

    if not os.path.exists(yaml_file):
        print(f"Config file not found: {yaml_file}")
        sys.exit(1)

    print(f"Loading configuration from {yaml_file}")
    config = load_config(yaml_file)

    max_iterations = config.get("max_iterations", 5)
    print(f"Starting director with max {max_iterations} iterations")

    success_achieved = False

    for iteration in range(1, max_iterations + 1):
        # Run iteration
        success, output = run_iteration(config, iteration)

        # Evaluate results
        should_continue, feedback = evaluate_results(config, iteration, success, output)

        if success:
            print(f"\n🎉 SUCCESS achieved in iteration {iteration}!")
            success_achieved = True
            break

        if not should_continue:
            print(f"\n⏹️ Stopping after iteration {iteration}: {feedback}")
            break

        # Update config with feedback for next iteration
        config["current_feedback"] = feedback
        print(f"Continuing with feedback: {feedback}")

    # Print summary
    print(f"\n{'='*50}")
    print("DIRECTOR SUMMARY")
    print(f"{'='*50}")

    if success_achieved:
        print("✅ Task completed successfully!")
    else:
        print("❌ Task not completed within iteration limit")

    print(f"Total iterations: {iteration}")
    print(f"Configuration: {yaml_file}")


if __name__ == "__main__":
    main()