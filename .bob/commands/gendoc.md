# /gendoc

## Purpose
Generate Google-style docstrings for every class and function in the target file,
then produce a matching markdown documentation file in the docs/ folder.

## Instructions
1. Read the target file specified by the user
2. For every class, generate a class-level docstring covering:
   - What the class represents
   - Its constructor arguments and their types
   - Its key attributes
3. For every method and function, generate a docstring covering:
   - What it does in one sentence
   - Args: name, type, and description for each parameter
   - Returns: type and description
   - Raises: exception type and condition for each exception raised
4. Write the docstrings directly into the source file
5. Create a markdown file in docs/ named after the source file
   (e.g. src/task_service.py → docs/task_service.md)
6. The markdown file should contain:
   - A project title and one-paragraph overview
   - A section for each class with its docstring rendered
   - A section for each method with its docstring rendered
   - A usage example showing how to instantiate and call the main class

## Output confirmation
After completing, summarize:
- How many classes were documented
- How many functions/methods were documented
- The path to the generated markdown file