from godscore_demo.src.engine import calculate_total, format_receipt

def test_receipt_total():
    total = calculate_total([10, 5, 2.5])
    assert total == 17.5
    assert format_receipt(total) == "TOTAL=$17.50"
