# Environment context (loaded when a prompt mentions the environment, grid, step, slip or reward)

## `VacuumEnv` contract
| Call | Returns | Notes |
|---|---|---|
| `reset(start=START)` | start state | START = (0, 0) |
| `step(action)` | `(next_state, reward, done, info)` | raises if called after a terminal |
| `actions(s)` | list of actions | empty in terminal states |
| `states` | all non-obstacle cells | public |
| `terminals` | `{(3, 1), (3, 3)}` | public |

- `info["actual"]` is the direction the robot really moved. It is for human logs only; learning code must not use it.
- Reward from `step` = living reward + terminal value when the robot enters a terminal cell
  (charger: -0.04 + 10 = 9.96, trap: -0.04 - 1 = -1.04).

## Hidden model (inside the class only)
- `_grid`, `_living_reward`, `_rng`.
- Slip directions: `SLIPS = {up: (left, right), down: (right, left), left: (down, up), right: (up, down)}`.

## Known results with seed 0, 500 random episodes, max 50 steps
- Charger 135, trap 256, timeout 109. Average return 1.04.
- Estimated T((2,2), right): (2,3) 0.821, (1,2) 0.095, (3,2) 0.084.
