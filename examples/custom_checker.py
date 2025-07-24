#!/usr/bin/env python3
"""
Example of creating a custom checker for pycc.

This example shows how to create a custom checker that:
1. Checks for TODO comments in code
2. Validates that all Python files have a shebang line
3. Ensures consistent line endings
"""

import re
from pathlib import Path
from typing import List

from pycc.core import BaseChecker, CheckResult, CheckStatus, registry


class TODOChecker(BaseChecker):
    """Checker for TODO comments in code."""
    
    def __init__(self):
        super().__init__("todo-checker", "Check for TODO comments in code")
    
    def is_available(self) -> bool:
        """This checker is always available as it doesn't require external tools."""
        return True
    
    def check(self, project_path: Path) -> CheckResult:
        """Check for TODO comments in Python files."""
        todo_pattern = re.compile(r'#\s*TODO', re.IGNORECASE)
        todo_files = []
        
        # Find all Python files
        for py_file in project_path.rglob("*.py"):
            # Skip test files and virtual environments
            if any(part in str(py_file) for part in ["test", "tests", ".venv", "__pycache__"]):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if todo_pattern.search(content):
                        todo_files.append(str(py_file.relative_to(project_path)))
            except Exception as e:
                return CheckResult(
                    name=self.name,
                    status=CheckStatus.ERROR,
                    error=f"Error reading {py_file}: {e}"
                )
        
        if todo_files:
            return CheckResult(
                name=self.name,
                status=CheckStatus.FAILED,
                output=f"Found TODO comments in {len(todo_files)} files: {', '.join(todo_files)}"
            )
        else:
            return CheckResult(
                name=self.name,
                status=CheckStatus.PASSED,
                output="No TODO comments found"
            )
    
    def get_config_files(self):
        """No configuration files needed for this checker."""
        return []


class ShebangChecker(BaseChecker):
    """Checker for shebang lines in Python files."""
    
    def __init__(self):
        super().__init__("shebang-checker", "Check that Python files have proper shebang lines")
    
    def is_available(self) -> bool:
        """This checker is always available."""
        return True
    
    def check(self, project_path: Path) -> CheckResult:
        """Check that Python files have proper shebang lines."""
        files_without_shebang = []
        
        for py_file in project_path.rglob("*.py"):
            # Skip test files and virtual environments
            if any(part in str(py_file) for part in ["test", "tests", ".venv", "__pycache__"]):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if not first_line.startswith('#!'):
                        files_without_shebang.append(str(py_file.relative_to(project_path)))
            except Exception as e:
                return CheckResult(
                    name=self.name,
                    status=CheckStatus.ERROR,
                    error=f"Error reading {py_file}: {e}"
                )
        
        if files_without_shebang:
            return CheckResult(
                name=self.name,
                status=CheckStatus.FAILED,
                output=f"Files without shebang: {', '.join(files_without_shebang)}"
            )
        else:
            return CheckResult(
                name=self.name,
                status=CheckStatus.PASSED,
                output="All Python files have proper shebang lines"
            )
    
    def get_config_files(self):
        """No configuration files needed for this checker."""
        return []


class LineEndingChecker(BaseChecker):
    """Checker for consistent line endings."""
    
    def __init__(self):
        super().__init__("line-ending-checker", "Check for consistent line endings (Unix style)")
    
    def is_available(self) -> bool:
        """This checker is always available."""
        return True
    
    def check(self, project_path: Path) -> CheckResult:
        """Check for consistent Unix line endings."""
        files_with_windows_endings = []
        
        for py_file in project_path.rglob("*.py"):
            # Skip test files and virtual environments
            if any(part in str(py_file) for part in ["test", "tests", ".venv", "__pycache__"]):
                continue
            
            try:
                with open(py_file, 'rb') as f:
                    content = f.read()
                    if b'\r\n' in content:
                        files_with_windows_endings.append(str(py_file.relative_to(project_path)))
            except Exception as e:
                return CheckResult(
                    name=self.name,
                    status=CheckStatus.ERROR,
                    error=f"Error reading {py_file}: {e}"
                )
        
        if files_with_windows_endings:
            return CheckResult(
                name=self.name,
                status=CheckStatus.FAILED,
                output=f"Files with Windows line endings: {', '.join(files_with_windows_endings)}"
            )
        else:
            return CheckResult(
                name=self.name,
                status=CheckStatus.PASSED,
                output="All files use Unix line endings"
            )
    
    def get_config_files(self):
        """No configuration files needed for this checker."""
        return []


def register_custom_checkers():
    """Register all custom checkers."""
    registry.register(TODOChecker())
    registry.register(ShebangChecker())
    registry.register(LineEndingChecker())


if __name__ == "__main__":
    # Example usage
    register_custom_checkers()
    
    # Now you can use pycc with these custom checkers
    print("Custom checkers registered:")
    print("- todo-checker: Check for TODO comments")
    print("- shebang-checker: Check for proper shebang lines")
    print("- line-ending-checker: Check for consistent line endings")
    
    print("\nYou can now run:")
    print("pycc --check todo-checker shebang-checker line-ending-checker") 