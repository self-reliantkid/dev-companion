"""Advanced prompt template system with versioning and few-shot examples."""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class PromptVersion(Enum):
    """Prompt template versions for A/B testing."""
    V1_BASIC = "v1_basic"
    V2_ENHANCED = "v2_enhanced"
    V3_FEWSHOT = "v3_fewshot"


@dataclass
class FewShotExample:
    """Few-shot example for prompt engineering."""
    input_code: str
    expected_output: str
    description: str


class PromptTemplateManager:
    """Manages prompt templates with versioning and few-shot examples."""
    
    def __init__(self):
        self.current_version = PromptVersion.V2_ENHANCED
        self.few_shot_examples = self._load_few_shot_examples()
    
    def get_docs_prompt(
        self,
        code: str,
        language: str,
        doc_style: str,
        style_guide: str,
        version: Optional[PromptVersion] = None,
        include_examples: bool = True
    ) -> Tuple[str, str]:
        """Get documentation generation prompt with optional few-shot examples.
        
        Args:
            code: Source code to document
            language: Programming language
            doc_style: Documentation style (Google, JSDoc, etc.)
            style_guide: Style guide to follow
            version: Prompt version to use (defaults to current)
            include_examples: Whether to include few-shot examples
            
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        version = version or self.current_version
        
        if version == PromptVersion.V3_FEWSHOT and include_examples:
            return self._get_docs_prompt_with_examples(code, language, doc_style, style_guide)
        elif version == PromptVersion.V2_ENHANCED:
            return self._get_docs_prompt_enhanced(code, language, doc_style, style_guide)
        else:
            return self._get_docs_prompt_basic(code, language, doc_style, style_guide)
    
    def get_tests_prompt(
        self,
        code: str,
        language: str,
        test_framework: str,
        test_conventions: str,
        import_style: str,
        version: Optional[PromptVersion] = None,
        include_examples: bool = True
    ) -> Tuple[str, str]:
        """Get test generation prompt with optional few-shot examples.
        
        Args:
            code: Source code to test
            language: Programming language
            test_framework: Test framework to use
            test_conventions: Testing conventions
            import_style: Import style for tests
            version: Prompt version to use
            include_examples: Whether to include few-shot examples
            
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        version = version or self.current_version
        
        if version == PromptVersion.V3_FEWSHOT and include_examples:
            return self._get_tests_prompt_with_examples(
                code, language, test_framework, test_conventions, import_style
            )
        elif version == PromptVersion.V2_ENHANCED:
            return self._get_tests_prompt_enhanced(
                code, language, test_framework, test_conventions, import_style
            )
        else:
            return self._get_tests_prompt_basic(
                code, language, test_framework, test_conventions, import_style
            )
    
    def _get_docs_prompt_enhanced(
        self, code: str, language: str, doc_style: str, style_guide: str
    ) -> Tuple[str, str]:
        """Enhanced documentation prompt (V2)."""
        system = f"""You are a senior {language} engineer and technical writer with expertise in production-quality documentation.

Your task: add comprehensive documentation to {language} source code.

CRITICAL REQUIREMENTS (YOU MUST FOLLOW ALL):
1. Use {doc_style} format EXCLUSIVELY — no other format is acceptable
2. Document EVERY SINGLE function, method, and class — skipping any is forbidden
3. For EACH function you MUST include:
   - One-line summary (what it does)
   - Args section: name, type, and detailed description for EVERY parameter
   - Returns section: type and detailed description of return value
   - Raises section: exception type and exact condition when raised
   - Example section: concrete usage example for non-trivial functions
4. Do NOT modify any logic, variable names, or code structure — ONLY add documentation
5. Follow {style_guide} conventions strictly
6. Write detailed, professional documentation — minimum 2-3 sentences per function description

QUALITY STANDARDS:
- Minimum 500 tokens of documentation
- Every function must have at least 3 sentences of description
- All parameters must be documented with types and descriptions
- Include realistic code examples that demonstrate actual usage

OUTPUT STRUCTURE (MANDATORY):
Part 1: Complete source file with documentation added to every function/class
Part 2: Exactly this separator line by itself: ### MARKDOWN_DOCS ###
Part 3: Comprehensive markdown API reference containing:
   - Module overview (3-4 sentences explaining purpose and main components)
   - One section per class with: description, attributes table, usage example
   - One section per public function with: signature, detailed description, parameter table, returns description, exceptions list, code example"""

        user = f"""Add complete, comprehensive {doc_style} documentation to every function and class in this {language} code.

SOURCE CODE:
```{language.lower().split()[0]}
{code}
```

REQUIRED OUTPUT FORMAT:
1. Fully documented source code (with docstrings added to every function/class)
2. The separator: ### MARKDOWN_DOCS ###
3. Complete markdown API reference documentation

Begin generating the documented code now:"""
        
        return system, user
    
    def _get_docs_prompt_with_examples(
        self, code: str, language: str, doc_style: str, style_guide: str
    ) -> Tuple[str, str]:
        """Documentation prompt with few-shot examples (V3)."""
        examples = self.few_shot_examples.get("docs", {}).get(language.lower().split()[0], [])
        
        system = f"""You are a senior {language} engineer and technical writer with expertise in production-quality documentation.

Your task: add comprehensive documentation to {language} source code.

CRITICAL REQUIREMENTS (YOU MUST FOLLOW ALL):
1. Use {doc_style} format EXCLUSIVELY — no other format is acceptable
2. Document EVERY SINGLE function, method, and class — skipping any is forbidden
3. For EACH function you MUST include:
   - One-line summary (what it does)
   - Args section: name, type, and detailed description for EVERY parameter
   - Returns section: type and detailed description of return value
   - Raises section: exception type and exact condition when raised
   - Example section: concrete usage example for non-trivial functions
4. Do NOT modify any logic, variable names, or code structure — ONLY add documentation
5. Follow {style_guide} conventions strictly
6. Write detailed, professional documentation — minimum 2-3 sentences per function description

QUALITY STANDARDS:
- Minimum 500 tokens of documentation
- Every function must have at least 3 sentences of description
- All parameters must be documented with types and descriptions
- Include realistic code examples that demonstrate actual usage

OUTPUT STRUCTURE (MANDATORY):
Part 1: Complete source file with documentation added to every function/class
Part 2: Exactly this separator line by itself: ### MARKDOWN_DOCS ###
Part 3: Comprehensive markdown API reference"""

        # Add few-shot examples if available
        if examples:
            system += "\n\nEXAMPLES OF CORRECT DOCUMENTATION:\n\n"
            for i, example in enumerate(examples[:2], 1):  # Limit to 2 examples
                system += f"Example {i}: {example.description}\n"
                system += f"Input:\n```{language.lower().split()[0]}\n{example.input_code}\n```\n\n"
                system += f"Expected Output:\n{example.expected_output}\n\n"

        user = f"""Add complete, comprehensive {doc_style} documentation to every function and class in this {language} code.

SOURCE CODE:
```{language.lower().split()[0]}
{code}
```

REQUIRED OUTPUT FORMAT:
1. Fully documented source code (with docstrings added to every function/class)
2. The separator: ### MARKDOWN_DOCS ###
3. Complete markdown API reference documentation

Begin generating the documented code now:"""
        
        return system, user
    
    def _get_docs_prompt_basic(
        self, code: str, language: str, doc_style: str, style_guide: str
    ) -> Tuple[str, str]:
        """Basic documentation prompt (V1)."""
        system = f"""You are a senior {language} engineer and technical writer.

Add comprehensive documentation to {language} source code using {doc_style}.

RULES:
- Document every function, method, and class
- Include Args, Returns, Raises, and Example sections
- Follow {style_guide}

OUTPUT:
1. Documented source code
2. ### MARKDOWN_DOCS ###
3. Markdown API reference"""

        user = f"""Document this {language} code:

```{language.lower().split()[0]}
{code}
```"""
        
        return system, user
    
    def _get_tests_prompt_enhanced(
        self, code: str, language: str, test_framework: str, test_conventions: str, import_style: str
    ) -> Tuple[str, str]:
        """Enhanced test generation prompt (V2)."""
        system = f"""You are a senior {language} engineer specializing in test-driven development and comprehensive test coverage.

Your task: write a production-quality, comprehensive test suite using {test_framework} for {language} code.

CRITICAL REQUIREMENTS (YOU MUST FOLLOW ALL):
1. Import setup: {import_style}
2. Test conventions: {test_conventions}
3. Coverage requirements - For EVERY public function/method you MUST create tests for:
   a) Happy path — normal expected inputs with correct outputs (minimum 2 test cases)
   b) Edge cases — empty input, zero, None/null, empty string, empty list/array, whitespace-only strings
   c) Boundary values — minimum values, maximum values, single-element collections, large inputs
   d) Error conditions — invalid types, out-of-range values, all expected exceptions with proper assertions
4. Test naming: Use descriptive names that read as sentences (e.g., test_add_two_positive_numbers_returns_correct_sum)
5. Test independence: Every test MUST be self-contained and runnable independently
6. Real implementations: Write COMPLETE, RUNNABLE tests — no placeholder comments, no empty test bodies, no TODO markers
7. Fixtures: Create fixtures for common setup/teardown operations
8. Assertions: Use descriptive assertion messages explaining what is being tested

QUALITY STANDARDS:
- Minimum 1000 tokens of test code
- At least 4-6 test functions per public method/function
- Include module-level docstring explaining what is being tested
- Group related tests using test classes or describe blocks
- Add comments explaining complex test scenarios
- Use parametrized tests for similar test cases with different inputs

OUTPUT FORMAT (MANDATORY):
- Complete, runnable test file with all imports
- NO markdown code fences around the entire file
- NO explanatory text before or after the code
- Start directly with imports and end with the last test function"""

        user = f"""Write a complete, comprehensive {test_framework} test suite for this {language} code.

SOURCE CODE TO TEST:
```{language.lower().split()[0]}
{code}
```

REQUIREMENTS:
- Test EVERY public function and method
- Include happy path, edge cases, boundaries, and error conditions
- Minimum 4-6 tests per function
- Use fixtures for setup
- Write complete, runnable code

Begin generating the complete test file now:"""
        
        return system, user
    
    def _get_tests_prompt_with_examples(
        self, code: str, language: str, test_framework: str, test_conventions: str, import_style: str
    ) -> Tuple[str, str]:
        """Test generation prompt with few-shot examples (V3)."""
        examples = self.few_shot_examples.get("tests", {}).get(language.lower().split()[0], [])
        
        system = self._get_tests_prompt_enhanced(
            code, language, test_framework, test_conventions, import_style
        )[0]
        
        # Add few-shot examples if available
        if examples:
            system += "\n\nEXAMPLES OF CORRECT TEST SUITES:\n\n"
            for i, example in enumerate(examples[:2], 1):
                system += f"Example {i}: {example.description}\n"
                system += f"Code to test:\n```{language.lower().split()[0]}\n{example.input_code}\n```\n\n"
                system += f"Expected test suite:\n```{language.lower().split()[0]}\n{example.expected_output}\n```\n\n"
        
        user = self._get_tests_prompt_enhanced(
            code, language, test_framework, test_conventions, import_style
        )[1]
        
        return system, user
    
    def _get_tests_prompt_basic(
        self, code: str, language: str, test_framework: str, test_conventions: str, import_style: str
    ) -> Tuple[str, str]:
        """Basic test generation prompt (V1)."""
        system = f"""You are a {language} engineer specializing in testing.

Write a {test_framework} test suite for {language} code.

RULES:
- {import_style}
- {test_conventions}
- Cover happy path, edge cases, and errors
- Write real, runnable tests

OUTPUT: Complete test file only."""

        user = f"""Write tests for this {language} code:

```{language.lower().split()[0]}
{code}
```"""
        
        return system, user
    
    def _load_few_shot_examples(self) -> Dict[str, Dict[str, List[FewShotExample]]]:
        """Load few-shot examples for different languages and tasks."""
        return {
            "docs": {
                "python": [
                    FewShotExample(
                        input_code="""def calculate_total(items, tax_rate=0.1):
    total = sum(items)
    return total * (1 + tax_rate)""",
                        expected_output='''def calculate_total(items, tax_rate=0.1):
    """Calculate the total cost of items including tax.
    
    This function sums all item prices and applies the specified tax rate
    to calculate the final total cost. The tax rate defaults to 10% if not
    specified.
    
    Args:
        items (list): List of item prices as floats or integers.
        tax_rate (float, optional): Tax rate as a decimal (e.g., 0.1 for 10%).
            Defaults to 0.1.
    
    Returns:
        float: Total cost including tax, rounded to 2 decimal places.
    
    Raises:
        TypeError: If items is not iterable or contains non-numeric values.
        ValueError: If tax_rate is negative.
    
    Example:
        >>> calculate_total([10.0, 20.0, 30.0])
        66.0
        >>> calculate_total([100], tax_rate=0.2)
        120.0
    """
    total = sum(items)
    return total * (1 + tax_rate)''',
                        description="Simple function with default parameter"
                    )
                ]
            },
            "tests": {
                "python": [
                    FewShotExample(
                        input_code="""def add(a, b):
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Arguments must be numbers")
    return a + b""",
                        expected_output='''import pytest

def test_add_two_positive_numbers_returns_correct_sum():
    """Test adding two positive numbers."""
    assert add(2, 3) == 5
    assert add(10, 20) == 30

def test_add_negative_numbers_returns_correct_sum():
    """Test adding negative numbers."""
    assert add(-5, -3) == -8
    assert add(-10, 5) == -5

def test_add_zero_returns_other_number():
    """Test adding zero."""
    assert add(0, 5) == 5
    assert add(10, 0) == 10

def test_add_floats_returns_correct_sum():
    """Test adding floating point numbers."""
    assert add(1.5, 2.5) == 4.0
    assert add(0.1, 0.2) == pytest.approx(0.3)

def test_add_with_non_numeric_raises_type_error():
    """Test that non-numeric arguments raise TypeError."""
    with pytest.raises(TypeError, match="Arguments must be numbers"):
        add("1", 2)
    with pytest.raises(TypeError, match="Arguments must be numbers"):
        add(1, "2")
    with pytest.raises(TypeError, match="Arguments must be numbers"):
        add(None, 5)''',
                        description="Comprehensive test suite for simple add function"
                    )
                ]
            }
        }


# Global template manager instance
_global_template_manager: Optional[PromptTemplateManager] = None


def get_template_manager() -> PromptTemplateManager:
    """Get or create the global template manager instance.
    
    Returns:
        PromptTemplateManager instance
    """
    global _global_template_manager
    if _global_template_manager is None:
        _global_template_manager = PromptTemplateManager()
    return _global_template_manager

# Made with Bob
