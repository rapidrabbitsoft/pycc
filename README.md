# pycc - Python Code Checker

A comprehensive CLI tool for running various Python code quality checks with extensible architecture for custom checkers.

## Features

- **Multiple Code Quality Tools**: Integrates with Black, isort, Flake8, Pylint, MyPy, Bandit, Safety, Pydocstyle, Vulture, and Radon
- **Extensible Architecture**: Easy to add custom checkers through a plugin system
- **Configuration Generation**: Auto-generate project configuration files for all supported tools
- **Category-based Execution**: Run checks by category (formatting, linting, type checking, security, documentation, complexity)
- **JSON Output**: Get results in machine-readable JSON format
- **Timeout Support**: Configurable timeouts for long-running checks
- **Verbose Output**: Detailed output for debugging and CI/CD integration

## Installation

### From PyPI (Recommended)

```bash
pip install pycc
```

### From Source

```bash
git clone https://github.com/rapidrabbitsoft/pycc.git
cd pycc
pip install -e .
```

## Quick Start

### 1. Generate Configuration Files

Set up your project with all necessary configuration files:

```bash
pycc --generate-config
```

This creates:
- `pyproject.toml` - Modern Python packaging configuration
- `setup.cfg` - Legacy packaging configuration
- `Pipfile` - Development dependencies management
- `.flake8` - Flake8 configuration
- `.bandit` - Bandit security configuration

### 2. Install Development Dependencies

Using pipenv (recommended):

```bash
pipenv install --dev
```

Or using pip:

```bash
pip install -r requirements.txt  # if you have one
```

### 3. Run Code Quality Checks

```bash
# Run all available checks
pycc --all

# Run specific categories
pycc --format --lint

# Run specific checkers
pycc --check black flake8

# List all available checkers
pycc --list
```

## Usage

### Basic Commands

```bash
# Run all available checks
pycc --all

# Run checks by category
pycc --format          # Black, isort
pycc --lint           # Flake8, Pylint
pycc --type           # MyPy
pycc --security       # Bandit, Safety
pycc --docs           # Pydocstyle
pycc --complexity     # Vulture, Radon

# Run specific checkers
pycc --check black flake8 mypy

# Generate configuration files
pycc --generate-config

# List available checkers
pycc --list
```

### Advanced Options

```bash
# Specify project path
pycc --all --project-path /path/to/project

# Verbose output
pycc --all --verbose

# Quiet mode (errors only)
pycc --all --quiet

# JSON output
pycc --all --json

# Custom timeout (in seconds)
pycc --all --timeout 600
```

### Output Examples

#### Standard Output
```
=== Running black ===
✓ black passed (1.23s)

=== Running flake8 ===
✗ flake8 failed (0.45s)
  Error: E501 line too long (89 > 88)

Summary:
  Total checks: 2
  Passed: 1
  Failed: 1
  Errors: 0
  Skipped: 0

Some checks failed!
```

#### JSON Output
```json
{
  "project_path": "/path/to/project",
  "timestamp": 1640995200.0,
  "results": [
    {
      "name": "black",
      "status": "passed",
      "duration": 1.23,
      "output": "",
      "error": ""
    }
  ],
  "summary": {
    "total": 1,
    "passed": 1,
    "failed": 0,
    "error": 0,
    "skipped": 0
  }
}
```

## Extensibility

### Creating Custom Checkers

Create a custom checker by inheriting from `BaseChecker`:

```python
from pycc.core import BaseChecker, CheckResult, CheckStatus
from pathlib import Path

class CustomChecker(BaseChecker):
    def __init__(self):
        super().__init__("custom", "My custom checker")
    
    def check(self, project_path: Path) -> CheckResult:
        # Your custom logic here
        return CheckResult(
            name=self.name,
            status=CheckStatus.PASSED,
            output="Custom check passed"
        )
    
    def is_available(self) -> bool:
        # Check if your tool is available
        return True

# Register your checker
from pycc.core import registry
registry.register(CustomChecker())
```

### Example Custom Checkers

See `examples/custom_checker.py` for complete examples including:
- TODO comment checker
- Shebang line checker
- Line ending checker

## Configuration

### Generated Configuration Files

When you run `pycc --generate-config`, the following files are created:

#### pyproject.toml
Modern Python packaging configuration with tool-specific settings for:
- Black (code formatting)
- isort (import sorting)
- Pylint (linting)
- MyPy (type checking)
- Pydocstyle (documentation)
- Pytest (testing)
- Coverage (test coverage)

#### Pipfile
Development dependencies management with:
- All code quality tools
- Testing frameworks
- Convenient scripts for common tasks

#### setup.cfg
Legacy packaging configuration for compatibility.

#### Tool-specific Configs
- `.flake8` - Flake8 linting configuration
- `.bandit` - Bandit security configuration

### Customizing Configuration

Edit the generated files to customize tool behavior:

```toml
# pyproject.toml
[tool.black]
line-length = 100  # Custom line length

[tool.isort]
profile = "black"
line_length = 100
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install pycc
        run: pip install pycc
      
      - name: Generate configs
        run: pycc --generate-config
      
      - name: Install dev dependencies
        run: pip install -e .[dev]
      
      - name: Run code quality checks
        run: pycc --all --json > results.json
      
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: quality-results
          path: results.json
```

### GitLab CI Example

```yaml
code_quality:
  image: python:3.10
  script:
    - pip install pycc
    - pycc --generate-config
    - pip install -e .[dev]
    - pycc --all
  artifacts:
    reports:
      junit: test-results.xml
```

## Development

### Setting Up Development Environment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/rapidrabbitsoft/pycc.git
   cd pycc
   ```

2. **Set up pipenv environment**:
   ```bash
   pipenv install --dev
   pipenv shell
   ```

3. **Install the package in development mode**:
   ```bash
   pip install -e .
   ```

### Running Tests

```bash
# Run all tests
pipenv run pytest tests/ -v

# Run with coverage
pipenv run pytest tests/ --cov=pycc --cov-report=html

# Run specific test file
pipenv run pytest tests/test_core.py -v
```

### Code Quality Checks

```bash
# Run all quality checks
pipenv run pycc --all

# Run specific checks
pipenv run pycc --format --lint

# Format code
pipenv run black pycc/ tests/

# Sort imports
pipenv run isort pycc/ tests/

# Lint code
pipenv run flake8 pycc/ tests/
```

### Building the Package

```bash
# Clean previous builds
pipenv run python build.py clean

# Build package
pipenv run python setup.py sdist bdist_wheel

# Install locally
pipenv run python build.py install
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Set up development environment (see above)
4. Make your changes
5. Run tests: `pipenv run pytest tests/ -v`
6. Run quality checks: `pipenv run pycc --all`
7. Commit your changes: `git commit -m 'Add amazing feature'`
8. Push to the branch: `git push origin feature/amazing-feature`
9. Open a Pull Request

### Code Style

This project follows strict code quality standards:
- **Black** for code formatting
- **isort** for import sorting
- **Flake8** for linting
- **MyPy** for type checking
- **Pydocstyle** for documentation style

All code must pass these checks before merging.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Black**: Code formatting
- **isort**: Import sorting
- **Flake8**: Linting
- **Pylint**: Advanced linting
- **MyPy**: Type checking
- **Bandit**: Security linting
- **Safety**: Security vulnerability checking
- **Pydocstyle**: Documentation style
- **Vulture**: Dead code detection
- **Radon**: Code complexity analysis

## Changelog

### [0.1.0] - 2024-01-XX
- Initial release
- Support for 10 code quality tools
- Extensible checker architecture
- Configuration file generation
- JSON output support
- Comprehensive test suite 