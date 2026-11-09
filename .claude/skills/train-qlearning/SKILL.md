---
name: train-qlearning
description: Trains and evaluates the vacuum robot Q-learning agent, or sweeps one hyperparameter. Use when the user asks to train the robot, run Q-learning, show the learned policy or Q-table, test a living reward, discount factor (gamma), learning rate (alpha) or epsilon value, compare values, or check results against value iteration.
allowed-tools: Read, Bash(python3 .claude/skills/train-qlearning/scripts/train.py *)
---

# Train and evaluate the Q-learning agent

Do not re-implement training in the chat or write a new script. Run the bundled
script; do not read its source unless it fails. Only its output costs context.

## 1. Train with chosen hyperparameters
```bash
python3 .claude/skills/train-qlearning/scripts/train.py
```
Defaults come from `vacuum_rl.py` (living reward -0.04, gamma 0.9, alpha 0.1,
epsilon 1.0 -> 0.05, 5000 episodes, seed 0). Override any of them:
```bash
python3 .claude/skills/train-qlearning/scripts/train.py --alpha 0.5 --epsilon-end 0.05 --seed 3
```
Add `--save` to write `logs/q_table.csv`, `logs/policy.txt` and `logs/learning_curve.csv`.

## 2. Sweep one hyperparameter
```bash
python3 .claude/skills/train-qlearning/scripts/train.py --sweep alpha --values 0.01 0.1 0.5 0.9
```
Sweepable: `living_reward`, `gamma`, `alpha`, `epsilon` (constant epsilon). Each value is
averaged over 5 seeds.

## 3. Report back to the user
Keep it short, in this order:
1. The learned policy grid (arrows) and the value iteration grid from the output.
2. `Charger %`, `Avg discounted return` vs `V*(start)`, and `Policy match`.
3. One or two sentences on what changed and why, using the explanations in
   `references/hyperparameters.md` (read it only when explaining a choice).

If the script errors, show the last lines of the error and stop. Do not edit `vacuum_rl.py`
to make numbers look better.
