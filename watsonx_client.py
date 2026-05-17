import os
import requests
from dotenv import load_dotenv

load_dotenv()

# ─── AUTH ────────────────────────────────────────────────────────────────────

def _get_iam_token() -> str:
    """Exchange IBM API key for a short-lived IAM bearer token."""
    resp = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": os.getenv("WATSONX_API_KEY")
        },
        timeout=20
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def _generate(prompt: str, max_tokens: int = 3000) -> str:
    """Call the watsonx.ai text generation REST endpoint."""
    token = _get_iam_token()
    base_url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com").rstrip("/")
    project_id = os.getenv("WATSONX_PROJECT_ID")

    resp = requests.post(
        f"{base_url}/ml/v1/text/generation?version=2023-05-29",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        json={
            "model_id": "meta-llama/llama-3-3-70b-instruct",
            "project_id": project_id,
            "input": prompt,
            "parameters": {
                "max_new_tokens": 3000,
                "temperature": 0.2,
                "repetition_penalty": 1.05,
                "stop_sequences": ["```markdown", "---END---"]
            }
        },
        timeout=60
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    return results[0].get("generated_text", "").strip() if results else ""


# ─── FEATURE FUNCTIONS ───────────────────────────────────────────────────────

def generate_docs(code: str, language: str = "code") -> str:
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
    framework = framework_hints.get(language.lower().split()[0], "an appropriate test framework")
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
    structure_section = f"\nProject structure:\n{structure}" if structure.strip() else ""
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
    import re
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:])
    if text.rstrip().endswith("```"):
        text = text.rstrip()[:-3].rstrip()
    h1_matches = [m.start() for m in re.finditer(r"^# ", text, re.MULTILINE)]
    if len(h1_matches) >= 2:
        text = text[:h1_matches[1]].rstrip()
    return text