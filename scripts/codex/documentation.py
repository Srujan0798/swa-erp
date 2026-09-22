"""
Documentation Generation using Codex SDK
Generates API documentation, user guides, and technical docs
"""
import sys
from pathlib import Path
from cursor_sdk import Agent, LocalAgentOptions, CursorAgentError

from config import config


def generate_api_docs(module_path: str) -> dict:
    """
    Generate API documentation for a specific module
    
    Args:
        module_path: Relative path from backend root (e.g., "api/invoices.py")
    
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
Generate comprehensive API documentation for the code in {module_path}.

Include:
1. Overview of the module's purpose
2. All endpoint paths and HTTP methods
3. Request/response schemas (Pydantic models)
4. Authentication/authorization requirements
5. Error responses and status codes
6. Usage examples with curl commands
7. Integration notes with other modules

Format in Markdown. Include code blocks for examples.
Ensure accuracy by reading the actual code structure.
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
                    "error": "Documentation generation failed",
                    "module": module_path,
                    "run_id": result.id
                }
            
            # Save documentation
            doc_file = config.reports_dir / f"api_docs_{module_path.replace('/', '_')}.md"
            with open(doc_file, 'w') as f:
                f.write(f"# API Documentation: {module_path}\n\n")
                f.write(result.result)
            
            return {
                "status": "success",
                "module": module_path,
                "run_id": result.id,
                "doc_file": str(doc_file),
                "agent_id": agent.agent_id
            }
            
    except CursorAgentError as err:
        return {
            "status": "error",
            "error": f"Codex startup failed: {err.message}",
            "retryable": err.is_retryable,
            "module": module_path
        }


def generate_user_guide() -> dict:
    """
    Generate user guide for the SWA ERP system
    """
    prompt = """
Generate a comprehensive user guide for the SWA ERP system based on the existing documentation.

Include:
1. System overview for non-technical users
2. Step-by-step guide for common workflows:
   - Creating inquiries and converting to clients
   - Creating projects and service agreements
   - Issuing tokens and document references
   - Time tracking and invoice generation
3. Role-based access (admin, PM, designer, auditor, viewer)
4. Common troubleshooting steps
5. Best practices and tips

Reference the existing documentation in docs/ and deliverables/ directories.
Format in Markdown with clear sections and examples.
Make it suitable for business users at SWA Consultancy.
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
                    "error": "User guide generation failed",
                    "run_id": result.id
                }
            
            # Save user guide
            guide_file = config.reports_dir / "user_guide.md"
            with open(guide_file, 'w') as f:
                f.write("# SWA ERP User Guide\n\n")
                f.write(result.result)
            
            return {
                "status": "success",
                "run_id": result.id,
                "guide_file": str(guide_file),
                "agent_id": agent.agent_id
            }
            
    except CursorAgentError as err:
        return {
            "status": "error",
            "error": f"Codex startup failed: {err.message}",
            "retryable": err.is_retryable
        }


def generate_architecture_overview() -> dict:
    """
    Generate architecture overview documentation
    """
    prompt = """
Generate a detailed architecture overview for the SWA ERP system.

Include:
1. System architecture diagram description
2. Component breakdown (backend services, frontend components, database schema)
3. Data flow between components
4. Technology stack rationale
5. Deployment architecture (Docker Compose setup)
6. Security architecture (JWT auth, RBAC, rate limiting)
7. Performance considerations

Reference the existing docs/ARCHITECTURE.md and ensure consistency.
Format in Markdown with mermaid diagrams where appropriate.
This is for technical stakeholders and internship submission.
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
                    "error": "Architecture overview generation failed",
                    "run_id": result.id
                }
            
            # Save architecture overview
            arch_file = config.reports_dir / "architecture_overview.md"
            with open(arch_file, 'w') as f:
                f.write("# SWA ERP Architecture Overview\n\n")
                f.write(result.result)
            
            return {
                "status": "success",
                "run_id": result.id,
                "arch_file": str(arch_file),
                "agent_id": agent.agent_id
            }
            
    except CursorAgentError as err:
        return {
            "status": "error",
            "error": f"Codex startup failed: {err.message}",
            "retryable": err.is_retryable
        }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Documentation generation using Codex SDK")
    parser.add_argument(
        "--api-docs",
        action="store_true",
        help="Generate API documentation for all modules"
    )
    parser.add_argument(
        "--user-guide",
        action="store_true",
        help="Generate user guide"
    )
    parser.add_argument(
        "--architecture",
        action="store_true",
        help="Generate architecture overview"
    )
    parser.add_argument(
        "--module",
        type=str,
        help="Generate docs for specific module"
    )
    
    args = parser.parse_args()
    
    if args.api_docs:
        # Generate docs for all API modules
        api_modules = [
            "api/invoices.py",
            "api/auth.py",
            "api/projects.py",
            "api/clients.py",
            "api/tasks.py",
        ]
        
        results = []
        for module in api_modules:
            print(f"\nGenerating API docs for: {module}")
            result = generate_api_docs(module)
            results.append(result)
            print(f"Status: {result['status']}")
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        print(f"\nAPI Docs Generated: {success_count}/{len(results)}")
        
    elif args.user_guide:
        print("Generating user guide...")
        result = generate_user_guide()
        print(f"\nStatus: {result['status']}")
        if result['status'] == 'success':
            print(f"User guide saved to: {result['guide_file']}")
        
    elif args.architecture:
        print("Generating architecture overview...")
        result = generate_architecture_overview()
        print(f"\nStatus: {result['status']}")
        if result['status'] == 'success':
            print(f"Architecture overview saved to: {result['arch_file']}")
        
    elif args.module:
        result = generate_api_docs(args.module)
        print(f"\nStatus: {result['status']}")
        if result['status'] == 'success':
            print(f"Documentation saved to: {result['doc_file']}")
        else:
            print(f"Error: {result.get('error')}")
            sys.exit(1)
        
    else:
        parser.print_help()
        sys.exit(1)