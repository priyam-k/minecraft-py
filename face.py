from coordinate import Coordinate


class Face:
    def __init__(self, vertices: list[Coordinate], color=(255, 255, 255)):
        self.vertices = vertices
        self.color = color

    def get_vertices(self) -> list[Coordinate]:
        return self.vertices

    def get_center(self) -> Coordinate:
        return Coordinate.add(*self.vertices) / len(self.vertices)

    def get_normal(self):
        """get the normal of the face, vec 0->1 x vec 0->2"""
        # get two vectors on the face
        v1 = self.vertices[1] - self.vertices[0]
        v2 = self.vertices[2] - self.vertices[0]
        # cross product of the two vectors is the normal
        return (
            v1.y * v2.z - v1.z * v2.y,
            v1.z * v2.x - v1.x * v2.z,
            v1.x * v2.y - v1.y * v2.x,
        )
