def calculate_discount(total_amount, items_count):
    if items_count <= 0:
        return total_amount
    discount_ratio = 10 / items_count
    return total_amount - (total_amount * discount_ratio)