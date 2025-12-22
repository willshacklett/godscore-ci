from __future__ import annotations

from gv_baseline.evolution import run_parameter_evolution


def main() -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception as e:
        raise SystemExit(
            "matplotlib is required to plot. Install it with:\n"
            "  pip install matplotlib\n"
        ) from e

    res = run_parameter_evolution()

    gens = list(range(1, len(res.mean_scores) + 1))
    alphas = [c.alpha for c in res.best_cfgs]
    betas = [c.beta for c in res.best_cfgs]
    gammas = [c.gamma for c in res.best_cfgs]

    plt.figure()
    plt.plot(gens, res.mean_scores, label="mean godscore")
    plt.plot(gens, res.best_scores, label="best godscore")
    plt.xlabel("generation")
    plt.ylabel("score")
    plt.title("GodScore Evolution")
    plt.legend()
    plt.tight_layout()
    plt.savefig("godscore_evolution_scores.png", dpi=200)
    plt.close()

    plt.figure()
    plt.plot(gens, alphas, label="alpha (order weight)")
    plt.plot(gens, betas, label="beta (entropy weight)")
    plt.plot(gens, gammas, label="gamma (sharpness)")
    plt.xlabel("generation")
    plt.ylabel("value")
    plt.title("Best Config Parameters Over Time")
    plt.legend()
    plt.tight_layout()
    plt.savefig("godscore_evolution_params.png", dpi=200)
    plt.close()

    print("Saved:")
    print(" - godscore_evolution_scores.png")
    print(" - godscore_evolution_params.png")


if __name__ == "__main__":
    main()
