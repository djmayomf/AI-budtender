import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

promo_codes = {
    'DISCOUNT10': 10,
    'SUMMER20': 20,
}

def apply_promo_code(code, total_amount):
    if not isinstance(total_amount, (int, float)) or total_amount <= 0:
        raise ValueError("Total amount must be a positive number")

    discount = promo_codes.get(code, 0)
    if discount == 0:
        logging.warning(f"Promo code '{code}' is invalid or not found")

    discount_amount = (total_amount * discount) / 100
    final_amount = total_amount - discount_amount

    logging.info(f"Applied promo code '{code}': {discount}% off, total amount reduced from {total_amount} to {final_amount}")

    return final_amount

# Example usage
if __name__ == "__main__":
    try:
        total = 100.0
        code = 'DISCOUNT10'
        new_total = apply_promo_code(code, total)
        print(f"New total after applying promo code '{code}': {new_total}")
    except ValueError as e:
        print(e)