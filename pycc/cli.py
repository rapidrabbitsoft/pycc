"""
Command-line interface for pycc.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Set

from .core import registry, CheckStatus
from .runner import CheckRunner
from .config_generator import ConfigGenerator
from .utils import print_header, print_result, print_summary


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="pycc",
        description="Python Code Checker - A comprehensive tool for running various Python code quality checks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pycc --all                    # Run all available checks
  pycc --format --lint          # Run formatting and linting checks
  pycc --generate-config        # Generate configuration files
  pycc --list                   # List all available checkers
  pycc --check black flake8     # Run specific checkers
        """
    )
    
    # Main action groups
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        "--all", "-a",
        action="store_true",
        help="Run all available checks"
    )
    action_group.add_argument(
        "--check", "-c",
        nargs="+",
        metavar="CHECKER",
        help="Run specific checkers"
    )
    action_group.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all available checkers"
    )
    action_group.add_argument(
        "--generate-config", "-g",
        action="store_true",
        help="Generate configuration files for all checkers"
    )
    
    # Check categories
    category_group = parser.add_argument_group("Check Categories")
    category_group.add_argument(
        "--format", "-f",
        action="store_true",
        help="Run formatting checks (black, isort)"
    )
    category_group.add_argument(
        "--lint",
        action="store_true",
        help="Run linting checks (flake8, pylint)"
    )
    category_group.add_argument(
        "--type", "-t",
        action="store_true",
        help="Run type checking (mypy)"
    )
    category_group.add_argument(
        "--security", "-s",
        action="store_true",
        help="Run security checks (bandit, safety)"
    )
    category_group.add_argument(
        "--docs", "-d",
        action="store_true",
        help="Run documentation checks (pydocstyle)"
    )
    category_group.add_argument(
        "--complexity", "-x",
        action="store_true",
        help="Run complexity checks (vulture, radon)"
    )
    
    # General options
    parser.add_argument(
        "--project-path", "-p",
        type=Path,
        default=Path.cwd(),
        help="Project path to check (default: current directory)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress output except for errors"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout for each check in seconds (default: 300)"
    )
    
    return parser


def get_checkers_by_category() -> dict:
    """Get checkers organized by category."""
    categories = {
        "format": ["black", "isort"],
        "lint": ["flake8", "pylint"],
        "type": ["mypy"],
        "security": ["bandit", "safety"],
        "docs": ["pydocstyle"],
        "complexity": ["vulture", "radon"]
    }
    return categories


def get_checkers_for_categories(selected_categories: Set[str]) -> List[str]:
    """Get checker names for selected categories."""
    categories = get_checkers_by_category()
    checkers = []
    
    for category in selected_categories:
        if category in categories:
            checkers.extend(categories[category])
    
    return list(set(checkers))  # Remove duplicates


def list_checkers():
    """List all available checkers."""
    print_header("Available Checkers")
    
    available_checkers = registry.get_available_checkers()
    all_checkers = registry.get_all_checkers()
    
    categories = get_checkers_by_category()
    
    for category, checker_names in categories.items():
        print(f"\n{category.upper()} CHECKS:")
        for name in checker_names:
            checker = all_checkers.get(name)
            if checker:
                status = "✓" if name in available_checkers else "✗"
                print(f"  {status} {name}: {checker.description}")
    
    # Show custom checkers if any
    custom_checkers = {name: checker for name, checker in all_checkers.items() 
                      if name not in [c for cats in categories.values() for c in cats]}
    
    if custom_checkers:
        print(f"\nCUSTOM CHECKS:")
        for name, checker in custom_checkers.items():
            status = "✓" if name in available_checkers else "✗"
            print(f"  {status} {name}: {checker.description}")
    
    print(f"\nTotal: {len(available_checkers)}/{len(all_checkers)} checkers available")


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle list command
    if args.list:
        list_checkers()
        return
    
    # Handle generate-config command
    if args.generate_config:
        config_gen = ConfigGenerator(args.project_path)
        config_gen.generate_all()
        return
    
    # Determine which checkers to run
    checkers_to_run = []
    
    if args.all:
        # Run all available checkers
        available_checkers = registry.get_available_checkers()
        checkers_to_run = list(available_checkers.keys())
    elif args.check:
        # Run specific checkers
        checkers_to_run = args.check
    else:
        # Run checkers based on categories
        selected_categories = set()
        
        if args.format:
            selected_categories.add("format")
        if args.lint:
            selected_categories.add("lint")
        if args.type:
            selected_categories.add("type")
        if args.security:
            selected_categories.add("security")
        if args.docs:
            selected_categories.add("docs")
        if args.complexity:
            selected_categories.add("complexity")
        
        if selected_categories:
            checkers_to_run = get_checkers_for_categories(selected_categories)
        else:
            parser.error("No checkers selected. Use --all, --check, or specify categories.")
    
    # Validate project path
    if not args.project_path.exists():
        print(f"Error: Project path '{args.project_path}' does not exist.", file=sys.stderr)
        sys.exit(1)
    
    if not args.project_path.is_dir():
        print(f"Error: Project path '{args.project_path}' is not a directory.", file=sys.stderr)
        sys.exit(1)
    
    # Run the checks
    runner = CheckRunner(
        project_path=args.project_path,
        verbose=args.verbose,
        quiet=args.quiet,
        json_output=args.json,
        timeout=args.timeout
    )
    
    results = runner.run_checks(checkers_to_run)
    
    # Print summary and exit
    failed_count = sum(1 for result in results if result.status == CheckStatus.FAILED)
    error_count = sum(1 for result in results if result.status == CheckStatus.ERROR)
    
    if not args.json:
        print_summary(results, failed_count, error_count)
    
    # Exit with appropriate code
    if failed_count > 0 or error_count > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main() 