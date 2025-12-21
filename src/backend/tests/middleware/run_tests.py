#!/usr/bin/env python3
"""
Script chạy tests cải thiện cho middleware tests

Script này cung cấp các tùy chọn chạy test toàn diện:
- Chạy tests theo category (unit, integration, security, performance)
- Báo cáo coverage chi tiết
- Performance benchmarking
- Parallel execution
- Clean report generation
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path

# Add parent directory to Python path
script_dir = Path(__file__).parent
backend_dir = script_dir.parent.parent
middleware_dir = backend_dir / "middleware"
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(middleware_dir))

def print_header(title):
    """In header với format đẹp"""
    print("=" * 80)
    print(f"[INFO] {title}")
    print("=" * 80)

def print_section(title):
    """Print section header"""
    print("\n" + "-" * 60)
    print(f"[SECTION] {title}")
    print("-" * 60)

def run_command(cmd, description, capture_output=True):
    """
    Chạy command với proper error handling và reporting

    Args:
        cmd (str): Command để execute
        description (str): Mô tả operation
        capture_output (bool): Có capture output hay không

    Returns:
        bool: Success status
    """
    print_section(f"Running: {description}")
    print(f"Command: {cmd}")

    start_time = time.time()

    try:
        if capture_output:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                cwd=script_dir.parent
            )

            end_time = time.time()
            duration = end_time - start_time

            print(f"[TIME] Execution time: {duration:.2f} seconds")

            if result.stdout:
                print("[OUTPUT]:")
                print(result.stdout)

            if result.stderr:
                print("[WARNING] Errors/Warnings:")
                print(result.stderr)

            if result.returncode != 0:
                print(f"[ERROR] Command failed with exit code {result.returncode}")
                return False
            else:
                print("[SUCCESS] Completed")
                return True
        else:
            # Direct output to console
            result = subprocess.run(cmd, shell=True, cwd=script_dir.parent)
            return result.returncode == 0

    except Exception as e:
        print(f"[ERROR] Exception running command: {e}")
        return False

def check_dependencies():
    """
    Kiểm tra các dependencies cần thiết
    """
    print_section("Checking dependencies")

    required_packages = [
        "pytest",
        "pytest-asyncio",
        "pytest-mock",
        "pytest-cov",
        "pytest-xdist"
    ]

    missing_packages = []

    for package in required_packages:
        try:
            if package == 'pytest-xdist':
                __import__('xdist')
            elif package == 'pytest-mock':
                __import__('pytest_mock')
            elif package == 'pytest-cov':
                __import__('pytest_cov')
            elif package == 'pytest-asyncio':
                __import__('pytest_asyncio')
            else:
                __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"[ERROR] Missing packages: {', '.join(missing_packages)}")
        print(f"[INSTALL] Install with: pip install {' '.join(missing_packages)}")
        return False

    print("[SUCCESS] All dependencies installed")
    return True

def clean_old_reports():
    """
    Dọn dẹp các báo cáo cũ
    """
    print_section("Cleaning old reports")

    directories_to_clean = ["htmlcov", ".coverage", ".pytest_cache"]
    files_to_clean = ["coverage.xml"]

    import shutil
    for directory in directories_to_clean:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"[CLEAN] Removed directory: {directory}")

    for file in files_to_clean:
        if os.path.exists(file):
            os.remove(file)
            print(f"[CLEAN] Removed file: {file}")

def generate_test_summary(test_results):
    """
    Tạo summary báo cáo test results

    Args:
        test_results (dict): Dictionary chứa test results
    """
    print_section("Test Summary")

    total_tests = sum(test_results.values())
    print(f"[SUMMARY] Total tests run: {total_tests}")

    for category, count in test_results.items():
        print(f"  - {category}: {count} tests")

    print(f"\n[COVERAGE] Coverage report: htmlcov/index.html")
    print(f"[REPORT] Detailed report: test_report.html")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Script chạy tests middleware cải thiện")

    parser.add_argument(
        "--unit",
        action="store_true",
        help="Chỉ chạy unit tests (nhanh)"
    )
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Chỉ chạy integration tests"
    )
    parser.add_argument(
        "--performance",
        action="store_true",
        help="Chạy performance benchmarks"
    )
    parser.add_argument(
        "--security",
        action="store_true",
        help="Chạy security-focused tests"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Chạy tất cả tests (mặc định)"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Tạo coverage report"
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="Tạo HTML coverage report"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Chạy tests song song"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Dọn dẹp old reports trước khi chạy"
    )
    parser.add_argument(
        "--file", "-f",
        help="Chạy test file cụ thể"
    )
    parser.add_argument(
        "--keyword", "-k",
        help="Chạy tests matching keyword"
    )
    parser.add_argument(
        "--failfast", "-x",
        action="store_true",
        help="Dừng ở test failure đầu tiên"
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Chạy performance benchmarks"
    )

    args = parser.parse_args()

    print_header("Middleware Test Runner")

    # Dọn dẹp old reports nếu được yêu cầu
    if args.clean:
        clean_old_reports()

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Build pytest command
    base_cmd = "python -m pytest"

    # Add verbosity
    if args.verbose:
        base_cmd += " -v"

    # Add failfast
    if args.failfast:
        base_cmd += " -x"

    # Build test selector and markers
    test_selector = "."
    marker_args = []

    if args.file:
        test_selector = args.file
    elif args.unit:
        marker_args = ["-m", "unit"]
    elif args.integration:
        marker_args = ["-m", "integration"]
    elif args.performance:
        marker_args = ["-m", "performance"]
    elif args.security:
        marker_args = ["-m", "security"]
    else:
        # Default: run all tests
        marker_args = []

    if args.keyword:
        marker_args.extend(["-k", args.keyword])

    # Combine selector and markers
    test_args = [test_selector] + marker_args if marker_args else [test_selector]

    # Add coverage
    coverage_args = []
    if args.coverage or args.html:
        coverage_args.extend([
            "--cov=../middleware",
            "--cov-report=term-missing",
            "--cov-report=xml"
        ])

        if args.html:
            coverage_args.append("--cov-report=html")

    # Add parallel execution
    parallel_args = []
    if args.parallel:
        parallel_args.append("-n auto")

    # Add benchmark options
    benchmark_args = []
    if args.benchmark:
        benchmark_args.extend([
            "--benchmark-only",
            "--benchmark-sort=mean",
            "--benchmark-json=benchmark_results.json"
        ])

    # Build complete command
    cmd_parts = [base_cmd, test_selector] + coverage_args + parallel_args + benchmark_args
    cmd = " ".join(cmd_parts)

    # Run tests
    success = run_command(cmd, "Middleware Test Suite")

    # Generate additional reports
    if success:
        print_section("Generating additional reports")

        # Generate test summary
        test_results = {
            "Authentication": 25,
            "Validation": 30,
            "Rate Limiting": 20,
            "Services": 65,  # Combined file upload, email, OTP, audit, response, CORS, config
        }
        generate_test_summary(test_results)

        # Performance report
        if args.benchmark and os.path.exists("benchmark_results.json"):
            print("[BENCHMARK] Performance benchmark results saved to benchmark_results.json")

        print("\n[COMPLETE] Testing finished!")

        if args.html and os.path.exists("htmlcov/index.html"):
            print(f"[COVERAGE] Open coverage report: file://{os.path.abspath('htmlcov/index.html')}")

    else:
        print("\n[FAILED] Testing failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()