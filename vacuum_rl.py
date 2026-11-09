"""Vacuum robot RL for CS440 Lab 5.

The environment is the same as Lab 4: the robot does not know T or R and can only
call reset(), step(a), actions(s), states and terminals. Lab 5 adds a Q-learning
agent that learns a policy from (s, a, r, s') samples.

The notebook CS440_LAB5.ipynb and the train-qlearning skill both import this file.
"""

import random
from collections import Counter, defaultdict

MOVES = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}

SLIPS = {
    "up": ("left", "right"),
    "down": ("right", "left"),
    "left": ("down", "up"),
    "right": ("up", "down"),
}

ARROWS = {"up": "^", "down": "v", "left": "<", "right": ">"}

X = None  # obstacle
GRID = [
    [0, 0,  0, 0],
    [0, X,  0, 0],
    [0, 0,  0, 0],
    [0, -1, 0, 10],
]

START = (0, 0)
CHARGER = (3, 3)
TRAP = (3, 1)
TERMINALS = {CHARGER, TRAP}
P_INTENDED, P_SLIP = 0.8, 0.1

# Lab 5 hyperparameters (justified in docs/DESIGN_DECISIONS.md)
LIVING_REWARD = -0.04
GAMMA = 0.9
ALPHA = 0.1
EPSILON_START, EPSILON_END = 1.0, 0.05
N_EPISODES = 5000
MAX_STEPS = 100


def show_grid(grid, title):
    # S = start, X = obstacle
    print(title)
    for r, row in enumerate(grid):
        cells = []
        for c, value in enumerate(row):
            mark = "S" if (r, c) == START else " "
            text = "X" if value is None else value
            cells.append(f"{text:>4}{mark}")
        print("  " + "".join(cells))
    print()


class VacuumEnv:
    """Same environment as Lab 4. The model (T and R) is hidden in underscore attributes."""

    def __init__(self, grid=GRID, living_reward=LIVING_REWARD, seed=None):
        # Hidden model: the agent never reads these directly
        self._grid = grid
        self._living_reward = living_reward
        self._rng = random.Random(seed)
        # Public: what any robot knows about its world
        self.states = [(r, c) for r in range(len(grid))
                       for c in range(len(grid[0])) if grid[r][c] is not None]
        self.terminals = TERMINALS
        self.state = None

    def actions(self, s):
        return [] if s in self.terminals else list(MOVES)

    def reset(self, start=START):
        self.state = start
        return self.state

    def _go(self, s, direction):
        # Move one cell; walls and the obstacle keep the robot in place
        r, c = s
        dr, dc = MOVES[direction]
        nxt = (r + dr, c + dc)
        return nxt if nxt in self.states else s

    def step(self, action):
        # Returns (next_state, reward, done, info). info is for our logs only.
        if self.state in self.terminals:
            raise RuntimeError("Episode is over, call reset()")
        left, right = SLIPS[action]
        actual = self._rng.choices([action, left, right],
                                   weights=[P_INTENDED, P_SLIP, P_SLIP])[0]
        nxt = self._go(self.state, actual)
        reward = self._living_reward
        if nxt in self.terminals:
            r, c = nxt
            reward += self._grid[r][c]
        done = nxt in self.terminals
        self.state = nxt
        return nxt, reward, done, dict(actual=actual)


class QLearningAgent:
    """Tabular Q-learning with epsilon-greedy exploration.

    Update after every step (course slides RL-L2):
        sample  = r + gamma * max_a' Q(s', a')      (0 if s' is terminal)
        Q(s, a) = (1 - alpha) * Q(s, a) + alpha * sample
    Epsilon decays linearly from epsilon_start to epsilon_end over the first
    `decay_fraction` of training, so the robot explores first and exploits later.
    """

    def __init__(self, alpha=ALPHA, gamma=GAMMA, epsilon_start=EPSILON_START,
                 epsilon_end=EPSILON_END, n_episodes=N_EPISODES, decay_fraction=0.8, seed=None):
        self.alpha, self.gamma = alpha, gamma
        self.epsilon_start, self.epsilon_end = epsilon_start, epsilon_end
        self.decay_episodes = max(1, int(n_episodes * decay_fraction))
        self.epsilon = epsilon_start
        self.q = defaultdict(float)          # Q[(s, a)], starts at 0
        self.rng = random.Random(seed)

    def set_episode(self, episode):
        frac = min(1.0, episode / self.decay_episodes)
        self.epsilon = self.epsilon_start + frac * (self.epsilon_end - self.epsilon_start)

    def best_action(self, env, s):
        # Ties broken at random so early training does not favour one direction
        actions = env.actions(s)
        best = max(self.q[(s, a)] for a in actions)
        return self.rng.choice([a for a in actions if self.q[(s, a)] == best])

    def choose(self, env, s):
        if self.rng.random() < self.epsilon:
            return self.rng.choice(env.actions(s))
        return self.best_action(env, s)

    def update(self, env, s, a, r, s2, done):
        future = 0.0 if done else max(self.q[(s2, a2)] for a2 in env.actions(s2))
        sample = r + self.gamma * future
        self.q[(s, a)] = (1 - self.alpha) * self.q[(s, a)] + self.alpha * sample

    def policy(self, env):
        return {s: self.best_action(env, s) for s in env.states if s not in env.terminals}

    def values(self, env):
        return {s: (0.0 if s in env.terminals else max(self.q[(s, a)] for a in env.actions(s)))
                for s in env.states}


def outcome_of(state):
    if state == CHARGER:
        return "charger"
    if state == TRAP:
        return "trap"
    return "timeout"


def train(agent, env, n_episodes=N_EPISODES, max_steps=MAX_STEPS):
    """Run Q-learning episodes. Returns one dict per episode (return, steps, outcome, epsilon)."""
    history = []
    for episode in range(n_episodes):
        agent.set_episode(episode)
        s, total = env.reset(), 0.0
        for step in range(1, max_steps + 1):
            a = agent.choose(env, s)
            s2, r, done, _ = env.step(a)          # info["actual"] is never used for learning
            agent.update(env, s, a, r, s2, done)
            total += r
            s = s2
            if done:
                break
        history.append(dict(Episode=episode + 1, Return=total, Steps=step,
                            Outcome=outcome_of(s), Epsilon=agent.epsilon))
    return history


def evaluate(policy, living_reward=LIVING_REWARD, n_episodes=2000, max_steps=MAX_STEPS,
             gamma=GAMMA, seed=123):
    """Run a fixed policy with no exploration. Returns outcome counts, average return,
    average discounted return and average steps."""
    env = VacuumEnv(GRID, living_reward=living_reward, seed=seed)
    outcomes, total, disc_total, steps = Counter(), 0.0, 0.0, 0
    for _ in range(n_episodes):
        s, ret, disc = env.reset(), 0.0, 0.0
        for t in range(max_steps):
            s, r, done, _ = env.step(policy[s])
            ret += r
            disc += (gamma ** t) * r
            if done:
                break
        outcomes[outcome_of(s)] += 1
        total += ret
        disc_total += disc
        steps += t + 1
    return dict(outcomes=outcomes, avg_return=total / n_episodes,
                avg_discounted=disc_total / n_episodes, avg_steps=steps / n_episodes)


def value_iteration_reference(living_reward=LIVING_REWARD, gamma=GAMMA, tol=1e-9):
    """Lab 3 style value iteration using the published spec (GRID, MOVES, SLIPS, P_*).

    Used ONLY to check the learned policy afterwards. The Q-learning agent never calls it.
    Returns (U, policy) with the same reward convention as VacuumEnv.step().
    """
    states = [(r, c) for r in range(len(GRID)) for c in range(len(GRID[0])) if GRID[r][c] is not None]

    def go(s, d):
        nxt = (s[0] + MOVES[d][0], s[1] + MOVES[d][1])
        return nxt if nxt in states else s

    def q_value(U, s, a):
        total = 0.0
        for d, p in ((a, P_INTENDED), (SLIPS[a][0], P_SLIP), (SLIPS[a][1], P_SLIP)):
            s2 = go(s, d)
            r = living_reward + (GRID[s2[0]][s2[1]] if s2 in TERMINALS else 0)
            total += p * (r + gamma * U[s2])
        return total

    U = {s: 0.0 for s in states}
    while True:
        new = {s: 0.0 if s in TERMINALS else max(q_value(U, s, a) for a in MOVES) for s in states}
        if max(abs(new[s] - U[s]) for s in states) < tol:
            U = new
            break
        U = new
    policy = {s: max(MOVES, key=lambda a: q_value(U, s, a)) for s in states if s not in TERMINALS}
    return U, policy


def policy_grid(policy, title="POLICY"):
    """Text grid of arrows. X = obstacle, C = charger, T = trap."""
    lines = [title]
    for r in range(len(GRID)):
        row = []
        for c in range(len(GRID[0])):
            s = (r, c)
            if GRID[r][c] is None:
                row.append("X")
            elif s == CHARGER:
                row.append("C")
            elif s == TRAP:
                row.append("T")
            else:
                row.append(ARROWS[policy[s]])
        lines.append("  " + "  ".join(f"{x:>2}" for x in row))
    return "\n".join(lines)


def run_qlearning(living_reward=LIVING_REWARD, gamma=GAMMA, alpha=ALPHA,
                  epsilon_start=EPSILON_START, epsilon_end=EPSILON_END,
                  n_episodes=N_EPISODES, seed=0):
    """Train one agent and return (agent, env, history). Seeded for reproducibility."""
    env = VacuumEnv(GRID, living_reward=living_reward, seed=seed)
    agent = QLearningAgent(alpha=alpha, gamma=gamma, epsilon_start=epsilon_start,
                           epsilon_end=epsilon_end, n_episodes=n_episodes, seed=seed)
    history = train(agent, env, n_episodes=n_episodes)
    return agent, env, history
