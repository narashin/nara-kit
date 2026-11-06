import unittest

from fee import amount_due, shipping_fee


class ShippingFeeTest(unittest.TestCase):
    def test_small_order_pays_base_fee(self):
        self.assertEqual(shipping_fee(10000), 3000)

    def test_amount_due_adds_fee(self):
        self.assertEqual(amount_due(10000), 13000)


if __name__ == "__main__":
    unittest.main()
