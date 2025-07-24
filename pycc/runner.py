"""
Check runner for executing code quality checks.
"""

import json
import time
from pathlib import Path
from typing import List

from .core import registry, CheckResult, CheckStatus


class CheckRunner:
    """Runner for executing code quality checks."""

    def __init__(
        self,
        project_path: Path,
        verbose: bool = False,
        quiet: bool = False,
        json_output: bool = False,
        timeout: int = 300,
    ):
        self.project_path = project_path
        self.verbose = verbose
        self.quiet = quiet
        self.json_output = json_output
        self.timeout = timeout

    def run_checks(self, checker_names: List[str]) -> List[CheckResult]:
        """Run the specified checks and return results."""
        results = []
        all_checkers = registry.get_all_checkers()
        available_checkers = registry.get_available_checkers()

        # Filter checkers
        checkers_to_run = []
        for name in checker_names:
            if name not in all_checkers:
                if not self.quiet:
                    print(f"Warning: Checker '{name}' not found")
                continue

            if name not in available_checkers:
                if not self.quiet:
                    print(f"Warning: Checker '{name}' is not available (not installed)")
                results.append(
                    CheckResult(
                        name=name,
                        status=CheckStatus.SKIPPED,
                        error=f"Checker '{name}' is not available",
                    )
                )
                continue

            checkers_to_run.append(name)

        # Run checks
        for name in checkers_to_run:
            checker = all_checkers[name]
            result = self._run_single_check(checker)
            results.append(result)

            # Print result if not in quiet mode
            if not self.quiet and not self.json_output:
                self._print_check_result(result)

        return results

    def _run_single_check(self, checker) -> CheckResult:
        """Run a single check."""
        if not self.quiet and not self.json_output:
            print(f"\n=== Running {checker.name} ===")

        try:
            result = checker.check(self.project_path)
            return result
        except Exception as e:
            return CheckResult(
                name=checker.name,
                status=CheckStatus.ERROR,
                error=f"Unexpected error: {str(e)}",
            )

    def _print_check_result(self, result: CheckResult):
        """Print the result of a single check."""
        if result.status == CheckStatus.PASSED:
            print(f"✓ {result.name} passed ({result.duration:.2f}s)")
        elif result.status == CheckStatus.FAILED:
            print(f"✗ {result.name} failed ({result.duration:.2f}s)")
            if self.verbose and result.error:
                print(f"  Error: {result.error}")
        elif result.status == CheckStatus.ERROR:
            print(f"✗ {result.name} error ({result.duration:.2f}s)")
            if result.error:
                print(f"  Error: {result.error}")
        elif result.status == CheckStatus.SKIPPED:
            print(f"- {result.name} skipped")
            if result.error:
                print(f"  Reason: {result.error}")

    def get_json_results(self, results: List[CheckResult]) -> str:
        """Convert results to JSON format."""
        json_results = []

        for result in results:
            json_result = {
                "name": result.name,
                "status": result.status.value,
                "duration": result.duration,
                "output": result.output,
                "error": result.error,
            }
            json_results.append(json_result)

        return json.dumps(
            {
                "project_path": str(self.project_path),
                "timestamp": time.time(),
                "results": json_results,
                "summary": {
                    "total": len(results),
                    "passed": sum(
                        1 for r in results if r.status == CheckStatus.PASSED
                    ),
                    "failed": sum(
                        1 for r in results if r.status == CheckStatus.FAILED
                    ),
                    "error": sum(
                        1 for r in results if r.status == CheckStatus.ERROR
                    ),
                    "skipped": sum(
                        1 for r in results if r.status == CheckStatus.SKIPPED
                    ),
                },
            },
            indent=2,
        )
