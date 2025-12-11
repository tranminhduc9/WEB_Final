#!/usr/bin/env python3
"""
Test runner script for middleware tests.

This script provides convenient ways to run different types of tests:
- All tests
- Unit tests only
- Integration tests only
- Specific middleware component tests
- Coverage reporting
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    return result.returncode


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run middleware tests")
    parser.add_argument(
        "--type",
        choices=["unit", "integration", "all"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--component",
        choices=["auth", "validation", "rate_limit", "error_handlers"],
        help="Run tests for specific component"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run with coverage reporting"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--failfast",
        action="store_true",
        help="Stop on first failure"
    )

    args = parser.parse_args()

    # Change to middleware directory
    middleware_dir = Path(__file__).parent
    os.chdir(middleware_dir)

    # Build pytest command
    cmd = ["python", "-m", "pytest"]

    # Add test selection
    if args.type == "unit":
        cmd.append("tests/unit")
    elif args.type == "integration":
        cmd.append("tests/integration")
    else:  # all
        cmd.append("tests")

    # Add component filter
    if args.component:
        cmd.extend(["-k", args.component])

    # Add coverage
    if args.coverage:
        cmd.extend([
            "--cov=.",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-report=xml"
        ])

    # Add verbosity
    if args.verbose:
        cmd.append("-vv")
    else:
        cmd.append("-v")

    # Add failfast
    if args.failfast:
        cmd.append("--failfast")

    # Run tests
    returncode = run_command(cmd)

    if returncode == 0:
        print("\n[PASS] All tests passed!")

        if args.coverage:
            print("\n[INFO] Coverage report generated in htmlcov/index.html")
    else:
        print(f"\n[FAIL] Tests failed with return code: {returncode}")
        sys.exit(returncode)


if __name__ == "__main__":
    main()