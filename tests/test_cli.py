"""
Tests for the CLI functionality of pycc.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO

from pycc.cli import create_parser, get_checkers_by_category, get_checkers_for_categories, list_checkers


class TestCLIParser:
    """Test the CLI argument parser."""
    
    def test_create_parser(self):
        """Test that the parser is created correctly."""
        parser = create_parser()
        assert parser is not None
        assert parser.prog == "pycc"
    
    def test_parser_help(self):
        """Test that help is available."""
        parser = create_parser()
        help_text = parser.format_help()
        assert "pycc" in help_text
        assert "--all" in help_text
        assert "--check" in help_text


class TestCheckerCategories:
    """Test checker category functions."""
    
    def test_get_checkers_by_category(self):
        """Test getting checkers organized by category."""
        categories = get_checkers_by_category()
        
        assert "format" in categories
        assert "lint" in categories
        assert "type" in categories
        assert "security" in categories
        assert "docs" in categories
        assert "complexity" in categories
        
        # Check that each category has checkers
        for category, checkers in categories.items():
            assert isinstance(checkers, list)
            assert len(checkers) > 0
    
    def test_get_checkers_for_categories(self):
        """Test getting checkers for specific categories."""
        selected_categories = {"format", "lint"}
        checkers = get_checkers_for_categories(selected_categories)
        
        # Should include checkers from both categories
        assert "black" in checkers  # format
        assert "flake8" in checkers  # lint
        
        # Should not include checkers from other categories
        assert "mypy" not in checkers  # type
    
    def test_get_checkers_for_empty_categories(self):
        """Test getting checkers for empty category set."""
        checkers = get_checkers_for_categories(set())
        assert checkers == []
    
    def test_get_checkers_for_nonexistent_category(self):
        """Test getting checkers for non-existent category."""
        selected_categories = {"nonexistent"}
        checkers = get_checkers_for_categories(selected_categories)
        assert checkers == []


class TestListCheckers:
    """Test the list_checkers function."""
    
    @patch('pycc.cli.registry')
    @patch('pycc.cli.print_header')
    def test_list_checkers(self, mock_print_header, mock_registry):
        """Test listing checkers."""
        # Mock the registry
        mock_registry.get_available_checkers.return_value = {
            "black": MagicMock(description="Code formatting"),
            "flake8": MagicMock(description="Linting")
        }
        mock_registry.get_all_checkers.return_value = {
            "black": MagicMock(description="Code formatting"),
            "flake8": MagicMock(description="Linting"),
            "unavailable": MagicMock(description="Unavailable checker")
        }
        
        # Capture stdout
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            list_checkers()
            output = mock_stdout.getvalue()
        
        # Check that output contains expected information
        assert "black" in output
        assert "flake8" in output
        assert "Code formatting" in output
        assert "Linting" in output


class TestCLIMain:
    """Test the main CLI function."""
    
    @patch('pycc.cli.sys.exit')
    def test_main_list_command(self, mock_exit):
        """Test the --list command."""
        with patch('sys.argv', ['pycc', '--list']):
            with patch('pycc.cli.list_checkers') as mock_list:
                from pycc.cli import main
                main()
                mock_list.assert_called_once()
    
    @patch('pycc.cli.sys.exit')
    def test_main_generate_config_command(self, mock_exit):
        """Test the --generate-config command."""
        with patch('sys.argv', ['pycc', '--generate-config']):
            with patch('pycc.cli.ConfigGenerator') as mock_config_gen:
                mock_instance = MagicMock()
                mock_config_gen.return_value = mock_instance
                
                from pycc.cli import main
                main()
                
                mock_config_gen.assert_called_once()
                mock_instance.generate_all.assert_called_once()
    
    def test_main_no_arguments(self):
        """Test main with no arguments."""
        with patch('sys.argv', ['pycc']):
            from pycc.cli import main
            # This should raise SystemExit due to missing required arguments
            with pytest.raises(SystemExit):
                main()
    
    def test_main_invalid_project_path(self):
        """Test main with invalid project path."""
        with patch('sys.argv', ['pycc', '--all', '--project-path', '/nonexistent']):
            with patch('pycc.cli.Path') as mock_path:
                mock_path.return_value.exists.return_value = False
                
                from pycc.cli import main
                # This should raise SystemExit due to invalid project path
                with pytest.raises(SystemExit):
                    main()
    
    @patch('pycc.cli.sys.exit')
    def test_main_all_checks(self, mock_exit):
        """Test running all checks."""
        with patch('sys.argv', ['pycc', '--all']):
            with patch('pycc.cli.CheckRunner') as mock_runner_class:
                mock_runner = MagicMock()
                mock_runner.run_checks.return_value = []
                mock_runner_class.return_value = mock_runner
                
                from pycc.cli import main
                main()
                
                mock_runner_class.assert_called_once()
                mock_runner.run_checks.assert_called_once() 