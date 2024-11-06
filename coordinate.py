class Coordinate:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def get(self) -> tuple:
        return (self.x, self.y, self.z)

    def __add__(self, other: "Coordinate") -> "Coordinate":
        return Coordinate(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Coordinate") -> "Coordinate":
        return Coordinate(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other: int | float) -> "Coordinate":
        return Coordinate(self.x * other, self.y * other, self.z * other)

    def __truediv__(self, other: int | float) -> "Coordinate":
        return Coordinate(self.x / other, self.y / other, self.z / other)

    @staticmethod
    def add(*coords: "Coordinate") -> "Coordinate":
        c = Coordinate(0, 0, 0)
        for coord in coords:
            c += coord
        return c