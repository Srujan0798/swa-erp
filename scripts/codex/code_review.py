"""
Automated Code Review using Codex SDK
Reviews backend Python code for quality, security, and compliance
"""
import sys
import os
from pathlib import Path
from cursor_sdk import Agent, LocalAgentOptions, CursorAgentError

from config import config


def review_backend_module(module_path: str) -> dict:
    """
    Review a specific backend module using Codex
    
    Args:
        module_path: Relative path from backend root (e.g., "api/invoices.py")
    
    Returns:
        Review results dict with status and findings
    """
    full_path = config.get_backend_path(module_path)
    if not full_path.exists():
        return {
            "status": "error",
            "error": f"File not found: {module_path}",
            "module": module_path
        }
    
    prompt = f"""
Review the code in {module_path} for:
1. Code quality and Python best practices (PEP 8 compliance, type hints, docstrings)
2. Security vulnerabilities (SQL injection, XSS, authentication/authorization issues)
3. Performance issues (N+1 queries, inefficient algorithms, memory leaks)
4. Testing coverage gaps
5. Alignment with SWA ERP project conventions (as documented in AGENTS.md)

Provide specific line numbers and actionable recommendations.
Focus on production-readiness since this is for internship submission.
"""
    
    try:
        with Agent.create(
            model=config.model,
            api_key=config.api_key,
            local=LocalAgentOptions(cwd=str(config.project_root)),
        ) as agent:
            run = agent.send(prompt)
            
            # Stream output for real-time feedback
            for message in run.messages():
                if message.type == "assistant":
                    for block in message.message.content:
                        if block.type == "text":
                            print(block.text, end="")
            
            result = run.wait()
            
            if result.status == "error":
                return {
                    "status": "error",
                    "error": "Codex agent failed during review",
                    "module": module_path,
                    "run_id": result.id
                }
            
            return {
                "status": "success",
                "module": module_path,
                "run_id": result.id,
                "review": result.result,
                "agent_id": agent.agent_id
            }
            
    except CursorAgentError as err:
        return {
            "status": "error",
            "error": f"Codex startup failed: {err.message}",
            "retryable": err.is_retryable,
            "module": module_path
        }


def review_critical_modules() -> list[dict]:
    """
    Review all critical backend modules for production readiness
    """
    critical_modules = [
        "api/invoices.py",
        "api/auth.py",
        "services/invoice_service.py",
        "services/auth_service.py",
        "core/security.py",
        "db/session.py",
        "main.py",
    ]
    
    results = []
    for module in critical_modules:
        print(f"\n{'='*60}")
        print(f"Reviewing: {module}")
        print(f"{'='*60}")
        result = review_backend_module(module)
        results.append(result)
        
        # Save individual review to file
        report_file = config.reports_dir / f"review_{module.replace('/', '_')}.md"
        with open(report_file, 'w') as f:
            f.write(f"# Code Review: {module}\n\n")
            if result["status"] == "success":
                f.write(f"**Status:** {result['status']}\n")
                f.write(f"**Run ID:** {result['run_id']}\n")
                f.write(f"**Agent ID:** {result['agent_id']}\n\n")
                f.write("## Review Findings\n\n")
                f.write(result['review'])
            else:
                f.write(f"**Status:** {result['status']}\n")
                f.write(f"**Error:** {result.get('error', 'Unknown error')}\n")
        
        print(f"Review saved to: {report_file}")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Code review using Codex SDK")
    parser.add_argument(
        "--module",
        type=str,
        help="Specific module to review (e.g., api/invoices.py)"
    )
    parser.add_argument(
        "--critical",
        action="store_true",
        help="Review all critical modules"
    )
    
    args = parser.parse_args()
    
    if args.module:
        result = review_backend_module(args.module)
        print(f"\nReview Result: {result['status']}")
        if result['status'] == 'error':
            print(f"Error: {result.get('error')}")
            sys.exit(1)
    elif args.critical:
        results = review_critical_modules()
        print(f"\n{'='*60}")
        print("Summary")
        print(f"{'='*60}")
        success_count = sum(1 for r in results if r['status'] == 'success')
        error_count = len(results) - success_count
        print(f"Successful reviews: {success_count}/{len(results)}")
        print(f"Failed reviews: {error_count}/{len(results)}")
        
        if error_count > 0:
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)