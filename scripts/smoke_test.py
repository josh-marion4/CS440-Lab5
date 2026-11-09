"""Fast checks (about 1 second) run by the PostToolUse hook after vacuum_rl.py changes."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vacuum_rl import (CHARGER, GRID, START, TERMINALS, TRAP, VacuumEnv,  # noqa: E402
                       run_qlearning)

env = VacuumEnv(GRID, seed=0)
assert env.reset() == START == (0, 0), "start must be (0, 0)"
assert TERMINALS == {(3, 1), (3, 3)} and TRAP == (3, 1) and CHARGER == (3, 3), "terminals changed"
assert (1, 1) not in env.states and len(env.states) == 15, "obstacle must be at (1, 1)"

# Slip model: about 80% intended
env, hits = VacuumEnv(GRID, seed=1), 0
for _ in range(5000):
    env.state = (2, 2)
    s2, *_ = env.step("right")
    hits += s2 == (2, 3)
assert 0.77 < hits / 5000 < 0.83, f"intended move rate {hits / 5000:.2f}, expected ~0.80"

# Terminal rewards
env = VacuumEnv(GRID, seed=0)
env.state = (3, 2)
for _ in range(50):
    env.state = (3, 2)
    s2, r, done, _ = env.step("right")
    if s2 == CHARGER:
        assert abs(r - 9.96) < 1e-9 and done, "charger reward must be -0.04 + 10"
        break

# A short training run must work and learn something
agent, env, history = run_qlearning(n_episodes=300, seed=0)
assert len(history) == 300 and len(agent.q) > 0, "training produced no Q-values"
print("smoke test OK")
