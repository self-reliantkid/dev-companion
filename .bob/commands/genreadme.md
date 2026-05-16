# /genreadme

## Purpose
Generate a professional, comprehensive README.md for the target repository
by analyzing the codebase, existing documentation, and project structure.

## Instructions
1. Scan the entire repository structure
2. Read all files in src/ to understand what the project does
3. Read any existing docs/ files for additional context
4. Read AGENTS.md for project intent
5. Generate a README.md in the root directory containing:
   - Project name and one-paragraph description
   - Badges section (Python version, license, tests passing)
   - Features list derived from actual code capabilities
   - Installation instructions
   - Usage examples with real code snippets from src/
   - Project structure tree
   - How IBM Bob is used in this project
   - Contributing guidelines
   - License section
6. The README must be based entirely on what actually exists in the codebase
   — do not invent features or capabilities that are not present
7. Overwrite any existing README.md

## Output confirmation
After completing, summarize:
- Sections generated
- Word count
- Any sections skipped and why