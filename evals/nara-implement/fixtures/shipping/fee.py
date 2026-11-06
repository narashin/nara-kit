"""Shipping fee for an order in the web-ui checkout (placeholder domain)."""

BASE_FEE = 3000
FREE_THRESHOLD = 30000


def shipping_fee(order_total: int, coupon: int = 0) -> int:
    """Return the shipping fee in won for an order total before coupon."""
    if order_total >= FREE_THRESHOLD:
        return 0
    return BASE_FEE


def amount_due(order_total: int, coupon: int = 0) -> int:
    """Return what the customer pays: discounted goods plus shipping."""
    return max(order_total - coupon, 0) + shipping_fee(order_total, coupon)
