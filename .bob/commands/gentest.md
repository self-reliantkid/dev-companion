# /gentest

## Purpose
Generate a complete pytest test file for the target source file.

## Instructions
1. Read the target file specified by the user
2. Create a test file in tests/ named test_{original_filename}
   (e.g. src/task_service.py → tests/test_task_service.py)
3. For every class and function, generate test functions that cover:
   - Happy path: normal expected usage
   - Edge cases: empty inputs, boundary values
   - Error cases: every exception the function raises
4. Each test function must:
   - Have a descriptive name starting with test_
   - Include a one-line comment explaining what it tests
   - Use pytest conventions (assert statements, pytest.raises for exceptions)
5. Add a module-level docstring to the test file explaining what is being tested
6. Include a fixture for the main service class if applicable

## Output confirmation
After completing, summarize:
- How many test functions were generated
- Which functions have full coverage
- The path to the generated test file