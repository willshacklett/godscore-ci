# engine.py
# Clean baseline: no external dependencies

def calculate_total(prices):
    return sum(prices)

def format_receipt(total):
    return f"TOTAL=${total:.2f}"
