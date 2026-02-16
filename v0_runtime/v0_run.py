import pandas as pd
from dataclasses import dataclass


@dataclass
class GVState:
    gv: float = 0.0
    threshold: float = 1.0

    @property
    def godscore(self):
        return round(1.0 - self.gv, 4)

    @property
    def status(self):
        return "PASS" if self.gv <= self.threshold else "FAIL"


def run(name, scenario_fn, threshold=1.0):
    gv_value = scenario_fn()

    state = GVState(
        gv=gv_value,
        threshold=threshold
    )

    return {
        "scenario": name,
        "gv": state.gv,
        "godscore": state.godscore,
        "threshold": state.threshold,
        "status": state.status
    }


# --- Example scenarios --- #

class scenarios:

    @staticmethod
    def stable():
        return 0.2

    @staticmethod
    def risky():
        return 1.4


def main():
    out = []

    out.append(run("stable", scenarios.stable, threshold=1.0))
    out.append(run("risky", scenarios.risky, threshold=1.0))

    df = pd.DataFrame(out)
    print(df)


if __name__ == "__main__":
    main()
