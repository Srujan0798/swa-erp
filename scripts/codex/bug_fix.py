"""
Bug Fixing and Refactoring using Codex SDK
Identifies and fixes bugs, refactors code for better quality
"""
import sys
from pathlib import Path
from cursor_sdk import Agent, LocalAgentOptions, CursorAgentError

from config import config


def fix_bug_in_module(module_path: str, bug_description: str) -> dict:
    """
    Fix a specific bug in a module
    
    Args:
        module_path: Relative path from backend root
        bug_description: Description of the bug to fix
    
    Returns:
        Fix results dict
    """
    full_path = config.get_backend_path(module_path)
    if not full_path.exists():
        return {
            "status": "error",
            "error": f"File not found: {module_path}",
            "module": module_path
        }
    
    prompt = f"""
Fix the following bug in {module_path}:

Bug Description: {bug_description}

Requirements:
1. Analyze the code to understand the root cause
2. Implement a minimal fix that addresses the issue
3. Ensure the fix doesn't break existing functionality
4. Add comments explaining the fix
5. Follow SWA ERP coding conventions (type hints, immutability, etc.)
6. Update related tests if necessary

Provide the complete fixed code for the affected function(s).
"""
    
    try:
        with Agent.create(
            model=config.model,
            api_key=config.api_key,
            local=LocalAgentOptions(cwd=str(config.project_root)),
        ) as agent:
            run = agent.send(prompt)
            
            for message in run.messages():
                if message.type == "assistant":
                    for block in message.message.content:
                        if block.type == "text":
                            print(block.text, end="")
            
            result = run.wait()
            
            if result.status == "error":
                return {
                    "status": "error",
                    "error": "Bug fix failed",
                    "module": module_path,
                    "run_id": result.id
                }
            
            # Save fix report
            fix_file = config.reports_dir / f"fix_{module_path.replace('/', '_').replace('.py', '')}.md"
            with open(fix_file, 'w') as f:
                f.write(f"# Bug Fix: {module_path}\n\n")
                f.write(f"**Bug:** {bug_description}\n\n")
                f.write("## Fix\n\n")
                f.write(result.result)
            
            return {
                "status": "success",
                "module": module_path,
                "run_id": result.id,
                "fix_file": str(fix_file),
                "agent_id": agent.agent_id
            }
            
    except CursorAgentError as err:
        return {
            "status": "error",
            "error": f"Codex startup failed: {err.message}",
            "retryable": err.is_retryable,
            "module": module_path
        }


def refactor_module(module_path: str, refactoring_goal: str) -> dict:
    """
    Refactor a module for better code quality
    
    Args:
        module_path: Relative path from backend root
        refactoring_goal: What to improve (e.g., "reduce complexity", "improve readability")
    
    Returns:
        Refactoring results dict
    """
    full_path = config.get_backend_path(module_path)
    if not full_path.exists():
        return {
            "status": "error",
            "error": f"File not found: {module_path}",
            "module": module_path
        }
    
    prompt = f"""
Refactor the code in {module_path} to: {refactoring_goal}

Requirements:
1. Maintain all existing functionality
2. Follow SWA ERP coding conventions:
   - Immutable patterns (no in-place mutations)
   - Type hints on all functions
   - Small, focused functions (<50 lines)
   - Clear naming
3. Improve code organization and structure
4. Add or improve docstrings
5. Ensure tests still pass after refactoring

Provide the complete refactored code.
"""
    
    try:
        with Agent.create(
            model=config.model,
            api_key=config.api_key,
            local=LocalAgentOptions(cwd=str(config.project_root)),
        ) as agent:
            run = agent.send(prompt)
            
            for message in run.messages():
                if message.type == "assistant":
                    for block in message.message.content:
                        if block.type == "text":
                            print(block.text, end="")
            
            result = run.wait()
            
            if result.status == "error":
                return {
                    "status": "error",
                    "error": "Refactoring failed",
                    "module": module_path,
                    "run_id": result.id
                }
            
            # Save refactoring report
            refactor_file = config.reports_dir / f"refactor_{module_path.replace('/', '_').replace('.py', '')}.md"
            with open(refactor_file, 'w') as f:
                f.write(f"# Refactoring: {module_path}\n\n")
                f.write(f"**Goal:** {refactoring_goal}\n\n")
                f.write("## Refactored Code\n\n")
                f.write(result.result)
            
            return {
                "status": "success",
                "module": module_path,
                "run_id": result.id,
                "refactor_file": str(refactor_file),
                "agent_id": agent.agent_id
            }
            
    except CursorAgentError as err:
        return {
            "status": "error",
            "error": f"Codex startup failed: {err.message}",
            "retryable": err.is_retryable,
            "module": module_path
        }


def analyze_and_fix_issues(module_path: str) -> dict:
    """
    Automatically analyze a module and suggest fixes for common issues
    
    Args:
        module_path: Relative path from backend root
    
    Returns:
        Analysis and fix results dict
    """
    full_path = config.get_backend_path(module_path)
    if not full_path.exists():
        return {
            "status": "error",
            "error": f"File not found: {module_path}",
            "module": module_path
        }
    
    prompt = f"""
Analyze the code in {module_path} for common issues and provide fixes:

Check for:
1. Type safety issues (missing type hints, incorrect types)
2. Code complexity (functions >50 lines, deep nesting)
3. Security vulnerabilities (SQL injection, XSS, auth issues)
4. Performance issues (inefficient algorithms, N+1 queries)
5. Code duplication
6. Error handling gaps
7. Immutable pattern violations
8. Naming conventions violations

For each issue found:
- Describe the issue clearly
- Explain why it's a problem
- Provide the fix with code
- Indicate severity (CRITICAL, HIGH, MEDIUM, LOW)

Format as a structured report with code blocks for fixes.
"""
    
    try:
        with Agent.create(
            model=config.model,
            api_key=config.api_key,
            local=LocalAgentOptions(cwd=str(config.project_root)),
        ) as agent:
            run = agent.send(prompt)
            
            for message in run.messages():
                if message.type == "assistant":
                    for block in message.message.content:
                        if block.type == "text":
                            print(block.text, end="")
            
            result = run.wait()
            
            if result.status == "error":
                return {
                    "status": "error",
                    "error": "Analysis failed",
                    "module": module_path,
                    "run_id": result.id
                }
            
            # Save analysis report
            analysis_file = config.reports_dir / f"analysis_{module_path.replace('/', '_').replace('.py', '')}.md"
            with open(analysis_file, 'w') as f:
                f.write(f"# Code Analysis: {module_path}\n\n")
                f.write(result.result)
            
            return {
                "status": "success",
                "module": module_path,
                "run_id": result.id,
                "analysis_file": str(analysis_file),
                "agent_id": agent.agent_id
            }
            
    except CursorAgentError as err:
        return {
            "status": "error",
            "error": f"Codex startup failed: {err.message}",
            "retryable": err.is_retryable,
            "module": module_path
        }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Bug fixing and refactoring using Codex SDK")
    parser.add_argument(
        "--fix-bug",
        nargs=2,
        metavar=("MODULE", "DESCRIPTION"),
        help="Fix a specific bug: --fix-bug module.py 'bug description'"
    )
    parser.add_argument(
        "--refactor",
        nargs=2,
        metavar=("MODULE", "GOAL"),
        help="Refactor module: --refactor module.py 'improve readability'"
    )
    parser.add_argument(
        "--analyze",
        type=str,
        help="Analyze module for common issues"
    )
    
    args = parser.parse_args()
    
    if args.fix_bug:
        module, description = args.fix_bug
        result = fix_bug_in_module(module, description)
        print(f"\nStatus: {result['status']}")
        if result['status'] == 'success':
            print(f"Fix report saved to: {result['fix_file']}")
        else:
            print(f"Error: {result.get('error')}")
            sys.exit(1)
            
    elif args.refactor:
        module, goal = args.refactor
        result = refactor_module(module, goal)
        print(f"\nStatus: {result['status']}")
        if result['status'] == 'success':
            print(f"Refactoring report saved to: {result['refactor_file']}")
        else:
            print(f"Error: {result.get('error')}")
            sys.exit(1)
            
    elif args.analyze:
        result = analyze_and_fix_issues(args.analyze)
        print(f"\nStatus: {result['status']}")
        if result['status'] == 'success':
            print(f"Analysis report saved to: {result['analysis_file']}")
        else:
            print(f"Error: {result.get('error')}")
            sys.exit(1)
            
    else:
        parser.print_help()
        sys.exit(1)