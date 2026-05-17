# dev-companion

**AI-powered documentation and test generation tool built with IBM Bob**

dev-companion is an intelligent development assistant that automatically generates comprehensive documentation, unit tests, code reviews, and README files for your codebase. Built with IBM watsonx.ai and IBM Bob IDE, it streamlines the documentation workflow and helps maintain code quality across Python, JavaScript, TypeScript, Java, Go, Rust, and 15+ other languages.

---

## 🎯 Features

### Core Capabilities
- **📄 Documentation Generation** — Automatically adds Google-style docstrings to every function and class, plus generates markdown reference documentation
- **🧪 Test Suite Generation** — Creates comprehensive pytest-compatible test suites covering happy paths, edge cases, and error conditions
- **🔍 Code Review** — Performs structured reviews flagging complexity, security, performance, and style issues with severity ratings
- **🔄 Sync Check** — Detects when code changes make existing documentation or tests stale and flags them for updates
- **📝 README Generation** — Scans codebases and generates professional README files based strictly on actual code capabilities

### Additional Features
- **Multi-language Support** — Works with Python, JavaScript, TypeScript, Java, Go, Rust, C/C++, Ruby, PHP, and more
- **GitHub Integration** — Fetch and analyze entire repositories or individual files directly from GitHub URLs
- **Web Interface** — Beautiful Streamlit-based UI with real-time generation and downloadable outputs
- **CLI Mode** — Command-line interface for integration into development workflows
- **IBM Bob Commands** — Custom `/gendoc`, `/gentest`, `/sync`, and `/genreadme` commands for Bob IDE

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- IBM watsonx.ai account with API credentials
- (Optional) GitHub personal access token for private repository access

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/dev-companion.git
cd dev-companion
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure credentials**

Create a `.env` file in the project root:
```env
WATSONX_API_KEY=your_ibm_api_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
GITHUB_TOKEN=your_github_token  # Optional, for private repos
```

Get your IBM watsonx.ai credentials from [IBM Cloud](https://dataplatform.cloud.ibm.com/).

---

## 🚀 Usage

### Web Interface (Streamlit)

Launch the interactive web application:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`. You can:
1. Paste code directly or provide a GitHub URL
2. Select an action (Generate Docs, Tests, Review, Sync, or README)
3. Click "run dev-companion" to generate output
4. Download the results

### Command Line Interface

Run the demo to see all features:
```bash
python main.py demo
```

Run the test suite:
```bash
python main.py test
```

### IBM Bob IDE Integration

dev-companion includes custom Bob commands for seamless IDE integration:

**Generate documentation:**
```
/gendoc src/task_service.py
```

**Generate tests:**
```
/gentest src/task_service.py
```

**Check for stale docs/tests:**
```
/sync src/task_service.py
```

**Generate README:**
```
/genreadme
```

---

## 📁 Project Structure

```
dev-companion/
├── src/                    # Source code being documented and tested
│   ├── __init__.py
│   └── task_service.py    # Example: Task management service
├── tests/                  # Auto-generated test files
│   ├── __init__.py
│   └── test_task_service.py
├── docs/                   # Auto-generated markdown documentation
│   ├── task_service.md
│   └── review_report.md
├── bob_sessions/          # Bob task session reports (for judging)
│   ├── gendoc-output.md
│   ├── gentest-output.md
│   ├── sync-output.md
│   └── genreadme-output.md
├── app.py                 # Streamlit web interface
├── main.py                # CLI entry point
├── watsonx_client.py      # watsonx.ai API client
├── conftest.py            # pytest configuration
├── requirements.txt       # Python dependencies
├── AGENTS.md             # Bob agent instructions
└── README.md             # This file
```

---

## 🤖 How IBM Bob is Used

dev-companion leverages IBM Bob IDE in several key ways:

### 1. Custom Commands
Bob's command system enables natural language task invocation:
- `/gendoc` — Triggers documentation generation workflow
- `/gentest` — Initiates test suite creation
- `/sync` — Runs synchronization checks
- `/genreadme` — Generates project README

### 2. Agent Instructions (AGENTS.md)
The `AGENTS.md` file provides Bob with:
- Project context and core workflows
- Documentation style guidelines (Google-style docstrings)
- Test framework preferences (pytest)
- Sync detection rules (function signature comparison)

### 3. Session Tracking
All Bob interactions are logged in `bob_sessions/` for:
- Reproducibility and debugging
- Performance analysis (token consumption)
- Hackathon judging requirements

### 4. Intelligent Code Analysis
Bob analyzes codebases to:
- Understand project structure and dependencies
- Generate contextually appropriate documentation
- Create comprehensive test coverage
- Detect stale documentation through signature comparison

---

## 🧪 Example: Task Service

The repository includes a complete example demonstrating all features:

**Source:** `src/task_service.py` — A task management service with CRUD operations

**Generated Documentation:** `docs/task_service.md` — Complete API reference with usage examples

**Generated Tests:** `tests/test_task_service.py` — 68 test cases with 100% pass rate covering:
- Happy paths for all methods
- Edge cases (empty inputs, whitespace, boundary conditions)
- Error conditions (invalid priorities, nonexistent IDs)
- Fixtures for test setup and teardown

**Test Results:**
```bash
$ pytest tests/ -v
======================== 68 passed in 0.42s ========================
```

---

## 🛠️ Technology Stack

- **Language:** Python 3.8+
- **AI Model:** IBM watsonx.ai (Llama 3.3 70B Instruct)
- **Web Framework:** Streamlit
- **Testing:** pytest
- **Documentation Format:** Markdown + Google-style docstrings
- **API Client:** requests + python-dotenv
- **IDE Integration:** IBM Bob

---

## 📊 Performance

- **Average generation time:** 20-60 seconds per file
- **Token efficiency:** Cached IAM tokens reduce API overhead
- **Test coverage:** 100% pass rate on generated tests
- **Languages supported:** 15+ programming languages
- **Repository analysis:** Up to 20 source files per scan

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow Google-style docstrings for Python code
- Write pytest-compatible tests for new features
- Update documentation when adding features
- Run `pytest tests/` before submitting PRs

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2026 Sena Folikumah

---

## 🏆 IBM Bob Hackathon

This project was built for the **IBM Bob Hackathon (May 2026)** to demonstrate:
- Custom Bob command integration
- watsonx.ai API usage for code generation
- Multi-language documentation and test generation
- Intelligent sync detection for maintaining code quality

**Session Reports:** All Bob interactions are documented in `bob_sessions/` with token consumption metrics and output samples.

---

## 🔗 Links

- **IBM watsonx.ai:** [https://dataplatform.cloud.ibm.com/](https://dataplatform.cloud.ibm.com/)
- **IBM Bob IDE:** [https://www.ibm.com/products/watsonx-code-assistant](https://www.ibm.com/products/watsonx-code-assistant)
- **Streamlit:** [https://streamlit.io/](https://streamlit.io/)

---

**Built with ❤️ using IBM Bob + watsonx.ai**