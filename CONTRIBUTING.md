# Contributing to Toonify

Thank you for your interest in contributing to Toonify! We welcome contributions from the community and are excited to work with you.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Reporting Issues](#reporting-issues)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for everyone. Please be respectful and professional in all interactions. Key principles:

- **Be respectful**: Value differing viewpoints and experiences
- **Be constructive**: Provide helpful feedback and criticism
- **Be collaborative**: Work together to improve the project
- **Be patient**: Remember that everyone was once a beginner

Unacceptable behavior includes harassment, trolling, personal attacks, or any conduct that would be inappropriate in a professional setting.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/toonify.git
   cd toonify
   ```
3. **Add the upstream repository** as a remote:
   ```bash
   git remote add upstream https://github.com/ScrapeGraphAI/toonify.git
   ```
4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip or uv package manager
- Git

### Installation

1. **Install in development mode with all dependencies**:
   ```bash
   pip install -e .[dev,pydantic]
   ```

   Or using `uv` (recommended):
   ```bash
   uv pip install -e .[dev,pydantic]
   ```

2. **Verify the installation**:
   ```bash
   python -c "import toon; print(toon.__version__)"
   pytest --version
   ```

### Project Structure

```
toonify/
├── toon/               # Main package
│   ├── encoder.py      # TOON encoding logic
│   ├── decoder.py      # TOON decoding logic
│   ├── cli.py          # Command-line interface
│   ├── pydantic_converter.py  # Pydantic integration
│   └── utils.py        # Utility functions
├── tests/              # Test suite
├── examples/           # Example scripts
├── benchmark/          # Performance benchmarks
└── docs/               # Documentation
```

## How to Contribute

### Types of Contributions

We welcome many types of contributions:

- 🐛 **Bug fixes**: Fix issues reported in GitHub Issues
- ✨ **New features**: Add new functionality or improve existing features
- 📝 **Documentation**: Improve README, docstrings, or examples
- 🧪 **Tests**: Add or improve test coverage
- 🚀 **Performance**: Optimize code for better performance
- 🌐 **Internationalization**: Add translations or improve i18n support
- 🎨 **Examples**: Create new examples or improve existing ones

### Finding Issues to Work On

- Check the [Issues page](https://github.com/ScrapeGraphAI/toonify/issues)
- Look for issues labeled `good first issue` or `help wanted`
- Comment on an issue to let others know you're working on it

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some exceptions:

- **Line length**: Maximum 100 characters (not 79)
- **Imports**: Group standard library, third-party, and local imports
- **Docstrings**: Use Google-style docstrings for all public functions/classes
- **Type hints**: Add type hints to function signatures when practical

### Example Code Style

```python
from typing import Dict, List, Optional, Union


def encode_array(
    items: List[Union[str, int, float, bool, None]],
    options: Optional[Dict[str, any]] = None
) -> str:
    """Encode a Python list to TOON array format.
    
    Args:
        items: List of values to encode
        options: Optional encoding configuration with:
            - delimiter: 'comma', 'tab', or 'pipe' (default: 'comma')
            - indent: Number of spaces per level (default: 2)
    
    Returns:
        TOON-formatted array string
        
    Raises:
        ValueError: If items list is empty or contains unsupported types
        
    Example:
        >>> encode_array([1, 2, 3], {'delimiter': 'comma'})
        '[1,2,3]'
    """
    if not items:
        raise ValueError("Cannot encode empty array")
    
    # Implementation...
    pass
```

### Best Practices

- ✅ Write self-documenting code with clear variable names
- ✅ Keep functions small and focused on a single responsibility
- ✅ Add comments for complex logic, but prefer clear code over comments
- ✅ Handle edge cases and validate inputs
- ✅ Use meaningful error messages
- ❌ Don't leave commented-out code in PRs
- ❌ Don't use wildcard imports (`from module import *`)

## Testing

### Running Tests

Run all tests:
```bash
pytest
```

Run with coverage report:
```bash
pytest --cov=toon --cov-report=term-missing
```

Run specific test file:
```bash
pytest tests/test_encoder.py
```

Run specific test:
```bash
pytest tests/test_encoder.py::test_encode_simple_dict
```

### Writing Tests

- **Location**: Place test files in the `tests/` directory
- **Naming**: Name test files `test_*.py` and test functions `test_*`
- **Coverage**: Aim for >90% code coverage for new features
- **Structure**: Use AAA pattern (Arrange, Act, Assert)

Example test:
```python
def test_encode_nested_object():
    """Test encoding of nested objects."""
    # Arrange
    data = {
        'user': {
            'name': 'Alice',
            'profile': {
                'age': 30
            }
        }
    }
    
    # Act
    result = encode(data)
    
    # Assert
    assert 'user:' in result
    assert 'name: Alice' in result
    assert 'age: 30' in result
    
    # Verify round-trip
    decoded = decode(result)
    assert decoded == data
```

### Test Types

1. **Unit tests**: Test individual functions and methods
2. **Integration tests**: Test component interactions
3. **Round-trip tests**: Ensure encode/decode consistency
4. **Edge case tests**: Test boundary conditions and error handling

### Running Examples

Test example scripts to ensure they work:
```bash
python examples/basic_usage.py
python examples/advanced_features.py
python examples/pydantic_usage.py
```

## Pull Request Process

### Before Submitting

1. ✅ Ensure all tests pass: `pytest`
2. ✅ Add tests for new functionality
3. ✅ Update documentation if needed
4. ✅ Run examples to verify they still work
5. ✅ Write clear commit messages
6. ✅ Update CHANGELOG.md if applicable

### Submitting a Pull Request

1. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open a Pull Request** on GitHub with:
   - **Clear title**: Summarize the change in one line
   - **Description**: Explain what changed and why
   - **Issue reference**: Link to related issues (e.g., "Fixes #123")
   - **Testing**: Describe how you tested the changes
   - **Breaking changes**: Note any breaking changes

3. **PR Template** (use this format):
   ```markdown
   ## Description
   Brief description of what this PR does.
   
   ## Related Issue
   Fixes #123
   
   ## Type of Change
   - [ ] Bug fix (non-breaking change which fixes an issue)
   - [ ] New feature (non-breaking change which adds functionality)
   - [ ] Breaking change (fix or feature that would cause existing functionality to change)
   - [ ] Documentation update
   
   ## Testing
   - [ ] All tests pass
   - [ ] Added new tests for the changes
   - [ ] Tested manually with examples
   
   ## Checklist
   - [ ] Code follows the project's style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] No new warnings or errors introduced
   ```

### Review Process

- A maintainer will review your PR within 3-5 business days
- Address any feedback or requested changes
- Once approved, a maintainer will merge your PR
- Your contribution will be credited in the release notes!

## Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `style`: Code style changes (formatting, etc.)
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

### Examples

```bash
# Feature
feat(encoder): add support for custom delimiters

# Bug fix
fix(decoder): handle escaped quotes in strings

# Documentation
docs(readme): update installation instructions

# Breaking change
feat(encoder)!: change default delimiter to tab

BREAKING CHANGE: The default delimiter has changed from comma to tab.
Update your code if you rely on the default behavior.
```

### Scope

Use these scopes when applicable:
- `encoder`: Encoding logic
- `decoder`: Decoding logic
- `cli`: Command-line interface
- `pydantic`: Pydantic integration
- `utils`: Utility functions
- `tests`: Test suite
- `docs`: Documentation

## Reporting Issues

### Bug Reports

When reporting a bug, include:

1. **Description**: Clear description of the bug
2. **Steps to reproduce**: Minimal code example
3. **Expected behavior**: What should happen
4. **Actual behavior**: What actually happens
5. **Environment**:
   - Python version
   - Toonify version
   - Operating system

**Bug Report Template**:
```markdown
## Description
Brief description of the bug

## Steps to Reproduce
```python
from toon import encode

data = {...}
result = encode(data)
```

## Expected Behavior
The output should be...

## Actual Behavior
But instead it is...

## Environment
- Python version: 3.11.5
- Toonify version: 0.0.2
- OS: macOS 14.0
```

### Feature Requests

When suggesting a feature:

1. **Use case**: Describe the problem you're trying to solve
2. **Proposed solution**: Your idea for solving it
3. **Alternatives**: Other solutions you've considered
4. **Additional context**: Examples, mockups, or references

## Documentation

### Types of Documentation

- **README.md**: Project overview and quick start
- **API docs**: Function/class docstrings (Google style)
- **Examples**: Working code examples in `examples/`
- **Inline comments**: Complex logic explanations

### Documentation Standards

- Use clear, concise language
- Include code examples when helpful
- Keep formatting consistent
- Update docs when changing functionality
- Add examples for new features

### Building Documentation Locally

```bash
# Install documentation dependencies (if applicable in future)
pip install -e .[docs]

# Run examples as documentation tests
python examples/basic_usage.py
```

## Community

### Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **Discussions**: For questions and general discussion
- **Email**: Contact the ScrapeGraph team at [scrapegraphai.com](https://scrapegraphai.com)

### Stay Connected

- **GitHub**: [ScrapeGraphAI/toonify](https://github.com/ScrapeGraphAI/toonify)
- **Website**: [scrapegraphai.com](https://scrapegraphai.com)
- **TOON Format Spec**: [toon-format/toon](https://github.com/toon-format/toon)

## Recognition

Contributors are recognized in:
- GitHub contributors list
- Release notes
- CHANGELOG.md

Thank you for contributing to Toonify! 🎉

---

**Questions?** Feel free to open a [GitHub Discussion](https://github.com/ScrapeGraphAI/toonify/discussions) or create an issue.

Made with ❤️ by the [ScrapeGraph team](https://scrapegraphai.com)

