"""
Main CLI Orchestration for Codex SDK Integration
Provides a unified interface for all Codex-powered operations
"""
import sys
import argparse
from pathlib import Path

# Import individual modules
from code_review import review_backend_module, review_critical_modules
from documentation import generate_api_docs, generate_user_guide, generate_architecture_overview
from test_generation import generate_tests_for_module, generate_frontend_tests, generate_edge_case_tests
from bug_fix import fix_bug_in_module, refactor_module, analyze_and_fix_issues
from config import config


def print_banner():
    """Print welcome banner"""
    print("=" * 60)
    print("SWA ERP - Codex SDK Integration")
    print("=" * 60)
    print()


def cmd_review(args):
    """Handle code review commands"""
    print("🔍 Code Review")
    print("-" * 60)
    
    if args.critical:
        print("Reviewing critical modules...")
        results = review_critical_modules()
        success_count = sum(1 for r in results if r['status'] == 'success')
        print(f"\n✓ Completed: {success_count}/{len(results)} modules reviewed")
        return success_count == len(results)
    elif args.module:
        print(f"Reviewing module: {args.module}")
        result = review_backend_module(args.module)
        print(f"\nStatus: {result['status']}")
        if result['status'] == 'success':
            print(f"✓ Review saved to reports directory")
            return True
        else:
            print(f"✗ Error: {result.get('error')}")
            return False
    else:
        print("Error: Specify --module or --critical")
        return False


def cmd_documentation(args):
    """Handle documentation generation commands"""
    print("📚 Documentation Generation")
    print("-" * 60)
    
    if args.api:
        print("Generating API documentation...")
        api_modules = [
            "api/invoices.py",
            "api/auth.py",
            "api/projects.py",
            "api/clients.py",
            "api/tasks.py",
        ]
        results = []
        for module in api_modules:
            print(f"  - {module}")
            result = generate_api_docs(module)
            results.append(result)
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        print(f"\n✓ Completed: {success_count}/{len(results)} API docs generated")
        return success_count == len(results)
        
    elif args.user:
        print("Generating user guide...")
        result = generate_user_guide()
        print(f"\nStatus: {result['status']}")
        if result['status'] == 'success':
            print(f"✓ User guide saved to: {result['guide_file']}")
            return True
        else:
            print(f"✗ Error: {result.get('error')}")
            return False
            
    elif args.architecture:
        print("Generating architecture overview...")
        result = generate_architecture_overview()
        print(f"\nStatus: {result['status']}")
        if result['status'] == 'success':
            print(f"✓ Architecture overview saved to: {result['arch_file']}")
            return True
        else:
            print(f"✗ Error: {result.get('error')}")
            return False
            
    elif args.module:
        print(f"Generating docs for: {args.module}")
        result = generate_api_docs(args.module)
        print(f"\nStatus: {result['status']}")
        if result['status'] == 'success':
            print(f"✓ Documentation saved to: {result['doc_file']}")
            return True
        else:
            print(f"✗ Error: {result.get('error')}")
            return False
    else:
        print("Error: Specify one of --api, --user, --architecture, or --module")
        return False


def cmd_test(args):
    """Handle test generation commands"""
    print("🧪 Test Generation")
    print("-" * 60)
    
    if args.backend:
        print(f"Generating tests for: {args.backend}")
        result = generate_tests_for_module(args.backend)
        print(f"\nStatus: {result['status']}")
        if result['status'] == 'success':
            print(f"✓ Tests saved to: {result['test_file']}")
            return True
        else:
            print(f"✗ Error: {result.get('error')}")
            return False
            
    elif args.frontend:
        print(f"Generating tests for: {args.frontend}")
        result = generate_frontend_tests(args.frontend)
        print(f"\nStatus: {result['status']}")
        if result['status'] == 'success':
            print(f"✓ Tests saved to: {result['test_file']}")
            return True
        else:
            print(f"✗ Error: {result.get('error')}")
            return False
            
    elif args.edge:
        print(f"Generating edge case tests for: {args.edge}")
        result = generate_edge_case_tests(args.edge)
        print(f"\nStatus: {result['status']}")
        if result['status'] == 'success':
            print(f"✓ Tests saved to: {result['test_file']}")
            return True
        else:
            print(f"✗ Error: {result.get('error')}")
            return False
            
    elif args.low_coverage:
        print("Generating tests for low-coverage modules...")
        low_coverage_modules = [
            "services/pdf_service.py",
            "services/quote_service.py",
            "services/notification_service.py",
            "services/task_service.py",
            "services/import_service.py",
        ]
        
        results = []
        for module in low_coverage_modules:
            print(f"  - {module}")
            result = generate_tests_for_module(module)
            results.append(result)
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        print(f"\n✓ Completed: {success_count}/{len(results)} test suites generated")
        return success_count == len(results)
    else:
        print("Error: Specify one of --backend, --frontend, --edge, or --low-coverage")
        return False


def cmd_fix(args):
    """Handle bug fixing and refactoring commands"""
    print("🔧 Bug Fix & Refactoring")
    print("-" * 60)
    
    if args.fix:
        module, description = args.fix
        print(f"Fixing bug in: {module}")
        print(f"Description: {description}")
        result = fix_bug_in_module(module, description)
        print(f"\nStatus: {result['status']}")
        if result['status'] == 'success':
            print(f"✓ Fix report saved to: {result['fix_file']}")
            return True
        else:
            print(f"✗ Error: {result.get('error')}")
            return False
            
    elif args.refactor:
        module, goal = args.refactor
        print(f"Refactoring: {module}")
        print(f"Goal: {goal}")
        result = refactor_module(module, goal)
        print(f"\nStatus: {result['status']}")
        if result['status'] == 'success':
            print(f"✓ Refactoring report saved to: {result['refactor_file']}")
            return True
        else:
            print(f"✗ Error: {result.get('error')}")
            return False
            
    elif args.analyze:
        print(f"Analyzing: {args.analyze}")
        result = analyze_and_fix_issues(args.analyze)
        print(f"\nStatus: {result['status']}")
        if result['status'] == 'success':
            print(f"✓ Analysis report saved to: {result['analysis_file']}")
            return True
        else:
            print(f"✗ Error: {result.get('error')}")
            return False
    else:
        print("Error: Specify one of --fix, --refactor, or --analyze")
        return False


def cmd_all(args):
    """Run comprehensive analysis - review, docs, tests, fixes"""
    print("🚀 Running Comprehensive Analysis")
    print("=" * 60)
    
    all_success = True
    
    # 1. Code Review
    print("\n1. Code Review")
    print("-" * 60)
    review_results = review_critical_modules()
    review_success = sum(1 for r in review_results if r['status'] == 'success')
    print(f"Review: {review_success}/{len(review_results)} successful")
    all_success = all_success and (review_success == len(review_results))
    
    # 2. Documentation
    print("\n2. Documentation Generation")
    print("-" * 60)
    user_result = generate_user_guide()
    arch_result = generate_architecture_overview()
    docs_success = (user_result['status'] == 'success' and arch_result['status'] == 'success')
    print(f"Documentation: {'✓' if docs_success else '✗'}")
    all_success = all_success and docs_success
    
    # 3. Test Generation for low-coverage modules
    print("\n3. Test Generation (Low Coverage)")
    print("-" * 60)
    low_coverage_modules = [
        "services/pdf_service.py",
        "services/quote_service.py",
        "services/notification_service.py",
    ]
    
    test_results = []
    for module in low_coverage_modules:
        result = generate_tests_for_module(module)
        test_results.append(result)
    
    test_success = sum(1 for r in test_results if r['status'] == 'success')
    print(f"Tests: {test_success}/{len(test_results)} generated")
    all_success = all_success and (test_success == len(test_results))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Overall Status: {'✓ SUCCESS' if all_success else '✗ SOME FAILURES'}")
    print(f"\nReports saved to: {config.reports_dir}")
    
    return all_success


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="SWA ERP Codex SDK Integration - AI-powered code analysis and generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Code review
  python main.py review --critical
  python main.py review --module api/invoices.py
  
  # Documentation
  python main.py docs --api
  python main.py docs --user
  python main.py docs --architecture
  
  # Test generation
  python main.py test --backend services/invoice_service.py
  python main.py test --frontend components/clients/ClientForm.tsx
  python main.py test --low-coverage
  
  # Bug fixing
  python main.py fix --fix api/invoices.py "type error in idempotent handler"
  python main.py fix --analyze services/invoice_service.py
  
  # Comprehensive analysis
  python main.py all
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Review subcommand
    review_parser = subparsers.add_parser('review', help='Code review')
    review_parser.add_argument('--module', type=str, help='Specific module to review')
    review_parser.add_argument('--critical', action='store_true', help='Review all critical modules')
    
    # Documentation subcommand
    docs_parser = subparsers.add_parser('docs', help='Documentation generation')
    docs_parser.add_argument('--api', action='store_true', help='Generate API documentation')
    docs_parser.add_argument('--user', action='store_true', help='Generate user guide')
    docs_parser.add_argument('--architecture', action='store_true', help='Generate architecture overview')
    docs_parser.add_argument('--module', type=str, help='Generate docs for specific module')
    
    # Test subcommand
    test_parser = subparsers.add_parser('test', help='Test generation')
    test_parser.add_argument('--backend', type=str, help='Generate tests for backend module')
    test_parser.add_argument('--frontend', type=str, help='Generate tests for frontend component')
    test_parser.add_argument('--edge', type=str, help='Generate edge case tests')
    test_parser.add_argument('--low-coverage', action='store_true', help='Generate tests for low-coverage modules')
    
    # Fix subcommand
    fix_parser = subparsers.add_parser('fix', help='Bug fixing and refactoring')
    fix_parser.add_argument('--fix', nargs=2, metavar=('MODULE', 'DESCRIPTION'), help='Fix specific bug')
    fix_parser.add_argument('--refactor', nargs=2, metavar=('MODULE', 'GOAL'), help='Refactor module')
    fix_parser.add_argument('--analyze', type=str, help='Analyze module for issues')
    
    # All subcommand
    all_parser = subparsers.add_parser('all', help='Run comprehensive analysis')
    
    args = parser.parse_args()
    
    print_banner()
    
    # Check API key
    if not config.api_key:
        print("✗ Error: CURSOR_API_KEY environment variable not set")
        print("\nSet it with:")
        print("  export CURSOR_API_KEY='your-api-key'")
        sys.exit(1)
    
    # Route to appropriate command
    if args.command == 'review':
        success = cmd_review(args)
    elif args.command == 'docs':
        success = cmd_documentation(args)
    elif args.command == 'test':
        success = cmd_test(args)
    elif args.command == 'fix':
        success = cmd_fix(args)
    elif args.command == 'all':
        success = cmd_all(args)
    else:
        parser.print_help()
        sys.exit(1)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()