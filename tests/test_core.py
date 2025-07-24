"""
Tests for the core functionality of pycc.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from pycc.core import (
    CheckStatus, CheckResult, BaseChecker, CommandChecker, 
    CheckerRegistry, registry
)


class TestCheckStatus:
    """Test the CheckStatus enum."""
    
    def test_status_values(self):
        """Test that status values are correct."""
        assert CheckStatus.PASSED.value == "passed"
        assert CheckStatus.FAILED.value == "failed"
        assert CheckStatus.SKIPPED.value == "skipped"
        assert CheckStatus.ERROR.value == "error"


class TestCheckResult:
    """Test the CheckResult dataclass."""
    
    def test_check_result_creation(self):
        """Test creating a CheckResult."""
        result = CheckResult(
            name="test-checker",
            status=CheckStatus.PASSED,
            output="Success",
            duration=1.5
        )
        
        assert result.name == "test-checker"
        assert result.status == CheckStatus.PASSED
        assert result.output == "Success"
        assert result.duration == 1.5
        assert result.error == ""


class TestBaseChecker:
    """Test the BaseChecker abstract class."""
    
    def test_base_checker_creation(self):
        """Test creating a BaseChecker."""
        class TestChecker(BaseChecker):
            def check(self, project_path):
                return CheckResult(self.name, CheckStatus.PASSED)
            
            def is_available(self):
                return True
        
        checker = TestChecker("test", "Test checker")
        assert checker.name == "test"
        assert checker.description == "Test checker"
        assert checker.enabled is True


class TestCommandChecker:
    """Test the CommandChecker class."""
    
    def test_command_checker_creation(self):
        """Test creating a CommandChecker."""
        checker = CommandChecker(
            name="test-command",
            command="echo",
            args=["hello"],
            description="Test command checker"
        )
        
        assert checker.name == "test-command"
        assert checker.command == "echo"
        assert checker.args == ["hello"]
        assert checker.description == "Test command checker"
    
    @patch('subprocess.run')
    def test_command_checker_available(self, mock_run):
        """Test checking if command is available."""
        mock_run.return_value.returncode = 0
        
        checker = CommandChecker("test", "echo")
        assert checker.is_available() is True
    
    @patch('subprocess.run')
    def test_command_checker_not_available(self, mock_run):
        """Test checking if command is not available."""
        mock_run.side_effect = FileNotFoundError()
        
        checker = CommandChecker("test", "nonexistent-command")
        assert checker.is_available() is False
    
    @patch('subprocess.run')
    def test_command_checker_success(self, mock_run):
        """Test successful command execution."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        checker = CommandChecker("test", "echo", ["hello"])
        result = checker.check(Path("."))
        
        assert result.status == CheckStatus.PASSED
        assert result.output == "Success output"
        assert result.error == ""
    
    @patch('subprocess.run')
    def test_command_checker_failure(self, mock_run):
        """Test failed command execution."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "Output"
        mock_result.stderr = "Error message"
        mock_run.return_value = mock_result
        
        checker = CommandChecker("test", "echo", ["hello"])
        result = checker.check(Path("."))
        
        assert result.status == CheckStatus.FAILED
        assert result.output == "Output"
        assert result.error == "Error message"


class TestCheckerRegistry:
    """Test the CheckerRegistry class."""
    
    def test_registry_creation(self):
        """Test creating a registry."""
        registry = CheckerRegistry()
        assert registry.get_all_checkers() == {}
    
    def test_register_checker(self):
        """Test registering a checker."""
        registry = CheckerRegistry()
        
        class TestChecker(BaseChecker):
            def check(self, project_path):
                return CheckResult(self.name, CheckStatus.PASSED)
            
            def is_available(self):
                return True
        
        checker = TestChecker("test", "Test checker")
        registry.register(checker)
        
        assert "test" in registry.get_all_checkers()
        assert registry.get_checker("test") == checker
    
    def test_get_nonexistent_checker(self):
        """Test getting a checker that doesn't exist."""
        registry = CheckerRegistry()
        assert registry.get_checker("nonexistent") is None
    
    def test_get_available_checkers(self):
        """Test getting available checkers."""
        registry = CheckerRegistry()
        
        class AvailableChecker(BaseChecker):
            def check(self, project_path):
                return CheckResult(self.name, CheckStatus.PASSED)
            
            def is_available(self):
                return True
        
        class UnavailableChecker(BaseChecker):
            def check(self, project_path):
                return CheckResult(self.name, CheckStatus.PASSED)
            
            def is_available(self):
                return False
        
        available = AvailableChecker("available", "Available checker")
        unavailable = UnavailableChecker("unavailable", "Unavailable checker")
        
        registry.register(available)
        registry.register(unavailable)
        
        available_checkers = registry.get_available_checkers()
        assert "available" in available_checkers
        assert "unavailable" not in available_checkers


class TestGlobalRegistry:
    """Test the global registry instance."""
    
    def test_global_registry_has_checkers(self):
        """Test that the global registry has built-in checkers."""
        # The global registry should have checkers registered
        all_checkers = registry.get_all_checkers()
        assert len(all_checkers) > 0
        
        # Should have some common checkers
        expected_checkers = ["black", "flake8", "mypy"]
        for checker_name in expected_checkers:
            assert checker_name in all_checkers 