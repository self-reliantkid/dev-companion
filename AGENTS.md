# AGENTS.md

## Project: dev-companion

### What this project does
dev-companion is an AI-powered documentation and test generation tool built
with IBM Bob. It reads a Python codebase, generates docstrings and markdown
documentation on demand, generates unit tests for functions, and detects when
code changes make existing docs or tests stale.

### Core workflow
1. /gendoc — generate documentation for a target file or function
2. /gentest — generate unit tests for a target file or function  
3. /sync — scan for stale docs/tests after code changes and flag them

### Stack
- Language: Python
- Testing: pytest
- Docs format: markdown + docstrings
- AI partner: IBM Bob IDE

### Key folders
- src/ — source code being documented and tested
- tests/ — auto-generated test files
- docs/ — auto-generated markdown documentation
- bob_sessions/ — Bob task session reports (required for judging)

### Bob instructions
- Always generate docstrings in Google style format
- Always generate pytest-compatible test functions
- When syncing, compare function signatures against existing docs and tests
- Flag stale items with a comment: # STALE: reason