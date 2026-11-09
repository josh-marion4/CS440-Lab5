#!/usr/bin/env python3
"""HOOK (PostToolUse on Edit|Write|MultiEdit|NotebookEdit).

Runs right after Claude changes a file, so mistakes are caught immediately
instead of at the end:
  * any .py file      -> syntax check (py_compile)
  * vacuum_rl.py      -> also a fast smoke test (env rules + short training run)
  * any .ipynb file   -> must still be valid notebook JSON
On failure it exits 2 and the error is fed back to Claude to fix.
"""
import json
import os
import py_compile
import subprocess
import sys


def fail(message):
    print(message, file=sys.stderr)
    return 2


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    tool_input = data.get("tool_input", {}) or {}
    path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    project = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())

    if path.endswith(".py"):
        try:
            py_compile.compile(path, doraise=True)
        except py_compile.PyCompileError as err:
            return fail(f"Syntax error after editing {path}:\n{err.msg}")
        if os.path.basename(path) == "vacuum_rl.py":
            result = subprocess.run(
                [sys.executable, os.path.join(project, "scripts", "smoke_test.py")],
                capture_output=True, text=True, timeout=60, cwd=project,
            )
            if result.returncode != 0:
                return fail("Smoke test failed after editing vacuum_rl.py:\n"
                            + (result.stdout + result.stderr)[-2000:])

    elif path.endswith(".ipynb"):
        try:
            with open(path) as f:
                nb = json.load(f)
            assert "cells" in nb
        except Exception as err:  # noqa: BLE001 - any parse problem is a failure
            return fail(f"{path} is no longer a valid notebook: {err}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
