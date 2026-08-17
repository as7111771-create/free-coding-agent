"""
Gradio web UI for the Free Coding Agent — for Hugging Face Spaces.
Run: python app.py  (or it auto-runs on HF Spaces)
"""

from __future__ import annotations

import os
from pathlib import Path

import gradio as gr

from src.agent import Agent, HFClient, parse_tool_call, SYSTEM_PROMPT

DEFAULT_MODEL = "meta-llama/Llama-3.3-70B-Instruct"


def create_agent(model: str, token: str, workspace: str) -> Agent | str:
    try:
        client = HFClient(model, token or None)
        ws = Path(workspace) if workspace else Path("/tmp/agent_workspace")
        ws.mkdir(parents=True, exist_ok=True)
        return Agent(client, ws, verbose=False)
    except Exception as exc:  # noqa: BLE001
        return f"⚠ Setup error: {exc}"


def run_task(agent_state, task: str, model: str, token: str, workspace: str):
    if agent_state is None or isinstance(agent_state, str):
        agent_state = create_agent(model, token, workspace)
        if isinstance(agent_state, str):
            yield agent_state, agent_state
            return
    try:
        # Stream the agent's turns
        agent_state.messages.append({"role": "user", "content": task})
        log_parts: list[str] = [f"**You:** {task}\n"]
        yield "", "\n".join(log_parts)
        for _turn in range(1, Agent.MAX_TURNS + 1):
            reply = agent_state.client.chat(agent_state.messages)
            agent_state.messages.append({"role": "assistant", "content": reply})
            tool_call = parse_tool_call(reply)
            if tool_call is None:
                log_parts.append(f"\n**Agent:** {reply.strip()}")
                yield "", "\n".join(log_parts)
                return
            tool_label = tool_call.get("tool", "?")
            detail = tool_call.get("path") or tool_call.get("command", "")
            log_parts.append(f"\n**→ {tool_label}** `{detail}`")
            result = agent_state.executor.execute(tool_call)
            agent_state.messages.append({"role": "tool", "content": result})
            preview = result[:300] + ("..." if len(result) > 300 else "")
            log_parts.append(f"```\n{preview}\n```")
            yield "", "\n".join(log_parts)
        yield "", "\n".join(log_parts) + "\n\n⚠ Max turns reached."
    except Exception as exc:  # noqa: BLE001
        yield "", f"\n⚠ Error: {exc}"


CSS = """
.gradio-container { max-width: 900px !important; }
#header { text-align: center; }
"""

with gr.Blocks(css=CSS, title="Free Coding Agent") as demo:
    gr.Markdown(
        "# 🤖 Free Coding Agent\n"
        "A Claude Code style agent powered by Hugging Face Inference API (free)."
    )
    with gr.Row():
        model_in = gr.Textbox(label="Model", value=DEFAULT_MODEL)
        token_in = gr.Textbox(label="HF Token", type="password", placeholder="hf_xxx")
        ws_in = gr.Textbox(label="Workspace", value="/tmp/agent_workspace")
    agent_state = gr.State(None)
    chat_out = gr.Markdown(label="Agent log", value="Enter a task to begin.")
    task_in = gr.Textbox(label="Task", placeholder="e.g. Create a Flask app with a /health endpoint", lines=2)
    btn = gr.Button("Run", variant="primary")
    btn.click(run_task, [agent_state, task_in, model_in, token_in, ws_in], [task_in, chat_out], [agent_state])


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
