import os
import re
import time
import requests
from dotenv import load_dotenv

load_dotenv()

# ─── IAM TOKEN CACHE ─────────────────────────────────────────────────────────
_token_cache: dict = {"token": None, "expires_at": 0.0}


def _get_iam_token() -> str:
    """Exchange IBM API key for a short-lived IAM bearer token.

    Caches the token and only refreshes when within 60 seconds of expiry,
    avoiding a redundant auth roundtrip on every generate() call.

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
    """Wrap system and user messages in the Llama 3 instruct chat template.

    llama-3-3-70b-instruct expects this exact format. Sending a raw string
    bypasses the instruction tuning and produces noticeably weaker output.

    Args:
        system: System prompt defining role, rules, and output format.
        user: User-turn message containing the code and specific task.

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

# Per-language doc style, test framework, and conventions.
# Injected into prompts so the model produces genuinely idiomatic output
# rather than generic Python-flavoured answers for every language.
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
        "style_guide": "Rust API Guidelines (https://rust-lang.github.io/api-guidelines/)",
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
        "import_style": "using Xunit; using Xunit.Abstractions;",
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
    """Look up the language profile for prompt injection.

    Args:
        language: Language string as detected or provided
                  (e.g. "Python", "JavaScript (React)", "TypeScript").

    Returns:
        dict: Language profile with doc_style, test_framework, etc.
    """
    key = language.lower().split()[0].rstrip("(")
    return _LANG_PROFILES.get(key, _DEFAULT_PROFILE)


# ─── CORE GENERATE ───────────────────────────────────────────────────────────

def _generate(prompt: str, max_tokens: int = 4096, temperature: float = 0.15) -> str:
    """Call the watsonx.ai text generation REST endpoint.

    Args:
        prompt: Fully formatted Llama 3 chat-template prompt string.
        max_tokens: Maximum new tokens. 4096 default prevents mid-output
                    truncation on large files (old default of 3000 was too low).
        temperature: Sampling temperature. 0.1-0.2 for code, 0.3 for prose.

    Returns:
        str: Generated text, stripped of leading/trailing whitespace.

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
                "temperature": temperature,
                # repetition_penalty removed — it penalised re-use of variable
                # and function names, which are legitimately repeated in code.
                "stop_sequences": ["<|eot_id|>", "---END---"],
            },
        },
        timeout=120,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    return results[0].get("generated_text", "").strip() if results else ""


# ─── FEATURE FUNCTIONS ───────────────────────────────────────────────────────

def generate_docs(code: str, language: str = "Python") -> str:
    """Generate inline documentation comments and a markdown API reference.

    Produces language-idiomatic doc comments inserted directly into the code,
    plus a structured markdown reference section delimited by ### MARKDOWN_DOCS ###.

    Args:
        code: Source code string to document.
        language: Programming language name (e.g. "Python", "TypeScript").

    Returns:
        str: Documented source code optionally followed by ### MARKDOWN_DOCS ###
             and a markdown API reference.
    """
    p = _get_profile(language)

    system = f"""You are a senior {language} engineer and technical writer with expertise in production-quality documentation.

Your task: add comprehensive documentation to {language} source code.

RULES:
- Use {p['doc_style']} — no other format
- Document EVERY function, method, and class — do not skip any
- For each function include: one-line summary, Args (name, type, description), Returns (type + description), Raises (exception type + when), and an Example for non-obvious functions
- Do NOT change any logic, variable names, or structure — add documentation only
- Do NOT add comments inside function bodies unless explaining genuinely complex logic
- Follow {p['style_guide']} throughout

OUTPUT STRUCTURE:
1. The complete source file with documentation added
2. Exactly this line by itself: ### MARKDOWN_DOCS ###
3. A markdown API reference with:
   - Module overview (2-3 sentences)
   - One section per class (description + attributes table)
   - One section per public function (signature, description, parameter table, returns, exceptions, example)"""

    user = f"""Add complete {p['doc_style']} documentation to every function and class in this {language} code.

```{language.lower().split()[0]}
{code}
```

Return: documented source code → ### MARKDOWN_DOCS ### → markdown API reference."""

    return _generate(_build_prompt(system, user), max_tokens=4096, temperature=0.15)


def generate_tests(code: str, language: str = "Python") -> str:
    """Generate a comprehensive, immediately runnable test suite.

    Covers happy paths, edge cases, boundary conditions, and error handling
    using the idiomatic test framework for the target language.

    Args:
        code: Source code string to generate tests for.
        language: Programming language name.

    Returns:
        str: A complete, runnable test file with no placeholders or stubs.
    """
    p = _get_profile(language)

    system = f"""You are a senior {language} engineer specialising in test-driven development.

Your task: write a production-quality test suite using {p['test_framework']} for {language} code.

RULES:
- {p['import_style']}
- {p['test_conventions']}
- Cover ALL of the following for every public function/method:
  1. Happy path — normal expected input and output
  2. Edge cases — empty input, zero, None/null, empty string, empty list/array
  3. Boundary values — min/max values, single-element collections, very large inputs
  4. Error conditions — invalid types, out-of-range values, expected exceptions
- Test names must read as sentences: test_add_two_positive_numbers_returns_correct_sum
- Add a one-line comment above each test group: # --- Tests for ClassName.method_name ---
- Every test must be self-contained and runnable independently
- Write REAL tests — no "# TODO: add test here" or empty test bodies
- Do NOT test private/internal methods directly

OUTPUT: The complete test file only. No explanation. No markdown fences wrapping the whole file."""

    user = f"""Write a complete {p['test_framework']} test suite for this {language} code.

Every public function and method needs tests for happy paths, edge cases, boundaries, and errors.

```{language.lower().split()[0]}
{code}
```

Return the complete runnable test file:"""

    return _generate(_build_prompt(system, user), max_tokens=4096, temperature=0.15)


def generate_review(code: str, language: str = "Python") -> str:
    """Perform a structured senior-level code review.

    Analyses for correctness, security, performance, maintainability, error
    handling, and language idioms. Returns a structured markdown report with
    severity ratings and concrete fix suggestions.

    Args:
        code: Source code string to review.
        language: Programming language name.

    Returns:
        str: Markdown review report with categorised issues and health score.
    """
    p = _get_profile(language)

    system = f"""You are a principal {language} engineer conducting a thorough code review. You follow {p['style_guide']}.

Be specific and actionable. Cite actual function names and line numbers. Do not pad with generic praise.

REVIEW CATEGORIES:
1. CORRECTNESS — logic errors, off-by-one errors, wrong assumptions, missing null/None checks
2. SECURITY — injection risks, unvalidated input, insecure defaults, unsafe operations
3. PERFORMANCE — unnecessary loops, redundant computation, inefficient data structures, missing caching
4. MAINTAINABILITY — complex functions, poor naming, magic numbers, deep nesting, missing abstractions
5. ERROR HANDLING — unhandled exceptions, swallowed errors, missing validation, unhelpful messages
6. {language.upper()} IDIOMS — non-idiomatic patterns, missed language features, {p['style_guide']} violations

FOR EACH ISSUE:
- Location: function name or line number
- Severity: 🔴 HIGH / 🟡 MEDIUM / 🟢 LOW
- Category: one of the six above
- Problem: one clear sentence
- Fix: a concrete code snippet or specific instruction

OUTPUT (strict markdown):
## Executive Summary
[2-3 sentence honest overall assessment]

## Issues Found

### 🔴 HIGH Severity
[issues or "None found"]

### 🟡 MEDIUM Severity
[issues or "None found"]

### 🟢 LOW Severity
[issues or "None found"]

## Positive Observations
[genuine specific strengths — no generic filler]

## Overall Health Score
[X/10 — one sentence justification]

## Top 3 Priority Fixes
1. [most critical fix]
2. [second]
3. [third]"""

    user = f"""Review this {language} code. Be specific — cite actual function names and line numbers.

```{language.lower().split()[0]}
{code}
```

Return the complete structured review:"""

    return _generate(_build_prompt(system, user), max_tokens=3000, temperature=0.3)


def sync_check(code: str, docs: str, tests: str, language: str = "Python") -> str:
    """Compare source code against its existing documentation and test suite.

    Finds mismatches: changed signatures without updated docs/tests, functions
    without documentation or tests, and tests/docs referencing deleted functions.

    Args:
        code: Current source code string.
        docs: Existing documentation to compare against.
        tests: Existing test file to compare against.
        language: Programming language name.

    Returns:
        str: Markdown sync report with status, issue list, and recommended actions.
    """
    system = f"""You are a code synchronisation checker for {language} projects.

Your task: compare source code against its documentation and tests to find every mismatch.

CHECK FOR:
1. Functions/methods in source with NO corresponding documentation
2. Functions/methods in source with NO corresponding tests
3. Signatures that CHANGED (added/removed/renamed parameters) but docs show the old signature
4. Signatures that CHANGED but tests still call the old signature
5. Tests calling functions that NO LONGER EXIST in source
6. Documented functions that NO LONGER EXIST in source

FOR EACH STALE ITEM:
- Location: function/method name
- Type: MISSING_DOCS / MISSING_TESTS / STALE_DOCS / STALE_TESTS / GHOST_TEST / GHOST_DOC
- Detail: specific description of what is out of sync
- Action: exact fix needed

OUTPUT (strict markdown):
## Sync Status
[FULLY SYNCED ✅ or NEEDS UPDATE ⚠️]

## Summary
- Functions/methods scanned: N
- Stale items found: N
- Missing documentation: N
- Missing tests: N
- Outdated references: N

## Stale Items
[detailed list with Type, Location, Detail, Action for each]

## Recommended Actions
[ordered list, most to least critical]"""

    user = f"""Check this {language} codebase for sync issues.

### SOURCE CODE
```{language.lower().split()[0]}
{code}
```

### EXISTING DOCUMENTATION
{docs}

### EXISTING TESTS
```{language.lower().split()[0]}
{tests}
```

Return the complete sync report:"""

    return _generate(_build_prompt(system, user), max_tokens=2500, temperature=0.1)


def generate_readme(code: str, structure: str = "", language: str = "Python") -> str:
    """Generate a professional README.md strictly from the source code.

    Args:
        code: Source code string to base the README on.
        structure: Optional project structure string. Inferred from code if blank.
        language: Programming language name.

    Returns:
        str: Clean raw markdown README without wrapping code fences.
    """
    structure_hint = (
        f"\nProject structure provided:\n{structure}" if structure.strip() else ""
    )

    system = f"""You are a technical writer creating professional open-source documentation for a {language} project.

RULES:
- Base EVERYTHING strictly on what exists in the provided code — do not invent features or examples
- All code examples must use actual function/class names from the source
- Write in clear, confident, active voice: "Generates docstrings" not "Can be used to generate"
- No filler: "This project aims to..." → just say what it does

REQUIRED SECTIONS (all of them):
# ProjectName
[one-line description]

## Features
[bullet list — only real features visible in the code]

## Installation
[exact commands based on actual language and dependencies]

## Usage
[real working examples using actual names from the source]

## Project Structure
[based on what's provided]

## Contributing
[standard contributing guidelines]

## License
[MIT unless otherwise indicated]

OUTPUT: Raw markdown only. No wrapping fences. Start directly with # ProjectName."""

    user = f"""Generate a complete professional README.md for this {language} project.
{structure_hint}

Source code:
```{language.lower().split()[0]}
{code}
```

Return raw markdown README:"""

    result = _generate(_build_prompt(system, user), max_tokens=2500, temperature=0.2)
    return _clean_readme(result)


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def _clean_readme(text: str) -> str:
    """Strip wrapping code fences and remove duplicated README content.

    Args:
        text: Raw string returned by the model.

    Returns:
        str: Clean markdown string ready to display or download.
    """
    text = text.strip()

    # Strip opening fence (```markdown, ```md, or plain ```)
    if text.startswith("```"):
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1:]

    # Strip closing fence
    if text.rstrip().endswith("```"):
        text = text.rstrip()[:-3].rstrip()

    # If model repeated itself (two top-level # headings), keep only first block
    h1_matches = [m.start() for m in re.finditer(r"^# ", text, re.MULTILINE)]
    if len(h1_matches) >= 2:
        text = text[: h1_matches[1]].rstrip()

    return text.strip()