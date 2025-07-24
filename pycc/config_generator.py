"""
Configuration file generator for pycc.
"""

import os
from pathlib import Path
from typing import Dict, List, Any

from .core import registry


class ConfigGenerator:
    """Generator for configuration files."""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.config_files = {}
        self._collect_config_files()
    
    def _collect_config_files(self):
        """Collect all configuration files from registered checkers."""
        all_checkers = registry.get_all_checkers()
        
        for checker in all_checkers.values():
            config_files = checker.get_config_files()
            for config in config_files:
                filename = config["name"]
                if filename not in self.config_files:
                    self.config_files[filename] = []
                self.config_files[filename].append(config)
    
    def generate_all(self):
        """Generate all configuration files."""
        print("Generating configuration files...")
        
        for filename, configs in self.config_files.items():
            self._generate_file(filename, configs)
        
        # Generate additional common files
        self._generate_pyproject_toml()
        self._generate_setup_cfg()
        self._generate_requirements_dev_txt()
        
        print("Configuration files generated successfully!")
    
    def _generate_file(self, filename: str, configs: List[Dict[str, Any]]):
        """Generate a specific configuration file."""
        file_path = self.project_path / filename
        
        if file_path.exists():
            print(f"  Warning: {filename} already exists, skipping...")
            return
        
        # For pyproject.toml, we need to merge multiple configurations
        if filename == "pyproject.toml":
            content = self._merge_pyproject_configs(configs)
        else:
            # For other files, use the first config
            content = configs[0]["content"]
        
        # Write the file
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"  Generated: {filename}")
    
    def _merge_pyproject_configs(self, configs: List[Dict[str, Any]]) -> str:
        """Merge multiple pyproject.toml configurations."""
        # Start with a basic project configuration
        content = """[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "your-project-name"
version = "0.1.0"
description = "Your project description"
authors = [
    {name = "RapidRabbit Software", email = "pycc@rapidrabbit.software"}
]
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    # Add your dependencies here
]

[project.optional-dependencies]
dev = [
    "black",
    "isort",
    "flake8",
    "pylint",
    "mypy",
    "bandit",
    "safety",
    "pydocstyle",
    "vulture",
    "radon",
]

[tool.setuptools.packages.find]
where = ["."]
include = ["*"]
exclude = ["tests*", "test*"]

"""
        
        # Add tool-specific configurations
        for config in configs:
            if config["content"].strip():
                content += config["content"] + "\n"
        
        return content
    
    def _generate_pyproject_toml(self):
        """Generate a comprehensive pyproject.toml file."""
        file_path = self.project_path / "pyproject.toml"
        
        if file_path.exists():
            return  # Already handled by _generate_file
        
        # This is a fallback if no checkers provided pyproject.toml configs
        content = """[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "your-project-name"
version = "0.1.0"
description = "Your project description"
authors = [
    {name = "RapidRabbit Software", email = "pycc@rapidrabbit.software"}
]
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    # Add your dependencies here
]

[project.optional-dependencies]
dev = [
    "black",
    "isort",
    "flake8",
    "pylint",
    "mypy",
    "bandit",
    "safety",
    "pydocstyle",
    "vulture",
    "radon",
]

[tool.setuptools.packages.find]
where = ["."]
include = ["*"]
exclude = ["tests*", "test*"]

# Black configuration
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

# isort configuration
[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["your_package_name"]

# Pylint configuration
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

# MyPy configuration
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

# Pydocstyle configuration
[tool.pydocstyle]
convention = "google"
add_select = ["D100", "D104", "D105", "D106", "D107"]
add_ignore = ["D100", "D104"]
"""
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"  Generated: pyproject.toml")
    
    def _generate_setup_cfg(self):
        """Generate a setup.cfg file for compatibility."""
        file_path = self.project_path / "setup.cfg"
        
        if file_path.exists():
            return
        
        content = """[metadata]
name = your-project-name
version = 0.1.0
description = Your project description
author = RapidRabbit Software
author_email = pycc@rapidrabbit.software
long_description = file: README.md
long_description_content_type = text/markdown
classifiers =
    Development Status :: 3 - Alpha
    Intended Audience :: Developers
    License :: OSI Approved :: MIT License
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3.8
    Programming Language :: Python :: 3.9
    Programming Language :: Python :: 3.10
    Programming Language :: Python :: 3.11

[options]
packages = find:
python_requires = >=3.8
install_requires =
    # Add your dependencies here

[options.packages.find]
exclude =
    tests*
    test*

[options.extras_require]
dev =
    black
    isort
    flake8
    pylint
    mypy
    bandit
    safety
    pydocstyle
    vulture
    radon

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

[pycodestyle]
max-line-length = 88
ignore = E203, W503

[pydocstyle]
convention = google
add_select = D100,D104,D105,D106,D107
add_ignore = D100,D104
"""
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"  Generated: setup.cfg")
    
    def _generate_requirements_dev_txt(self):
        """Generate a requirements-dev.txt file."""
        file_path = self.project_path / "requirements-dev.txt"
        
        if file_path.exists():
            return
        
        content = """# Development dependencies for code quality tools
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

# Additional useful development tools
pytest>=7.0.0
pytest-cov>=3.0.0
coverage>=6.0.0
pre-commit>=2.20.0
"""
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"  Generated: requirements-dev.txt") 