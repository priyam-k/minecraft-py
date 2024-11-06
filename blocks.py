from coordinate import Coordinate
from genericblock import GenericBlock


class Block(GenericBlock):
    """A full cube block (1x1x1)"""

    def __init__(self, pos: Coordinate, color, transparent=False):
        super().__init__(pos, color, transparent)
        self.facemap = [
            (0, 3, 2, 1),  # Front face (-z)
            (4, 5, 6, 7),  # Back face (+z)
            (0, 1, 5, 4),  # Bottom face (-y)
            (2, 3, 7, 6),  # Top face (+y)
            (1, 2, 6, 5),  # Right face (+x)
            (0, 4, 7, 3),  # Left face (-x)
        ]
        self.verts = self._calc_verts()
        self.faces = self._calc_faces()

    def _calc_verts(self):
        """calculate vertices of block for caching"""
        return [
            Coordinate(self.pos.x, self.pos.y, self.pos.z),
            Coordinate(self.pos.x + 1, self.pos.y, self.pos.z),
            Coordinate(self.pos.x + 1, self.pos.y + 1, self.pos.z),
            Coordinate(self.pos.x, self.pos.y + 1, self.pos.z),
            Coordinate(self.pos.x, self.pos.y, self.pos.z + 1),
            Coordinate(self.pos.x + 1, self.pos.y, self.pos.z + 1),
            Coordinate(self.pos.x + 1, self.pos.y + 1, self.pos.z + 1),
            Coordinate(self.pos.x, self.pos.y + 1, self.pos.z + 1),
        ]

    def get_center(self):
        return Coordinate(self.pos.x + 0.5, self.pos.y + 0.5, self.pos.z + 0.5)


class BlockSlab(GenericBlock):
    """A slab thats half the height of normal block (1x0.5x1)"""

    def __init__(self, pos: Coordinate, color, bottom=True, transparent=False):
        super().__init__(pos, color, transparent)
        self.facemap = [
            (0, 3, 2, 1),  # Front face (-z)
            (4, 5, 6, 7),  # Back face (+z)
            (0, 1, 5, 4),  # Bottom face (-y)
            (2, 3, 7, 6),  # Top face (+y)
            (1, 2, 6, 5),  # Right face (+x)
            (0, 4, 7, 3),  # Left face (-x)
        ]
        self.bottom = bottom
        self.verts = self._calc_verts()
        self.faces = self._calc_faces()

    def _calc_verts(self):
        """calculate vertices of block for caching"""
        if self.bottom:
            return [
                Coordinate(self.pos.x, self.pos.y, self.pos.z),
                Coordinate(self.pos.x + 1, self.pos.y, self.pos.z),
                Coordinate(self.pos.x + 1, self.pos.y + 0.5, self.pos.z),
                Coordinate(self.pos.x, self.pos.y + 0.5, self.pos.z),
                Coordinate(self.pos.x, self.pos.y, self.pos.z + 1),
                Coordinate(self.pos.x + 1, self.pos.y, self.pos.z + 1),
                Coordinate(self.pos.x + 1, self.pos.y + 0.5, self.pos.z + 1),
                Coordinate(self.pos.x, self.pos.y + 0.5, self.pos.z + 1),
            ]
        else:
            return [
                Coordinate(self.pos.x, self.pos.y + 0.5, self.pos.z),
                Coordinate(self.pos.x + 1, self.pos.y + 0.5, self.pos.z),
                Coordinate(self.pos.x + 1, self.pos.y + 1, self.pos.z),
                Coordinate(self.pos.x, self.pos.y + 1, self.pos.z),
                Coordinate(self.pos.x, self.pos.y + 0.5, self.pos.z + 1),
                Coordinate(self.pos.x + 1, self.pos.y + 0.5, self.pos.z + 1),
                Coordinate(self.pos.x + 1, self.pos.y + 1, self.pos.z + 1),
                Coordinate(self.pos.x, self.pos.y + 1, self.pos.z + 1),
            ]

    def get_center(self):
        return Coordinate(
            self.pos.x + 0.5,
            self.pos.y + 0.25 if self.bottom else self.pos.y + 0.75,
            self.pos.z + 0.5,
        )


class BlockStairs(GenericBlock):
    """A stair block"""

    # add direction and top/bottom properties also
    def __init__(
        self, pos: Coordinate, color, direction="n", bottom=True, transparent=False
    ):
        super().__init__(pos, color, transparent)
        self.facemap = [
            (0, 1, 2, 3),  # back
            (1, 4, 5, 2),  # bottom
            (4, 7, 6, 5),  # front of step1
            (8, 9, 3, 2, 5, 6),  # left side
            (10, 7, 4, 1, 0, 11),  # right side
            (8, 6, 7, 10),  # top of step1
            (8, 10, 11, 9),  # front of step2
            (3, 9, 11, 0),  # top of step2
        ]
        self.direction = direction
        self.bottom = bottom
        self.baseoffsets = [
            Coordinate(1, 1, 0),
            Coordinate(1, 0, 0),
            Coordinate(0, 0, 0),
            Coordinate(0, 1, 0),
            Coordinate(1, 0, 1),
            Coordinate(0, 0, 1),
            Coordinate(0, 0.5, 1),
            Coordinate(1, 0.5, 1),
            Coordinate(0, 0.5, 0.5),
            Coordinate(0, 1, 0.5),
            Coordinate(1, 0.5, 0.5),
            Coordinate(1, 1, 0.5),
        ]
        self.currentoffsets = self.baseoffsets
        self.verts = self._calc_verts()
        self.faces = self._calc_faces()

    def _calc_verts(self):
        """calculate vertices of block for caching"""
        if self.direction == "n":
            pass  # default, facing +z
        elif self.direction == "e":
            # facing +x
            self.currentoffsets = [
                Coordinate(c.z, c.y, 1 - c.x) for c in self.baseoffsets
            ]
        elif self.direction == "s":
            # facing -z
            self.currentoffsets = [
                Coordinate(1 - c.x, c.y, 1 - c.z) for c in self.baseoffsets
            ]
        elif self.direction == "w":
            # facing -x
            self.currentoffsets = [
                Coordinate(1 - c.z, c.y, c.x) for c in self.baseoffsets
            ]
        if not self.bottom:  # flip the block
            self.currentoffsets = [
                Coordinate(1 - c.x, 1 - c.y, c.z) for c in self.baseoffsets
            ]
        return [self.pos + offset for offset in self.currentoffsets]

    def get_center(self):  # varies based on direction/top/bottom
        return Coordinate(self.pos.x + 0.5, self.pos.y + 0.5, self.pos.z + 0.5)


class BlockVerticalSlab(GenericBlock):
    """A vertical slab that's half the width of a normal block (0.5x1x1)"""

    def __init__(self, pos: Coordinate, color, left=True, transparent=False):
        super().__init__(pos, color, transparent)
        self.facemap = [
            (0, 3, 2, 1),  # Front face (-z)
            (4, 5, 6, 7),  # Back face (+z)
            (0, 1, 5, 4),  # Bottom face (-y)
            (2, 3, 7, 6),  # Top face (+y)
            (1, 2, 6, 5),  # Right face (+x)
            (0, 4, 7, 3),  # Left face (-x)
        ]
        self.left = left
        self.verts = self._calc_verts()
        self.faces = self._calc_faces()

    def _calc_verts(self):
        """calculate vertices of block for caching"""
        if self.left:
            return [
                Coordinate(self.pos.x, self.pos.y, self.pos.z),
                Coordinate(self.pos.x + 0.5, self.pos.y, self.pos.z),
                Coordinate(self.pos.x + 0.5, self.pos.y + 1, self.pos.z),
                Coordinate(self.pos.x, self.pos.y + 1, self.pos.z),
                Coordinate(self.pos.x, self.pos.y, self.pos.z + 1),
                Coordinate(self.pos.x + 0.5, self.pos.y, self.pos.z + 1),
                Coordinate(self.pos.x + 0.5, self.pos.y + 1, self.pos.z + 1),
                Coordinate(self.pos.x, self.pos.y + 1, self.pos.z + 1),
            ]
        else:
            return [
                Coordinate(self.pos.x + 0.5, self.pos.y, self.pos.z),
                Coordinate(self.pos.x + 1, self.pos.y, self.pos.z),
                Coordinate(self.pos.x + 1, self.pos.y + 1, self.pos.z),
                Coordinate(self.pos.x + 0.5, self.pos.y + 1, self.pos.z),
                Coordinate(self.pos.x + 0.5, self.pos.y, self.pos.z + 1),
                Coordinate(self.pos.x + 1, self.pos.y, self.pos.z + 1),
                Coordinate(self.pos.x + 1, self.pos.y + 1, self.pos.z + 1),
                Coordinate(self.pos.x + 0.5, self.pos.y + 1, self.pos.z + 1),
            ]

    def get_center(self):
        return Coordinate(
            self.pos.x + 0.25 if self.left else self.pos.x + 0.75,
            self.pos.y + 0.5,
            self.pos.z + 0.5,
        )


class Model(GenericBlock):
    """A generic model block"""

    def __init__(self, pos: Coordinate, color, facemap, verts, transparent=False):
        super().__init__(pos, color, transparent)
        self.facemap = facemap
        self.offsets = verts
        self.verts = self._calc_verts()
        self.faces = self._calc_faces()

    def _calc_verts(self):
        """calculate vertices of block for caching"""
        return [self.pos + offset for offset in self.offsets]

    def get_center(self):
        return Coordinate(self.pos.x + 0.5, self.pos.y + 0.5, self.pos.z + 0.5)
