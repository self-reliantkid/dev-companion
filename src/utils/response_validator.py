"""Response validation and quality scoring for generated outputs."""

import re
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of response validation with quality score and issues."""
    is_valid: bool
    quality_score: float  # 0.0 to 1.0
    issues: List[str]
    metrics: Dict[str, Any]
    suggestions: List[str]


class ResponseValidator:
    """Validates and scores generated responses for quality."""
    
    def __init__(self):
        self.min_quality_threshold = 0.7
    
    def validate_documentation(self, response: str, code: str, language: str) -> ValidationResult:
        """Validate documentation generation response.
        
        Args:
            response: Generated documentation output
            code: Original source code
            language: Programming language
            
        Returns:
            ValidationResult with quality score and issues
        """
        issues = []
        metrics = {}
        suggestions = []
        
        # Check for separator presence
        has_separator = "### MARKDOWN_DOCS ###" in response
        if not has_separator:
            issues.append("Missing '### MARKDOWN_DOCS ###' separator")
            suggestions.append("Ensure output includes both code and markdown sections")
        
        # Split into code and markdown sections
        if has_separator:
            parts = response.split("### MARKDOWN_DOCS ###")
            code_section = parts[0].strip()
            markdown_section = parts[1].strip() if len(parts) > 1 else ""
        else:
            code_section = response
            markdown_section = ""
        
        # Validate code section
        metrics['code_length'] = len(code_section)
        metrics['has_docstrings'] = self._count_docstrings(code_section, language)
        
        if metrics['has_docstrings'] == 0:
            issues.append("No docstrings found in code section")
            suggestions.append("Add docstrings to all functions and classes")
        
        # Count functions in original code
        func_count = self._count_functions(code, language)
        metrics['original_functions'] = func_count
        metrics['documented_functions'] = metrics['has_docstrings']
        
        if func_count > 0 and metrics['documented_functions'] < func_count:
            issues.append(f"Only {metrics['documented_functions']}/{func_count} functions documented")
            suggestions.append("Document all functions in the code")
        
        # Validate markdown section
        if markdown_section:
            metrics['markdown_length'] = len(markdown_section)
            metrics['has_headers'] = markdown_section.count('#')
            metrics['has_code_blocks'] = markdown_section.count('```')
            
            if metrics['markdown_length'] < 500:
                issues.append("Markdown documentation too short (< 500 chars)")
                suggestions.append("Expand markdown documentation with more details and examples")
            
            if metrics['has_headers'] < 2:
                issues.append("Insufficient section headers in markdown")
                suggestions.append("Add more structured sections (classes, functions, usage)")
        else:
            issues.append("No markdown documentation section found")
            suggestions.append("Generate comprehensive markdown API reference")
        
        # Calculate quality score
        quality_score = self._calculate_docs_quality_score(metrics, func_count)
        is_valid = quality_score >= self.min_quality_threshold and len(issues) <= 2
        
        return ValidationResult(
            is_valid=is_valid,
            quality_score=quality_score,
            issues=issues,
            metrics=metrics,
            suggestions=suggestions
        )
    
    def validate_tests(self, response: str, code: str, language: str) -> ValidationResult:
        """Validate test generation response.
        
        Args:
            response: Generated test code
            code: Original source code
            language: Programming language
            
        Returns:
            ValidationResult with quality score and issues
        """
        issues = []
        metrics = {}
        suggestions = []
        
        # Basic metrics
        metrics['test_length'] = len(response)
        metrics['test_count'] = self._count_test_functions(response, language)
        metrics['has_imports'] = self._has_test_imports(response, language)
        metrics['has_fixtures'] = 'fixture' in response.lower() or '@pytest.fixture' in response
        
        # Count functions in original code
        func_count = self._count_functions(code, language)
        metrics['original_functions'] = func_count
        
        # Validation checks
        if metrics['test_length'] < 1000:
            issues.append("Test file too short (< 1000 chars)")
            suggestions.append("Add more comprehensive test cases")
        
        if not metrics['has_imports']:
            issues.append("Missing test framework imports")
            suggestions.append(f"Add proper imports for {self._get_test_framework(language)}")
        
        if metrics['test_count'] == 0:
            issues.append("No test functions found")
            suggestions.append("Generate test functions with proper naming (test_*)")
        elif func_count > 0:
            expected_tests = func_count * 4  # Minimum 4 tests per function
            if metrics['test_count'] < expected_tests:
                issues.append(f"Insufficient test coverage: {metrics['test_count']}/{expected_tests} tests")
                suggestions.append("Add more test cases for edge cases and error conditions")
        
        # Check for test patterns
        has_happy_path = any(word in response.lower() for word in ['normal', 'valid', 'success', 'correct'])
        has_edge_cases = any(word in response.lower() for word in ['empty', 'none', 'null', 'zero', 'boundary'])
        has_error_tests = any(word in response.lower() for word in ['error', 'exception', 'invalid', 'raises'])
        
        metrics['has_happy_path'] = has_happy_path
        metrics['has_edge_cases'] = has_edge_cases
        metrics['has_error_tests'] = has_error_tests
        
        if not has_happy_path:
            issues.append("Missing happy path tests")
            suggestions.append("Add tests for normal expected behavior")
        
        if not has_edge_cases:
            issues.append("Missing edge case tests")
            suggestions.append("Add tests for empty inputs, boundaries, and special values")
        
        if not has_error_tests:
            issues.append("Missing error condition tests")
            suggestions.append("Add tests for exception handling and invalid inputs")
        
        # Calculate quality score
        quality_score = self._calculate_test_quality_score(metrics, func_count)
        is_valid = quality_score >= self.min_quality_threshold and len(issues) <= 3
        
        return ValidationResult(
            is_valid=is_valid,
            quality_score=quality_score,
            issues=issues,
            metrics=metrics,
            suggestions=suggestions
        )
    
    def validate_review(self, response: str, code: str) -> ValidationResult:
        """Validate code review response.
        
        Args:
            response: Generated code review
            code: Original source code
            
        Returns:
            ValidationResult with quality score and issues
        """
        issues = []
        metrics = {}
        suggestions = []
        
        # Basic metrics
        metrics['review_length'] = len(response)
        metrics['has_sections'] = response.count('##')
        metrics['has_severity'] = any(emoji in response for emoji in ['🔴', '🟡', '🟢'])
        metrics['issue_count'] = response.count('###')
        
        # Check for required sections
        required_sections = ['Executive Summary', 'Issues Found', 'Overall Health Score']
        for section in required_sections:
            if section not in response:
                issues.append(f"Missing required section: {section}")
        
        if metrics['review_length'] < 600:
            issues.append("Review too short (< 600 chars)")
            suggestions.append("Provide more detailed analysis and specific recommendations")
        
        if not metrics['has_severity']:
            issues.append("Missing severity indicators (🔴/🟡/🟢)")
            suggestions.append("Add severity ratings to all issues")
        
        if metrics['issue_count'] < 2:
            issues.append("Too few issues identified")
            suggestions.append("Provide more thorough code analysis")
        
        # Check for actionable recommendations
        has_code_snippets = '```' in response
        has_specific_fixes = any(word in response.lower() for word in ['change', 'replace', 'add', 'remove', 'refactor'])
        
        metrics['has_code_snippets'] = has_code_snippets
        metrics['has_specific_fixes'] = has_specific_fixes
        
        if not has_specific_fixes:
            issues.append("Missing specific, actionable recommendations")
            suggestions.append("Provide concrete code changes or refactoring suggestions")
        
        # Calculate quality score
        quality_score = self._calculate_review_quality_score(metrics)
        is_valid = quality_score >= self.min_quality_threshold and len(issues) <= 2
        
        return ValidationResult(
            is_valid=is_valid,
            quality_score=quality_score,
            issues=issues,
            metrics=metrics,
            suggestions=suggestions
        )
    
    # Helper methods
    
    def _count_docstrings(self, code: str, language: str) -> int:
        """Count docstrings in code."""
        if language.lower().startswith('python'):
            # Count triple-quoted strings after def/class
            pattern = r'(def|class)\s+\w+[^:]*:\s*"""'
            return len(re.findall(pattern, code))
        elif language.lower().startswith('javascript') or language.lower().startswith('typescript'):
            # Count JSDoc comments
            pattern = r'/\*\*[\s\S]*?\*/'
            return len(re.findall(pattern, code))
        elif language.lower().startswith('java'):
            # Count Javadoc comments
            pattern = r'/\*\*[\s\S]*?\*/'
            return len(re.findall(pattern, code))
        return 0
    
    def _count_functions(self, code: str, language: str) -> int:
        """Count functions/methods in code."""
        if language.lower().startswith('python'):
            pattern = r'\bdef\s+\w+'
        elif language.lower().startswith('javascript') or language.lower().startswith('typescript'):
            pattern = r'\bfunction\s+\w+|\w+\s*=\s*\([^)]*\)\s*=>'
        elif language.lower().startswith('java'):
            pattern = r'(public|private|protected)\s+\w+\s+\w+\s*\('
        elif language.lower().startswith('go'):
            pattern = r'\bfunc\s+\w+'
        else:
            pattern = r'\bdef\s+\w+|\bfunction\s+\w+'
        
        return len(re.findall(pattern, code))
    
    def _count_test_functions(self, code: str, language: str) -> int:
        """Count test functions in test code."""
        if language.lower().startswith('python'):
            pattern = r'\bdef\s+test_\w+'
        elif language.lower().startswith('javascript') or language.lower().startswith('typescript'):
            pattern = r'\b(test|it)\s*\('
        elif language.lower().startswith('java'):
            pattern = r'@Test'
        elif language.lower().startswith('go'):
            pattern = r'\bfunc\s+Test\w+'
        else:
            pattern = r'\bdef\s+test_\w+|\btest\s*\('
        
        return len(re.findall(pattern, code))
    
    def _has_test_imports(self, code: str, language: str) -> bool:
        """Check if test code has proper imports."""
        if language.lower().startswith('python'):
            return 'import pytest' in code or 'import unittest' in code
        elif language.lower().startswith('javascript') or language.lower().startswith('typescript'):
            return 'jest' in code.lower() or 'mocha' in code.lower()
        elif language.lower().startswith('java'):
            return 'import org.junit' in code
        elif language.lower().startswith('go'):
            return 'import "testing"' in code
        return True  # Assume valid for other languages
    
    def _get_test_framework(self, language: str) -> str:
        """Get expected test framework for language."""
        frameworks = {
            'python': 'pytest',
            'javascript': 'Jest',
            'typescript': 'Jest',
            'java': 'JUnit',
            'go': 'testing',
            'rust': 'built-in test',
            'ruby': 'RSpec'
        }
        return frameworks.get(language.lower().split()[0], 'appropriate test framework')
    
    def _calculate_docs_quality_score(self, metrics: Dict, func_count: int) -> float:
        """Calculate quality score for documentation (0.0 to 1.0)."""
        score = 0.0
        
        # Code section score (40%)
        if metrics.get('has_docstrings', 0) > 0:
            if func_count > 0:
                coverage = min(metrics['has_docstrings'] / func_count, 1.0)
                score += 0.4 * coverage
            else:
                score += 0.4
        
        # Markdown section score (40%)
        markdown_len = metrics.get('markdown_length', 0)
        if markdown_len >= 1000:
            score += 0.4
        elif markdown_len >= 500:
            score += 0.2
        
        # Structure score (20%)
        if metrics.get('has_headers', 0) >= 3:
            score += 0.1
        if metrics.get('has_code_blocks', 0) >= 2:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_test_quality_score(self, metrics: Dict, func_count: int) -> float:
        """Calculate quality score for tests (0.0 to 1.0)."""
        score = 0.0
        
        # Test count score (40%)
        test_count = metrics.get('test_count', 0)
        if func_count > 0:
            expected = func_count * 4
            coverage = min(test_count / expected, 1.0)
            score += 0.4 * coverage
        elif test_count >= 10:
            score += 0.4
        
        # Test patterns score (30%)
        if metrics.get('has_happy_path'):
            score += 0.1
        if metrics.get('has_edge_cases'):
            score += 0.1
        if metrics.get('has_error_tests'):
            score += 0.1
        
        # Structure score (30%)
        if metrics.get('has_imports'):
            score += 0.15
        if metrics.get('has_fixtures'):
            score += 0.15
        
        return min(score, 1.0)
    
    def _calculate_review_quality_score(self, metrics: Dict) -> float:
        """Calculate quality score for code review (0.0 to 1.0)."""
        score = 0.0
        
        # Length score (20%)
        review_len = metrics.get('review_length', 0)
        if review_len >= 1500:
            score += 0.2
        elif review_len >= 800:
            score += 0.1
        
        # Structure score (30%)
        if metrics.get('has_sections', 0) >= 4:
            score += 0.15
        if metrics.get('has_severity'):
            score += 0.15
        
        # Content score (50%)
        if metrics.get('issue_count', 0) >= 5:
            score += 0.2
        elif metrics.get('issue_count', 0) >= 3:
            score += 0.1
        
        if metrics.get('has_specific_fixes'):
            score += 0.15
        if metrics.get('has_code_snippets'):
            score += 0.15
        
        return min(score, 1.0)

# Made with Bob
