# Free Coding Agent 🤖

A **free, open-source coding agent** — like a miniature Claude Code — that runs in your terminal and is powered entirely by the **Hugging Face Inference API** (free tier). No paid API keys required.

## What it does

- 💬 **Multi-turn chat** — have a conversation with the agent about your codebase
- 📂 **File operations** — read, write, list files in your workspace
- ⚙️ **Shell commands** — run build commands, tests, git, etc. inside the workspace
- 🔒 **Sandboxed** — all operations are confined to the workspace directory (path traversal blocked)
- 🆓 **100% free** — uses Hugging Face's free Inference API tier
- 🔧 **Pluggable models** — swap between Llama 3.3 70B, Mistral, Qwen, or any HF Inference model

## Quick start

```bash
# 1. Clone
git clone https://github.com/as7111771-create/free-coding-agent.git
cd free-coding-agent

# 2. Install
pip install -r requirements.txt

# 3. Get a free HF token
#    Visit https://huggingface.co/settings/tokens and create a "Read" token

# 4. Run
export HF_TOKEN="hf_xxxxx"
python -m src.agent

# Or specify a model + workspace
python -m src.agent --model meta-llama/Llama-3.3-70B-Instruct --workspace ./myproject
```

## How it works

The agent runs in a **REPL loop**:

1. You give it a task (e.g. *"Create a FastAPI app with a /health endpoint"*)
2. The agent thinks step-by-step and emits a **tool call** — `read_file`, `write_file`, `list_dir`, or `run_command`
3. The runtime executes the tool inside your workspace and feeds the result back
4. The agent continues calling tools until the task is done, then returns a summary

```
You: Create a Python script that prints the first 10 Fibonacci numbers

Agent → write_file: fib.py
Agent → run_command: python3 fib.py
Agent: Done! I created fib.py and verified it runs — output: 0 1 1 2 3 5 8 13 21 34
```

## Tools available to the agent

| Tool | Description |
|------|-------------|
| `read_file` | Read a file's contents (relative path) |
| `write_file` | Write/create a file |
| `list_dir` | List directory contents |
| `run_command` | Execute a shell command (with timeout) |

## Configuration

| Flag / Env | Default | Description |
|------------|---------|-------------|
| `--model` | `meta-llama/Llama-3.3-70B-Instruct` | Any HF Inference API model |
| `--workspace` | `.` (cwd) | Workspace directory |
| `--token` | `$HF_TOKEN` | Hugging Face API token |
| `--verbose` / `-v` | off | Print raw model turns |

### Recommended free models

- `meta-llama/Llama-3.3-70B-Instruct` — best all-rounder
- `mistralai/Mistral-7B-Instruct-v0.3` — fast, lightweight
- `Qwen/Qwen2.5-Coder-32B-Instruct` — great for code generation

## Deploy on Hugging Face Spaces

This repo is also structured as a HF Space. You can duplicate it to your HF account:

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Choose **SDK: Gradio**
3. Copy the files from this repo (app.py, requirements-spaces.txt, src/)
4. Set `HF_TOKEN` as a Space secret
5. The Space will serve a web UI for the agent

## Examples

```bash
# Create a project from scratch
python -m src.agent --workspace ./newproject
> Create a Flask web app with a /api/status endpoint that returns JSON

# Work on existing code
cd my-existing-repo
python -m src.agent
> Add unit tests for the auth module
```

## Limitations

- HF Inference API (free tier) may have rate limits and cold starts
- No streaming (full generation per turn)
- Single tool call per turn (no parallel execution)
- Context window depends on the model chosen

## License

MIT — free to use, modify, and distribute.

## Contributing

PRs welcome! Ideas for contributions:
- Streaming responses
- Parallel tool calls
- More tools (web search, git operations)
- Better context management / summarization
- Support for local models via Ollama
