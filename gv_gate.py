import sys

def enforce_gv(score: float, threshold: float) -> None:
    """
    CI gate for the God Variable.

    Fails the build if Gv < threshold.
    """
    if score < threshold:
        print(f"❌ Gv gate failed: score={score:.4f} < threshold={threshold:.4f}")
        sys.exit(1)

    print(f"✅ Gv gate passed: score={score:.4f} ≥ threshold={threshold:.4f}")


if __name__ == "__main__":
    # Temporary placeholder values.
    # Replace `score` with your actual Gv computation.
    score = 0.82
    threshold = 0.80

    enforce_gv(score, threshold)
