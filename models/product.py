
from bson.decimal128 import Decimal128

class Product:
    def __init__(
        self,
        name,
        description,
        category_id,
        price,
        stock,
        status=True
    ):
        self.name = name
        self.description = description
        self.category_id = category_id
        self.price = Decimal128(str(price))
        self.stock = stock
        self.status = status

    def toDBCollection(self):
        return {
            'name': self.name,
            'description': self.description,
            'category_id': self.category_id,
            'price': self.price,
            'stock': self.stock,
            'status': self.status
        }
