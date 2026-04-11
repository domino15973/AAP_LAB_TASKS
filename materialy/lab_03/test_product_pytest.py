import pytest
from product import Product

@pytest.fixture
def product():
    """Fixture providing a fresh Product instance."""
    return Product("Laptop", 1000.0, 10)

def test_is_available(product):
    """Test product availability."""
    assert product.is_available() is True
    product.remove_stock(10)
    assert product.is_available() is False

@pytest.mark.parametrize("amount, expected_quantity", [
    (5, 15),
    (0, 10),
    (100, 110),
])
def test_add_stock_parametrized(product, amount, expected_quantity):
    """Parameterized test for adding stock."""
    product.add_stock(amount)
    assert product.quantity == expected_quantity

def test_remove_stock_too_much_raises(product):
    """Test removing more stock than available raises ValueError."""
    with pytest.raises(ValueError, match="Insufficient stock"):
        product.remove_stock(11)

@pytest.mark.parametrize("percent, expected_price", [
    (0, 1000.0),
    (10, 900.0),
    (50, 500.0),
    (100, 0.0),
])
def test_apply_discount_parametrized(product, percent, expected_price):
    """Parameterized test for applying valid discounts."""
    product.apply_discount(percent)
    assert product.price == expected_price

@pytest.mark.parametrize("invalid_percent", [
    -1,
    101,
])
def test_apply_discount_invalid_raises(product, invalid_percent):
    """Test applying invalid discount percentages raises ValueError."""
    with pytest.raises(ValueError, match="between 0 and 100"):
        product.apply_discount(invalid_percent)
