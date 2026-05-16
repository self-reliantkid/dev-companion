# /review

## Purpose
Perform a comprehensive code quality review of the target file and produce
a structured review report saved to docs/review_report.md

## Instructions
1. Read the target file specified by the user
2. Analyze every class and function for the following:
   - Complexity: flag any function exceeding 10 lines of logic
   - Missing input validation: parameters that are not validated
   - Potential bugs: logic that could fail under edge cases
   - Code style: naming conventions, readability issues
   - Security: any obvious vulnerabilities or unsafe patterns
   - Performance: inefficient patterns or unnecessary operations
3. For each issue found, record:
   - File name and line number
   - Severity: HIGH / MEDIUM / LOW
   - Issue type: Complexity / Validation / Bug / Style / Security / Performance
   - Description of the issue
   - Suggested fix in plain English
4. Write a structured report to docs/review_report.md containing:
   - Executive summary: total issues by severity
   - Detailed findings table: line, severity, type, description, suggestion
   - Overall code health score out of 10
   - Top 3 priority fixes
5. Also print the executive summary to the terminal

## Output confirmation
After completing, summarize:
- Total issues found by severity
- Overall code health score
- Path to the generated report