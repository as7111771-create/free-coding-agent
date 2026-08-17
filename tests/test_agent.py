"""Quick smoke test for tool-call parsing and the tool executor."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.agent import parse_tool_call, ToolExecutor  # noqa: E402


def test_parse_tool_call():
    text = 'Sure! Let me read the file.\n```tool\n{"tool":"read_file","path":"main.py"}\n```'
    tc = parse_tool_call(text)
    assert tc is not None
    assert tc["tool"] == "read_file"
    assert tc["path"] == "main.py"
    print("✓ parse_tool_call works")


def test_parse_truncated():
    text = '```tool\n{"tool":"write_file","path":"a.txt","content":"hi"'  # no closing brace
    tc = parse_tool_call(text)
    assert tc is not None
    assert tc["tool"] == "write_file"
    print("✓ parse truncated tool call works")


def test_parse_none():
    assert parse_tool_call("just a plain summary") is None
    print("✓ parse returns None for plain text")


def test_executor_roundtrip(tmp_path: Path | None = None):
    tmp = tmp_path or Path("/tmp/_agent_test")
    tmp.mkdir(parents=True, exist_ok=True)
    ex = ToolExecutor(tmp)

    # write
    r = ex.execute({"tool": "write_file", "path": "hello.py", "content": "print('hi')\n"})
    assert "Wrote" in r
    # read
    r = ex.execute({"tool": "read_file", "path": "hello.py"})
    assert "print('hi')" in r
    # list
    r = ex.execute({"tool": "list_dir", "path": "."})
    assert "hello.py" in r
    # run command
    r = ex.execute({"tool": "run_command", "command": "python3 hello.py"})
    assert "hi" in r
    print("✓ executor write/read/list/run works")


def test_path_traversal_blocked():
    ex = ToolExecutor(Path("/tmp/_agent_test2"))
    r = ex.execute({"tool": "read_file", "path": "../../etc/passwd"})
    assert "escapes workspace" in r or "not found" in r
    print("✓ path traversal blocked")


if __name__ == "__main__":
    test_parse_tool_call()
    test_parse_truncated()
    test_parse_none()
    test_executor_roundtrip()
    test_path_traversal_blocked()
    print("\nAll tests passed ✓")
