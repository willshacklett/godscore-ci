from gv_runtime import GVConfig, GVRuntime


def run(name: str, signals: list[float], threshold: float = 1.0):
    cfg = GVConfig(threshold=threshold)
    runtime = GVRuntime(cfg)

    print(f"\n--- Scenario: {name} ---")

    for s in signals:
        result = runtime.step(s)
        print(result)

    print("Breached:", runtime.breached())
    return runtime.breached()


def main():

    stable_signals = [0.2, 0.1, 0.3, 0.2]
    unstable_signals = [-0.4, -0.6, -0.5, -0.7]

    run("stable", stable_signals, threshold=1.0)
    run("unstable", unstable_signals, threshold=1.0)


if __name__ == "__main__":
    main()
