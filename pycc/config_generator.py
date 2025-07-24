"""
Configuration file generator for pycc.
"""

from pathlib import Path

from .core import registry


class ConfigGenerator:
    """Generator for project configuration files."""

    def __init__(self, project_path: Path):
        self.project_path = project_path

    def generate_all(self):
        """Generate all configuration files."""
        print("Generating configuration files...")

        # Generate pyproject.toml
        self._generate_pyproject_toml()

        # Generate setup.cfg
        self._generate_setup_cfg()

        # Generate Pipfile
        self._generate_pipfile()

        # Generate tool-specific config files
        self._generate_tool_configs()

        print("Configuration files generated successfully!")

    def _generate_pyproject_toml(self):
        """Generate pyproject.toml file."""
        content = """[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "your-project-name"
version = "0.1.0"
description = "Your project description"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
    {name = "RapidRabbit Software", email = "pycc@rapidrabbit.software"}
]
keywords = ["python", "code-quality", "linting"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "click>=8.0.0",
]

[project.optional-dependencies]
dev = [
    "black>=22.0.0",
    "isort>=5.0.0",
    "flake8>=4.0.0",
    "pylint>=2.12.0",
    "mypy>=0.950",
    "bandit>=1.7.0",
    "safety>=1.10.0",
    "pydocstyle>=6.0.0",
    "vulture>=2.0.0",
    "radon>=5.0.0",
    "pytest>=6.0.0",
    "pytest-cov>=3.0.0",
]

[project.urls]
Homepage = "https://github.com/rapidrabbitsoft/pycc"
Repository = "https://github.com/rapidrabbitsoft/pycc"
Documentation = "https://github.com/rapidrabbitsoft/pycc#readme"
"Bug Tracker" = "https://github.com/rapidrabbitsoft/pycc/issues"

[project.scripts]
pycc = "pycc.cli:main"

[tool.black]
line-length = 88
target-version = ['py37']
include = '\\.pyi?$'
extend-exclude = '''
/(
  # directories
  \\.eggs
  | \\.git
  | \\.hg
  | \\.mypy_cache
  | \\.tox
  | \\.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["your_package_name"]

[tool.pylint.messages_control]
disable = [
    "C0114",  # missing-module-docstring
    "C0115",  # missing-class-docstring
    "C0116",  # missing-function-docstring
]

[tool.pylint.format]
max-line-length = 88

[tool.pylint.design]
max-args = 10
max-attributes = 10
max-bool-expr = 5
max-branches = 12
max-locals = 15
max-parents = 7
max-public-methods = 20
max-returns = 6
max-statements = 50

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[[tool.mypy.overrides]]
module = [
    "tests.*",
]
disallow_untyped_defs = false

[tool.pydocstyle]
convention = "google"
add_select = ["D100", "D104", "D105", "D106", "D107"]
add_ignore = ["D100", "D104"]

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q"
testpaths = [
    "tests",
]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

[tool.coverage.run]
source = ["your_package_name"]
omit = [
    "*/tests/*",
    "*/test_*",
    "*/__pycache__/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
]
"""
        self._write_file("pyproject.toml", content)

    def _generate_setup_cfg(self):
        """Generate setup.cfg file."""
        content = """[metadata]
name = your-project-name
version = 0.1.0
description = Your project description
long_description = file: README.md
long_description_content_type = text/markdown
author = RapidRabbit Software
author_email = pycc@rapidrabbit.software
url = https://github.com/rapidrabbitsoft/pycc
project_urls =
    Bug Tracker = https://github.com/rapidrabbitsoft/pycc/issues
    Documentation = https://github.com/rapidrabbitsoft/pycc#readme
    Source Code = https://github.com/rapidrabbitsoft/pycc
classifiers =
    Development Status :: 3 - Alpha
    Intended Audience :: Developers
    License :: OSI Approved :: MIT License
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3.8
    Programming Language :: Python :: 3.9
    Programming Language :: Python :: 3.10
    Programming Language :: Python :: 3.11
    Programming Language :: Python :: 3.12
keywords = python, code-quality, linting
license = MIT
platforms = unix, linux, osx, cygwin, win32
python_requires = >=3.8

[options]
packages = find:
python_requires = >=3.8
install_requires =
    click>=8.0.0

[options.packages.find]
include = your_package_name*

[options.extras_require]
dev =
    black>=22.0.0
    isort>=5.0.0
    flake8>=4.0.0
    pylint>=2.12.0
    mypy>=0.950
    bandit>=1.7.0
    safety>=1.10.0
    pydocstyle>=6.0.0
    vulture>=2.0.0
    radon>=5.0.0
    pytest>=6.0.0
    pytest-cov>=3.0.0

[options.entry_points]
console_scripts =
    pycc = pycc.cli:main

[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude =
    .git,
    __pycache__,
    .venv,
    build,
    dist,
    *.egg-info

[coverage:run]
source = your_package_name
omit =
    */tests/*
    */test_*
    */__pycache__/*

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    if self.debug:
    if settings.DEBUG
    raise AssertionError
    raise NotImplementedError
    if 0:
    if __name__ == .__main__.:
    class .*\\bProtocol\\):
    @(abc\\.)?abstractmethod
"""
        self._write_file("setup.cfg", content)

    def _generate_pipfile(self):
        """Generate Pipfile for development dependencies."""
        content = """[[source]]
url = "https://pypi.org/simple"
verify_ssl = true
name = "pypi"

[packages]
# Add your main dependencies here
# example-package = "*"

[dev-packages]
# Development dependencies for code quality tools
black = ">=22.0.0"
isort = ">=5.0.0"
flake8 = ">=4.0.0"
pylint = ">=2.12.0"
mypy = ">=0.950"
bandit = ">=1.7.0"
safety = ">=1.10.0"
pydocstyle = ">=6.0.0"
vulture = ">=2.0.0"
radon = ">=5.0.0"
pytest = ">=6.0.0"
pytest-cov = ">=3.0.0"

[requires]
python_version = "3.8"

[scripts]
test = "pytest tests/ -v"
lint = "flake8 pycc/ tests/"
format = "black pycc/ tests/"
sort-imports = "isort pycc/ tests/"
"""
        self._write_file("Pipfile", content)

    def _generate_tool_configs(self):
        """Generate tool-specific configuration files."""
        all_checkers = registry.get_all_checkers()

        for checker in all_checkers.values():
            config_files = checker.get_config_files()
            for config in config_files:
                self._write_file(config["name"], config["content"])

    def _write_file(self, filename: str, content: str):
        """Write content to a file."""
        file_path = self.project_path / filename
        file_path.write_text(content)
        print(f"Generated: {filename}")
