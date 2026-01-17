import json
import glob
import os
import sys

FLAG_PATH = "governance/gv_config.yml"  # presence = enable
EXAMPLES_GLOB = "governance/examples/*.json"

def main():
    if not os.path.exists(FLAG_PATH):
        print(f"GV governance check: SKIPPED (flag not enabled: {FLAG_PATH})")
        return 0

    failures = []
    for path in glob.glob(EXAMPLES_GLOB):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        gv = data.get("gv_net_delta", None)
        result = (data.get("evaluation", {}) or {}).get("result", "UNKNOWN")

        # Treat explicit FAIL or negative gv as failing
        if result == "FAIL" or (isinstance(gv, (int, float)) and gv < 0):
            failures.append((path, gv, result))

    if failures:
        print("GV governance check: FAIL")
        for path, gv, result in failures:
            print(f"- {path}: gv_net_delta={gv} evaluation={result}")
        return 1

    print("GV governance check: PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
