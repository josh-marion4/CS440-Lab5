#!/usr/bin/env python3
"""Bundled script for the train-qlearning skill. Run it; no need to read it.

Train once:   python3 .claude/skills/train-qlearning/scripts/train.py [--alpha 0.1 ...] [--save]
Sweep:        python3 .claude/skills/train-qlearning/scripts/train.py --sweep alpha --values 0.01 0.1 0.5
"""
import argparse
import csv
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)

import vacuum_rl as vr  # noqa: E402


def train_and_score(args, seed):
    agent, env, history = vr.run_qlearning(
        living_reward=args.living_reward, gamma=args.gamma, alpha=args.alpha,
        epsilon_start=args.epsilon_start, epsilon_end=args.epsilon_end,
        n_episodes=args.episodes, seed=seed)
    policy = agent.policy(env)
    U, vi_policy = vr.value_iteration_reference(args.living_reward, args.gamma)
    ev = vr.evaluate(policy, living_reward=args.living_reward, gamma=args.gamma)
    match = sum(policy[s] == vi_policy[s] for s in policy) / len(policy)
    return agent, env, history, policy, vi_policy, U, ev, match


def single(args):
    agent, env, history, policy, vi_policy, U, ev, match = train_and_score(args, args.seed)
    print(f"Hyperparameters: living_reward={args.living_reward} gamma={args.gamma} "
          f"alpha={args.alpha} epsilon={args.epsilon_start}->{args.epsilon_end} "
          f"episodes={args.episodes} seed={args.seed}\n")
    print(vr.policy_grid(policy, "LEARNED POLICY (Q-learning)"))
    print()
    print(vr.policy_grid(vi_policy, "VALUE ITERATION POLICY (check only)"))
    last = history[-500:]
    print(f"\nTraining, last 500 episodes: charger {sum(h['Outcome'] == 'charger' for h in last) / 5:.1f}%  "
          f"avg return {sum(h['Return'] for h in last) / 500:.2f}")
    n = sum(ev["outcomes"].values())
    print(f"Greedy evaluation ({n} episodes): charger {100 * ev['outcomes']['charger'] / n:.1f}%  "
          f"trap {100 * ev['outcomes']['trap'] / n:.1f}%  avg steps {ev['avg_steps']:.1f}")
    print(f"Avg discounted return {ev['avg_discounted']:.2f}   V*(start) {U[vr.START]:.2f}")
    print(f"Policy match with value iteration: {round(match * len(policy))}/{len(policy)} states")
    diffs = {s: (policy[s], vi_policy[s]) for s in policy if policy[s] != vi_policy[s]}
    if diffs:
        print("Differences (learned, optimal):", diffs)

    if args.save:
        logs = os.path.join(ROOT, "logs")
        os.makedirs(logs, exist_ok=True)
        with open(os.path.join(logs, "q_table.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["State"] + list(vr.MOVES) + ["Best"])
            for s in sorted(policy):
                w.writerow([str(s)] + [f"{agent.q[(s, a)]:.3f}" for a in vr.MOVES] + [policy[s]])
        with open(os.path.join(logs, "policy.txt"), "w") as f:
            f.write(vr.policy_grid(policy, "LEARNED POLICY") + "\n")
        with open(os.path.join(logs, "learning_curve.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(history[0]))
            w.writeheader()
            w.writerows(history)
        print("\nsaved logs/q_table.csv, logs/policy.txt, logs/learning_curve.csv")


def sweep(args):
    print(f"Sweep of {args.sweep}, 5 seeds each, {args.episodes} episodes\n")
    print(f"{args.sweep:>14} | charger % | avg disc. return | V*(start) | policy match")
    print("-" * 70)
    for value in args.values:
        if args.sweep == "epsilon":
            args.epsilon_start = args.epsilon_end = value
        else:
            setattr(args, args.sweep, value)
        charger = disc = match = 0.0
        for seed in range(5):
            *_, U, ev, m = train_and_score(args, seed)
            charger += 100 * ev["outcomes"]["charger"] / sum(ev["outcomes"].values()) / 5
            disc += ev["avg_discounted"] / 5
            match += m / 5
        print(f"{value:>14} | {charger:9.1f} | {disc:16.2f} | {U[vr.START]:9.2f} | {match:12.2f}")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--living-reward", dest="living_reward", type=float, default=vr.LIVING_REWARD)
    p.add_argument("--gamma", type=float, default=vr.GAMMA)
    p.add_argument("--alpha", type=float, default=vr.ALPHA)
    p.add_argument("--epsilon-start", dest="epsilon_start", type=float, default=vr.EPSILON_START)
    p.add_argument("--epsilon-end", dest="epsilon_end", type=float, default=vr.EPSILON_END)
    p.add_argument("--episodes", type=int, default=vr.N_EPISODES)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--save", action="store_true")
    p.add_argument("--sweep", choices=["living_reward", "gamma", "alpha", "epsilon"])
    p.add_argument("--values", type=float, nargs="+")
    args = p.parse_args()
    if args.sweep:
        if not args.values:
            p.error("--sweep needs --values")
        sweep(args)
    else:
        single(args)


if __name__ == "__main__":
    main()
