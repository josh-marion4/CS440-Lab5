#!/bin/bash
# Strategy 1 (Write): dynamic imports via the UserPromptSubmit hook.
#
# Picks task-relevant context from the git branch and the user's prompt.
# For each match it adds an @import line to CLAUDE.md ONLY if that line is not
# already there (grep -qxF), so CLAUDE.md never fills up with duplicates.
# The first time a file is imported, its content is also printed to stdout so
# Claude sees it on this prompt; later sessions get it through CLAUDE.md.

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
CLAUDE_MD="$PROJECT_DIR/CLAUDE.md"
CONTEXT_DIR=".claude/context"

touch "$CLAUDE_MD"

# Hook input arrives as JSON on stdin: {"prompt": "...", ...}
INPUT=$(cat)
if command -v jq >/dev/null 2>&1; then
  PROMPT=$(printf '%s' "$INPUT" | jq -r '.prompt // ""')
else
  PROMPT=$(printf '%s' "$INPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("prompt",""))' 2>/dev/null)
fi

add_context() {
  local name="$1"
  local import_line="@$CONTEXT_DIR/$name"
  [[ -f "$PROJECT_DIR/$CONTEXT_DIR/$name" ]] || return 0
  if grep -qxF "$import_line" "$CLAUDE_MD"; then
    return 0                                   # already imported: do nothing
  fi
  echo "$import_line" >> "$CLAUDE_MD"          # persist for future sessions
  cat "$PROJECT_DIR/$CONTEXT_DIR/$name"        # inject now for this prompt
}

# --- Branch-based context ---
BRANCH=$(git -C "$PROJECT_DIR" branch --show-current 2>/dev/null)
case "$BRANCH" in
  env*|environment*) add_context "environment.md" ;;
  qlearning*|rl*)    add_context "rl-theory.md" ;;
  docs*|style*)      add_context "notebook-style.md" ;;
esac

# --- Query-based context ---
if echo "$PROMPT" | grep -Eiq 'environment|grid|step\(|slip|reward|terminal|trap|charger'; then
  add_context "environment.md"
fi
if echo "$PROMPT" | grep -Eiq 'q-?learning|q-?value|alpha|epsilon|explor|policy|temporal difference|\bTD\b'; then
  add_context "rl-theory.md"
fi
if echo "$PROMPT" | grep -Eiq 'notebook|cell|style|log|csv|plot|format'; then
  add_context "notebook-style.md"
fi

exit 0
