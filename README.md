# dev-companion

**AI-powered documentation and test generation tool built with IBM Bob**

dev-companion is an intelligent development assistant that automatically generates docstrings, markdown documentation, and unit tests for Python codebases. It leverages IBM Bob IDE to analyze code, generate comprehensive documentation in Google style format, create pytest-compatible test suites, and detect when code changes make existing documentation or tests stale.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

---

## Features

- **📝 Automatic Documentation Generation** (`/gendoc`)
  - Generates Google-style docstrings for Python functions and classes
  - Creates comprehensive markdown documentation files
  - Includes usage examples, parameter descriptions, and return types

- **🧪 Intelligent Test Generation** (`/gentest`)
  - Generates pytest-compatible unit tests automatically
  - Covers happy paths, edge cases, and error conditions
  - Creates fixtures and comprehensive test suites

- **🔄 Staleness Detection** (`/sync`)
  - Scans codebase for changes in function signatures
  - Compares existing documentation and tests against current code
  - Flags stale items with clear comments indicating what changed

- **📊 Task Management Demo**
  - Includes a complete task management system as a demonstration
  - Features CRUD operations, priority management, and subtask support
  - Fully documented and tested using dev-companion's own tools

---

## Installation

### Prerequisites

- Python 3.8 or higher
- IBM Bob IDE
- pytest (for running tests)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/dev-companion.git
cd dev-companion
```

2. Install dependencies:
```bash
pip install pytest
```

3. Verify installation:
```bash
python main.py test
```

---

## Usage

### Command-Line Interface

dev-companion provides a CLI for quick access to common operations:

```bash
# Run the full demo
python main.py demo

# Run the test suite
python main.py test

# Show instructions for generating documentation
python main.py gendoc

# Show instructions for generating tests
python main.py gentest

# Show instructions for syncing docs/tests
python main.py sync
```

### Using IBM Bob Commands

The core functionality is accessed through IBM Bob IDE custom commands:

#### Generate Documentation

```
/gendoc src/task_service.py
```

This command:
- Analyzes the target Python file
- Generates Google-style docstrings for all classes and methods
- Creates a markdown documentation file in `docs/`
- Includes usage examples and comprehensive API documentation

#### Generate Tests

```
/gentest src/task_service.py
```

This command:
- Analyzes the target Python file
- Generates pytest-compatible test functions
- Creates test fixtures for common scenarios
- Covers edge cases and error conditions
- Saves tests to `tests/test_<filename>.py`

#### Sync Documentation and Tests

```
/sync src/task_service.py
```

This command:
- Compares function signatures against existing documentation
- Checks test files for outdated function calls
- Flags stale items with `# STALE: reason` comments
- Reports all detected inconsistencies

### Example Workflow

```python
# 1. Write your code
# src/my_service.py
class MyService:
    def process_data(self, data, format="json"):
        # Your implementation
        pass

# 2. Generate documentation in Bob IDE
# /gendoc src/my_service.py
# → Creates docs/my_service.md with full API documentation

# 3. Generate tests in Bob IDE
# /gentest src/my_service.py
# → Creates tests/test_my_service.py with comprehensive test suite

# 4. Make code changes
def process_data(self, data, format="json", validate=True):  # Added parameter
    pass

# 5. Detect stale documentation
# /sync src/my_service.py
# → Flags outdated docs and tests with STALE comments
```

---

## Project Structure

```
dev-companion/
├── .bob/
│   └── commands/          # Custom Bob IDE commands
│       ├── gendoc.md      # Documentation generation command
│       ├── gentest.md     # Test generation command
│       ├── sync.md        # Staleness detection command
│       └── genreadme.md   # README generation command
├── bob_sessions/          # Bob task session reports (for judging)
│   ├── gendoc-output.md
│   ├── gendoc-consumption.png
│   ├── gentest-output.md
│   ├── gentest-consumption.png
│   ├── sync-output.md
│   └── sync-consumption.png
├── docs/                  # Auto-generated markdown documentation
│   └── task_service.md
├── src/                   # Source code being documented and tested
│   ├── __init__.py
│   ├── task_service.py    # Demo: Task management system
│   └── sample_service.py
├── tests/                 # Auto-generated test files
│   ├── __init__.py
│   └── test_task_service.py
├── AGENTS.md              # Project intent and Bob instructions
├── conftest.py            # Pytest configuration
├── LICENSE                # MIT License
├── main.py                # CLI entry point
└── README.md              # This file
```

---

## How IBM Bob is Used

dev-companion is built entirely around IBM Bob IDE's capabilities:

### Custom Commands

The project defines four custom Bob commands in `.bob/commands/`:

1. **gendoc** - Analyzes Python files and generates comprehensive documentation
2. **gentest** - Creates pytest-compatible test suites with fixtures
3. **sync** - Detects stale documentation and tests after code changes
4. **genreadme** - Generates project README files

### Agent Rules (AGENTS.md)

The `AGENTS.md` file provides Bob with:
- Project context and purpose
- Coding standards (Google-style docstrings, pytest format)
- Workflow instructions for each command
- Directory structure and conventions

### Session Reports

All Bob task executions are logged in `bob_sessions/` with:
- Complete output of generated documentation/tests
- Token consumption metrics
- Screenshots of the generation process

### Integration Pattern

```
Developer writes code
    ↓
Invokes Bob command (/gendoc, /gentest, /sync)
    ↓
Bob reads AGENTS.md for context
    ↓
Bob analyzes target file
    ↓
Bob generates output (docs/tests/reports)
    ↓
Developer reviews and commits
```

---

## Demo: Task Management System

The repository includes a fully functional task management system (`src/task_service.py`) that demonstrates dev-companion's capabilities:

### Features
- Create, read, update, and delete tasks
- Priority management (low, medium, high)
- Task completion tracking
- Subtask support with hierarchical IDs
- Filtering by priority and completion status
- Statistics generation

### Generated Artifacts

**Documentation** (`docs/task_service.md`):
- Complete API reference for `Task` and `TaskService` classes
- Usage examples for all methods
- Error handling documentation

**Tests** (`tests/test_task_service.py`):
- 461 lines of comprehensive test coverage
- Fixtures for common scenarios
- Tests for happy paths, edge cases, and error conditions
- 100% method coverage

### Running the Demo

```bash
# Run the interactive demo
python main.py demo

# Run just the tests
python main.py test

# Or use pytest directly
pytest tests/ -v
```

---

## Contributing

Contributions are welcome! Here's how to get started:

1. **Fork the repository**

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow Google-style docstring format
   - Add tests for new functionality
   - Update documentation as needed

4. **Run tests**
   ```bash
   pytest tests/ -v
   ```

5. **Use dev-companion on your code**
   ```
   /gendoc src/your_file.py
   /gentest src/your_file.py
   /sync src/your_file.py
   ```

6. **Commit and push**
   ```bash
   git commit -m "Add: your feature description"
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request**

### Coding Standards

- **Docstrings**: Google style format
- **Tests**: pytest-compatible, comprehensive coverage
- **Code Style**: PEP 8 compliant
- **Documentation**: Markdown format in `docs/`

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2026 Sena Folikumah

---

## Acknowledgments

- Built with [IBM Bob IDE](https://www.ibm.com/bob) - AI-powered development assistant
- Inspired by the need for automated, consistent documentation and testing
- Demo task management system showcases real-world application

---

## Support

For questions, issues, or feature requests:
- Open an issue on GitHub
- Check existing documentation in `docs/`
- Review Bob session reports in `bob_sessions/`

---

**Made with ❤️ and IBM Bob**