import streamlit as st
import os
import io
import time
import requests
import base64
from urllib.parse import urlparse
from dotenv import load_dotenv
from watsonx_client import (
    stream_docs, stream_tests, stream_review, stream_sync, stream_readme,
)

load_dotenv()

st.set_page_config(
    page_title="dev-companion",
    page_icon="⚙",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── STYLES ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Syne:wght@400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Syne', sans-serif; }
.stApp { background: #0a0e1a; }
.main .block-container { padding: 2rem 3rem 4rem; max-width: 1100px; }

.hero-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(99,179,237,0.08); border: 1px solid rgba(99,179,237,0.2);
    border-radius: 20px; padding: 4px 14px;
    font-family: 'JetBrains Mono', monospace; font-size: 11px;
    color: #63b3ed; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 1.2rem;
}
.hero-title {
    font-family: 'Syne', sans-serif; font-size: 3.2rem; font-weight: 700;
    color: #f0f4ff; letter-spacing: -0.03em; line-height: 1.1; margin: 0 0 0.6rem;
}
.hero-title span { color: #63b3ed; }
.hero-sub { font-size: 1.05rem; color: #8892a4; max-width: 560px; line-height: 1.6; margin-bottom: 2rem; }

.stat-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; margin-bottom: 2rem; }
.stat-card { background: #111827; border: 1px solid #1f2937; border-radius: 10px; padding: 1rem 1.2rem; }
.stat-label { font-family: 'JetBrains Mono',monospace; font-size: 10px; color: #4b5563; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 4px; }
.stat-value { font-size: 1.6rem; font-weight: 700; color: #63b3ed; }
.stat-unit { font-size: 0.8rem; color: #6b7280; font-weight: 400; }

.section-label { font-family: 'JetBrains Mono',monospace; font-size: 10px; color: #4b5563; text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 0.8rem; }
.lang-chip { display: inline-flex; align-items: center; gap: 5px; background: rgba(52,211,153,0.08); border: 1px solid rgba(52,211,153,0.2); border-radius: 20px; padding: 2px 10px; font-family: 'JetBrains Mono',monospace; font-size: 10px; color: #34d399; text-transform: uppercase; letter-spacing: 0.08em; }

.output-header { display: flex; align-items: center; gap: 8px; margin-bottom: 1rem; padding-bottom: 0.8rem; border-bottom: 1px solid #1f2937; }
.output-dot { width: 8px; height: 8px; background: #34d399; border-radius: 50%; animation: pulse 1.5s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
.output-dot.done { animation: none; background: #34d399; }
.output-title { font-family: 'JetBrains Mono',monospace; font-size: 12px; color: #34d399; text-transform: uppercase; letter-spacing: 0.1em; }
.output-time { margin-left: auto; font-family: 'JetBrains Mono',monospace; font-size: 10px; color: #4b5563; }

.footer-bar { display: flex; align-items: center; justify-content: space-between; padding: 1rem 0; border-top: 1px solid #111827; margin-top: 3rem; }
.footer-text { font-family: 'JetBrains Mono',monospace; font-size: 10px; color: #374151; letter-spacing: 0.06em; }
.footer-badges { display: flex; gap: 8px; }
.footer-badge { background: #111827; border: 1px solid #1f2937; border-radius: 4px; padding: 2px 8px; font-family: 'JetBrains Mono',monospace; font-size: 9px; color: #4b5563; letter-spacing: 0.08em; }

.stTextArea textarea { background: #0d1117 !important; border: 1px solid #1f2937 !important; color: #e2e8f0 !important; font-family: 'JetBrains Mono',monospace !important; font-size: 13px !important; border-radius: 8px !important; }
.stTextInput input { background: #0d1117 !important; border: 1px solid #1f2937 !important; color: #e2e8f0 !important; font-family: 'JetBrains Mono',monospace !important; font-size: 13px !important; border-radius: 8px !important; }
.stButton button { background: #1e3a5f !important; border: 1px solid #2563eb !important; color: #63b3ed !important; font-family: 'JetBrains Mono',monospace !important; font-size: 12px !important; letter-spacing: 0.05em !important; border-radius: 8px !important; padding: 0.5rem 1.8rem !important; font-weight: 600 !important; }
.stButton button:hover { background: #1d4ed8 !important; border-color: #3b82f6 !important; color: #bfdbfe !important; }
.stTabs [data-baseweb="tab-list"] { background: #0d1424; border: 1px solid #1f2937; border-radius: 8px; padding: 3px; gap: 2px; }
.stTabs [data-baseweb="tab"] { background: transparent; border-radius: 6px; color: #6b7280; font-family: 'JetBrains Mono',monospace; font-size: 12px; padding: 6px 16px; }
.stTabs [aria-selected="true"] { background: #1e3a5f !important; color: #63b3ed !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem; }
div[data-testid="stFileUploader"] { background: #0d1117; border: 1px dashed #1f2937; border-radius: 8px; padding: 0.5rem; }
#MainMenu {visibility:hidden;} footer {visibility:hidden;} header {visibility:hidden;} .stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)


# ─── CREDENTIALS CHECK ───────────────────────────────────────────────────────

def _check_credentials() -> bool:
    missing = [k for k in ("WATSONX_API_KEY","WATSONX_PROJECT_ID","WATSONX_URL") if not os.getenv(k)]
    if missing:
        st.error(
            f"**Missing credentials:** `{'`, `'.join(missing)}`\n\n"
            "**Running locally?** Create a `.env` file:\n"
            "```\nWATSONX_API_KEY=your_key\nWATSONX_PROJECT_ID=your_id\n"
            "WATSONX_URL=https://us-south.ml.cloud.ibm.com\n```\n\n"
            "**Streamlit Cloud?** Go to **Settings → Secrets** and add the same keys.\n\n"
            "Get credentials at [IBM watsonx.ai](https://dataplatform.cloud.ibm.com/)."
        )
        return False
    return True


# ─── LANGUAGE DETECTION ──────────────────────────────────────────────────────

LANGUAGE_MAP = {
    ".py":"Python", ".js":"JavaScript", ".ts":"TypeScript",
    ".jsx":"JavaScript (React)", ".tsx":"TypeScript (React)",
    ".java":"Java", ".c":"C", ".cpp":"C++", ".cs":"C#",
    ".go":"Go", ".rs":"Rust", ".rb":"Ruby", ".php":"PHP",
    ".swift":"Swift", ".kt":"Kotlin", ".scala":"Scala",
    ".sh":"Shell", ".r":"R", ".sql":"SQL",
    ".html":"HTML", ".htm":"HTML", ".css":"CSS",
    ".vue":"Vue", ".svelte":"Svelte", ".md":"Markdown", ".mdx":"Markdown",
}
ANALYZABLE_EXTENSIONS = set(LANGUAGE_MAP.keys())
ALWAYS_INCLUDE = {"readme.md","readme.mdx","readme.txt","index.html","index.js","index.ts","main.py","app.py"}
REPO_FILE_CAP = 20


def detect_language_from_code(code: str) -> str:
    s = code.strip()[:500]
    if "#include" in s: return "C/C++"
    if "package " in s and "func " in s: return "Go"
    if "fn " in s and ("let " in s or "impl " in s): return "Rust"
    if "public class " in s or "System.out." in s: return "Java"
    if "<?php" in s: return "PHP"
    if s.upper().startswith("SELECT") or s.upper().startswith("CREATE TABLE"): return "SQL"
    if "def " in s or ("import " in s and ":" in s): return "Python"
    if "function " in s or "const " in s or "=>" in s: return "JavaScript"
    if "interface " in s and ("string" in s or "number" in s): return "TypeScript"
    if "<html" in s.lower() or "<!doctype" in s.lower(): return "HTML"
    if "{" in s and any(p in s for p in ("color:","margin:","padding:")): return "CSS"
    return "Unknown"


# ─── GITHUB FETCHER ──────────────────────────────────────────────────────────

def parse_github_url(url):
    parsed = urlparse(url.strip())
    if parsed.netloc not in ("github.com","www.github.com"): return None
    parts = parsed.path.strip("/").split("/")
    if len(parts) < 2: return None
    owner, repo = parts[0], parts[1].replace(".git","")
    if len(parts) >= 5 and parts[2] in ("blob","tree"):
        return owner, repo, "/".join(parts[4:]), parts[3]
    return owner, repo, None, "main"


def _gh_get(url, headers, timeout=20):
    try:
        return requests.get(url, headers=headers, timeout=timeout)
    except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError):
        return None


def fetch_github_files(url):
    result = parse_github_url(url)
    if not result:
        return None, "Invalid GitHub URL.", False, 0
    owner, repo, file_path, ref = result
    token = os.getenv("GITHUB_TOKEN","")
    headers = {"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","User-Agent":"dev-companion/1.0"}
    if token: headers["Authorization"] = f"token {token}"

    if file_path:
        ext = ("." + file_path.split(".")[-1]) if "." in file_path else ""
        if ext not in ANALYZABLE_EXTENSIONS:
            return None, f"File type `{ext}` not supported.", False, 0
        r = _gh_get(f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={ref}", headers)
        if not r: return None, "GitHub connection timed out.", False, 0
        if r.status_code != 200: return None, f"Could not fetch file (HTTP {r.status_code}).", False, 0
        d = r.json()
        content = base64.b64decode(d["content"]).decode("utf-8","replace") if d.get("encoding")=="base64" else d.get("content","")
        return [(file_path.split("/")[-1], LANGUAGE_MAP.get(ext,"Unknown"), content)], None, False, 1

    resp = None
    for branch in [ref,"master","develop"]:
        r = _gh_get(f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1", headers)
        if r and r.status_code == 200:
            resp = r; ref = branch; break

    if not resp or resp.status_code != 200:
        code = resp.status_code if resp else "timeout"
        if code == 404: return None, "Repo not found. Is it public?", False, 0
        if code == 403: return None, "GitHub rate limit hit. Add GITHUB_TOKEN to .env.", False, 0
        return None, f"Could not access repo (HTTP {code}).", False, 0

    SKIP = {"node_modules",".git","vendor","dist","build","__pycache__",".next","coverage",".venv","venv","env"}
    tree = [i for i in resp.json().get("tree",[]) if i["type"]=="blob" and not any(s in i["path"].split("/") for s in SKIP)]

    always, source = [], []
    for item in tree:
        fname = item["path"].split("/")[-1].lower()
        ext = ("." + fname.split(".")[-1]) if "." in fname else ""
        (always if fname in ALWAYS_INCLUDE else source if ext in ANALYZABLE_EXTENSIONS else []).append(item)

    always_paths = {i["path"] for i in always}
    source = sorted([i for i in source if i["path"] not in always_paths], key=lambda i:(i["path"].count("/"),i["path"]))
    total = len(always) + len(source)
    capped = total > (len(always) + REPO_FILE_CAP)
    selected = always + source[:REPO_FILE_CAP]
    if not selected: return None, "No analysable source files found.", False, 0

    files_out = []
    for item in selected:
        r = _gh_get(f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{item['path']}", headers, timeout=15)
        if r and r.status_code == 200:
            ext = "." + item["path"].split(".")[-1]
            files_out.append((item["path"], LANGUAGE_MAP.get(ext.lower(),"Text"), r.text))

    return (files_out or None), (None if files_out else "Could not fetch file contents."), capped, total


def combine_files(files):
    sep = "\n\n" + "="*60 + "\n\n"
    return sep.join(f"# File: {p} ({l})\n{c}" for p,l,c in files), list(dict.fromkeys(f[1] for f in files))


# ─── EXAMPLE SNIPPETS ────────────────────────────────────────────────────────
# Pre-loaded code snippets for the "Try an example" button.

EXAMPLES = {
    "Python — Task Manager": {
        "lang": "Python",
        "code": '''\
class TaskManager:
    def __init__(self):
        self.tasks = {}
        self._next_id = 1

    def add_task(self, title, priority="medium"):
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")
        if priority not in ("low", "medium", "high"):
            raise ValueError(f"Invalid priority: {priority}")
        task_id = self._next_id
        self.tasks[task_id] = {
            "id": task_id,
            "title": title.strip(),
            "priority": priority,
            "done": False,
        }
        self._next_id += 1
        return task_id

    def complete_task(self, task_id):
        if task_id not in self.tasks:
            raise KeyError(f"Task {task_id} not found")
        self.tasks[task_id]["done"] = True

    def get_pending(self, priority=None):
        tasks = [t for t in self.tasks.values() if not t["done"]]
        if priority:
            tasks = [t for t in tasks if t["priority"] == priority]
        return sorted(tasks, key=lambda t: ("high","medium","low").index(t["priority"]))

    def delete_task(self, task_id):
        if task_id not in self.tasks:
            raise KeyError(f"Task {task_id} not found")
        return self.tasks.pop(task_id)

    def stats(self):
        total = len(self.tasks)
        done = sum(1 for t in self.tasks.values() if t["done"])
        return {"total": total, "done": done, "pending": total - done}
'''
    },
    "JavaScript — Shopping Cart": {
        "lang": "JavaScript",
        "code": '''\
class ShoppingCart {
    constructor() {
        this.items = new Map();
        this.discountCode = null;
    }

    addItem(id, name, price, quantity = 1) {
        if (price < 0) throw new Error("Price cannot be negative");
        if (quantity < 1) throw new Error("Quantity must be at least 1");
        if (this.items.has(id)) {
            this.items.get(id).quantity += quantity;
        } else {
            this.items.set(id, { id, name, price, quantity });
        }
    }

    removeItem(id) {
        if (!this.items.has(id)) throw new Error(`Item ${id} not in cart`);
        this.items.delete(id);
    }

    applyDiscount(code) {
        const codes = { SAVE10: 0.10, SAVE20: 0.20, HALF: 0.50 };
        if (!codes[code]) throw new Error("Invalid discount code");
        this.discountCode = code;
        return codes[code];
    }

    getTotal() {
        const subtotal = [...this.items.values()]
            .reduce((sum, item) => sum + item.price * item.quantity, 0);
        const discounts = { SAVE10: 0.10, SAVE20: 0.20, HALF: 0.50 };
        const discount = this.discountCode ? discounts[this.discountCode] : 0;
        return parseFloat((subtotal * (1 - discount)).toFixed(2));
    }

    clear() {
        this.items.clear();
        this.discountCode = null;
    }
}

module.exports = { ShoppingCart };
'''
    },
    "TypeScript — User Auth": {
        "lang": "TypeScript",
        "code": '''\
interface User {
    id: string;
    email: string;
    hashedPassword: string;
    role: "admin" | "user" | "guest";
    createdAt: Date;
}

class AuthService {
    private users: Map<string, User> = new Map();

    register(email: string, password: string, role: User["role"] = "user"): User {
        if (!email.includes("@")) throw new Error("Invalid email address");
        if (password.length < 8) throw new Error("Password must be at least 8 characters");
        if ([...this.users.values()].some(u => u.email === email)) {
            throw new Error("Email already registered");
        }
        const user: User = {
            id: crypto.randomUUID(),
            email,
            hashedPassword: this.hash(password),
            role,
            createdAt: new Date(),
        };
        this.users.set(user.id, user);
        return user;
    }

    login(email: string, password: string): User {
        const user = [...this.users.values()].find(u => u.email === email);
        if (!user || user.hashedPassword !== this.hash(password)) {
            throw new Error("Invalid credentials");
        }
        return user;
    }

    getUserById(id: string): User | undefined {
        return this.users.get(id);
    }

    private hash(value: string): string {
        return Buffer.from(value).toString("base64");
    }
}

export { AuthService, User };
'''
    },
}


# ─── PAGE: LANDING ────────────────────────────────────────────────────────────

def render_landing():
    st.markdown("""
<div style="padding:4rem 0 2rem; text-align:center;">
    <div class="hero-badge" style="margin:0 auto 1.2rem;">⚙ AI-Powered Developer Tooling</div>
    <div class="hero-title" style="font-size:4rem; text-align:center;">dev<span>-companion</span></div>
    <div class="hero-sub" style="max-width:620px; margin:0.8rem auto 2.5rem; text-align:center; font-size:1.15rem;">
        Drop any codebase. Get production-quality docs, tests, reviews,
        and READMEs — streamed live, powered by watsonx.ai.
    </div>
</div>
""", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    features = [
        ("📄", "Generate Docs", "Google/JSDoc/Javadoc docstrings + full markdown API reference"),
        ("🧪", "Generate Tests", "Complete test suites covering happy paths, edge cases, and errors"),
        ("🔍", "Code Review", "Severity-rated issues across correctness, security, and performance"),
        ("🔄", "Sync Check", "Detect stale docs and tests after code changes"),
    ]
    for col, (icon, title, desc) in zip([c1,c2,c3,c4], features):
        with col:
            st.markdown(f"""
<div style="background:#111827;border:1px solid #1f2937;border-radius:12px;padding:1.4rem;height:160px;">
    <div style="font-size:1.6rem;margin-bottom:0.6rem;">{icon}</div>
    <div style="font-family:'Syne',sans-serif;font-weight:600;color:#f0f4ff;margin-bottom:0.4rem;">{title}</div>
    <div style="font-size:0.82rem;color:#6b7280;line-height:1.5;">{desc}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
    st.markdown("""
<div style="background:#111827;border:1px solid #1f2937;border-radius:12px;padding:2rem;margin-bottom:2rem;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#4b5563;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:1rem;">Supported languages</div>
    <div style="display:flex;flex-wrap:wrap;gap:8px;">
""" + "".join(
        f'<span style="background:#0d1424;border:1px solid #1f2937;border-radius:6px;padding:4px 12px;font-family:\'JetBrains Mono\',monospace;font-size:11px;color:#63b3ed;">{l}</span>'
        for l in ["Python","JavaScript","TypeScript","Java","Go","Rust","C#","Ruby","C/C++","PHP","Swift","Kotlin","SQL","HTML","CSS"]
    ) + """
    </div>
</div>
""", unsafe_allow_html=True)

    col_l, col_r = st.columns([1, 1])
    with col_l:
        st.markdown("""
<div style="background:linear-gradient(135deg,#0d1f3c,#111827);border:1px solid #2563eb;border-radius:12px;padding:2rem;">
    <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1.1rem;color:#f0f4ff;margin-bottom:0.5rem;">⚡ Real-time streaming</div>
    <div style="color:#6b7280;font-size:0.9rem;line-height:1.6;">Output streams token by token — no more staring at a spinner for 40 seconds. You see results the moment the model starts generating.</div>
</div>""", unsafe_allow_html=True)
    with col_r:
        st.markdown("""
<div style="background:linear-gradient(135deg,#0d2618,#111827);border:1px solid #059669;border-radius:12px;padding:2rem;">
    <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1.1rem;color:#f0f4ff;margin-bottom:0.5rem;">🔗 Any input method</div>
    <div style="color:#6b7280;font-size:0.9rem;line-height:1.6;">Paste code directly, upload a file, or point at a GitHub repo URL. dev-companion handles the rest — no setup required.</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    if st.button("▶ Launch the tool →", type="primary", use_container_width=False):
        st.session_state["page"] = "tool"
        st.rerun()


# ─── PAGE: TOOL ───────────────────────────────────────────────────────────────

def render_tool():

    # ── Header ────────────────────────────────────────────────────────────────
    col_back, col_title = st.columns([1, 8])
    with col_back:
        if st.button("← Home"):
            st.session_state["page"] = "landing"
            st.rerun()
    with col_title:
        st.markdown('<div style="padding-top:0.2rem"><span style="font-family:\'Syne\',sans-serif;font-size:1.4rem;font-weight:700;color:#f0f4ff;">dev<span style="color:#63b3ed;">-companion</span></span></div>', unsafe_allow_html=True)

    st.markdown("---")

    # ── 01 SOURCE ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">01 — source</div>', unsafe_allow_html=True)

    input_tab, github_tab, upload_tab = st.tabs(["📋 Paste code", "🔗 GitHub URL", "📁 Upload file"])

    user_code = ""
    detected_lang = ""

    with input_tab:
        # Try-an-example row
        ex_col, spacer = st.columns([3, 5])
        with ex_col:
            example_choice = st.selectbox(
                "Try an example",
                ["— load an example —"] + list(EXAMPLES.keys()),
                label_visibility="collapsed",
                key="example_select",
            )
        if example_choice != "— load an example —":
            ex = EXAMPLES[example_choice]
            st.session_state["example_code"] = ex["code"]
            st.session_state["example_lang"] = ex["lang"]

        default_code = st.session_state.get("example_code", "")
        pasted = st.text_area(
            "Code input",
            value=default_code,
            height=280,
            placeholder="Paste any code here — Python, JavaScript, TypeScript, Java, Go, Rust, C/C++, and more...",
            label_visibility="collapsed",
            key="paste_area",
        )
        if pasted.strip():
            user_code = pasted
            detected_lang = st.session_state.get("example_lang", "") or detect_language_from_code(pasted)
            st.markdown(f'<div style="margin-top:6px"><span class="lang-chip">⬡ {detected_lang}</span></div>', unsafe_allow_html=True)

    with github_tab:
        github_url = st.text_input(
            "GitHub URL",
            placeholder="https://github.com/owner/repo  or  https://github.com/owner/repo/blob/main/src/app.py",
            label_visibility="collapsed",
        )
        if github_url.strip():
            with st.spinner("Fetching from GitHub..."):
                files, err, capped, total = fetch_github_files(github_url.strip())
            if err:
                st.error(f"⚠ {err}")
            elif files:
                if capped:
                    st.warning(f"⚠ Repo has {total} files — only the first {REPO_FILE_CAP} source files were fetched. For full analysis, link directly to a file.")
                st.success(f"✓ Fetched {len(files)} file(s)")
                with st.expander(f"View {len(files)} scanned files"):
                    for fp, *_ in files:
                        st.markdown(f"`{fp}`")
                user_code, langs = combine_files(files)
                detected_lang = ", ".join(langs)
                st.markdown(f'<div style="margin-top:4px"><span class="lang-chip">⬡ {detected_lang}</span></div>', unsafe_allow_html=True)

    with upload_tab:
        uploaded = st.file_uploader(
            "Upload a source file",
            type=["py","js","ts","jsx","tsx","java","go","rs","rb","php","cs","swift","kt","c","cpp","h","sql","sh","r","vue","svelte","html","css","md"],
            label_visibility="collapsed",
        )
        if uploaded is not None:
            try:
                content = uploaded.read().decode("utf-8", errors="replace")
                ext = "." + uploaded.name.rsplit(".", 1)[-1].lower() if "." in uploaded.name else ""
                detected_lang = LANGUAGE_MAP.get(ext, detect_language_from_code(content))
                user_code = content
                st.success(f"✓ Loaded `{uploaded.name}` ({len(content):,} chars)")
                st.markdown(f'<div style="margin-top:4px"><span class="lang-chip">⬡ {detected_lang}</span></div>', unsafe_allow_html=True)
                with st.expander("Preview file"):
                    st.code(content[:2000] + ("\n... (truncated)" if len(content) > 2000 else ""), language=detected_lang.lower().split()[0])
            except Exception as e:
                st.error(f"Could not read file: {e}")

    st.markdown('<div style="height:1.2rem"></div>', unsafe_allow_html=True)

    # ── 02 ACTION ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">02 — action</div>', unsafe_allow_html=True)

    ACTION_MAP = {
        "— select an action —": None,
        "📄 Generate Documentation": "docs",
        "🧪 Generate Tests": "tests",
        "🔍 Code Review": "review",
        "🔄 Sync Check": "sync",
        "📝 Generate README": "readme",
    }
    ACTION_DESC = {
        "docs": "Adds idiomatic docstrings to every function and class + a full markdown API reference.",
        "tests": "Generates a complete test suite covering happy paths, edge cases, and error conditions.",
        "review": "Severity-rated review across correctness, security, performance, and language idioms.",
        "sync": "Compares source against existing docs and tests. Flags every stale or missing item.",
        "readme": "Generates a professional README strictly from what exists in the code.",
    }

    action_label = st.selectbox("Select action", list(ACTION_MAP.keys()), label_visibility="collapsed")
    action = ACTION_MAP[action_label]

    if action:
        st.markdown(f'<p style="font-size:12px;color:#4b5563;font-family:\'JetBrains Mono\',monospace;margin:4px 0 1rem;">> {ACTION_DESC[action]}</p>', unsafe_allow_html=True)

    extra_docs = extra_tests = extra_structure = ""

    if action == "sync":
        st.markdown('<div class="section-label">02b — existing artifacts</div>', unsafe_allow_html=True)
        ca, cb = st.columns(2)
        with ca:
            extra_docs = st.text_area("Current documentation", height=120, placeholder="Paste existing docs...")
        with cb:
            extra_tests = st.text_area("Current tests", height=120, placeholder="Paste existing tests...")

    if action == "readme":
        extra_structure = st.text_input("Project structure (optional)", placeholder="e.g. src/, tests/, docs/")

    st.markdown('<div style="height:0.6rem"></div>', unsafe_allow_html=True)
    run = st.button("▶ run dev-companion", type="primary")
    st.markdown("---")

    # ── OUTPUT ────────────────────────────────────────────────────────────────
    if run:
        if not user_code.strip():
            st.error("No code provided. Paste code, enter a GitHub URL, or upload a file above.")
            return
        if not action:
            st.error("Select an action first.")
            return
        if action == "sync" and (not extra_docs.strip() or not extra_tests.strip()):
            st.error("Sync Check requires existing docs and tests to compare against.")
            return
        if not _check_credentials():
            return

        lang_label = detected_lang if detected_lang and detected_lang != "Unknown" else "Python"
        lang_short = lang_label.lower().split()[0]

        t0 = time.time()

        # Pulsing output header shown while streaming
        st.markdown(f"""
<div class="output-header">
    <div class="output-dot" id="odot"></div>
    <div class="output-title">{action_label.split(' ',1)[1].lower() if ' ' in action_label else action_label} output</div>
    <div class="output-time" id="otime">streaming · {lang_label}</div>
</div>""", unsafe_allow_html=True)

        full = ""
        elapsed = 0.0
        
        try:
            if action == "docs":
                # Docs splits into two parts — stream into a buffer then separate
                full = "".join(st.write_stream(stream_docs(user_code, lang_label)))
                elapsed = round(time.time() - t0, 1)
                st.markdown(f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:#4b5563;margin-bottom:1rem;">✓ done in {elapsed}s</div>', unsafe_allow_html=True)
                if "### MARKDOWN_DOCS ###" in full:
                    code_part, md_part = full.split("### MARKDOWN_DOCS ###", 1)
                    t1, t2 = st.tabs(["Documented Code", "Markdown Reference"])
                    with t1:
                        st.code(code_part.strip(), language=lang_short)
                    with t2:
                        st.markdown(md_part.strip())
                    st.download_button("⬇ documented_code", full, file_name=f"documented_code.{lang_short}")
                else:
                    st.code(full, language=lang_short)
                    st.download_button("⬇ documented_code", full, file_name=f"documented_code.{lang_short}")

            elif action == "tests":
                full = "".join(st.write_stream(stream_tests(user_code, lang_label)))
                elapsed = round(time.time() - t0, 1)
                st.markdown(f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:#4b5563;margin-bottom:1rem;">✓ done in {elapsed}s</div>', unsafe_allow_html=True)
                st.code(full, language=lang_short)
                st.download_button("⬇ test_generated.py", full, file_name="test_generated.py")

            elif action == "review":
                full = "".join(st.write_stream(stream_review(user_code, lang_label)))
                elapsed = round(time.time() - t0, 1)
                st.markdown(f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:#4b5563;margin-bottom:1rem;">✓ done in {elapsed}s</div>', unsafe_allow_html=True)
                st.download_button("⬇ review_report.md", full, file_name="review_report.md")

            elif action == "sync":
                full = "".join(st.write_stream(stream_sync(user_code, extra_docs, extra_tests, lang_label)))
                elapsed = round(time.time() - t0, 1)
                st.markdown(f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:#4b5563;margin-bottom:1rem;">✓ done in {elapsed}s</div>', unsafe_allow_html=True)
                st.download_button("⬇ sync_report.md", full, file_name="sync_report.md")

            elif action == "readme":
                full = "".join(st.write_stream(stream_readme(user_code, extra_structure, lang_label)))
                elapsed = round(time.time() - t0, 1)
                st.markdown(f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:#4b5563;margin-bottom:1rem;">✓ done in {elapsed}s</div>', unsafe_allow_html=True)
                st.download_button("⬇ README.md", full, file_name="README.md")

            # Store in session history
            if "history" not in st.session_state:
                st.session_state["history"] = []
            st.session_state["history"].insert(0, {
                "action": action_label,
                "lang": lang_label,
                "result": full,
                "elapsed": elapsed,
            })
            # Keep last 10
            st.session_state["history"] = st.session_state["history"][:10]

        except ValueError as e:
            st.error(f"**Configuration error:** {e}")
        except requests.exceptions.Timeout:
            st.error("⏱ watsonx.ai timed out. Try again in a moment.")
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else "unknown"
            st.error(f"watsonx.ai API error (HTTP {status}): {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

    # ── SESSION HISTORY ───────────────────────────────────────────────────────
    if st.session_state.get("history"):
        st.markdown("---")
        st.markdown('<div class="section-label">session history</div>', unsafe_allow_html=True)
        for i, entry in enumerate(st.session_state["history"]):
            with st.expander(f"{entry['action']} · {entry['lang']} · {entry['elapsed']}s"):
                if "review" in entry["action"].lower() or "sync" in entry["action"].lower() or "readme" in entry["action"].lower():
                    st.markdown(entry["result"])
                else:
                    st.code(entry["result"], language=entry["lang"].lower().split()[0])
                st.download_button(
                    f"⬇ download",
                    entry["result"],
                    file_name=f"result_{i}.txt",
                    key=f"dl_hist_{i}",
                )

    # ── FOOTER ────────────────────────────────────────────────────────────────
    st.markdown("""
<div class="footer-bar">
    <div class="footer-text">BUILT WITH IBM BOB + WATSONX.AI · IBM BOB HACKATHON MAY 2026 · SENANU</div>
    <div class="footer-badges">
        <div class="footer-badge">MIT LICENSE</div>
        <div class="footer-badge">LLAMA 3.3 70B</div>
        <div class="footer-badge">STREAMLIT</div>
    </div>
</div>""", unsafe_allow_html=True)


# ─── ROUTER ──────────────────────────────────────────────────────────────────

if "page" not in st.session_state:
    st.session_state["page"] = "landing"

if st.session_state["page"] == "landing":
    render_landing()
else:
    render_tool()