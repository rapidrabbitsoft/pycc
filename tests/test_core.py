"""
Tests for core module.
"""

from unittest.mock import patch, MagicMock

from pycc.core import (
    CheckStatus,
    CheckResult,
    BaseChecker,
    CommandChecker,
    CheckerRegistry,
    registry,
)


class TestCheckStatus:
    """Test CheckStatus enum."""

    def test_status_values(self):
        """Test that CheckStatus has the expected values."""
        assert CheckStatus.PASSED.value == "passed"
        assert CheckStatus.FAILED.value == "failed"
        assert CheckStatus.SKIPPED.value == "skipped"
        assert CheckStatus.ERROR.value == "error"


class TestCheckResult:
    """Test CheckResult dataclass."""

    def test_check_result_creation(self):
        """Test creating a CheckResult."""
        result = CheckResult(
            name="test_checker",
            status=CheckStatus.PASSED,
            output="Success!",
            error="",
            duration=1.5,
        )

        assert result.name == "test_checker"
        assert result.status == CheckStatus.PASSED
        assert result.output == "Success!"
        assert result.error == ""
        assert result.duration == 1.5


class TestBaseChecker:
    """Test BaseChecker abstract class."""

    def test_base_checker_creation(self):
        """Test creating a BaseChecker."""
        class ConcreteChecker(BaseChecker):
            def check(self, project_path):
                return CheckResult(self.name, CheckStatus.PASSED)
            
            def is_available(self):
                return True
        
        checker = ConcreteChecker("test", "Test checker")
        assert checker.name == "test"
        assert checker.description == "Test checker"
        assert checker.enabled is True


class TestCommandChecker:
    """Test CommandChecker class."""

    def test_command_checker_creation(self):
        """Test creating a CommandChecker."""
        checker = CommandChecker(
            name="test",
            command="echo",
            args=["hello"],
            description="Test command",
        )

        assert checker.name == "test"
        assert checker.command == "echo"
        assert checker.args == ["hello"]
        assert checker.description == "Test command"

    @patch("subprocess.run")
    def test_command_checker_available(self, mock_run):
        """Test checking if command is available."""
        mock_run.return_value.returncode = 0

        checker = CommandChecker("test", "echo")
        assert checker.is_available() is True

    @patch("subprocess.run")
    def test_command_checker_not_available(self, mock_run):
        """Test checking if command is not available."""
        mock_run.side_effect = FileNotFoundError()

        checker = CommandChecker("test", "nonexistent")
        assert checker.is_available() is False

    @patch("subprocess.run")
    def test_command_checker_success(self, mock_run):
        """Test successful command execution."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success!"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        checker = CommandChecker("test", "echo", ["hello"])
        result = checker.check(None)

        assert result.status == CheckStatus.PASSED
        assert result.output == "Success!"
        assert result.error == ""

    @patch("subprocess.run")
    def test_command_checker_failure(self, mock_run):
        """Test failed command execution."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error occurred"
        mock_run.return_value = mock_result

        checker = CommandChecker("test", "echo", ["hello"])
        result = checker.check(None)

        assert result.status == CheckStatus.FAILED
        assert result.output == ""
        assert result.error == "Error occurred"


class TestCheckerRegistry:
    """Test CheckerRegistry class."""

    def test_registry_creation(self):
        """Test creating a CheckerRegistry."""
        registry = CheckerRegistry()
        assert registry is not None

    def test_register_checker(self):
        """Test registering a checker."""
        registry = CheckerRegistry()
        checker = CommandChecker("test", "echo")

        registry.register(checker)
        assert "test" in registry.get_all_checkers()

    def test_get_nonexistent_checker(self):
        """Test getting a nonexistent checker."""
        registry = CheckerRegistry()
        checker = registry.get_checker("nonexistent")
        assert checker is None

    def test_get_available_checkers(self):
        """Test getting available checkers."""
        registry = CheckerRegistry()

        # Mock checker that is available
        available_checker = CommandChecker("available", "echo")
        available_checker.is_available = lambda: True

        # Mock checker that is not available
        unavailable_checker = CommandChecker("unavailable", "nonexistent")
        unavailable_checker.is_available = lambda: False

        registry.register(available_checker)
        registry.register(unavailable_checker)

        available = registry.get_available_checkers()
        assert "available" in available
        assert "unavailable" not in available


class TestGlobalRegistry:
    """Test the global registry instance."""

    def test_global_registry_has_checkers(self):
        """Test that the global registry has checkers registered."""
        all_checkers = registry.get_all_checkers()
        assert len(all_checkers) > 0

        # Check that common checkers are registered
        expected_checkers = ["black", "flake8", "pylint", "mypy"]
        for checker_name in expected_checkers:
            assert checker_name in all_checkers
