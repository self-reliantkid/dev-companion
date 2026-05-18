import os
import re
import time
import json
import requests
from typing import Generator
from dotenv import load_dotenv

load_dotenv()

# ─── IAM TOKEN CACHE ─────────────────────────────────────────────────────────
_token_cache: dict = {"token": None, "expires_at": 0.0}


def _get_iam_token() -> str:
    """Exchange IBM API key for a short-lived IAM bearer token.

    Caches the token and only refreshes when within 60 seconds of expiry.

    Returns:
        str: A valid IAM bearer token.

    Raises:
        ValueError: If WATSONX_API_KEY is not set.
        requests.HTTPError: If the IAM endpoint returns a non-2xx response.
    """
    api_key = os.getenv("WATSONX_API_KEY")
    if not api_key:
        raise ValueError(
            "WATSONX_API_KEY is not set. "
            "Add it to your .env file or Streamlit secrets."
        )
    if _token_cache["token"] and time.time() < _token_cache["expires_at"] - 60:
        return _token_cache["token"]

    resp = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": api_key,
        },
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()
    _token_cache["token"] = data["access_token"]
    _token_cache["expires_at"] = time.time() + data.get("expires_in", 3600)
    return _token_cache["token"]


# ─── LLAMA 3 CHAT TEMPLATE ───────────────────────────────────────────────────

def _build_prompt(system: str, user: str) -> str:
    """Wrap messages in the Llama 3 instruct chat template.

    Args:
        system: System prompt defining role, rules, and output format.
        user: User-turn message containing the code and task.

    Returns:
        str: Correctly formatted prompt string for the watsonx input field.
    """
    return (
        "<|begin_of_text|>"
        "<|start_header_id|>system<|end_header_id|>\n\n"
        f"{system.strip()}"
        "<|eot_id|>"
        "<|start_header_id|>user<|end_header_id|>\n\n"
        f"{user.strip()}"
        "<|eot_id|>"
        "<|start_header_id|>assistant<|end_header_id|>\n\n"
    )


# ─── LANGUAGE PROFILES ───────────────────────────────────────────────────────

_LANG_PROFILES = {
    "python": {
        "doc_style": "Google-style docstrings (Args, Returns, Raises, Example sections)",
        "test_framework": "pytest",
        "test_conventions": (
            "use fixtures for shared setup, parametrize for edge cases, "
            "assert with descriptive messages, group tests in classes by feature"
        ),
        "style_guide": "PEP 8",
        "import_style": "import pytest at the top; use `from <module> import <class>` pattern",
    },
    "javascript": {
        "doc_style": "JSDoc (/** @param {type} name - desc, @returns {type}, @throws {Error}, @example */)",
        "test_framework": "Jest",
        "test_conventions": (
            "use describe/it blocks, beforeEach for setup, "
            "expect().toBe / toEqual / toThrow, mock with jest.fn()"
        ),
        "style_guide": "Airbnb JavaScript Style Guide",
        "import_style": "use ES module imports: `import { x } from './module'`",
    },
    "typescript": {
        "doc_style": "TSDoc (/** @param name - desc, @returns desc, @throws {ErrorType} when */)",
        "test_framework": "Jest with ts-jest",
        "test_conventions": (
            "use describe/it blocks, type all test variables explicitly, "
            "mock with jest.fn<ReturnType, ArgsType>()"
        ),
        "style_guide": "TypeScript ESLint recommended + strict mode",
        "import_style": "use ES module imports with explicit type imports where needed",
    },
    "java": {
        "doc_style": "Javadoc (@param name description, @return description, @throws ExceptionType when)",
        "test_framework": "JUnit 5",
        "test_conventions": (
            "use @Test, @BeforeEach, @ParameterizedTest with @ValueSource or @CsvSource, "
            "assertThrows for exceptions, Assertions.assertEquals with message"
        ),
        "style_guide": "Google Java Style Guide",
        "import_style": "import org.junit.jupiter.api.*; import static org.junit.jupiter.api.Assertions.*",
    },
    "go": {
        "doc_style": (
            "Go doc comments: // FunctionName does X. starts with the function name, "
            "no special tags, package-level comment at top"
        ),
        "test_framework": "Go standard testing package",
        "test_conventions": (
            "use table-driven tests with []struct{ name, input, want }, "
            "t.Run for subtests, t.Errorf with descriptive format strings"
        ),
        "style_guide": "Effective Go + gofmt conventions",
        "import_style": 'import "testing"',
    },
    "rust": {
        "doc_style": (
            "Rustdoc triple-slash comments (/// Summary line. "
            "# Examples, # Errors, # Panics sections with code blocks)"
        ),
        "test_framework": "Rust built-in #[test] framework",
        "test_conventions": (
            "use #[cfg(test)] mod tests { use super::*; }, "
            "#[test] fn, assert_eq! with message, #[should_panic(expected=)] for panics"
        ),
        "style_guide": "Rust API Guidelines",
        "import_style": "use super::* inside the tests module",
    },
    "c#": {
        "doc_style": "XML doc comments (/// <summary>, <param name=>, <returns>, <exception cref=>)",
        "test_framework": "xUnit",
        "test_conventions": (
            "use [Fact] for single cases and [Theory] + [InlineData] for parametrized, "
            "Assert.Equal / Assert.Throws<T>, use IDisposable for cleanup"
        ),
        "style_guide": "Microsoft C# Coding Conventions",
        "import_style": "using Xunit;",
    },
    "ruby": {
        "doc_style": "YARD (@param name [Type] description, @return [Type], @raise [ExceptionClass], @example)",
        "test_framework": "RSpec",
        "test_conventions": (
            "use describe/context/it blocks, let for lazy setup, let! for eager, "
            "expect(subject).to eq(), shared_examples for common behaviour"
        ),
        "style_guide": "Ruby Style Guide (rubocop defaults)",
        "import_style": "require 'rspec'",
    },
}

_DEFAULT_PROFILE = {
    "doc_style": "standard documentation comments idiomatic to the language",
    "test_framework": "the standard test framework for the language",
    "test_conventions": "cover happy paths, edge cases, boundaries, and error conditions",
    "style_guide": "standard conventions for the language",
    "import_style": "standard imports for the test framework",
}


def _get_profile(language: str) -> dict:
    key = language.lower().split()[0].rstrip("(")
    return _LANG_PROFILES.get(key, _DEFAULT_PROFILE)


# ─── CORE: BLOCKING GENERATE ─────────────────────────────────────────────────

def _generate(prompt: str, max_tokens: int = 4096, temperature: float = 0.15, min_tokens: int = 500) -> str:
    """Call the watsonx.ai text generation endpoint (blocking, full response).

    Used as a fallback for contexts where streaming isn't supported.

    Args:
        prompt: Fully formatted Llama 3 chat-template prompt string.
        max_tokens: Maximum new tokens to generate.
        temperature: Sampling temperature.
        min_tokens: Minimum new tokens to generate (ensures substantial output).

    Returns:
        str: Complete generated text, stripped of whitespace.

    Raises:
        ValueError: If WATSONX_PROJECT_ID is not set.
        requests.HTTPError: If the endpoint returns a non-2xx response.
    """
    project_id = os.getenv("WATSONX_PROJECT_ID")
    if not project_id:
        raise ValueError(
            "WATSONX_PROJECT_ID is not set. "
            "Add it to your .env file or Streamlit secrets."
        )

    token = _get_iam_token()
    base_url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com").rstrip("/")

    resp = requests.post(
        f"{base_url}/ml/v1/text/generation?version=2023-05-29",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        json={
            "model_id": "meta-llama/llama-3-3-70b-instruct",
            "project_id": project_id,
            "input": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "min_new_tokens": min_tokens,
                "temperature": temperature,
                "top_p": 0.9,
                "repetition_penalty": 1.1,
                "stop_sequences": ["<|eot_id|>", "---END---"],
            },
        },
        timeout=180,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    return results[0].get("generated_text", "").strip() if results else ""


# ─── CORE: STREAMING GENERATE ────────────────────────────────────────────────

def _generate_stream(
    prompt: str, max_tokens: int = 4096, temperature: float = 0.15, min_tokens: int = 500
) -> Generator[str, None, None]:
    """Call the watsonx.ai streaming endpoint and yield text chunks as they arrive.

    Uses the /ml/v1/text/generation_stream SSE endpoint. Each server-sent event
    contains a JSON payload with a generated_text field holding the next token
    or token group. This function yields those chunks so callers can display
    output progressively rather than waiting for the full response.

    Args:
        prompt: Fully formatted Llama 3 chat-template prompt string.
        max_tokens: Maximum new tokens to generate.
        temperature: Sampling temperature.
        min_tokens: Minimum new tokens to generate (ensures substantial output).

    Yields:
        str: Text chunks as they are received from the model.

    Raises:
        ValueError: If WATSONX_PROJECT_ID is not set.
        requests.HTTPError: If the endpoint returns a non-2xx response.
    """
    project_id = os.getenv("WATSONX_PROJECT_ID")
    if not project_id:
        raise ValueError(
            "WATSONX_PROJECT_ID is not set. "
            "Add it to your .env file or Streamlit secrets."
        )

    token = _get_iam_token()
    base_url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com").rstrip("/")

    with requests.post(
        f"{base_url}/ml/v1/text/generation_stream?version=2023-05-29",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        },
        json={
            "model_id": "meta-llama/llama-3-3-70b-instruct",
            "project_id": project_id,
            "input": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "min_new_tokens": min_tokens,
                "temperature": temperature,
                "top_p": 0.9,
                "repetition_penalty": 1.1,
                "stop_sequences": ["<|eot_id|>", "---END---"],
            },
        },
        stream=True,
        timeout=180,
    ) as resp:
        resp.raise_for_status()
        for raw_line in resp.iter_lines():
            if not raw_line:
                continue
            line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else raw_line
            # SSE lines look like:  data: {"results": [{"generated_text": "..."}]}
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if payload in ("[DONE]", ""):
                continue
            try:
                chunk = json.loads(payload)
                results = chunk.get("results", [])
                if results:
                    text = results[0].get("generated_text", "")
                    if text:
                        yield text
            except json.JSONDecodeError:
                continue


# ─── FEATURE STREAMING WRAPPERS ──────────────────────────────────────────────
# Each public function now returns a generator via _generate_stream.
# The app uses st.write_stream() to render these directly.
# _build_*_prompt helpers keep the prompt logic separate from the streaming logic.

def _build_docs_prompt(code: str, language: str) -> tuple[str, str]:
    p = _get_profile(language)
    system = f"""You are a senior {language} engineer and technical writer with expertise in production-quality documentation.

Your task: add comprehensive documentation to {language} source code.

CRITICAL REQUIREMENTS (YOU MUST FOLLOW ALL):
1. Use {p['doc_style']} format EXCLUSIVELY — no other format is acceptable
2. Document EVERY SINGLE function, method, and class — skipping any is forbidden
3. For EACH function you MUST include:
   - One-line summary (what it does)
   - Args section: name, type, and detailed description for EVERY parameter
   - Returns section: type and detailed description of return value
   - Raises section: exception type and exact condition when raised
   - Example section: concrete usage example for non-trivial functions
4. Do NOT modify any logic, variable names, or code structure — ONLY add documentation
5. Follow {p['style_guide']} conventions strictly
6. Write detailed, professional documentation — minimum 2-3 sentences per function description

OUTPUT STRUCTURE (MANDATORY):
Part 1: Complete source file with documentation added to every function/class
Part 2: Exactly this separator line by itself: ### MARKDOWN_DOCS ###
Part 3: Comprehensive markdown API reference containing:
   - Module overview (3-4 sentences explaining purpose and main components)
   - One section per class with: description, attributes table, usage example
   - One section per public function with: signature, detailed description, parameter table, returns description, exceptions list, code example

QUALITY STANDARDS:
- Minimum 500 tokens of documentation
- Every function must have at least 3 sentences of description
- All parameters must be documented with types and descriptions
- Include realistic code examples that demonstrate actual usage"""

    user = f"""Add complete, comprehensive {p['doc_style']} documentation to every function and class in this {language} code.

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


def _build_tests_prompt(code: str, language: str) -> tuple[str, str]:
    p = _get_profile(language)
    system = f"""You are a senior {language} engineer specializing in test-driven development and comprehensive test coverage.

Your task: write a production-quality, comprehensive test suite using {p['test_framework']} for {language} code.

CRITICAL REQUIREMENTS (YOU MUST FOLLOW ALL):
1. Import setup: {p['import_style']}
2. Test conventions: {p['test_conventions']}
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

    user = f"""Write a complete, comprehensive {p['test_framework']} test suite for this {language} code.

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


def _build_review_prompt(code: str, language: str) -> tuple[str, str]:
    p = _get_profile(language)
    system = f"""You are a principal {language} engineer conducting a thorough code review. You follow {p['style_guide']}.

Be specific and actionable. Cite actual function names and line numbers.

REVIEW CATEGORIES:
1. CORRECTNESS — logic errors, off-by-one, wrong assumptions, missing null/None checks
2. SECURITY — injection risks, unvalidated input, insecure defaults, unsafe operations
3. PERFORMANCE — unnecessary loops, redundant computation, inefficient data structures
4. MAINTAINABILITY — complex functions, poor naming, magic numbers, deep nesting
5. ERROR HANDLING — unhandled exceptions, swallowed errors, missing validation
6. {language.upper()} IDIOMS — non-idiomatic patterns, missed language features, {p['style_guide']} violations

FOR EACH ISSUE:
- Location: function name or line number
- Severity: 🔴 HIGH / 🟡 MEDIUM / 🟢 LOW
- Problem: one clear sentence
- Fix: a concrete code snippet or specific instruction

OUTPUT (strict markdown):
## Executive Summary
## Issues Found (### 🔴 HIGH / ### 🟡 MEDIUM / ### 🟢 LOW)
## Positive Observations
## Overall Health Score (X/10)
## Top 3 Priority Fixes"""

    user = f"""Review this {language} code thoroughly.

```{language.lower().split()[0]}
{code}
```

Return the complete structured review:"""
    return system, user


def _build_sync_prompt(code: str, docs: str, tests: str, language: str) -> tuple[str, str]:
    system = f"""You are a code synchronisation checker for {language} projects.

CHECK FOR:
1. Functions in source with NO documentation
2. Functions in source with NO tests
3. Signatures that CHANGED but docs show old signature
4. Signatures that CHANGED but tests call old signature
5. Tests calling functions that NO LONGER EXIST
6. Documented functions that NO LONGER EXIST

FOR EACH STALE ITEM: Location, Type (MISSING_DOCS/MISSING_TESTS/STALE_DOCS/STALE_TESTS/GHOST_TEST/GHOST_DOC), Detail, Action.

OUTPUT (strict markdown):
## Sync Status [FULLY SYNCED ✅ or NEEDS UPDATE ⚠️]
## Summary (counts)
## Stale Items (detailed list)
## Recommended Actions (ordered)"""

    user = f"""Check this {language} codebase for sync issues.

### SOURCE
```{language.lower().split()[0]}
{code}
```
### DOCS
{docs}
### TESTS
```{language.lower().split()[0]}
{tests}
```

Return the complete sync report:"""
    return system, user


def _build_readme_prompt(code: str, structure: str, language: str) -> tuple[str, str]:
    structure_hint = f"\nProject structure:\n{structure}" if structure.strip() else ""
    system = f"""You are a technical writer creating professional open-source documentation for a {language} project.

RULES:
- Base EVERYTHING strictly on what exists in the provided code
- All code examples must use actual function/class names from the source
- Active voice, no filler phrases

REQUIRED SECTIONS: # ProjectName, ## Features, ## Installation, ## Usage, ## Project Structure, ## Contributing, ## License

OUTPUT: Raw markdown only. No wrapping fences. Start with # ProjectName."""

    user = f"""Generate a complete professional README.md for this {language} project.
{structure_hint}

Source code:
```{language.lower().split()[0]}
{code}
```

Return raw markdown README:"""
    return system, user


# ─── PUBLIC STREAMING API ────────────────────────────────────────────────────

def stream_docs(code: str, language: str = "Python") -> Generator[str, None, None]:
    """Stream documentation generation token by token.

    Args:
        code: Source code to document.
        language: Programming language name.

    Yields:
        str: Text chunks as they arrive from the model.
    """
    system, user = _build_docs_prompt(code, language)
    yield from _generate_stream(_build_prompt(system, user), max_tokens=8000, temperature=0.25, min_tokens=800)


def stream_tests(code: str, language: str = "Python") -> Generator[str, None, None]:
    """Stream test suite generation token by token.

    Args:
        code: Source code to generate tests for.
        language: Programming language name.

    Yields:
        str: Text chunks as they arrive from the model.
    """
    system, user = _build_tests_prompt(code, language)
    yield from _generate_stream(_build_prompt(system, user), max_tokens=8000, temperature=0.25, min_tokens=1000)


def stream_review(code: str, language: str = "Python") -> Generator[str, None, None]:
    """Stream code review generation token by token.

    Args:
        code: Source code to review.
        language: Programming language name.

    Yields:
        str: Text chunks as they arrive from the model.
    """
    system, user = _build_review_prompt(code, language)
    yield from _generate_stream(_build_prompt(system, user), max_tokens=5000, temperature=0.3, min_tokens=600)


def stream_sync(
    code: str, docs: str, tests: str, language: str = "Python"
) -> Generator[str, None, None]:
    """Stream sync check report token by token.

    Args:
        code: Current source code.
        docs: Existing documentation.
        tests: Existing test file.
        language: Programming language name.

    Yields:
        str: Text chunks as they arrive from the model.
    """
    system, user = _build_sync_prompt(code, docs, tests, language)
    yield from _generate_stream(_build_prompt(system, user), max_tokens=4000, temperature=0.15, min_tokens=500)


def stream_readme(
    code: str, structure: str = "", language: str = "Python"
) -> Generator[str, None, None]:
    """Stream README generation token by token.

    Args:
        code: Source code to base the README on.
        structure: Optional project structure description.
        language: Programming language name.

    Yields:
        str: Text chunks as they arrive from the model.
    """
    system, user = _build_readme_prompt(code, structure, language)
    yield from _generate_stream(_build_prompt(system, user), max_tokens=4000, temperature=0.25, min_tokens=600)


# ─── LEGACY BLOCKING API (kept for fallback) ─────────────────────────────────

def generate_docs(code: str, language: str = "Python") -> str:
    system, user = _build_docs_prompt(code, language)
    return _generate(_build_prompt(system, user), max_tokens=4096, temperature=0.15)

def generate_tests(code: str, language: str = "Python") -> str:
    system, user = _build_tests_prompt(code, language)
    return _generate(_build_prompt(system, user), max_tokens=4096, temperature=0.15)

def generate_review(code: str, language: str = "Python") -> str:
    system, user = _build_review_prompt(code, language)
    return _generate(_build_prompt(system, user), max_tokens=3000, temperature=0.3)

def sync_check(code: str, docs: str, tests: str, language: str = "Python") -> str:
    system, user = _build_sync_prompt(code, docs, tests, language)
    return _generate(_build_prompt(system, user), max_tokens=2500, temperature=0.1)

def generate_readme(code: str, structure: str = "", language: str = "Python") -> str:
    system, user = _build_readme_prompt(code, structure, language)
    result = _generate(_build_prompt(system, user), max_tokens=2500, temperature=0.2)
    return _clean_readme(result)


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def _clean_readme(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1:]
    if text.rstrip().endswith("```"):
        text = text.rstrip()[:-3].rstrip()
    h1_matches = [m.start() for m in re.finditer(r"^# ", text, re.MULTILINE)]
    if len(h1_matches) >= 2:
        text = text[: h1_matches[1]].rstrip()
    return text.strip()