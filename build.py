#!/usr/bin/env python3
"""
Build script for pycc package.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd, check=True):
    """Run a command and return the result."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, cmd)
    
    return result


def clean_build():
    """Clean build artifacts."""
    print("Cleaning build artifacts...")
    
    dirs_to_clean = ["build", "dist", "*.egg-info"]
    for pattern in dirs_to_clean:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"Removed: {path}")
            else:
                path.unlink()
                print(f"Removed: {path}")


def run_tests():
    """Run the test suite."""
    print("Running tests...")
    run_command("python -m pytest tests/ -v")


def run_linting():
    """Run linting checks."""
    print("Running linting checks...")
    
    # Check if tools are available
    tools = ["black", "isort", "flake8", "mypy"]
    for tool in tools:
        try:
            if tool == "black":
                run_command("black --check .")
            elif tool == "isort":
                run_command("isort --check-only .")
            elif tool == "flake8":
                run_command("flake8 pycc/ tests/")
            elif tool == "mypy":
                run_command("mypy pycc/")
        except subprocess.CalledProcessError:
            print(f"Warning: {tool} check failed or not available")


def build_package():
    """Build the package."""
    print("Building package...")
    run_command("python -m build")


def install_package():
    """Install the package in development mode."""
    print("Installing package in development mode...")
    run_command("pip install -e .")


def main():
    """Main build function."""
    if len(sys.argv) < 2:
        print("Usage: python build.py [clean|test|lint|build|install|all]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        if command == "clean":
            clean_build()
        elif command == "test":
            run_tests()
        elif command == "lint":
            run_linting()
        elif command == "build":
            build_package()
        elif command == "install":
            install_package()
        elif command == "all":
            clean_build()
            run_tests()
            run_linting()
            build_package()
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
            
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 