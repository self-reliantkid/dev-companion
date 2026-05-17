import streamlit as st
import os
import requests
import base64
from urllib.parse import urlparse
from dotenv import load_dotenv
from watsonx_client import (
    generate_docs,
    generate_tests,
    generate_review,
    sync_check,
    generate_readme
)

load_dotenv()

st.set_page_config(
    page_title="dev-companion",
    page_icon="⚙",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Syne:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
}

.stApp {
    background: #0a0e1a;
}

.main .block-container {
    padding: 2rem 3rem 4rem;
    max-width: 1100px;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(99, 179, 237, 0.08);
    border: 1px solid rgba(99, 179, 237, 0.2);
    border-radius: 20px;
    padding: 4px 14px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #63b3ed;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
}

.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 3.2rem;
    font-weight: 700;
    color: #f0f4ff;
    letter-spacing: -0.03em;
    line-height: 1.1;
    margin: 0 0 0.6rem;
}

.hero-title span {
    color: #63b3ed;
}

.hero-sub {
    font-size: 1.05rem;
    color: #8892a4;
    max-width: 560px;
    line-height: 1.6;
    margin-bottom: 2.4rem;
}

.stat-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 2.8rem;
}

.stat-card {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 10px;
    padding: 1rem 1.2rem;
}

.stat-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: #4b5563;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 4px;
}

.stat-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #63b3ed;
}

.stat-unit {
    font-size: 0.8rem;
    color: #6b7280;
    font-weight: 400;
}

.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: #4b5563;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.8rem;
}

.input-panel {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
}

.source-tab {
    display: inline-flex;
    gap: 4px;
    background: #0d1424;
    border: 1px solid #1f2937;
    border-radius: 8px;
    padding: 3px;
    margin-bottom: 1rem;
}

.source-tab-btn {
    padding: 5px 14px;
    border-radius: 5px;
    font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
    cursor: pointer;
    border: none;
    background: transparent;
    color: #6b7280;
}

.source-tab-btn.active {
    background: #1e3a5f;
    color: #63b3ed;
}

.action-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 8px;
    margin: 1.2rem 0;
}

.action-btn {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 8px;
    padding: 10px 8px;
    text-align: center;
    cursor: pointer;
    transition: all 0.15s;
    font-size: 12px;
    color: #6b7280;
    font-family: 'JetBrains Mono', monospace;
}

.action-btn:hover {
    border-color: #63b3ed;
    color: #63b3ed;
    background: rgba(99,179,237,0.05);
}

.action-btn.selected {
    border-color: #63b3ed;
    color: #63b3ed;
    background: rgba(99,179,237,0.08);
}

.run-btn {
    background: #1e3a5f;
    border: 1px solid #2563eb;
    color: #63b3ed;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    letter-spacing: 0.05em;
    padding: 0.65rem 2rem;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.2s;
}

.lang-chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(52, 211, 153, 0.08);
    border: 1px solid rgba(52, 211, 153, 0.2);
    border-radius: 20px;
    padding: 2px 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: #34d399;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.output-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 1rem;
    padding-bottom: 0.8rem;
    border-bottom: 1px solid #1f2937;
}

.output-dot {
    width: 8px;
    height: 8px;
    background: #34d399;
    border-radius: 50%;
}

.output-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #34d399;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

.output-time {
    margin-left: auto;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: #4b5563;
}

.result-box {
    background: #0d1117;
    border: 1px solid #1f2937;
    border-radius: 10px;
    padding: 1.4rem;
}

.footer-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 0;
    border-top: 1px solid #111827;
    margin-top: 3rem;
}

.footer-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: #374151;
    letter-spacing: 0.06em;
}

.footer-badges {
    display: flex;
    gap: 8px;
}

.footer-badge {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 4px;
    padding: 2px 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    color: #4b5563;
    letter-spacing: 0.08em;
}

/* Override Streamlit defaults for dark theme */
.stTextArea textarea {
    background: #0d1117 !important;
    border: 1px solid #1f2937 !important;
    color: #e2e8f0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
    border-radius: 8px !important;
}

.stTextInput input {
    background: #0d1117 !important;
    border: 1px solid #1f2937 !important;
    color: #e2e8f0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
    border-radius: 8px !important;
}

.stSelectbox select, div[data-baseweb="select"] {
    background: #0d1117 !important;
    border-color: #1f2937 !important;
    color: #e2e8f0 !important;
    font-family: 'JetBrains Mono', monospace !important;
}

.stButton button {
    background: #1e3a5f !important;
    border: 1px solid #2563eb !important;
    color: #63b3ed !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    letter-spacing: 0.05em !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.8rem !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}

.stButton button:hover {
    background: #1d4ed8 !important;
    border-color: #3b82f6 !important;
    color: #bfdbfe !important;
}

.stSuccess {
    background: rgba(52,211,153,0.06) !important;
    border: 1px solid rgba(52,211,153,0.2) !important;
    border-radius: 8px !important;
    color: #34d399 !important;
}

.stError {
    background: rgba(248,113,113,0.06) !important;
    border: 1px solid rgba(248,113,113,0.2) !important;
    border-radius: 8px !important;
}

.stSpinner {
    color: #63b3ed !important;
}

div[data-testid="stMetricValue"] {
    color: #63b3ed !important;
    font-family: 'JetBrains Mono', monospace !important;
}

.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    color: #f0f4ff !important;
    font-family: 'Syne', sans-serif !important;
}

.stMarkdown p, .stMarkdown li {
    color: #9ca3af !important;
}

.stCodeBlock {
    border: 1px solid #1f2937 !important;
    border-radius: 8px !important;
}

/* Hide default streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)


# ─── LANGUAGE DETECTION ────────────────────────────────────────────────────
LANGUAGE_MAP = {
    ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
    ".jsx": "JavaScript (React)", ".tsx": "TypeScript (React)",
    ".java": "Java", ".c": "C", ".cpp": "C++", ".cs": "C#",
    ".go": "Go", ".rs": "Rust", ".rb": "Ruby", ".php": "PHP",
    ".swift": "Swift", ".kt": "Kotlin", ".scala": "Scala",
    ".sh": "Shell", ".r": "R", ".sql": "SQL",
    ".html": "HTML", ".htm": "HTML", ".css": "CSS",
    ".vue": "Vue", ".svelte": "Svelte",
    ".md": "Markdown", ".mdx": "Markdown"
}

ANALYZABLE_EXTENSIONS = set(LANGUAGE_MAP.keys())

# Files to always include if present (by exact name, case-insensitive)
ALWAYS_INCLUDE = {"readme.md", "readme.mdx", "readme.txt", "index.html", "index.js", "index.ts", "main.py", "app.py"}

def detect_language_from_code(code: str) -> str:
    code = code.strip()
    if code.startswith("def ") or "import " in code[:200] or "class " in code[:200]:
        if ":#" in code or "    " in code:
            return "Python"
    if "function " in code[:300] or "const " in code[:300] or "=>" in code[:300]:
        return "JavaScript"
    if "public class" in code[:300] or "System.out" in code[:300]:
        return "Java"
    if "#include" in code[:200]:
        return "C/C++"
    if "func " in code[:200] and "package " in code[:200]:
        return "Go"
    if "fn " in code[:200] and "let " in code[:200]:
        return "Rust"
    return "Unknown"


# ─── GITHUB FETCHER ─────────────────────────────────────────────────────────
def parse_github_url(url: str):
    """Parse a GitHub URL and return (owner, repo, path, ref)."""
    parsed = urlparse(url.strip())
    if parsed.netloc not in ("github.com", "www.github.com"):
        return None
    parts = parsed.path.strip("/").split("/")
    if len(parts) < 2:
        return None
    owner, repo = parts[0], parts[1].replace(".git", "")
    # blob/tree URL: github.com/owner/repo/blob/branch/path/to/file
    if len(parts) >= 5 and parts[2] in ("blob", "tree"):
        ref = parts[3]
        file_path = "/".join(parts[4:])
        return owner, repo, file_path, ref
    # Plain repo URL
    return owner, repo, None, "main"


def _gh_get(url: str, headers: dict, timeout: int = 20):
    """Wrapper around requests.get with timeout and ConnectTimeout handling."""
    try:
        return requests.get(url, headers=headers, timeout=timeout)
    except requests.exceptions.ConnectTimeout:
        return None
    except requests.exceptions.ConnectionError:
        return None


def fetch_github_files(url: str):
    """
    Fetch code from a GitHub URL.
    Returns list of (filename, language, content) tuples.
    """
    result = parse_github_url(url)
    if not result:
        return None, "Invalid GitHub URL. Use: https://github.com/owner/repo or a direct file link."

    owner, repo, file_path, ref = result
    token = os.getenv("GITHUB_TOKEN", "")
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "dev-companion/1.0"
    } if token else {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "dev-companion/1.0"
    }

    # Direct file link
    if file_path:
        ext = "." + file_path.split(".")[-1] if "." in file_path else ""
        if ext not in ANALYZABLE_EXTENSIONS:
            return None, f"File type `{ext}` is not supported for analysis."
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={ref}"
        resp = _gh_get(api_url, headers)
        if resp is None:
            return None, "Connection to GitHub timed out. Check your internet connection and try again."
        if resp.status_code != 200:
            return None, f"Could not fetch file (HTTP {resp.status_code}). Check the URL or repo visibility."
        data = resp.json()
        content = base64.b64decode(data["content"]).decode("utf-8", errors="replace") if data.get("encoding") == "base64" else data.get("content", "")
        lang = LANGUAGE_MAP.get(ext, "Unknown")
        return [(file_path.split("/")[-1], lang, content)], None

    # Repo root — fetch full tree, try main then master then develop
    resp = None
    for branch in [ref, "master", "develop"]:
        tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
        r = _gh_get(tree_url, headers)
        if r is None:
            return None, "Connection to GitHub timed out. Check your internet connection and try again."
        if r.status_code == 200:
            resp = r
            ref = branch
            break

    if resp is None or resp.status_code != 200:
        code = resp.status_code if resp else "timeout"
        if code == 404:
            return None, f"Repo not found (HTTP 404). Make sure it's public and the URL is correct."
        if code == 403:
            return None, "GitHub rate limit hit. Add a GITHUB_TOKEN to your .env to increase the limit."
        return None, f"Could not access repo (HTTP {code}). Make sure it's public."

    SKIP_DIRS = {"node_modules", ".git", "vendor", "dist", "build", "__pycache__", ".next", "coverage", ".venv", "venv", "env"}

    tree = resp.json().get("tree", [])
    all_blobs = [
        item for item in tree
        if item["type"] == "blob"
        and not any(skip in item["path"].split("/") for skip in SKIP_DIRS)
    ]

    always = []
    source = []

    for item in all_blobs:
        fname = item["path"].split("/")[-1].lower()
        ext = "." + fname.split(".")[-1] if "." in fname else ""
        if fname in ALWAYS_INCLUDE:
            always.append(item)
        elif ext in ANALYZABLE_EXTENSIONS:
            source.append(item)

    always_paths = {i["path"] for i in always}
    source = [i for i in source if i["path"] not in always_paths]
    source.sort(key=lambda i: (i["path"].count("/"), i["path"]))
    selected = always + source[:20]

    if not selected:
        return None, "No analyzable source files found in this repo."

    files_out = []
    for item in selected:
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{item['path']}"
        r = _gh_get(raw_url, headers, timeout=15)
        if r is not None and r.status_code == 200:
            ext = "." + item["path"].split(".")[-1]
            lang = LANGUAGE_MAP.get(ext.lower(), "Text")
            files_out.append((item["path"], lang, r.text))

    if not files_out:
        return None, "Found source files but could not fetch their contents."

    return files_out, None


def combine_files(files):
    """Combine multiple files into a single block for analysis."""
    parts = []
    for fpath, lang, content in files:
        parts.append(f"# File: {fpath} ({lang})\n{content}")
    separator = "\n\n" + "=" * 60 + "\n\n"
    return separator.join(parts), list(dict.fromkeys(f[1] for f in files))


# ─── HERO SECTION ───────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 2.5rem 0 1rem;">
    <div class="hero-badge">⚙ IBM Bob Hackathon · May 2026</div>
    <div class="hero-title">dev<span>-companion</span></div>
    <div class="hero-sub">
        Drop any codebase. Get docs, tests, reviews, and READMEs — 
        generated live by watsonx.ai, built with IBM Bob.
    </div>
</div>
""", unsafe_allow_html=True)

# Stats row
st.markdown("""
<div class="stat-grid">
    <div class="stat-card">
        <div class="stat-label">Bob commands</div>
        <div class="stat-value">5</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Tests generated</div>
        <div class="stat-value">68</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Pass rate</div>
        <div class="stat-value">100<span class="stat-unit">%</span></div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Languages</div>
        <div class="stat-value">15<span class="stat-unit">+</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ─── INPUT SECTION ───────────────────────────────────────────────────────────
st.markdown('<div class="section-label">01 — source</div>', unsafe_allow_html=True)

input_mode = st.radio(
    "Input mode",
    ["📋 Paste code", "🔗 GitHub URL"],
    horizontal=True,
    label_visibility="collapsed"
)

user_code = ""
detected_lang = ""
fetched_files = []

if input_mode == "📋 Paste code":
    user_code = st.text_area(
        "Code input",
        height=280,
        placeholder="Paste any code here — Python, JavaScript, TypeScript, Java, Go, Rust, C/C++, and more...",
        label_visibility="collapsed"
    )
    if user_code.strip():
        detected_lang = detect_language_from_code(user_code)
        st.markdown(f'<div style="margin-top:6px"><span class="lang-chip">⬡ {detected_lang}</span></div>', unsafe_allow_html=True)

else:
    github_url = st.text_input(
        "GitHub URL",
        placeholder="https://github.com/owner/repo  or  https://github.com/owner/repo/blob/main/src/app.py",
        label_visibility="collapsed"
    )
    if github_url.strip():
        with st.spinner("Fetching from GitHub..."):
            files, err = fetch_github_files(github_url.strip())
        if err:
            st.error(f"⚠ {err}")
        else:
            fetched_files = files
            langs = list(dict.fromkeys(f[1] for f in files))
            detected_lang = ", ".join(langs)
            file_paths = [f[0] for f in files]
            # Show file list as expander to avoid clutter with many files
            st.success(f"✓ Fetched {len(files)} file(s)")
            with st.expander(f"View {len(files)} scanned files"):
                for fp in file_paths:
                    st.markdown(f'`{fp}`')
            st.markdown(f'<div style="margin-top:4px"><span class="lang-chip">⬡ {detected_lang}</span></div>', unsafe_allow_html=True)
            # Combine into single code block
            user_code, _ = combine_files(files)

st.markdown('<div style="height:1.2rem"></div>', unsafe_allow_html=True)

# ─── ACTION SECTION ──────────────────────────────────────────────────────────
st.markdown('<div class="section-label">02 — action</div>', unsafe_allow_html=True)

action = st.selectbox(
    "Select action",
    [
        "— select an action —",
        "📄 Generate Documentation",
        "🧪 Generate Tests",
        "🔍 Code Review",
        "🔄 Sync Check",
        "📝 Generate README"
    ],
    label_visibility="collapsed"
)

# Action descriptions
action_descriptions = {
    "📄 Generate Documentation": "Adds docstrings to every function and class. Returns annotated code + markdown reference.",
    "🧪 Generate Tests": "Generates a full test suite covering happy paths, edge cases, and exceptions.",
    "🔍 Code Review": "Structured review flagging complexity, security, performance, and style issues with severity ratings.",
    "🔄 Sync Check": "Compares source code against existing docs and tests. Flags stale or mismatched items.",
    "📝 Generate README": "Scans the codebase and generates a professional README based strictly on what's there."
}

if action != "— select an action —":
    st.markdown(f'<p style="font-size:12px; color:#4b5563; font-family:\'JetBrains Mono\',monospace; margin:4px 0 1rem;">> {action_descriptions[action]}</p>', unsafe_allow_html=True)

# ─── SYNC EXTRA INPUTS ───────────────────────────────────────────────────────
extra_docs = ""
extra_tests = ""
extra_structure = ""

if action == "🔄 Sync Check":
    st.markdown('<div class="section-label">02b — existing artifacts</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        extra_docs = st.text_area("Current documentation", height=120, placeholder="Paste your existing docs here...")
    with col_b:
        extra_tests = st.text_area("Current tests", height=120, placeholder="Paste your existing tests here...")

if action == "📝 Generate README":
    extra_structure = st.text_input(
        "Project structure (optional)",
        placeholder="e.g.  src/, tests/, docs/  — leave blank to infer from code"
    )

# ─── RUN BUTTON ──────────────────────────────────────────────────────────────
st.markdown('<div style="height:0.6rem"></div>', unsafe_allow_html=True)
run = st.button("▶ run dev-companion", type="primary", use_container_width=False)

st.markdown("---")

# ─── OUTPUT SECTION ──────────────────────────────────────────────────────────
if run:
    if not user_code or not user_code.strip():
        st.error("No code to analyse. Paste code or enter a valid GitHub URL above.")
    elif action == "— select an action —":
        st.error("Select an action first.")
    elif action == "🔄 Sync Check" and (not extra_docs.strip() or not extra_tests.strip()):
        st.error("Sync Check needs existing docs and tests to compare against.")
    else:
        lang_label = detected_lang if detected_lang and detected_lang != "Unknown" else "code"

        with st.spinner(f"Running {action} via watsonx.ai..."):
            try:
                import time
                t0 = time.time()

                if action == "📄 Generate Documentation":
                    result = generate_docs(user_code, lang_label)
                    elapsed = round(time.time() - t0, 1)
                    st.markdown(f"""
<div class="output-header">
    <div class="output-dot"></div>
    <div class="output-title">documentation output</div>
    <div class="output-time">{elapsed}s · {lang_label}</div>
</div>""", unsafe_allow_html=True)
                    if "### MARKDOWN_DOCS ###" in result:
                        parts = result.split("### MARKDOWN_DOCS ###")
                        tab1, tab2 = st.tabs(["Documented Code", "Markdown Reference"])
                        with tab1:
                            st.code(parts[0], language=lang_label.lower().split()[0] if lang_label else "python")
                        with tab2:
                            st.markdown(parts[1])
                    else:
                        st.code(result, language=lang_label.lower().split()[0] if lang_label else "python")
                    st.download_button("⬇ documented_code", result, file_name=f"documented_code.{lang_label.lower().split()[0] if lang_label else 'py'}")

                elif action == "🧪 Generate Tests":
                    result = generate_tests(user_code, lang_label)
                    elapsed = round(time.time() - t0, 1)
                    st.markdown(f"""
<div class="output-header">
    <div class="output-dot"></div>
    <div class="output-title">test suite output</div>
    <div class="output-time">{elapsed}s · {lang_label}</div>
</div>""", unsafe_allow_html=True)
                    st.code(result, language=lang_label.lower().split()[0] if lang_label else "python")
                    st.download_button("⬇ test_generated", result, file_name="test_generated.py")

                elif action == "🔍 Code Review":
                    result = generate_review(user_code, lang_label)
                    elapsed = round(time.time() - t0, 1)
                    st.markdown(f"""
<div class="output-header">
    <div class="output-dot"></div>
    <div class="output-title">review report</div>
    <div class="output-time">{elapsed}s · {lang_label}</div>
</div>""", unsafe_allow_html=True)
                    st.markdown(result)
                    st.download_button("⬇ review_report.md", result, file_name="review_report.md")

                elif action == "🔄 Sync Check":
                    result = sync_check(user_code, extra_docs, extra_tests, lang_label)
                    elapsed = round(time.time() - t0, 1)
                    st.markdown(f"""
<div class="output-header">
    <div class="output-dot"></div>
    <div class="output-title">sync report</div>
    <div class="output-time">{elapsed}s · {lang_label}</div>
</div>""", unsafe_allow_html=True)
                    st.markdown(result)
                    st.download_button("⬇ sync_report.md", result, file_name="sync_report.md")

                elif action == "📝 Generate README":
                    result = generate_readme(user_code, extra_structure, lang_label)
                    elapsed = round(time.time() - t0, 1)
                    st.markdown(f"""
<div class="output-header">
    <div class="output-dot"></div>
    <div class="output-title">readme output</div>
    <div class="output-time">{elapsed}s · {lang_label}</div>
</div>""", unsafe_allow_html=True)
                    st.markdown(result)
                    st.download_button("⬇ README.md", result, file_name="README.md")

            except Exception as e:
                st.error(f"watsonx.ai error: {str(e)}")
                st.info("Check .env → WATSONX_API_KEY · WATSONX_PROJECT_ID · WATSONX_URL")

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer-bar">
    <div class="footer-text">BUILT WITH IBM BOB + WATSONX.AI · IBM BOB HACKATHON MAY 2026 · SENANU</div>
    <div class="footer-badges">
        <div class="footer-badge">MIT LICENSE</div>
        <div class="footer-badge">LLAMA 3.3 70B</div>
        <div class="footer-badge">STREAMLIT</div>
    </div>
</div>
""", unsafe_allow_html=True)