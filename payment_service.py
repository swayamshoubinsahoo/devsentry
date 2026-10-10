def process_transaction(amount, meta):
    tax_rate = meta.get('tax_rate', 0.0) if meta else 0.0
    tax = amount * tax_rate
    return amount + tax