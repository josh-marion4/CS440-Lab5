# Why each hyperparameter has its value

Measured with the bundled script, 5 seeds x 5000 episodes, evaluated over 2000 greedy runs.
"Policy match" = share of the 13 non-terminal states where the learned action equals the
value iteration action (the true optimal policy from Lab 3, used only for checking).

## Living reward = -0.04
- It is a small cost per step, so the robot prefers shorter routes but is not desperate.
- Optimal policy is the same from 0 down to about -1.0: go right along the top, down the
  right side, avoid the trap row.
- At -2.0 the robot at (3, 0) steps right INTO the trap: ending at -1 beats walking around.
  At -4.0 more states rush toward ending. Too negative a living reward makes the robot suicidal.
- -0.04 is also the best value from Lab 3, so results stay comparable.

## Discount gamma = 0.9
- The +10 charger is about 6 steps from the start; 0.9^6 = 0.53, so it still dominates.
- gamma 0.5: the reward 6 steps away is worth 0.5^6 = 0.016, which is short-sighted; fewer charger visits.
- gamma 0.99: slightly better in this small grid, but learning is slower to settle and values are larger.
- 0.9 matches Lab 3 / Lab 4 so value iteration gives a direct comparison.

## Learning rate alpha = 0.1
- Moves are random (80/10/10), so one sample is noisy. alpha averages many samples.
- alpha 0.5 and 0.9: the Q-table chases the last sample; policy match drops to 0.77 and 0.65.
- alpha 0.01: too slow; after 5000 episodes rarely visited states are still close to 0 (match 0.80).
- 0.1 gave the best match (about 0.89) while still converging in 5000 episodes.

## Epsilon 1.0 -> 0.05, linear decay over the first 80% of episodes
- Start fully random (we know nothing), end mostly greedy (use what we learned).
- Constant 0.05 from the start: the robot finds one route and stops exploring; match falls to 0.69.
- Constant 1.0: plenty of exploration, but Q-values are learned from a random walk, and many
  episodes end in the trap.
- Keeping 0.05 at the end (not 0) means rare states are still visited occasionally.
- Constant 0.3 matches value iteration about as well (0.91 vs 0.89), so the key point is
  "do not start with a tiny epsilon". Decaying is chosen because it ends training almost greedy
  (97.6% charger in the last 500 episodes) instead of taking random moves forever.
- The slides say to lower epsilon over time.
