import unittest
from product import Product

class TestProduct(unittest.TestCase):

    def setUp(self):
        """Sets up a fresh Product instance before each test."""
        self.p = Product("Laptop", 1000.0, 10)

    def test_add_stock_positive(self):
        """Test adding a positive amount to stock."""
        self.p.add_stock(5)
        self.assertEqual(self.p.quantity, 15)

    def test_add_stock_negative_raises(self):
        """Test adding a negative amount to stock raises ValueError."""
        with self.assertRaises(ValueError):
            self.p.add_stock(-1)

    def test_remove_stock_positive(self):
        """Test removing a positive amount from stock."""
        self.p.remove_stock(5)
        self.assertEqual(self.p.quantity, 5)

    def test_remove_stock_too_much_raises(self):
        """Test removing more than current stock raises ValueError."""
        with self.assertRaises(ValueError):
            self.p.remove_stock(11)

    def test_remove_stock_negative_raises(self):
        """Test removing a negative amount raises ValueError."""
        with self.assertRaises(ValueError):
            self.p.remove_stock(-1)

    def test_is_available_when_in_stock(self):
        """Test is_available returns True when quantity > 0."""
        self.assertTrue(self.p.is_available())

    def test_is_not_available_when_empty(self):
        """Test is_available returns False when quantity is 0."""
        self.p.remove_stock(10)
        self.assertFalse(self.p.is_available())

    def test_total_value(self):
        """Test total_value calculation (price * quantity)."""
        self.assertEqual(self.p.total_value(), 10000.0)

if __name__ == "__main__":
    unittest.main()
