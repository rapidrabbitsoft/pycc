"""
Tests for CLI module.
"""

import pytest
from unittest.mock import patch, MagicMock

from pycc.cli import (
    create_parser,
    get_checkers_by_category,
    get_checkers_for_categories,
    list_checkers,
    main
)


class TestCLIParser:
    """Test CLI parser creation and functionality."""

    def test_create_parser(self):
        """Test that parser is created successfully."""
        parser = create_parser()
        assert parser is not None
        assert parser.prog == "pycc"

    def test_parser_help(self):
        """Test that parser has help text."""
        parser = create_parser()
        help_text = parser.format_help()
        assert "Python Code Checker" in help_text
        assert "--all" in help_text
        assert "--check" in help_text
        assert "--list" in help_text


class TestCheckerCategories:
    """Test checker category functions."""

    def test_get_checkers_by_category(self):
        """Test getting checkers by category."""
        categories = get_checkers_by_category()
        assert "format" in categories
        assert "lint" in categories
        assert "type" in categories
        assert "security" in categories
        assert "docs" in categories
        assert "complexity" in categories

    def test_get_checkers_for_categories(self):
        """Test getting checkers for specific categories."""
        checkers = get_checkers_for_categories({"format", "lint"})
        assert "black" in checkers
        assert "isort" in checkers
        assert "flake8" in checkers
        assert "pylint" in checkers

    def test_get_checkers_for_empty_categories(self):
        """Test getting checkers for empty categories."""
        checkers = get_checkers_for_categories(set())
        assert checkers == []

    def test_get_checkers_for_nonexistent_category(self):
        """Test getting checkers for nonexistent category."""
        checkers = get_checkers_for_categories({"nonexistent"})
        assert checkers == []


class TestListCheckers:
    """Test list checkers functionality."""

    @patch("pycc.cli.print")
    def test_list_checkers(self, mock_print):
        """Test listing checkers."""
        list_checkers()
        mock_print.assert_called()


class TestCLIMain:
    """Test main CLI functionality."""

    @patch("pycc.cli.list_checkers")
    def test_main_list_command(self, mock_list_checkers):
        """Test main function with --list argument."""
        with patch("sys.argv", ["pycc", "--list"]):
            main()
            mock_list_checkers.assert_called_once()

    @patch("pycc.cli.ConfigGenerator")
    def test_main_generate_config_command(self, mock_config_generator):
        """Test main function with --generate-config argument."""
        mock_instance = MagicMock()
        mock_config_generator.return_value = mock_instance

        with patch("sys.argv", ["pycc", "--generate-config"]):
            main()
            mock_config_generator.assert_called_once()
            mock_instance.generate_all.assert_called_once()

    @patch("sys.exit")
    def test_main_no_arguments(self, mock_exit):
        """Test main function with no arguments."""
        with patch("sys.argv", ["pycc"]):
            main()
            # Should exit due to missing required arguments
            mock_exit.assert_called()

    @patch("sys.exit")
    def test_main_invalid_project_path(self, mock_exit):
        """Test main function with invalid project path."""
        with patch("sys.argv", ["pycc", "--all", "--project-path", "/nonexistent"]):
            main()
            # Should exit due to invalid project path
            mock_exit.assert_called()

    @patch("pycc.cli.CheckRunner")
    def test_main_all_checks(self, mock_check_runner):
        """Test main function with --all argument."""
        mock_instance = MagicMock()
        mock_instance.run_checks.return_value = []
        mock_check_runner.return_value = mock_instance

        with patch("sys.argv", ["pycc", "--all"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
