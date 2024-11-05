import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

promo_codes = {
    'DISCOUNT10': 10,
    'SUMMER20': 20,
}

def apply_promo_code(code, total_amount):
    discount = promo_codes.get(code, 0)
    discount_amount = (total_amount * discount) / 100
    return total_amount - discount_amount
