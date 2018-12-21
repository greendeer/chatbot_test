class FourCal:
    def add(self, x, y):
        return x+y

    def minus(self, x, y):
        return x-y

    def multiply(self, x, y):
        return x*y

    def divide(self, x, y):
        if y == 0:
            return None
        return x/y

    def __init__(self):
        self.operator = {"+": self.add, "-": self.minus, "*": self.multiply, "/": self.divide}
