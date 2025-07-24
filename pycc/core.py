"""
Core checker system for pycc.
"""

import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


class CheckStatus(Enum):
    """Status of a check execution."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class CheckResult:
    """Result of a check execution."""

    name: str
    status: CheckStatus
    output: str = ""
    error: str = ""
    duration: float = 0.0


class BaseChecker(ABC):
    """Base class for all checkers."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.enabled = True

    @abstractmethod
    def check(self, project_path: Path) -> CheckResult:
        """Run the check and return the result."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the tool is available in the environment."""
        pass

    def get_config_files(self) -> List[Dict[str, Any]]:
        """Return configuration files needed for this checker."""
        return []


class CommandChecker(BaseChecker):
    """Checker that runs a command-line tool."""

    def __init__(
        self,
        name: str,
        command: str,
        args: List[str] = None,
        description: str = "",
        config_files: List[Dict[str, Any]] = None,
    ):
        super().__init__(name, description)
        self.command = command
        self.args = args or []
        self._config_files = config_files or []

    def is_available(self) -> bool:
        """Check if the command is available."""
        try:
            result = subprocess.run(
                [self.command, "--version"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def check(self, project_path: Path) -> CheckResult:
        """Run the command and return the result."""
        import time

        start_time = time.time()
        cmd = [self.command] + self.args

        try:
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes timeout
            )

            duration = time.time() - start_time

            if result.returncode == 0:
                return CheckResult(
                    name=self.name,
                    status=CheckStatus.PASSED,
                    output=result.stdout,
                    duration=duration,
                )
            else:
                return CheckResult(
                    name=self.name,
                    status=CheckStatus.FAILED,
                    output=result.stdout,
                    error=result.stderr,
                    duration=duration,
                )

        except subprocess.TimeoutExpired:
            return CheckResult(
                name=self.name,
                status=CheckStatus.ERROR,
                error="Check timed out after 5 minutes",
                duration=time.time() - start_time,
            )
        except Exception as e:
            return CheckResult(
                name=self.name,
                status=CheckStatus.ERROR,
                error=str(e),
                duration=time.time() - start_time,
            )

    def get_config_files(self) -> List[Dict[str, Any]]:
        """Return configuration files needed for this checker."""
        return self._config_files


class CheckerRegistry:
    """Registry for all available checkers."""

    def __init__(self):
        self._checkers: Dict[str, BaseChecker] = {}

    def register(self, checker: BaseChecker):
        """Register a new checker."""
        self._checkers[checker.name] = checker

    def get_checker(self, name: str) -> Optional[BaseChecker]:
        """Get a checker by name."""
        return self._checkers.get(name)

    def get_all_checkers(self) -> Dict[str, BaseChecker]:
        """Get all registered checkers."""
        return self._checkers.copy()

    def get_available_checkers(self) -> Dict[str, BaseChecker]:
        """Get all checkers that are available in the current environment."""
        return {
            name: checker
            for name, checker in self._checkers.items()
            if checker.is_available()
        }


# Global registry instance
registry = CheckerRegistry()


def register_builtin_checkers():
    """Register all built-in checkers."""

    # Formatting checkers
    registry.register(
        CommandChecker(
            name="black",
            command="black",
            args=["--check", "."],
            description="Code formatting with Black",
            config_files=[
                {
                    "name": "pyproject.toml",
                    "content": """[tool.black]
line-length = 88
target-version = ['py37']
include = '\\.pyi?$'
extend-exclude = '''
/(
  # directories
  \\.eggs
  | \\.git
  | \\.hg
  | \\.mypy_cache
  | \\.tox
  | \\.venv
  | build
  | dist
)/
'''
""",
                    "description": "Black configuration in pyproject.toml",
                }
            ],
        )
    )

    registry.register(
        CommandChecker(
            name="isort",
            command="isort",
            args=["--check-only", "."],
            description="Import sorting with isort",
            config_files=[
                {
                    "name": "pyproject.toml",
                    "content": """[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["your_package_name"]
""",
                    "description": "isort configuration in pyproject.toml",
                }
            ],
        )
    )

    # Linting checkers
    registry.register(
        CommandChecker(
            name="flake8",
            command="flake8",
            args=["."],
            description="Linting with Flake8",
            config_files=[
                {
                    "name": ".flake8",
                    "content": """[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude =
    .git,
    __pycache__,
    .venv,
    build,
    dist,
    *.egg-info
""",
                    "description": "Flake8 configuration file",
                }
            ],
        )
    )

    registry.register(
        CommandChecker(
            name="pylint",
            command="pylint",
            args=["."],
            description="Linting with Pylint",
            config_files=[
                {
                    "name": "pyproject.toml",
                    "content": """[tool.pylint.messages_control]
disable = [
    "C0114",  # missing-module-docstring
    "C0115",  # missing-class-docstring
    "C0116",  # missing-function-docstring
]

[tool.pylint.format]
max-line-length = 88

[tool.pylint.design]
max-args = 10
max-attributes = 10
max-bool-expr = 5
max-branches = 12
max-locals = 15
max-parents = 7
max-public-methods = 20
max-returns = 6
max-statements = 50
""",
                    "description": "Pylint configuration in pyproject.toml",
                }
            ],
        )
    )

    # Type checking
    registry.register(
        CommandChecker(
            name="mypy",
            command="mypy",
            args=["."],
            description="Type checking with MyPy",
            config_files=[
                {
                    "name": "pyproject.toml",
                    "content": """[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[[tool.mypy.overrides]]
module = [
    "tests.*",
]
disallow_untyped_defs = false
""",
                    "description": "MyPy configuration in pyproject.toml",
                }
            ],
        )
    )

    # Security checkers
    registry.register(
        CommandChecker(
            name="bandit",
            command="bandit",
            args=["-r", "."],
            description="Security linting with Bandit",
            config_files=[
                {
                    "name": ".bandit",
                    "content": """exclude_dirs: ['tests', 'test', 'testsuite']
skips: ['B101', 'B601']
""",
                    "description": "Bandit configuration file",
                }
            ],
        )
    )

    registry.register(
        CommandChecker(
            name="safety",
            command="safety",
            args=["check"],
            description="Security vulnerability checking with Safety",
            config_files=[],
        )
    )

    # Documentation checkers
    registry.register(
        CommandChecker(
            name="pydocstyle",
            command="pydocstyle",
            args=["."],
            description="Documentation style checking with Pydocstyle",
            config_files=[
                {
                    "name": "pyproject.toml",
                    "content": """[tool.pydocstyle]
convention = "google"
add_select = ["D100", "D104", "D105", "D106", "D107"]
add_ignore = ["D100", "D104"]
""",
                    "description": "Pydocstyle configuration in pyproject.toml",
                }
            ],
        )
    )

    # Complexity checkers
    registry.register(
        CommandChecker(
            name="vulture",
            command="vulture",
            args=[".", "--min-confidence=80"],
            description="Dead code detection with Vulture",
            config_files=[],
        )
    )

    registry.register(
        CommandChecker(
            name="radon",
            command="radon",
            args=["cc", ".", "--min=A"],
            description="Cyclomatic complexity with Radon",
            config_files=[],
        )
    )


# Register built-in checkers when module is imported
register_builtin_checkers()
