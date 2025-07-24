"""
Utility functions for pycc.
"""

import sys
from typing import List

from .core import CheckResult, CheckStatus

# Color constants for terminal output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
RESET = "\033[0m"


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{BOLD}{CYAN}{'=' * 60}{RESET}")
    print(f"{BOLD}{CYAN}{text:^60}{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 60}{RESET}")


def print_result(result: CheckResult, verbose: bool = False):
    """Print a single check result."""
    if result.status == CheckStatus.PASSED:
        status_color = GREEN
        status_symbol = "✓"
    elif result.status == CheckStatus.FAILED:
        status_color = RED
        status_symbol = "✗"
    elif result.status == CheckStatus.ERROR:
        status_color = RED
        status_symbol = "✗"
    else:  # SKIPPED
        status_color = YELLOW
        status_symbol = "-"

    print(f"{status_color}{status_symbol} {result.name}{RESET}")

    if verbose:
        if result.output:
            print(f"  Output: {result.output}")
        if result.error:
            print(f"  Error: {result.error}")
        if result.duration > 0:
            print(f"  Duration: {result.duration:.2f}s")


def print_summary(results: List[CheckResult], failed_count: int, error_count: int):
    """Print a summary of all results."""
    total = len(results)
    passed_count = sum(1 for r in results if r.status == CheckStatus.PASSED)
    skipped_count = sum(1 for r in results if r.status == CheckStatus.SKIPPED)

    print(f"\n{BOLD}Summary:{RESET}")
    print(f"  Total checks: {total}")
    print(f"  {GREEN}Passed: {passed_count}{RESET}")
    print(f"  {RED}Failed: {failed_count}{RESET}")
    print(f"  {RED}Errors: {error_count}{RESET}")
    print(f"  {YELLOW}Skipped: {skipped_count}{RESET}")

    if failed_count > 0 or error_count > 0:
        print(f"\n{RED}{BOLD}Some checks failed!{RESET}")
        return False
    else:
        print(f"\n{GREEN}{BOLD}All checks passed!{RESET}")
        return True


def print_available_checkers():
    """Print all available checkers."""
    from .core import registry

    available_checkers = registry.get_available_checkers()
    all_checkers = registry.get_all_checkers()

    print(f"\n{BOLD}Available Checkers:{RESET}")
    for name, checker in all_checkers.items():
        if name in available_checkers:
            print(f"  {GREEN}✓{RESET} {name}: {checker.description}")
        else:
            print(f"  {RED}✗{RESET} {name}: {checker.description} (not available)")


def print_config_files():
    """Print configuration files that will be generated."""
    from .core import registry

    all_checkers = registry.get_all_checkers()
    config_files = []

    for checker in all_checkers.values():
        config_files.extend(checker.get_config_files())

    print(f"\n{BOLD}Configuration Files:{RESET}")
    for config in config_files:
        print(f"  {BLUE}•{RESET} {config['name']}: {config['description']}")


def is_color_supported():
    """Check if the terminal supports color output."""
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
