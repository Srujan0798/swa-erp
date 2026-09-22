# Codex SDK Integration for SWA ERP

This directory contains Python scripts that use the Codex SDK to automate code review, documentation generation, test generation, and bug fixing for the SWA ERP project.

## Setup

1. Install the Codex SDK:
```bash
pip install cursor-sdk
```

2. Set your API key:
```bash
export CURSOR_API_KEY="your-cursor-api-key"
```

Get your API key from [Codex Dashboard → Integrations](https://cursor.com/dashboard/integrations)

## Usage

The main entry point is `main.py`. Run it from the `scripts/codex/` directory:

```bash
cd scripts/codex
python main.py <command> [options]
```

### Commands

#### Code Review (`review`)
Review code for quality, security, and compliance.

```bash
# Review all critical modules
python main.py review --critical

# Review a specific module
python main.py review --module api/invoices.py
```

#### Documentation Generation (`docs`)
Generate API documentation, user guides, and architecture overviews.

```bash
# Generate API documentation for all modules
python main.py docs --api

# Generate user guide
python main.py docs --user

# Generate architecture overview
python main.py docs --architecture

# Generate docs for specific module
python main.py docs --module api/invoices.py
```

#### Test Generation (`test`)
Generate test cases to improve coverage.

```bash
# Generate tests for backend module
python main.py test --backend services/invoice_service.py

# Generate tests for frontend component
python main.py test --frontend components/clients/ClientForm.tsx

# Generate edge case tests
python main.py test --edge services/invoice_service.py

# Generate tests for low-coverage modules
python main.py test --low-coverage
```

#### Bug Fix & Refactoring (`fix`)
Fix bugs and refactor code for better quality.

```bash
# Fix a specific bug
python main.py fix --fix api/invoices.py "type error in idempotent handler"

# Refactor a module
python main.py fix --refactor services/invoice_service.py "improve readability"

# Analyze module for issues
python main.py fix --analyze services/invoice_service.py
```

#### Comprehensive Analysis (`all`)
Run all analysis tasks in sequence.

```bash
python main.py all
```

This will:
1. Review all critical modules
2. Generate user guide and architecture overview
3. Generate tests for low-coverage modules

## Output

All reports are saved to `scripts/codex/reports/`:

- Code reviews: `review_<module>.md`
- API docs: `api_docs_<module>.md`
- User guide: `user_guide.md`
- Architecture: `architecture_overview.md`
- Tests: `test_<module>.py` or `.tsx`
- Bug fixes: `fix_<module>.md`
- Refactoring: `refactor_<module>.md`
- Analysis: `analysis_<module>.md`

## Individual Scripts

You can also run individual scripts directly:

```bash
# Code review
python code_review.py --critical
python code_review.py --module api/invoices.py

# Documentation
python documentation.py --api-docs
python documentation.py --user-guide
python documentation.py --architecture

# Test generation
python test_generation.py --backend-module services/invoice_service.py
python test_generation.py --frontend-component components/clients/ClientForm.tsx
python test_generation.py --low-coverage

# Bug fixing
python bug_fix.py --fix-bug api/invoices.py "description"
python bug_fix.py --refactor services/invoice_service.py "goal"
python bug_fix.py --analyze services/invoice_service.py
```

## Configuration

Edit `config.py` to customize:

- `model`: Codex model to use (default: `composer-2.5`)
- `runtime`: Runtime mode (default: `local`)
- `critical_modules`: List of modules for critical review
- `low_coverage_modules`: List of modules needing test coverage

## Integration with CI/CD

Add to your CI pipeline:

```yaml
- name: Run Codex Analysis
  run: |
    export CURSOR_API_KEY=${{ secrets.CURSOR_API_KEY }}
    cd scripts/codex
    python main.py all
```

## Notes

- The SDK uses local runtime by default, which runs against your local codebase
- For cloud runtime, set `runtime = "cloud"` in `config.py`
- Each operation creates a new Codex agent for isolation
- All agents are properly disposed to prevent resource leaks
- Results include run IDs for traceability in the Codex dashboard

## Troubleshooting

**API Key Error:**
```
Error: CURSOR_API_KEY environment variable not set
```
Solution: Set the environment variable before running scripts.

**Module Not Found:**
```
Error: File not found: services/unknown.py
```
Solution: Check the module path is relative to `src/backend/` or `src/frontend/`

**Codex Startup Failed:**
```
Error: Codex startup failed: ...
```
Solution: Check your API key is valid and you have network access.

## For Internship Submission

To prepare your project for submission:

1. Run comprehensive analysis:
```bash
python main.py all
```

2. Review generated reports in `scripts/codex/reports/`

3. Apply suggested fixes from bug analysis

4. Add generated tests to your test suite

5. Update documentation with generated content

6. Ensure all existing tests still pass
```bash
cd ../..
make test
```