# /sync

## Purpose
Detect stale documentation and tests after code changes and flag them.

## Instructions
1. Read every file in src/
2. For each function and class found, check:
   - Does a docstring exist in the source file?
   - Does the function signature match what is described in docs/?
   - Does a corresponding test exist in tests/?
3. Flag any item that is stale by adding a comment directly above it:
   # STALE: <reason>
   Examples of stale reasons:
   - "function signature changed, docstring not updated"
   - "no test found for this function"
   - "new parameter added but not documented"
4. Generate a sync report printed to the terminal listing:
   - Total functions scanned
   - Number of stale items found
   - Each stale item with its file, line number, and reason

## Output confirmation
After completing, print the full sync report.