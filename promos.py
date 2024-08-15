promo_codes = {
    'DISCOUNT10': 10,
    'SUMMER20': 20,
}

def apply_promo_code(code, total_amount):
    # Input validation
    if not isinstance(total_amount, (int, float)) or total_amount < 0:
        raise ValueError("Total amount must be a non-negative number.")
    
    if code not in promo_codes:
        return total_amount, "Invalid promo code."

    discount_percentage = promo_codes[code]
    discount_amount = (total_amount * discount_percentage) / 100
    new_total = total_amount - discount_amount

    # Prevent negative total
    if new_total < 0:
        new_total = 0

    return new_total, f"Promo code applied. You saved ${discount_amount:.2f}."

# Example usage
try:
    total = 100
    new_total, message = apply_promo_code('DISCOUNT10', total)
    print(f"New total: ${new_total:.2f}. {message}")
except ValueError as e:
    print(e)