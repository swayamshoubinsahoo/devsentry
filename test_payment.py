from payment_service import process_transaction
assert process_transaction(100, {'tax_rate': 0.1}) == 110.0
assert process_transaction(100, {}) == 100.0
print('ALL_TESTS_PASSED')
