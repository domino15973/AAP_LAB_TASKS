class Product:
    """Represents a product in an online store."""

    def __init__(self, name: str, price: float, quantity: int):
        if price < 0:
            raise ValueError("Price cannot be negative.")
        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")
        self.name = name
        self.price = price
        self.quantity = quantity

    def add_stock(self, amount: int):
        """Adds quantity to the stock. Raises ValueError if amount < 0."""
        if amount < 0:
            raise ValueError("Amount to add cannot be negative.")
        self.quantity += amount

    def remove_stock(self, amount: int):
        """Removes quantity from the stock. Raises ValueError if amount < 0 or > current quantity."""
        if amount < 0:
            raise ValueError("Amount to remove cannot be negative.")
        if amount > self.quantity:
            raise ValueError("Insufficient stock to remove that amount.")
        self.quantity -= amount

    def is_available(self) -> bool:
        """Returns True if quantity > 0."""
        return self.quantity > 0

    def total_value(self) -> float:
        """Returns total value (price * quantity)."""
        return self.price * self.quantity

    def apply_discount(self, percent: float):
        """Reduces the price by a given percentage (0-100)."""
        if not (0 <= percent <= 100):
            raise ValueError("Discount percentage must be between 0 and 100.")
        self.price -= self.price * (percent / 100)
