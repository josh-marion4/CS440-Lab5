#!/usr/bin/env python3
"""HOOK (PreToolUse on Edit|Write|MultiEdit|NotebookEdit).

CLAUDE.md *asks* Claude never to let agent code read the hidden model
(env._grid, env._living_reward, env._rng). This hook *enforces* it: if the text
Claude is about to write accesses those attributes through an env object,
the edit is blocked (exit code 2) and the reason is sent back to Claude.

Inside VacuumEnv the class uses self._grid etc., which is allowed.
"""
import json
import re
import sys

FORBIDDEN = re.compile(r"\b(?!self\b)\w*env\w*\._(grid|living_reward|rng)\b", re.IGNORECASE)


def notebook_code(text):
    # A whole notebook written at once: only check code cells, not markdown explanations
    try:
        nb = json.loads(text)
        return "\n".join("".join(c.get("source", "")) for c in nb.get("cells", [])
                         if c.get("cell_type") == "code")
    except (json.JSONDecodeError, AttributeError):
        return text


def written_code(tool_input):
    """New code this tool call would write. Docs (.md, .txt ...) and markdown cells may
    mention env._grid when explaining the rule, so they are not checked."""
    path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if "notebook_path" in tool_input:                     # NotebookEdit
        if tool_input.get("cell_type") == "markdown":
            return ""
        return tool_input.get("new_source", "") or ""
    if not path.endswith((".py", ".ipynb")):
        return ""
    parts = [tool_input.get(k, "") for k in ("content", "new_string")]
    for edit in tool_input.get("edits", []) or []:
        parts.append(edit.get("new_string", ""))
    text = "\n".join(p for p in parts if isinstance(p, str))
    if path.endswith(".ipynb") and tool_input.get("content"):
        return notebook_code(text)
    return text


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    tool_input = data.get("tool_input", {}) or {}
    match = FORBIDDEN.search(written_code(tool_input))
    if match:
        path = tool_input.get("file_path") or tool_input.get("notebook_path") or "file"
        print(
            f"BLOCKED by guard_hidden_model hook: '{match.group(0)}' in {path}.\n"
            "The robot must not know T or R. Agent code may only use env.reset(), env.step(a), "
            "env.actions(s), env.states and env.terminals. Rewrite without the hidden attribute.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
