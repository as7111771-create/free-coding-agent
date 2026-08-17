"""
Free Coding Agent — a Claude Code style CLI agent powered by the
Hugging Face Inference API (free tier). Supports multi-turn chat,
file read/write, directory listing, and shell command execution
inside a sandboxed workspace.

Usage:
    python -m src.agent
    python -m src.agent --model meta-llama/Llama-3.3-70B-Instruct
    python -m src.agent --workspace ./myproject
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None  # type: ignore


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

DEFAULT_MODEL = "meta-llama/Llama-3.3-70B-Instruct"
API_URL_TMPL = "https://api-inference.huggingface.co/models/{model}"
SYSTEM_PROMPT = """\
You are an autonomous coding agent — like a miniature Claude Code — living
inside a developer's terminal. You can read, write, and explore files, and
you can run shell commands, all inside the user's workspace.

You operate in a REPL loop: the user gives you a task; you think step by
step, decide which tool to call, and emit ONE action per turn. The runtime
executes it, feeds the result back, and you continue until the task is done.

Available tools (emit exactly one per turn as a JSON block):

  read_file     {"tool":"read_file","path":"relative/path"}
  write_file    {"tool":"write_file","path":"rel/path","content":"..."}
  list_dir      {"tool":"list_dir","path":"."}
  run_command   {"tool":"run_command","command":"ls -la","timeout":60}

Rules:
- Paths are RELATIVE to the workspace root.
- Prefer read_file/list_dir to understand context before writing.
- Keep command outputs small (pipe through head/wc when needed).
- When the task is complete, respond with plain text (no tool block) and
  summarise what you did.
- Always emit the JSON block on its own line, fenced as:
  ```tool
  { ... }
  ```
- Emit ONLY the tool block or a final summary, not both.
"""


# ---------------------------------------------------------------------------
# LLM client
# ---------------------------------------------------------------------------

class HFClient:
    """Thin wrapper around the Hugging Face Inference API."""

    def __init__(self, model: str, token: str | None) -> None:
        self.model = model
        self.token = token or os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACEHUB_API_TOKEN")
        if requests is None:
            raise RuntimeError(
                "The 'requests' package is required. Install it: pip install requests"
            )
        if not self.token:
            raise RuntimeError(
                "No HF token found. Set HF_TOKEN env var or pass --token.\n"
                "Get a free token at https://huggingface.co/settings/tokens"
            )
        self.url = API_URL_TMPL.format(model=model)

    def chat(self, messages: list[dict]) -> str:
        """Send the conversation to the model and return the assistant reply."""
        # Build a single prompt string for chat-completion-style models.
        prompt = self._format_messages(messages)
        payload: dict[str, Any] = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 2048,
                "temperature": 0.4,
                "top_p": 0.9,
                "return_full_text": False,
            },
            "options": {"wait_for_model": True},
        }
        headers = {"Authorization": f"Bearer {self.token}"}
        resp = requests.post(self.url, headers=headers, json=payload, timeout=120)
        if resp.status_code == 503:
            # Model loading — retry once after a short wait.
            import time

            time.sleep(8)
            resp = requests.post(self.url, headers=headers, json=payload, timeout=120)
        if resp.status_code != 200:
            raise RuntimeError(f"HF API error {resp.status_code}: {resp.text[:500]}")
        data = resp.json()
        # HF returns [{"generated_text": "..."}]
        if isinstance(data, list) and data:
            return data[0].get("generated_text", "")
        if isinstance(data, dict) and "generated_text" in data:
            return data["generated_text"]
        if isinstance(data, dict) and "error" in data:
            raise RuntimeError(f"Model error: {data['error']}")
        return str(data)

    @staticmethod
    def _format_messages(messages: list[dict]) -> str:
        """Convert OpenAI-style messages into a prompt string."""
        parts: list[str] = []
        for m in messages:
            role = m["role"]
            content = m["content"]
            if role == "system":
                parts.append(f"<tool_call>\n{content}")
            elif role == "user":
                parts.append(f"<tool_call>\n{content}")
            elif role == "assistant":
                parts.append(f"<tool_call>\n{content}")
            elif role == "tool":
                parts.append(f"<|tool_result|>\n{content}")
        parts.append("<tool_call>")
        return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Tool executor
# ---------------------------------------------------------------------------

class ToolExecutor:
    """Execute tool calls inside the workspace sandbox."""

    MAX_READ = 50_000  # chars
    MAX_OUTPUT = 20_000  # chars of command output kept

    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace.resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)

    # -- public --------------------------------------------------------------

    def execute(self, tool_call: dict) -> str:
        tool = tool_call.get("tool", "")
        try:
            if tool == "read_file":
                return self._read_file(tool_call["path"])
            if tool == "write_file":
                return self._write_file(tool_call["path"], tool_call.get("content", ""))
            if tool == "list_dir":
                return self._list_dir(tool_call.get("path", "."))
            if tool == "run_command":
                return self._run_command(
                    tool_call["command"],
                    int(tool_call.get("timeout", 60)),
                )
            return f"Error: unknown tool '{tool}'"
        except Exception as exc:  # noqa: BLE001
            return f"Error: {exc}"

    # -- helpers -------------------------------------------------------------

    def _safe_path(self, rel: str) -> Path:
        root = self.workspace
        target = (root / rel).resolve()
        # Prevent path traversal outside workspace.
        if not str(target).startswith(str(root)):
            raise ValueError(f"Path '{rel}' escapes workspace")
        return target

    def _read_file(self, rel: str) -> str:
        path = self._safe_path(rel)
        if not path.exists():
            return f"Error: file '{rel}' not found"
        text = path.read_text(encoding="utf-8", errors="replace")
        if len(text) > self.MAX_READ:
            text = text[: self.MAX_READ] + f"\n... [truncated, {len(text)} chars total]"
        return text

    def _write_file(self, rel: str, content: str) -> str:
        path = self._safe_path(rel)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Wrote {len(content)} bytes to {rel}"

    def _list_dir(self, rel: str) -> str:
        path = self._safe_path(rel)
        if not path.exists():
            return f"Error: dir '{rel}' not found"
        entries = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name))
        lines = []
        for e in entries:
            kind = "DIR " if e.is_dir() else "FILE"
            lines.append(f"{kind}  {e.name}")
        return "\n".join(lines) if lines else "(empty)"

    def _run_command(self, command: str, timeout: int) -> str:
        timeout = max(5, min(timeout, 120))
        try:
            proc = subprocess.run(
                command,
                shell=True,
                cwd=str(self.workspace),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            out = proc.stdout
            err = proc.stderr
            result = f"$ {command}\n[exit {proc.returncode}]\n"
            if out:
                result += out
            if err:
                result += f"\n[stderr]\n{err}"
        except subprocess.TimeoutExpired:
            result = f"$ {command}\n[TIMEOUT after {timeout}s]"
        if len(result) > self.MAX_OUTPUT:
            result = result[: self.MAX_OUTPUT] + "\n... [truncated]"
        return result


# ---------------------------------------------------------------------------
# Tool-call parser
# ---------------------------------------------------------------------------

TOOL_RE = re.compile(r"```tool\s*(\{.*?\})\s*```", re.DOTALL)
TOOL_RE_OPEN = re.compile(r"```tool\s*(\{.*)", re.DOTALL)


def _try_parse_json(raw: str) -> dict | None:
    raw = raw.strip()
    # Balance braces if truncated.
    if raw.count("{") > raw.count("}"):
        raw += "}" * (raw.count("{") - raw.count("}"))
    try:
        obj = json.loads(raw)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass
    # Fallback: extract first {...} block.
    start = raw.find("{")
    end = raw.rfind("}")
    if 0 <= start < end:
        try:
            obj = json.loads(raw[start : end + 1])
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            pass
    return None


def parse_tool_call(text: str) -> dict | None:
    """Extract the first JSON tool block from the model output."""
    # 1. Fully fenced block: ```tool {...} ```
    m = TOOL_RE.search(text)
    if m:
        tc = _try_parse_json(m.group(1))
        if tc:
            return tc
    # 2. Open fence (truncated, no closing ```): ```tool {...
    m = TOOL_RE_OPEN.search(text)
    if m:
        tc = _try_parse_json(m.group(1))
        if tc:
            return tc
    return None


# ---------------------------------------------------------------------------
# Agent loop
# ---------------------------------------------------------------------------

class Agent:
    """The agentic REPL loop."""

    MAX_TURNS = 25

    def __init__(self, client: HFClient, workspace: Path, verbose: bool = False) -> None:
        self.client = client
        self.executor = ToolExecutor(workspace)
        self.workspace = workspace
        self.verbose = verbose
        self.messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
        # Seed with a directory listing so the model has context.
        listing = self.executor.execute({"tool": "list_dir", "path": "."})
        self.messages.append(
            {
                "role": "user",
                "content": f"Here is the current workspace listing:\n{listing}",
            }
        )
        self.messages.append(
            {
                "role": "assistant",
                "content": "Got it — I can see the workspace. What would you like me to do?",
            }
        )

    def run_task(self, task: str) -> str:
        """Run a single user task to completion. Returns final summary."""
        self.messages.append({"role": "user", "content": task})
        for turn in range(1, self.MAX_TURNS + 1):
            reply = self.client.chat(self.messages)
            self.messages.append({"role": "assistant", "content": reply})
            if self.verbose:
                print(f"\n--- turn {turn} ---\n{reply}\n", file=sys.stderr)
            tool_call = parse_tool_call(reply)
            if tool_call is None:
                # No tool block → final answer.
                return reply.strip()
            print(f"  → {tool_call.get('tool')}: {tool_call.get('path') or tool_call.get('command','')}", file=sys.stderr)
            result = self.executor.execute(tool_call)
            self.messages.append({"role": "tool", "content": result})
        return "⚠ Reached max turns without a final summary."


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

BANNER = r"""
  ___ ___  ___ ___  _ _ ___ _ _
 | _ \ _ \/ __| _ \| | | __| | |
 |  _/   / (__|   /|_ _| _||_  |
 |_| |_|\___|_|_\ |_| |___|___|
  free coding agent · powered by HF Inference API
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Free coding agent (Claude Code style)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"HF model id (default: {DEFAULT_MODEL})")
    parser.add_argument("--workspace", default=".", help="Workspace directory (default: cwd)")
    parser.add_argument("--token", default=None, help="HF API token (or set HF_TOKEN env)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print raw model turns")
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    workspace.mkdir(parents=True, exist_ok=True)

    try:
        client = HFClient(args.model, args.token)
    except RuntimeError as exc:
        print(f"\n✗ {exc}\n", file=sys.stderr)
        return 1

    agent = Agent(client, workspace, verbose=args.verbose)
    print(BANNER, file=sys.stderr)
    print(f"  model:     {args.model}", file=sys.stderr)
    print(f"  workspace: {workspace}", file=sys.stderr)
    print(f"  type your task, or 'exit' to quit.\n", file=sys.stderr)

    while True:
        try:
            task = input("\n❯ ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye!", file=sys.stderr)
            break
        if not task:
            continue
        if task.lower() in {"exit", "quit", ":q"}:
            break
        try:
            summary = agent.run_task(task)
        except Exception as exc:  # noqa: BLE001
            print(f"\n✗ Error: {exc}", file=sys.stderr)
            continue
        print(f"\n{summary}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
