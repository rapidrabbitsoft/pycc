# pycc - Python Code Checker

A comprehensive CLI tool for running various Python code quality checks with extensible architecture for custom checkers.

## Features

- **Multiple Checkers**: Supports popular Python code quality tools including:
  - **Formatting**: Black, isort
  - **Linting**: Flake8, Pylint
  - **Type Checking**: MyPy
  - **Security**: Bandit, Safety
  - **Documentation**: Pydocstyle
  - **Complexity**: Vulture, Radon

- **Extensible Architecture**: Easy to add custom checkers
- **Configuration Generation**: Auto-generate configuration files for all tools
- **Flexible Execution**: Run all checks, specific categories, or individual checkers
- **JSON Output**: Machine-readable output for CI/CD integration
- **Cross-platform**: Works on Windows, macOS, and Linux

## Installation

### From PyPI (recommended)

```bash
pip install pycc
```

### From source

```bash
git clone git@github.com:rapidrabbitsoft/pycc.git
cd pycc
pip install -e .
```

## Quick Start

### 1. Generate Configuration Files

First, generate all the necessary configuration files for your project:

```bash
pycc --generate-config
```

This will create:
- `pyproject.toml` - Main project configuration
- `setup.cfg` - Alternative configuration format
- `requirements-dev.txt` - Development dependencies
- Tool-specific configuration files (`.flake8`, `.bandit`, etc.)

### 2. Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

### 3. Run Code Checks

```bash
# Run all available checks
pycc --all

# Run specific categories
pycc --format --lint

# Run specific checkers
pycc --check black flake8 mypy

# Run with verbose output
pycc --all --verbose

# Output results in JSON format
pycc --all --json
```

## Usage

### Command Line Options

```bash
pycc [OPTIONS] COMMAND
```

#### Main Commands

- `--all, -a`: Run all available checks
- `--check, -c CHECKER [CHECKER ...]`: Run specific checkers
- `--list, -l`: List all available checkers
- `--generate-config, -g`: Generate configuration files

#### Check Categories

- `--format, -f`: Run formatting checks (black, isort)
- `--lint, -l`: Run linting checks (flake8, pylint)
- `--type, -t`: Run type checking (mypy)
- `--security, -s`: Run security checks (bandit, safety)
- `--docs, -d`: Run documentation checks (pydocstyle)
- `--complexity, -x`: Run complexity checks (vulture, radon)

#### General Options

- `--project-path, -p PATH`: Project path to check (default: current directory)
- `--verbose, -v`: Verbose output
- `--quiet, -q`: Suppress output except for errors
- `--json`: Output results in JSON format
- `--timeout SECONDS`: Timeout for each check (default: 300)

### Examples

```bash
# Basic usage
pycc --all

# Check only formatting and linting
pycc --format --lint

# Run specific tools
pycc --check black flake8 mypy

# Check a different directory
pycc --all --project-path /path/to/project

# Verbose output with JSON
pycc --all --verbose --json

# List available checkers
pycc --list

# Generate configuration files
pycc --generate-config
```

## Extending pycc

### Creating Custom Checkers

You can easily create custom checkers by extending the `BaseChecker` class:

```python
from pycc.core import BaseChecker, CheckResult, CheckStatus
from pathlib import Path

class MyCustomChecker(BaseChecker):
    def __init__(self):
        super().__init__("my-custom-checker", "My custom code quality check")
    
    def is_available(self) -> bool:
        # Check if your tool is available
        return True  # or check if tool is installed
    
    def check(self, project_path: Path) -> CheckResult:
        # Implement your check logic here
        try:
            # Run your check
            # ...
            return CheckResult(
                name=self.name,
                status=CheckStatus.PASSED,
                output="Check passed successfully"
            )
        except Exception as e:
            return CheckResult(
                name=self.name,
                status=CheckStatus.FAILED,
                error=str(e)
            )
    
    def get_config_files(self):
        # Return configuration files needed for your checker
        return [
            {
                "name": "my-checker.conf",
                "content": "# Configuration for my checker\n",
                "description": "My checker configuration file"
            }
        ]

# Register your checker
from pycc.core import registry
registry.register(MyCustomChecker())
```

### Plugin System

For more advanced extensibility, you can create plugins:

```python
# my_plugin.py
from pycc.core import registry, BaseChecker, CheckResult, CheckStatus

class MyPluginChecker(BaseChecker):
    # ... implementation ...

def register_plugin():
    registry.register(MyPluginChecker())

# In your setup.py or pyproject.toml
[project.entry-points."pycc.plugins"]
my-plugin = "my_plugin:register_plugin"
```

## Configuration

### Project Configuration

The `--generate-config` command creates a comprehensive `pyproject.toml` file with configurations for all supported tools. You can customize these configurations as needed.

### Tool-Specific Configuration

Each tool can have its own configuration file:

- **Black**: `pyproject.toml` or `pyproject.toml`
- **isort**: `pyproject.toml` or `.isort.cfg`
- **Flake8**: `.flake8` or `setup.cfg`
- **Pylint**: `pyproject.toml` or `.pylintrc`
- **MyPy**: `pyproject.toml` or `mypy.ini`
- **Bandit**: `.bandit`
- **Pydocstyle**: `pyproject.toml` or `.pydocstyle`

## CI/CD Integration

### GitHub Actions

```yaml
name: Code Quality

on: [push, pull_request]

jobs:
  code-quality:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install pycc
        pip install -r requirements-dev.txt
    
    - name: Run code quality checks
      run: pycc --all --json > results.json
    
    - name: Upload results
      uses: actions/upload-artifact@v3
      with:
        name: code-quality-results
        path: results.json
```

### GitLab CI

```yaml
code_quality:
  stage: test
  image: python:3.11
  before_script:
    - pip install pycc
    - pip install -r requirements-dev.txt
  script:
    - pycc --all
```

## Development

### Setting up Development Environment

```bash
git clone git@github.com:rapidrabbitsoft/pycc.git
cd pycc
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Run all checks on the project itself
pycc --all

# Format code
black .
isort .

# Type checking
mypy pycc/

# Linting
flake8 pycc/
pylint pycc/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- All the amazing Python code quality tools that make this possible
- The Python community for creating such excellent development tools

## Changelog

### 0.1.0 (2024-01-XX)
- Initial release
- Support for major Python code quality tools
- Extensible architecture
- Configuration generation
- JSON output support 