<div align="center">

# 🤖 Free Coding Agent

### A free, open-source coding agent — like Claude Code, but powered by Hugging Face's free Inference API.

**No paid API keys. No credit card. Just pure AI.**

[![GitHub stars](https://img.shields.io/github/stars/as7111771-create/free-coding-agent?style=social)](https://github.com/as7111771-create/free-coding-agent/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/as7111771-create/free-coding-agent?style=social)](https://github.com/as7111771-create/free-coding-agent/network/members)
[![GitHub watchers](https://img.shields.io/github/watchers/as7111771-create/free-coding-agent?style=social)](https://github.com/as7111771-create/free-coding-agent/watchers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![GitHub issues](https://img.shields.io/github/issues/as7111771-create/free-coding-agent)](https://github.com/as7111771-create/free-coding-agent/issues)
[![GitHub contributors](https://img.shields.io/github/contributors/as7111771-create/free-coding-agent)](https://github.com/as7111771-create/free-coding-agent/graphs/contributors)
[![Open Source Love](https://img.shields.io/badge/Open%20Source-❤️-red)](https://github.com/as7111771-create/free-coding-agent)

</div>

---

> **⚡ TL;DR** — Clone, `pip install`, set your free HF token, and you have a Claude Code-style agent running in your terminal. It reads files, writes code, runs shell commands — all autonomously. **100% free forever.**

---

## 🎬 Demo

```text
╔══════════════════════════════════════════════════════════════════╗
║  ___ ___  ___ ___  _ _ ___ _ _                                  ║
║ | _ \ _ \/ __| _ \| | | __| | |                                 ║
║ |  _/   / (__|   /|_ _| _||_  |                                 ║
║ |_| |_|\___|_|_\ |_| |___|___|                                  ║
║  free coding agent · powered by HF Inference API                ║
╚══════════════════════════════════════════════════════════════════╝

  model:     meta-llama/Llama-3.3-70B-Instruct
  workspace: /home/user/myproject

❯ Create a FastAPI app with a /health endpoint that returns JSON

  → write_file: app/main.py
  → write_file: requirements.txt
  → run_command: pip install fastapi uvicorn
  → run_command: python -m uvicorn app.main:app --port 8000 &
  → run_command: curl -s http://localhost:8000/health
  → read_file: app/main.py

✅ Done! I created a FastAPI application with a /health endpoint.

File: app/main.py
  - GET /health returns {"status": "healthy", "timestamp": "..."}
  - Includes proper error handling and type hints

Dependencies: fastapi, uvicorn (added to requirements.txt)
Verified: started the server and confirmed /health returns 200 OK.
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🆓 **100% Free** | Powered by Hugging Face's free Inference API tier — no credit card, no paid keys |
| 🧠 **Multi-turn Agent** | Thinks step-by-step, calls tools, reads results, continues until task is done |
| 📂 **File Operations** | Read, write, list files — full workspace awareness |
| ⚙️ **Shell Commands** | Run builds, tests, git, npm — anything you can do in a terminal |
| 🔒 **Sandboxed** | Path traversal protection — the agent can't escape your workspace |
| 🔧 **Pluggable Models** | Swap between Llama 3.3 70B, Mistral, Qwen, or any HF model in one flag |
| 💻 **CLI + Web UI** | Use as a terminal tool OR deploy as a Gradio web app on HF Spaces |
| 🪶 **Lightweight** | Single dependency: `requests`. No bloat, no frameworks, no BS |

---

## 🚀 Quick Start

### 1. Clone

```bash
git clone https://github.com/as7111771-create/free-coding-agent.git
cd free-coding-agent
```

### 2. Install

```bash
pip install -r requirements.txt
```

### 3. Get a Free HF Token

Go to **[huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)** → Create a new token (Read access is enough) → Copy it.

```bash
export HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxx"
```

### 4. Run!

```bash
python -m src.agent
```

Or with options:

```bash
python -m src.agent --model meta-llama/Llama-3.3-70B-Instruct --workspace ./myproject --verbose
```

That's it. You now have a coding agent in your terminal. **Zero cost.**

---

## 🛠 How It Works

The agent runs in a **REPL (Read-Eval-Print Loop)**:

```
┌─────────┐     ┌──────────┐     ┌─────────────┐     ┌──────────┐
│  You    │────▶│  Agent   │────▶│  Tool Call  │────▶│ Runtime  │
│  give   │     │  thinks  │     │  (JSON)     │     │ executes │
│  task   │     │  step by │     │  read_file  │     │  & feeds │
│         │◀────│  step    │◀────│  write_file │◀────│  result  │
│         │     │          │     │  run_cmd    │     │  back    │
└─────────┘     └──────────┘     └─────────────┘     └──────────┘
                        │
                        ▼
                 ┌──────────────┐
                 │  Final       │
                 │  Summary     │
                 │  (no tool)   │
                 └──────────────┘
```

1. **You** give a task (e.g., *"Add unit tests for the auth module"*)
2. **Agent** thinks step-by-step and emits a **tool call** as JSON
3. **Runtime** executes the tool inside your workspace and feeds the result back
4. **Loop** repeats until the agent decides the task is done → returns a summary

---

## 🔧 Configuration

| Flag / Env | Default | Description |
|------------|---------|-------------|
| `--model` | `meta-llama/Llama-3.3-70B-Instruct` | Any HF Inference API model |
| `--workspace` | `.` (cwd) | Workspace directory |
| `--token` | `$HF_TOKEN` | Hugging Face API token |
| `--verbose` / `-v` | off | Print raw model turns for debugging |

### 🧪 Recommended Free Models

| Model | Why |
|-------|-----|
| `meta-llama/Llama-3.3-70B-Instruct` | 🏆 Best all-rounder (default) |
| `Qwen/Qwen2.5-Coder-32B-Instruct` | 💻 Best for pure code generation |
| `mistralai/Mistral-7B-Instruct-v0.3` | ⚡ Fast, lightweight, good for simple tasks |
| `deepseek-ai/DeepSeek-Coder-33B-Instruct` | 🔥 Excellent at code completion |

---

## 📋 Available Tools

The agent has 4 tools at its disposal. It decides which to use and in what order — autonomously.

| Tool | What it does | Example |
|------|-------------|---------|
| `read_file` | Read file contents | Check existing code before modifying |
| `write_file` | Create/update files | Write new modules, configs, tests |
| `list_dir` | Explore directory structure | Understand project layout |
| `run_command` | Execute shell commands | Run tests, builds, git, npm, pip |

---

## 🌐 Deploy on Hugging Face Spaces

Want a web UI instead of CLI? Deploy on HF Spaces:

1. Go to **[huggingface.co/new-space](https://huggingface.co/new-space)**
2. Choose **SDK: Gradio**
3. Upload `app.py`, `src/`, `requirements-spaces.txt`
4. Add `HF_TOKEN` as a Space **secret**
5. Your agent is now live on the web! 🎉

---

## 📂 Project Structure

```
free-coding-agent/
├── src/
│   ├── __init__.py
│   └── agent.py          # Core: HF client, tool executor, agent loop, CLI
├── tests/
│   └── test_agent.py     # Smoke tests for parsing & executor
├── examples/              # Example projects created by the agent
├── app.py                 # Gradio web UI for HF Spaces
├── requirements.txt       # CLI dependencies (just requests!)
├── requirements-spaces.txt# HF Spaces dependencies (gradio + requests)
├── LICENSE                # MIT
├── CONTRIBUTING.md        # How to contribute
└── README.md              # You are here ✨
```

---

## 🗺 Roadmap

- [x] Multi-turn agent loop
- [x] File operations (read/write/list)
- [x] Shell command execution
- [x] Path traversal sandboxing
- [x] Pluggable HF models
- [x] Gradio web UI
- [ ] **Streaming responses** (token-by-token)
- [ ] **Parallel tool calls** (multiple tools per turn)
- [ ] **Web search tool** (search the internet for docs)
- [ ] **Git operations tool** (commit, branch, PR)
- [ ] **Context summarization** (handle large codebases)
- [ ] **Ollama support** (run fully local, no internet needed)
- [ ] **Multi-file diffs** (show changes like `git diff`)
- [ ] **Voice mode** (talk to your agent)
- [ ] **VS Code extension**

> Vote for features by 👍 the issues below!

---

## 🤝 Contributing

We welcome contributions of all kinds! See **[CONTRIBUTING.md](CONTRIBUTING.md)** for details.

### Ways to contribute:

- 🐛 Report bugs
- ✨ Suggest new features
- 📖 Improve documentation
- 🧪 Add tests
- 🔧 Implement roadmap items
- 📝 Write example projects
- 🌍 Translate the README

**Good first issues are tagged with `good first issue`.**

---

## ⭐ Star History

<div align="center">

[![Star History Chart](https://api.star-history.com/svg?repos=as7111771-create/free-coding-agent&type=Date)](https://star-history.com/#as7111771-create/free-coding-agent&Date)

</div>

---

## 📊 Comparison

| Feature | Claude Code | GitHub Copilot | Cursor | **Free Coding Agent** |
|---------|-----------|---------------|--------|----------------------|
| Price | $20/mo | $10/mo | $20/mo | **$0** |
| Open Source | ❌ | ❌ | ❌ | **✅** |
| Self-hosted | ❌ | ❌ | ❌ | **✅** |
| File operations | ✅ | ❌ | ✅ | ✅ |
| Shell commands | ✅ | ❌ | ❌ | ✅ |
| Multi-turn agent | ✅ | ❌ | ✅ | ✅ |
| Pluggable models | ❌ | ❌ | ❌ | **✅** |
| Web UI | ❌ | ❌ | ❌ | **✅** |

---

## 💬 Community

- 🐛 **[Report a bug](https://github.com/as7111771-create/free-coding-agent/issues/new?labels=bug&template=bug_report.md)**
- ✨ **[Request a feature](https://github.com/as7111771-create/free-coding-agent/issues/new?labels=enhancement&template=feature_request.md)**
- 💬 **[Start a discussion](https://github.com/as7111771-create/free-coding-agent/discussions)**
- 📧 **[Contact](https://github.com/as7111771-create)**

---

## 📜 License

**MIT** — Free to use, modify, distribute, and even sell. No strings attached.

---

<div align="center">

### ⭐ If this project helped you, please give it a star!

**It helps others discover this project and keeps development going.**

[![GitHub stars](https://img.shields.io/github/stars/as7111771-create/free-coding-agent?style=social)](https://github.com/as7111771-create/free-coding-agent/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/as7111771-create/free-coding-agent?style=social)](https://github.com/as7111771-create/free-coding-agent/network/members)

### Built with ❤️ and powered by 🤗 Hugging Face

</div>
