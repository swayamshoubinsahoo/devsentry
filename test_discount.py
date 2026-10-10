from discount_service import calculate_discount
assert calculate_discount(100, 2) == 100 - (100 * 5)
assert calculate_discount(50, 0) == 50
print('ALL_TESTS_PASSED')
