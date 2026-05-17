import os
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from dotenv import load_dotenv

load_dotenv()


def get_model():
    credentials = Credentials(
        url=os.getenv("WATSONX_URL"),
        api_key=os.getenv("WATSONX_API_KEY")
    )
    client = APIClient(credentials)
    model = ModelInference(
        model_id="meta-llama/llama-3-3-70b-instruct",
        api_client=client,
        project_id=os.getenv("WATSONX_PROJECT_ID"),
        params={
            GenParams.MAX_NEW_TOKENS: 3000,
            GenParams.TEMPERATURE: 0.2,
            GenParams.REPETITION_PENALTY: 1.05,
            GenParams.STOP_SEQUENCES: ["```markdown", "---END---"]
        }
    )
    return model


def generate_docs(code: str, language: str = "code") -> str:
    model = get_model()
    prompt = f"""You are an expert {language} developer.
Generate idiomatic documentation comments for every class, function, and method in this {language} code.
Use the standard documentation style for {language} (e.g. JSDoc for JavaScript, Google-style docstrings for Python, Javadoc for Java).
Add the comments directly into the code and return the complete updated file.
Also generate a markdown documentation summary at the end after a line that says:
### MARKDOWN_DOCS ###

Code:
{code}

Return the fully documented code followed by the markdown docs."""
    return model.generate_text(prompt=prompt)


def generate_tests(code: str, language: str = "code") -> str:
    model = get_model()
    # Pick test framework hint based on language
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
    return model.generate_text(prompt=prompt)


def generate_review(code: str, language: str = "code") -> str:
    model = get_model()
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
    return model.generate_text(prompt=prompt)


def sync_check(code: str, docs: str, tests: str, language: str = "code") -> str:
    model = get_model()
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
    return model.generate_text(prompt=prompt)


def generate_readme(code: str, structure: str = "", language: str = "code") -> str:
    model = get_model()
    structure_section = f"\nProject structure:\n{structure}" if structure.strip() else ""
    prompt = f"""You are a technical writer creating documentation for a {language} project.
Generate a professional README.md based on this code{' and structure' if structure.strip() else ''}.
Include: project description, features, installation, usage examples, project structure, and license.
Base everything strictly on what exists in the code — do not invent features.
Output raw markdown only. Do not wrap in code fences. Do not repeat the content. Write it once and stop.
{structure_section}

Main source code:
{code}

README.md:"""
    result = model.generate_text(prompt=prompt)
    return _clean_readme(result)


def _clean_readme(text: str) -> str:
    """Strip any wrapping code fences and deduplicate repeated content."""
    text = text.strip()
    # Remove leading ```markdown or ``` fence
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:])
    # Remove trailing closing fence
    if text.rstrip().endswith("```"):
        text = text.rstrip()[:-3].rstrip()
    # Detect and remove duplication: if the content repeats itself,
    # keep only the first occurrence by finding the second H1 heading
    import re
    h1_matches = [m.start() for m in re.finditer(r"^# ", text, re.MULTILINE)]
    if len(h1_matches) >= 2:
        text = text[:h1_matches[1]].rstrip()
    return text