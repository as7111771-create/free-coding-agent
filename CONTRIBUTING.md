# Contributing to Free Coding Agent 🤝

First off — **thank you** for taking the time to contribute! 🎉

This project exists because the community believes powerful AI coding tools should be free and open for everyone. Every contribution matters.

---

## 🌟 Ways to Contribute

| Type | How |
|------|-----|
| 🐛 **Bug Reports** | [Open an issue](https://github.com/as7111771-create/free-coding-agent/issues/new?labels=bug&template=bug_report.md) |
| ✨ **Feature Requests** | [Suggest a feature](https://github.com/as7111771-create/free-coding-agent/issues/new?labels=enhancement&template=feature_request.md) |
| 📖 **Documentation** | Fix typos, add examples, improve guides |
| 🧪 **Tests** | Add test cases, improve coverage |
| 🔧 **Code** | Pick an issue from the [roadmap](https://github.com/as7111771-create/free-coding-agent#-roadmap) or issues tab |
| 📝 **Examples** | Create example projects the agent can build |
| ⭐ **Star & Share** | Star the repo, share on socials, tell your friends |

---

## 🛠 Development Setup

```bash
# Fork & clone
git clone https://github.com/YOUR_USERNAME/free-coding-agent.git
cd free-coding-agent

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run tests
python tests/test_agent.py

# Run the agent
export HF_TOKEN="hf_xxx"
python -m src.agent --verbose
```

---

## 📋 Pull Request Process

1. **Fork** the repository
2. **Create a branch**: `git checkout -b feat/my-cool-feature`
3. **Make your changes** — keep commits clean and descriptive
4. **Test your changes**: `python tests/test_agent.py`
5. **Commit** with a clear message:
   ```
   feat: add web search tool
   fix: handle 503 errors from HF API
   docs: add Ollama setup guide
   ```
6. **Push** to your fork: `git push origin feat/my-cool-feature`
7. **Open a Pull Request** — describe what changed and why

### Commit Message Convention

| Prefix | Use for |
|--------|---------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation |
| `refactor:` | Code restructuring (no behavior change) |
| `test:` | Adding tests |
| `chore:` | Maintenance, deps, config |

---

## 🏗 Architecture Overview

```
User Task → Agent.run_task()
                ↓
        HFClient.chat()  ← sends messages to HF Inference API
                ↓
        parse_tool_call()  ← extracts JSON tool block from response
                ↓
        ToolExecutor.execute()  ← runs the tool in workspace
                ↓
        (loop back to HFClient with tool result)
                ↓
        Agent returns summary (when no tool call is emitted)
```

Key files:
- `src/agent.py` — Everything: HFClient, ToolExecutor, Agent loop, CLI
- `app.py` — Gradio web UI for HF Spaces
- `tests/test_agent.py` — Smoke tests

---

## 💡 Ideas for Contributions

### Good First Issues
- Add a `delete_file` tool
- Add a `search_files` tool (grep-like)
- Add model warmup / health check
- Improve error messages

### Advanced
- Streaming token responses
- Parallel tool execution
- Context window management / summarization
- Ollama backend support
- Multi-language support (system prompt translations)
- VS Code extension

---

## 📜 Code Style

- Python 3.10+
- Type hints encouraged
- Keep functions small and focused
- Comments for "why", not "what"
- No external dependencies beyond `requests` (CLI) and `gradio` (web UI)

---

## 🤔 Questions?

- 💬 [Start a discussion](https://github.com/as7111771-create/free-coding-agent/discussions)
- 🐛 [Open an issue](https://github.com/as7111771-create/free-coding-agent/issues)

---

<div align="center">

**Built with ❤️ by the community, for the community.**

</div>
