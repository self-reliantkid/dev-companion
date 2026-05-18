# Contributing to dev-companion

Thank you for your interest in contributing to dev-companion! This document provides guidelines and instructions for contributing to the project.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)
- Relevant logs or error messages

### Suggesting Enhancements

We welcome feature suggestions! Please create an issue with:
- A clear description of the enhancement
- Use cases and benefits
- Any implementation ideas you have

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Test your changes** thoroughly
4. **Update documentation** if needed
5. **Submit a pull request** with a clear description

## 🛠️ Development Setup

### Prerequisites
- Python 3.8 or higher
- Git
- IBM watsonx.ai account

### Local Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/dev-companion.git
cd dev-companion

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials

# Run tests
pytest tests/ -v
```

## 📝 Coding Standards

### Python Style Guide

We follow [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html):

- Use Google-style docstrings for all functions and classes
- Maximum line length: 100 characters
- Use type hints where appropriate
- Follow PEP 8 naming conventions

**Example:**
```python
def generate_documentation(code: str, language: str) -> str:
    """Generate documentation for the given code.
    
    Args:
        code (str): Source code to document
        language (str): Programming language (e.g., "Python", "JavaScript")
    
    Returns:
        str: Generated documentation in markdown format
    
    Raises:
        ValueError: If code is empty or language is unsupported
    """
    # Implementation here
    pass
```

### Testing Standards

- Write pytest-compatible tests for all new features
- Aim for high test coverage (80%+ preferred)
- Include tests for:
  - Happy paths
  - Edge cases
  - Error conditions
- Use descriptive test names: `test_<function>_<scenario>_<expected_result>`

**Example:**
```python
def test_generate_docs_with_valid_code_returns_documentation():
    """Test that valid code generates proper documentation."""
    code = "def add(a, b): return a + b"
    result = generate_documentation(code, "Python")
    assert "def add" in result
    assert "Args:" in result
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions or changes
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

**Examples:**
```
feat: add support for Rust language documentation
fix: resolve token caching issue in watsonx client
docs: update installation instructions for Windows
test: add edge case tests for sync detection
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_task_service.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Writing Tests

Place tests in the `tests/` directory with the naming convention `test_<module>.py`:

```
tests/
├── __init__.py
├── test_task_service.py
├── test_watsonx_client.py
└── test_utils.py
```

## 📚 Documentation

### Code Documentation

- Add docstrings to all public functions, classes, and modules
- Use Google-style format
- Include usage examples for complex functions
- Document all parameters, return values, and exceptions

### README Updates

When adding features, update:
- Feature list
- Usage examples
- Installation instructions (if needed)
- Project structure (if adding new directories)

## 🔍 Code Review Process

All submissions require review. We use GitHub pull requests for this:

1. **Automated Checks:** CI/CD runs tests and linting
2. **Peer Review:** At least one maintainer reviews the code
3. **Feedback:** Address any requested changes
4. **Approval:** Once approved, your PR will be merged

### Review Criteria

- Code quality and readability
- Test coverage
- Documentation completeness
- Adherence to coding standards
- No breaking changes (unless discussed)

## 🎯 Priority Areas

We especially welcome contributions in these areas:

1. **Language Support:** Add support for more programming languages
2. **Test Coverage:** Improve test coverage for existing features
3. **Performance:** Optimize token usage and generation speed
4. **Documentation:** Improve user guides and examples
5. **Bug Fixes:** Address open issues

## 🚀 Release Process

Maintainers handle releases:

1. Version bump following [Semantic Versioning](https://semver.org/)
2. Update CHANGELOG.md
3. Create GitHub release with notes
4. Tag the release

## 💬 Communication

- **Issues:** For bug reports and feature requests
- **Pull Requests:** For code contributions
- **Discussions:** For questions and general discussion

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors.

### Expected Behavior

- Be respectful and considerate
- Welcome newcomers and help them get started
- Accept constructive criticism gracefully
- Focus on what's best for the community

### Unacceptable Behavior

- Harassment or discriminatory language
- Personal attacks or trolling
- Publishing others' private information
- Other conduct inappropriate in a professional setting

### Enforcement

Violations may result in temporary or permanent ban from the project.

## 🙏 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in relevant documentation

## ❓ Questions?

If you have questions about contributing:
- Check existing issues and discussions
- Create a new issue with the "question" label
- Reach out to maintainers

---

Thank you for contributing to dev-companion! 🎉