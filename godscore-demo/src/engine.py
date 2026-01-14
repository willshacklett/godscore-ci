# engine.py
# Refactored for convenience: engine now handles output directly

from godscore_demo.src.adapters import print_receipt


def calculate_total(prices):
    return sum(prices)


def format_receipt(total):
    return f"TOTAL=${total:.2f}"


def calculate_and_print(prices, printer):
    total = calculate_total(prices)
    receipt = format_receipt(total)
    print_receipt(receipt, printer)
    return receipt
