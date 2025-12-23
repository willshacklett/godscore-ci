"""
Plot survivability vs God Variable (Gv) score for toy systems.

This script runs repeated trials of fragile vs robust systems and
visualizes the relationship between Gv score and survival time.

Usage:
    python scripts/plot_gv_survival.py
"""

from statistics import mean
import matplotlib.pyplot as plt

from godscore_ci.toy_sim import ToySystem, run_trial


def run_population(system: ToySystem, seeds):
    steps = [run_trial(ToySystem(**system.__dict__), seed=s) for s in seeds]
    return mean(steps), system.score()


def main():
    seeds = list(range(40))

    # Define systems along a robustness spectrum
    systems = [
        ToySystem(0.10, 0.10, 0.80, 0.05),
        ToySystem(0.25, 0.20, 0.65, 0.10),
        ToySystem(0.40, 0.35, 0.50, 0.20),
        ToySystem(0.55, 0.45, 0.40, 0.30),
        ToySystem(0.70, 0.60, 0.30, 0.35),
    ]

    gv_scores = []
    survival_means = []

    for sys in systems:
        mean_steps, gv = run_population(sys, seeds)
        gv_scores.append(gv)
        survival_means.append(mean_steps)

    # Plot
    plt.figure()
    plt.scatter(gv_scores, survival_means)
    plt.plot(gv_scores, survival_means)
    plt.xlabel("Gv Score (Survivability Proxy)")
    plt.ylabel("Mean Survival Time (steps)")
    plt.title("Survivability Increases with Gv Score")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()

