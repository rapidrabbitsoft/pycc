"""
pycc - Python Code Checker

A comprehensive CLI tool for running various Python code quality checks
with extensible architecture for custom checkers.
"""

__version__ = "0.1.0"
__author__ = "RapidRabbit Software"
__email__ = "pycc@rapidrabbit.software"

from .cli import main

__all__ = ["main"]
