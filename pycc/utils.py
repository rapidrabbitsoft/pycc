"""
Utility functions for pycc.
"""

import sys
from typing import List

from .core import CheckResult, CheckStatus


# Colors for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{YELLOW}=== {text} ==={NC}\n")


def print_result(result: CheckResult, verbose: bool = False):
    """Print a check result."""
    if result.status == CheckStatus.PASSED:
        print(f"{GREEN}✓ {result.name} passed ({result.duration:.2f}s){NC}")
    elif result.status == CheckStatus.FAILED:
        print(f"{RED}✗ {result.name} failed ({result.duration:.2f}s){NC}")
        if verbose and result.error:
            print(f"  {RED}Error: {result.error}{NC}")
    elif result.status == CheckStatus.ERROR:
        print(f"{RED}✗ {result.name} error ({result.duration:.2f}s){NC}")
        if result.error:
            print(f"  {RED}Error: {result.error}{NC}")
    elif result.status == CheckStatus.SKIPPED:
        print(f"{YELLOW}- {result.name} skipped{NC}")
        if result.error:
            print(f"  {YELLOW}Reason: {result.error}{NC}")


def print_summary(results: List[CheckResult], failed_count: int, error_count: int):
    """Print a summary of all results."""
    print_header("Summary")
    
    total = len(results)
    passed_count = sum(1 for r in results if r.status == CheckStatus.PASSED)
    skipped_count = sum(1 for r in results if r.status == CheckStatus.SKIPPED)
    
    print(f"Total checks: {total}")
    print(f"{GREEN}Passed: {passed_count}{NC}")
    print(f"{RED}Failed: {failed_count}{NC}")
    print(f"{RED}Errors: {error_count}{NC}")
    print(f"{YELLOW}Skipped: {skipped_count}{NC}")
    
    if failed_count == 0 and error_count == 0:
        print(f"\n{GREEN}All checks passed!{NC}")
    else:
        print(f"\n{RED}{failed_count + error_count} check(s) failed{NC}")


def print_warning(message: str):
    """Print a warning message."""
    print(f"{YELLOW}Warning: {message}{NC}", file=sys.stderr)


def print_error(message: str):
    """Print an error message."""
    print(f"{RED}Error: {message}{NC}", file=sys.stderr)


def print_info(message: str):
    """Print an info message."""
    print(f"{BLUE}Info: {message}{NC}")


def format_duration(seconds: float) -> str:
    """Format duration in a human-readable way."""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s" 