from coordinate import Coordinate
from face import Face


class GenericBlock:
    """
    A generic block template.
    Attributes:
        pos (Coordinate): The position of the block.
        color: The color of the block.
        transparent (bool): Whether the block is transparent. Defaults to False.
        verts (list[Coordinate]): Cached vertices of the block.
        facemap (list[tuple[int]]): Mapping of vertices to faces.
        faces (list[Face]): Cached faces of the block.
    Methods:
        _calc_verts(): Template method to calculate vertices of the block for caching.
        get_center() -> Coordinate: Template method to get the center of the block.
        _calc_faces() -> list[Face]: Uses facemap to calculate faces of the block for caching.
        get_vertices() -> list[Coordinate]: Returns cached vertices of the block.
        get_faces() -> list[Face]: Returns cached faces of the block.
    """

    def __init__(self, pos: Coordinate, color, transparent=False):
        self.pos = pos
        self.color = color
        self.transparent = transparent
        self.verts = None
        self.facemap = None
        self.faces = None
        # self.verts = self._calc_verts()
        # self.facemap = [
        #     (0, 3, 2, 1),  # Front face (-z)
        #     (4, 5, 6, 7),  # Back face (+z)
        #     (0, 1, 5, 4),  # Bottom face (-y)
        #     (2, 3, 7, 6),  # Top face (+y)
        #     (1, 2, 6, 5),  # Right face (+x)
        #     (0, 4, 7, 3),  # Left face (-x)
        # ]
        # self.faces = self._calc_faces()

    def _calc_verts(self):
        """template to calculate vertices of block for caching"""
        raise NotImplementedError("Subclasses must implement this method")

    def get_center(self) -> Coordinate:
        """template to get center of block"""
        raise NotImplementedError("Subclasses must implement this method")
        # return Coordinate(self.pos.x + 0.5, self.pos.y + 0.5, self.pos.z + 0.5)

    def _calc_faces(self):
        """uses facemap to calculate faces of block for caching"""
        return [
            Face([self.verts[i] for i in face], color=self.color)
            for face in self.facemap
        ]

    def get_vertices(self) -> list[Coordinate]:
        """get cached vertices of block"""
        return self.verts

    def get_faces(self) -> list[Face]:
        """get cached faces of block"""
        return self.faces
