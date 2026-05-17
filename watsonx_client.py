import os
import time
import re
import requests
from dotenv import load_dotenv

load_dotenv()

# ─── IAM TOKEN CACHE ─────────────────────────────────────────────────────────
# Tokens are valid for 1 hour. We cache and reuse to avoid a redundant auth
# roundtrip on every single generate() call.
_token_cache: dict = {"token": None, "expires_at": 0.0}


def _get_iam_token() -> str:
    """Exchange IBM API key for a short-lived IAM bearer token.

    Caches the token in module-level state and only refreshes when it is
    within 60 seconds of expiry.

    Returns:
        str: A valid IAM bearer token string.

    Raises:
        requests.HTTPError: If the IAM endpoint returns a non-2xx response.
        ValueError: If WATSONX_API_KEY is not set in the environment.
    """
    api_key = os.getenv("WATSONX_API_KEY")
    if not api_key:
        raise ValueError(
            "WATSONX_API_KEY is not set. "
            "Add it to your .env file or Streamlit secrets."
        )

    # Return cached token if still valid (with 60-second buffer)
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
    # IBM tokens expire in 3600s; store the absolute expiry time
    _token_cache["expires_at"] = time.time() + data.get("expires_in", 3600)
    return _token_cache["token"]


def _generate(prompt: str, max_tokens: int = 3000) -> str:
    """Call the watsonx.ai text generation REST endpoint.

    Args:
        prompt: The full prompt string to send to the model.
        max_tokens: Maximum number of new tokens to generate.

    Returns:
        str: The generated text, stripped of leading/trailing whitespace.

    Raises:
        ValueError: If WATSONX_PROJECT_ID is not set.
        requests.HTTPError: If the watsonx endpoint returns a non-2xx response.
    """
    project_id = os.getenv("WATSONX_PROJECT_ID")
    if not project_id:
        raise ValueError(
            "WATSONX_PROJECT_ID is not set. "
            "Add it to your .env file or Streamlit secrets."
        )

    token = _get_iam_token()
    base_url = os.getenv(
        "WATSONX_URL", "https://us-south.ml.cloud.ibm.com"
    ).rstrip("/")

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
                "temperature": 0.2,
                "repetition_penalty": 1.05,
                # NOTE: "```markdown" was intentionally removed — it caused the
                # model to stop mid-response whenever it tried to open a
                # markdown code fence, silently truncating output.
                "stop_sequences": ["---END---"],
            },
        },
        timeout=90,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    return results[0].get("generated_text", "").strip() if results else ""


# ─── FEATURE FUNCTIONS ───────────────────────────────────────────────────────

def generate_docs(code: str, language: str = "code") -> str:
    """Generate inline documentation comments and a markdown reference for code.

    Args:
        code: Source code string to document.
        language: Programming language name (e.g. "Python", "JavaScript").

    Returns:
        str: Fully documented source code, optionally followed by a markdown
             reference section delimited by ``### MARKDOWN_DOCS ###``.
    """
    prompt = f"""You are an expert {language} developer.

Generate idiomatic documentation comments for every class, function, and method in this {language} code.
Use the standard documentation style for {language} (e.g. JSDoc for JavaScript, Google-style docstrings for Python, Javadoc for Java).
Add the comments directly into the code and return the complete updated file.

Also generate a markdown documentation summary at the end after a line that says:
### MARKDOWN_DOCS ###

Code:
{code}

Return the fully documented code followed by the markdown docs."""
    return _generate(prompt)


def generate_tests(code: str, language: str = "code") -> str:
    """Generate a complete test suite for the given source code.

    Args:
        code: Source code string to test.
        language: Programming language name.

    Returns:
        str: A complete test file covering happy paths, edge cases, and
             error conditions using the idiomatic test framework for the
             given language.
    """
    framework_hints = {
        "python": "pytest",
        "javascript": "Jest",
        "typescript": "Jest",
        "java": "JUnit 5",
        "go": "the standard testing package",
        "rust": "Rust's built-in #[test] framework",
        "c#": "xUnit",
        "ruby": "RSpec",
    }
    framework = framework_hints.get(
        language.lower().split()[0], "an appropriate test framework"
    )

    prompt = f"""You are an expert {language} developer specializing in testing.

Generate a complete test suite using {framework} for this {language} code.
Cover happy paths, edge cases, and all exceptions/error cases.
Use fixtures or setup/teardown where appropriate.
Return only the test file content, no explanation.

Code:
{code}

Return complete test file:"""
    return _generate(prompt)


def generate_review(code: str, language: str = "code") -> str:
    """Perform a structured code review of the given source code.

    Args:
        code: Source code string to review.
        language: Programming language name.

    Returns:
        str: A markdown-formatted review report covering complexity,
             security, performance, style issues, and an overall health
             score with top priority fixes.
    """
    prompt = f"""You are a senior {language} code reviewer.

Review this {language} code and provide a structured report covering:
- Complexity issues
- Missing input validation
- Potential bugs
- Code style issues (using idiomatic {language} conventions)
- Security concerns
- Performance issues

For each issue include: location (line number or function name), severity (HIGH/MEDIUM/LOW), type, description, and suggested fix.
End with an overall code health score out of 10 and the top 3 priority fixes.

Code:
{code}

Return structured review report in markdown:"""
    return _generate(prompt)


def sync_check(code: str, docs: str, tests: str, language: str = "code") -> str:
    """Compare source code against its existing documentation and tests.

    Args:
        code: Current source code string.
        docs: Existing documentation string to compare against.
        tests: Existing test file string to compare against.
        language: Programming language name.

    Returns:
        str: A markdown sync report indicating whether everything is in sync
             or listing stale items with recommended actions.
    """
    prompt = f"""You are a code synchronization checker for {language} codebases.

Compare this source code against its documentation and tests.
Identify any mismatches where:
- Function/method signatures changed but docs not updated
- New parameters exist without documentation
- Functions/methods exist without corresponding tests
- Tests reference functions that no longer exist

Source code:
{code}

Current documentation:
{docs}

Current tests:
{tests}

Return a sync report in markdown with:
- Status badge: FULLY SYNCED or SYNC NEEDED
- Total functions/methods scanned
- Stale items found (location, function name, reason)
- Recommended actions"""
    return _generate(prompt)


def generate_readme(code: str, structure: str = "", language: str = "code") -> str:
    """Generate a professional README.md from source code.

    Args:
        code: Source code string to base the README on.
        structure: Optional project structure description. If blank, the
                   model infers it from the code.
        language: Programming language name.

    Returns:
        str: A clean, raw markdown README string (no wrapping code fences).
    """
    structure_section = (
        f"\nProject structure:\n{structure}" if structure.strip() else ""
    )
    prompt = f"""You are a technical writer creating documentation for a {language} project.

Generate a professional README.md based on this code{' and structure' if structure.strip() else ''}.
Include: project description, features, installation, usage examples, project structure, and license.
Base everything strictly on what exists in the code - do not invent features.
Output raw markdown only. Do not wrap in code fences. Do not repeat the content. Write it once and stop.
{structure_section}

Main source code:
{code}

README.md:"""
    result = _generate(prompt)
    return _clean_readme(result)


def _clean_readme(text: str) -> str:
    """Strip wrapping code fences and deduplicate repeated README content.

    Args:
        text: Raw string returned by the model.

    Returns:
        str: Cleaned markdown string with no leading/trailing fences and
             any duplicated content past the second top-level heading removed.
    """
    text = text.strip()

    # Strip opening code fence (e.g. ```markdown or ```)
    if text.startswith("```"):
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1:]

    # Strip closing code fence
    if text.rstrip().endswith("```"):
        text = text.rstrip()[:-3].rstrip()

    # If the model repeated itself (two top-level # headings), keep only first
    h1_matches = [m.start() for m in re.finditer(r"^# ", text, re.MULTILINE)]
    if len(h1_matches) >= 2:
        text = text[: h1_matches[1]].rstrip()

    return text.strip()