"""
Codex SDK Configuration for SWA ERP Project
"""
import os
from pathlib import Path
from typing import Optional

class CodexConfig:
    """Configuration for Codex SDK operations"""
    
    def __init__(self):
        self.api_key = os.environ.get("CURSOR_API_KEY")
        if not self.api_key:
            raise ValueError("CURSOR_API_KEY environment variable must be set")
        
        self.project_root = Path(__file__).parent.parent.parent
        self.backend_dir = self.project_root / "src" / "backend"
        self.frontend_dir = self.project_root / "src" / "frontend"
        self.tests_dir = self.project_root / "tests"
        self.reports_dir = self.project_root / "scripts" / "codex" / "reports"
        
        # Create reports directory
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Model selection - use a high-quality model for code analysis
        self.model = "composer-2.5"
        
        # Runtime - use local for CI/integration, cloud for long-running tasks
        self.runtime = "local"  # Can be switched to "cloud" if needed
    
    def get_backend_path(self, *path_parts: str) -> Path:
        """Get path to backend file"""
        return self.backend_dir.joinpath(*path_parts)
    
    def get_frontend_path(self, *path_parts: str) -> Path:
        """Get path to frontend file"""
        return self.frontend_dir.joinpath(*path_parts)
    
    def get_tests_path(self, *path_parts: str) -> Path:
        """Get path to test file"""
        return self.tests_dir.joinpath(*path_parts)

# Global config instance
config = CodexConfig()