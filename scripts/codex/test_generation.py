"""
Test Generation using Codex SDK
Generates additional test cases to improve coverage and fix gaps
"""
import sys
from pathlib import Path
from cursor_sdk import Agent, LocalAgentOptions, CursorAgentError

from config import config


def generate_tests_for_module(module_path: str) -> dict:
    """
    Generate comprehensive tests for a specific module
    
    Args:
        module_path: Relative path from backend root (e.g., "services/invoice_service.py")
    
    Returns:
        Generation results dict
    """
    full_path = config.get_backend_path(module_path)
    if not full_path.exists():
        return {
            "status": "error",
            "error": f"File not found: {module_path}",
            "module": module_path
        }
    
    prompt = f"""
Generate comprehensive pytest test cases for the code in {module_path}.

Requirements:
1. Follow existing test patterns in tests/ directory
2. Use pytest fixtures appropriately
3. Include unit tests for all public functions
4. Include integration tests where appropriate
5. Test both success and error paths
6. Test edge cases and boundary conditions
7. Add type hints to test functions
8. Include docstrings explaining what each test validates

Focus on increasing test coverage for lines that are currently untested.
Ensure tests are deterministic and don't depend on external state.
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
                    "error": "Test generation failed",
                    "module": module_path,
                    "run_id": result.id
                }
            
            # Save generated tests
            test_file = config.reports_dir / f"test_{module_path.replace('/', '_').replace('.py', '')}.py"
            with open(test_file, 'w') as f:
                f.write(f"\"\"\"Generated tests for {module_path}\"\"\"\n\n")
                f.write(result.result)
            
            return {
                "status": "success",
                "module": module_path,
                "run_id": result.id,
                "test_file": str(test_file),
                "agent_id": agent.agent_id
            }
            
    except CursorAgentError as err:
        return {
            "status": "error",
            "error": f"Codex startup failed: {err.message}",
            "retryable": err.is_retryable,
            "module": module_path
        }


def generate_frontend_tests(component_path: str) -> dict:
    """
    Generate React Testing Library tests for a frontend component
    
    Args:
        component_path: Relative path from frontend src (e.g., "components/clients/ClientForm.tsx")
    
    Returns:
        Generation results dict
    """
    full_path = config.get_frontend_path(component_path)
    if not full_path.exists():
        return {
            "status": "error",
            "error": f"Component not found: {component_path}",
            "component": component_path
        }
    
    prompt = f"""
Generate comprehensive React Testing Library tests for the component at {component_path}.

Requirements:
1. Follow existing test patterns in src/frontend/src/components/__tests__/
2. Use @testing-library/react and @testing-library/user-event
3. Test user interactions (clicks, form submissions, etc.)
4. Test component rendering with different props
5. Test error states and loading states
6. Test accessibility (ARIA roles, keyboard navigation)
7. Mock API calls appropriately
8. Include role-based access testing if applicable

Focus on increasing coverage for untested code paths.
Ensure tests are deterministic and don't depend on external state.
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
                    "error": "Frontend test generation failed",
                    "component": component_path,
                    "run_id": result.id
                }
            
            # Save generated tests
            test_file = config.reports_dir / f"test_{component_path.replace('/', '_').replace('.tsx', '')}.tsx"
            with open(test_file, 'w') as f:
                f.write(f"{{/* Generated tests for {component_path} */}}\n\n")
                f.write(result.result)
            
            return {
                "status": "success",
                "component": component_path,
                "run_id": result.id,
                "test_file": str(test_file),
                "agent_id": agent.agent_id
            }
            
    except CursorAgentError as err:
        return {
            "status": "error",
            "error": f"Codex startup failed: {err.message}",
            "retryable": err.is_retryable,
            "component": component_path
        }


def generate_edge_case_tests(module_path: str) -> dict:
    """
    Generate edge case and boundary condition tests
    
    Args:
        module_path: Relative path from backend root
    
    Returns:
        Generation results dict
    """
    full_path = config.get_backend_path(module_path)
    if not full_path.exists():
        return {
            "status": "error",
            "error": f"File not found: {module_path}",
            "module": module_path
        }
    
    prompt = f"""
Generate edge case and boundary condition tests for {module_path}.

Focus on:
1. Empty/None values in input parameters
2. Maximum length strings/arrays
3. Negative numbers and zero values
4. Date boundary conditions (leap years, month ends, etc.)
5. Unicode and special characters
6. Concurrent access scenarios
7. Database constraint violations
8. Permission/authorization edge cases

Ensure tests verify the correct error handling and validation.
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
                    "error": "Edge case test generation failed",
                    "module": module_path,
                    "run_id": result.id
                }
            
            # Save generated tests
            test_file = config.reports_dir / f"test_edge_{module_path.replace('/', '_').replace('.py', '')}.py"
            with open(test_file, 'w') as f:
                f.write(f"\"\"\"Edge case tests for {module_path}\"\"\"\n\n")
                f.write(result.result)
            
            return {
                "status": "success",
                "module": module_path,
                "run_id": result.id,
                "test_file": str(test_file),
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
    
    parser = argparse.ArgumentParser(description="Test generation using Codex SDK")
    parser.add_argument(
        "--backend-module",
        type=str,
        help="Generate tests for specific backend module"
    )
    parser.add_argument(
        "--frontend-component",
        type=str,
        help="Generate tests for specific frontend component"
    )
    parser.add_argument(
        "--edge-cases",
        type=str,
        help="Generate edge case tests for backend module"
    )
    parser.add_argument(
        "--low-coverage",
        action="store_true",
        help="Generate tests for low-coverage modules"
    )
    
    args = parser.parse_args()
    
    if args.backend_module:
        result = generate_tests_for_module(args.backend_module)
        print(f"\nStatus: {result['status']}")
        if result['status'] == 'success':
            print(f"Tests saved to: {result['test_file']}")
        else:
            print(f"Error: {result.get('error')}")
            sys.exit(1)
            
    elif args.frontend_component:
        result = generate_frontend_tests(args.frontend_component)
        print(f"\nStatus: {result['status']}")
        if result['status'] == 'success':
            print(f"Tests saved to: {result['test_file']}")
        else:
            print(f"Error: {result.get('error')}")
            sys.exit(1)
            
    elif args.edge_cases:
        result = generate_edge_case_tests(args.edge_cases)
        print(f"\nStatus: {result['status']}")
        if result['status'] == 'success':
            print(f"Tests saved to: {result['test_file']}")
        else:
            print(f"Error: {result.get('error')}")
            sys.exit(1)
            
    elif args.low_coverage:
        # Generate tests for low-coverage modules
        low_coverage_modules = [
            "services/pdf_service.py",
            "services/quote_service.py",
            "services/notification_service.py",
            "services/task_service.py",
            "services/import_service.py",
        ]
        
        results = []
        for module in low_coverage_modules:
            print(f"\nGenerating tests for: {module}")
            result = generate_tests_for_module(module)
            results.append(result)
            print(f"Status: {result['status']}")
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        print(f"\nTests Generated: {success_count}/{len(results)}")
        
    else:
        parser.print_help()
        sys.exit(1)