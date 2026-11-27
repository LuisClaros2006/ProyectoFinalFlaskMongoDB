
class Category:
    def __init__(self, name, description="", status=True):
        self.name = name
        self.description = description
        self.status = status

    def toDBCollection(self):
        return {
            'name': self.name,
            'description': self.description,
            'status': self.status
        }
