# Vacuum Robot RL (CS440 Lab 5)

Project memory for Claude Code. Kept short on purpose: only rules that apply to every task.
Longer, task-specific context lives in `.claude/context/` and is imported on demand.

## Project
- A vacuum robot learns to reach a recharge station on a 4x4 grid with Q-learning.
- The robot does NOT know the transition model T or the reward function R.
- Code: `vacuum_rl.py` (environment + `QLearningAgent`). Notebook: `CS440_LAB5.ipynb`. Logs: `logs/`.

## Grid (row, col), start top-left
```
start  0   0   0
  0    X   0   0
  0    0   0   0
  0   -1   0  10
```
- X = obstacle (1,1). Trap = (3,1), reward -1. Charger = (3,3), reward +10. Both are terminal.
- Moves: up/down/left/right. 80% intended, 10% slip to each side. Walls and X keep the robot in place.
- Hyperparameters: living reward -0.04, gamma 0.9, alpha 0.1, epsilon 1.0 -> 0.05, 5000 episodes.
  Reasons are in `docs/DESIGN_DECISIONS.md`; do not change them without a sweep.

## Rules
- Agent code may only use `env.reset()`, `env.step(a)`, `env.actions(s)`, `env.states`, `env.terminals`.
  Never read underscore attributes (`env._grid`, `env._living_reward`, `env._rng`). That would be cheating.
  The PreToolUse hook blocks any edit that does this.
- `value_iteration_reference()` is for checking results only; the agent never calls it.
- Seed every random run so results are reproducible.
- Match the Lab 2 / Lab 3 notebook style (see `.claude/context/notebook-style.md`).

## Claude Code features in this repo
- Hooks (`.claude/settings.json`): context switcher (UserPromptSubmit), hidden-model guard (PreToolUse),
  syntax check + smoke test after edits (PostToolUse).
- Skill `train-qlearning`: use it to train, evaluate or sweep hyperparameters instead of writing new scripts.
- Sub-agents: `policy-reviewer`, `env-validator`, `rl-theory-researcher`, `notebook-style-reviewer`.

## Context imports
Lines below are added automatically by `scripts/context-switcher.sh` (UserPromptSubmit hook).
Each import is added at most once.

