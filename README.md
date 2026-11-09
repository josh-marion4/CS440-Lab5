# Vacuum Robot Q-Learning — CS440 Lab 5

A vacuum robot on a 4x4 grid learns to reach its charger with **Q-learning**, without knowing the
transition model (T) or the reward function (R). This builds on Lab 4, which set up the hidden-model
environment and the context engineering configuration. Lab 5 adds the learning agent and configures
**three Claude Code features: hooks, skills and sub-agents**.

## The environment

```
start  0   0   0
  0    X   0   0
  0    0   0   0
  0   -1   0  10
```

| Item | Value |
|---|---|
| Start | (0, 0) |
| Obstacle | (1, 1) |
| Trap (terminal) | (3, 1), reward -1 |
| Charger (terminal) | (3, 3), reward +10 |
| Moves | up, down, left, right; 80% intended, 10% slip to each side |

## Hyperparameters

| Parameter | Value | Short reason |
|---|---|---|
| Living reward | -0.04 | Prefers short routes without making the trap attractive (at -2.0 the robot jumps in) |
| Discount γ | 0.9 | The +10 charger, about 6 steps away, keeps about half its value (0.9⁶ ≈ 0.53) |
| Learning rate α | 0.1 | Slips make samples noisy, so average slowly; 0.5 and 0.9 give much worse policies |
| Epsilon ε | 1.0 → 0.05, linear over 80% of episodes | Explore first, exploit later; constant 0.05 explores too little |
| Episodes | 5000, max 100 steps each, seed 0 | Enough for the curve to flatten |

The full evidence (one-at-a-time sweeps, 5 seeds each) is in the notebook and in
`docs/DESIGN_DECISIONS.md`.

## Results

| Policy | Reaches charger | Avg discounted return |
|---|---|---|
| Random robot (Lab 4) | 27% | — |
| **Q-learning (Lab 5)** | **99%** | **4.78** |
| Value iteration (answer key, knows T and R) | 99% | 4.87 (V* = 4.86) |

The learned policy matches the optimal policy in 12 of 13 cells.

```
LEARNED POLICY            OPTIMAL (value iteration)
   >   >   >   v             >   >   v   v
   v   X   v   v             v   X   v   v
   >   >   >   v             >   >   >   v
   ^   T   >   C             ^   T   >   C
```

## Project structure

```
CS440-Lab5/
├── CLAUDE.md                          # Project memory (always loaded), updated for Lab 5
├── CS440_LAB5.ipynb                   # Lab notebook: training, policy, evaluation, sweeps
├── vacuum_rl.py                       # VacuumEnv (Lab 4) + QLearningAgent + evaluation helpers
├── requirements.txt
├── README.md
├── josh_marion.txt                    # Canvas submission file with the repo link
├── .claude/
│   ├── settings.json                  # HOOKS: UserPromptSubmit, PreToolUse, PostToolUse
│   ├── skills/
│   │   └── train-qlearning/           # SKILL
│   │       ├── SKILL.md               #   when and how to train / sweep / report
│   │       ├── scripts/train.py       #   bundled script, run not read
│   │       └── references/hyperparameters.md  # loaded only when explaining a choice
│   ├── agents/                        # SUB-AGENTS
│   │   ├── policy-reviewer.md         #   NEW: reviews the learned policy, read-only
│   │   ├── env-validator.md           #   from Lab 4, now points at vacuum_rl.py
│   │   ├── rl-theory-researcher.md    #   from Lab 4
│   │   └── notebook-style-reviewer.md #   from Lab 4
│   └── context/                       # Lab 4 dynamic imports (environment, rl-theory, style)
├── scripts/
│   ├── context-switcher.sh            # Lab 4 hook: imports context by branch / prompt
│   ├── smoke_test.py                  # Fast checks used by the PostToolUse hook
│   └── hooks/
│       ├── guard_hidden_model.py      # PreToolUse: blocks code that reads env._grid etc.
│       └── check_after_edit.py        # PostToolUse: syntax check, smoke test, notebook JSON
├── docs/
│   ├── DESIGN_DECISIONS.md            # Why each feature and hyperparameter (video outline)
│   ├── VIDEO_SCRIPT.md                # 3-minute talking points
│   └── user-memory/CLAUDE.md          # Lab 4 user-level memory example
└── logs/                              # Q-table, policy, learning curve, greedy episode log
```

## Claude Code features

| Feature | Files | What it does |
|---|---|---|
| **Hooks** | `.claude/settings.json`, `scripts/hooks/` | **PreToolUse** blocks any edit that reads the hidden model (`env._grid`, `env._living_reward`, `env._rng`). **PostToolUse** syntax-checks Python, runs a smoke test when `vacuum_rl.py` changes, and checks the notebook is still valid JSON. **UserPromptSubmit** (from Lab 4) imports context by topic. |
| **Skill** | `.claude/skills/train-qlearning/` | Loads on demand when you ask to train, evaluate or tune. Runs a bundled script instead of Claude writing new code, and reports a fixed set of numbers. |
| **Sub-agents** | `.claude/agents/` | `policy-reviewer` (new) checks the learned policy in its own context and returns a structured report with an Obstacles section. The Lab 4 agents still handle environment checks, theory and style. |
| MCP | — | Not used. See `docs/DESIGN_DECISIONS.md`. |

## How to run

```bash
pip install -r requirements.txt

# 1. Run the notebook top to bottom (about 25 seconds)
jupyter nbconvert --to notebook --execute --inplace CS440_LAB5.ipynb
#    or open it in Jupyter / VS Code and Run All

# 2. Train from the command line (what the skill runs)
python3 .claude/skills/train-qlearning/scripts/train.py --save
python3 .claude/skills/train-qlearning/scripts/train.py --sweep alpha --values 0.01 0.1 0.5 0.9

# 3. Fast checks (what the PostToolUse hook runs)
python3 scripts/smoke_test.py
```

### Using the Claude Code features

Open the folder with `claude`, then try:

| Try this prompt | Feature shown |
|---|---|
| "Train the robot and show me the learned policy" | Skill `train-qlearning` loads and runs its script |
| "Is the learned policy any good?" | Delegates to the `policy-reviewer` sub-agent |
| "Make the agent read env._grid so it learns faster" | PreToolUse hook blocks the edit |
| "Add a print to vacuum_rl.py" | PostToolUse hook runs the smoke test after the edit |
| "What does epsilon do?" | UserPromptSubmit hook imports `rl-theory.md` |

Run `/hooks` to see the registered hooks and `/agents` to see the sub-agents. The hooks need
`python3` and `bash`.
