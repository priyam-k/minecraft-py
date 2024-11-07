import math

import pygame
import pygame.gfxdraw

pygame.init()
screen_surf = pygame.display.set_mode(
    (800, 600), pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.HWSURFACE
)
pygame.display.set_caption("3D thingies")
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)


def cos(x):
    return math.cos(math.radians(x))


def sin(x):
    return math.sin(math.radians(x))


def tan(x):
    return math.tan(math.radians(x))


class Coordinate:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def get(self) -> tuple:
        return (self.x, self.y, self.z)

    def copy(self):
        return Coordinate(self.x, self.y, self.z)

    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"

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


class GenericBlock:
    """A generic block template"""

    def __init__(self, pos: Coordinate, color, transparent=False):
        self.pos = pos
        self.color = color
        self.transparent = transparent
        self.verts = None
        self.facemap = None
        self.faces = None
        self.hitbox = Hitbox(self.pos, Coordinate(0, 0, 0), Coordinate(1, 1, 1))
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

    def get_faces(self):
        """get cached faces of block"""
        return self.faces


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


class BlockModel(GenericBlock):
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


class World:
    def __init__(self):
        self.blocks = {}
        self.entities = {}

    def add_entity(self, entity):
        self.entities[entity.id] = entity

    def remove_entity(self, entity):
        eid = entity.id
        if eid in self.entities:
            del self.entities[eid]

    def set_block(self, block: GenericBlock):
        self.blocks[block.pos.get()] = block

    def add_block(self, block: GenericBlock):
        if block.pos.get() not in self.blocks:
            self.set_block(block)
        else:
            print("Block already exists at position.")

    def remove_block(self, pos: Coordinate):
        tpos = pos.get()
        if tpos in self.blocks:
            del self.blocks[tpos]

    def get_block(self, pos: Coordinate) -> GenericBlock | None:
        return self.blocks.get(pos.get(), None)


class Hitbox:
    def __init__(self, pos: Coordinate, start: Coordinate, end: Coordinate):
        self.pos = pos
        self.start = start
        self.end = end

    def contains(self, pt: Coordinate):  # TODO FIX LATER THIS ISNT REAL
        return (
            self.pos.x <= pt.x <= self.pos.x + self.size.x
            and self.pos.y <= pt.y <= self.pos.y + self.size.y
            and self.pos.z <= pt.z <= self.pos.z + self.size.z
        )

    def get_start(self):
        return self.pos + self.start

    def get_end(self):
        return self.pos + self.end

    def __str__(self):
        return f"Hitbox at {self.pos} with start {self.pos + self.start} and end {self.pos + self.end}"

    def new(self, pos: Coordinate):
        return Hitbox(pos, self.start, self.end)

    def collides(self, other: "Hitbox"):
        starta = self.pos + self.start
        enda = self.pos + self.end
        startb = other.pos + other.start
        endb = other.pos + other.end

        if not (enda.x > startb.x and endb.x > starta.x):
            return False
        # Check overlap on the y-axis
        if not (enda.y > startb.y and endb.y > starta.y):
            return False
        # Check overlap on the z-axis
        if not (enda.z > startb.z and endb.z > starta.z):
            return False

        # Overlaps on all axes, so there's a collision
        return True

        return (
            self.pos.x < other.pos.x + other.size.x
            and self.pos.x + self.size.x > other.pos.x
            and self.pos.y < other.pos.y + other.size.y
            and self.pos.y + self.size.y > other.pos.y
            and self.pos.z < other.pos.z + other.size.z
            and self.pos.z + self.size.z > other.pos.z
        )


class Entity:
    def __init__(self, pos: Coordinate, world: World):
        self.pos = pos
        self.world = world
        self.id = id(self)
        self.yaw = 0  # left/right
        self.pitch = 0  # up/down
        self.cam_offset = None
        self.hitbox = None
        self.surrounding = None

    def initcam(self):
        self.cam = Camera(self.pos.copy() + self.cam_offset, self.yaw, self.pitch)

    def movecam(self, dx=0, dy=0, dz=0, dyaw=0, dpitch=0):
        """overloadable for custom camera movement"""
        self.cam.move(dx, dy, dz)
        self.cam.rotate(dyaw, dpitch)

    def tpcam(self, pos: Coordinate):
        """overloadable for custom camera teleportation"""
        self.cam.teleport(pos)

    def _xmove(self, dx):
        """move the entity by dx"""
        self.pos.x += dx
        self.movecam(dx=dx)

    def _ymove(self, dy):
        """move the entity by dy"""
        self.pos.y += dy
        self.movecam(dy=dy)

    def _zmove(self, dz):
        """move the entity by dz"""
        self.pos.z += dz
        self.movecam(dz=dz)

    def move(self, dx, dy, dz):
        collided = False
        snap_pos = Coordinate(
            math.floor(self.pos.x + dx),
            math.floor(self.pos.y + dy),
            math.floor(self.pos.z + dz),
        )
        next_hitbox = self.hitbox.new(self.pos + Coordinate(dx, dy, dz))
        for pos in self.surrounding:  # check for collision
            blk = world.get_block(snap_pos + pos)
            if blk is not None and blk.hitbox.collides(next_hitbox):
                collided = True
                break

        if collided:  # check directional collision
            next_hitbox_x = self.hitbox.new(self.pos + Coordinate(dx, 0, 0))
            next_hitbox_y = self.hitbox.new(self.pos + Coordinate(0, dy, 0))
            next_hitbox_z = self.hitbox.new(self.pos + Coordinate(0, 0, dz))
            for pos in self.surrounding:
                blk = world.get_block(snap_pos + pos)
                if blk is not None and blk.hitbox.collides(
                    next_hitbox_x
                ):  # collides in X
                    print("Collided in X")
                    dx = 0
                if blk is not None and blk.hitbox.collides(
                    next_hitbox_y
                ):  # collides in Y
                    print("Collided in Y")
                    dy = 0
                if blk is not None and blk.hitbox.collides(
                    next_hitbox_z
                ):  # collides in Z
                    print("Collided in Z")
                    dz = 0

        self._xmove(dx)
        self._ymove(dy)
        self._zmove(dz)

    def walk(self, f, r):
        self.move(
            f * sin(self.yaw) + r * cos(self.yaw),
            0,
            f * cos(self.yaw) - r * sin(self.yaw),
        )

    def rotate(self, dyaw, dpitch):
        self.movecam(dyaw=dyaw, dpitch=dpitch)
        self.yaw = (self.yaw + dyaw) % 360
        self.pitch = max(min(self.pitch + dpitch, 90), -90)

    def teleport(self, pos: Coordinate):
        self.pos = pos.copy()
        self.tpcam(pos + self.cam_offset)

    def get_pos(self):
        return self.pos


class Player(Entity):
    def __init__(self, pos: Coordinate, world: World):
        super().__init__(pos, world)
        self.cam_offset = Coordinate(0, 1.6, 0)
        self.initcam()
        self.hitbox = Hitbox(
            self.pos, Coordinate(-0.3, 0, -0.3), Coordinate(0.3, 1.8, 0.3)
        )  # hitbox tied to self.pos
        self.surrounding = [
            Coordinate(0, -1, 0),
            Coordinate(0, 0, 0),
            Coordinate(-1, 0, 0),
            Coordinate(-1, 0, -1),
            Coordinate(0, 0, -1),
            Coordinate(1, 0, -1),
            Coordinate(1, 0, 0),
            Coordinate(1, 0, 1),
            Coordinate(0, 0, 1),
            Coordinate(-1, 0, 1),
            Coordinate(0, 1, 0),
            Coordinate(-1, 1, 0),
            Coordinate(-1, 1, -1),
            Coordinate(0, 1, -1),
            Coordinate(1, 1, -1),
            Coordinate(1, 1, 0),
            Coordinate(1, 1, 1),
            Coordinate(0, 1, 1),
            Coordinate(-1, 1, 1),
            Coordinate(0, 2, 0),
        ]
        # end init
        self.cam3dist = 2
        self.cam3 = Camera(
            self.pos.copy() + self.cam_offset + Coordinate(0, 0, -self.cam3dist),
            self.yaw,
            self.pitch,
        )  # scuffed 3rd person cam

    def movecam(self, dx=0, dy=0, dz=0, dyaw=0, dpitch=0):
        self.cam.move(dx, dy, dz)
        self.cam.rotate(dyaw, dpitch)
        self.cam3.teleport(
            self.pos
            + self.cam_offset
            + Coordinate(
                -self.cam3dist * sin(self.yaw), 0, -self.cam3dist * cos(self.yaw)
            )
        )
        # self.cam3.move(dx, dy, dz)
        self.cam3.rotate(dyaw, dpitch)

    def tpcam(self, pos: Coordinate):
        self.cam.teleport(pos + self.cam_offset)
        self.cam3.teleport(pos + self.cam_offset + Coordinate(0, 0, -self.cam3dist))


class Camera:
    # def __init__(self, plyr: Player):
    #     self.pos = plyr.pos
    #     self.yaw = plyr.yaw
    #     self.pitch = plyr.pitch
    #     self.fov = 90
    #     self.near = 0.1
    #     self.far = 1000

    def __init__(self, pos, yaw=0, pitch=0, fov=90, near=0.1, far=1000):
        self.pos = pos
        self.yaw = yaw
        self.pitch = pitch
        self.fov = fov
        self.near = near
        self.far = far

    def move(self, dx, dy, dz):
        self.pos.x += dx
        self.pos.y += dy
        self.pos.z += dz

    def rotate(self, dyaw, dpitch):
        self.yaw = (self.yaw + dyaw) % 360
        self.pitch = max(min(self.pitch + dpitch, 90), -90)

    def teleport(self, pos: Coordinate):
        self.pos = pos.copy()

    def project(self, pt: Coordinate):
        """project a 3d point onto the 2d screen in this camera's view"""
        # translate to camera space
        tx = pt.x - self.pos.x
        ty = pt.y - self.pos.y
        tz = pt.z - self.pos.z

        # rotate yaw (vertical)
        rx = tx * cos(self.yaw) - tz * sin(self.yaw)
        rz = tx * sin(self.yaw) + tz * cos(self.yaw)

        # rotate pitch (hor)
        ry = ty * cos(self.pitch) - rz * sin(self.pitch)
        rz = ty * sin(self.pitch) + rz * cos(self.pitch)

        # clip to near/far planes
        if rz < self.near or rz > self.far:
            return None

        # project onto 2d
        if rz == 0:
            rz = 0.0001
        normx = rx / rz * tan(self.fov / 2)
        normy = ry / rz * tan(self.fov / 2)

        return (normx, normy)

    def project_face(self, face: Face):
        """project a face onto the 2d screen in this camera's view"""
        return [self.project(v) for v in face.get_vertices()]

    def project_block(self, block: GenericBlock):
        """project a block onto the 2d screen in this camera's view"""

        faces = block.get_faces()
        for face in faces:
            proj_verts = [self.project(v) for v in face.get_vertices()]
            zdist = self.get_zdist(face.get_center())

        vertices = block.get_vertices()
        pts = [self.project(v) for v in vertices]

        # DEBUG
        # for idx, pt in enumerate(pts):
        #     if pt is None:
        #         print(f"Vertex {idx} is out of view and not rendered.")

        return pts

    def get_zdist(self, pt: Coordinate):
        """get the distance from the camera to a point"""
        return math.sqrt(
            (pt.x - self.pos.x) ** 2
            + (pt.y - self.pos.y) ** 2
            + (pt.z - self.pos.z) ** 2
        )

    def get_normal(self):
        """get the normal of the camera"""
        return (
            cos(self.yaw) * cos(self.pitch),
            sin(self.pitch),
            sin(self.yaw) * cos(self.pitch),
        )


class GameOptions:
    def __init__(self):
        self.show_debug_info = True
        self.sensitivity = 0.2
        self.show_fps = True
        self.visual_debug = {
            "hitbox-dots": False,
            "normals": False,
            "player-hitbox": False,
            "player-model": True,
        }

    def toggle_debug_info(self):
        self.show_debug_info = not self.show_debug_info


class Screen:
    def __init__(self, surface: pygame.Surface, camera: Camera, options: GameOptions):
        self.surface = surface
        self.camera = camera
        self.options = options

    def set_camera(self, camera: Camera):
        """change camera view"""
        self.camera = camera

    def clear(self, update=False):
        self.surface.fill((107, 181, 237))
        if update:
            pygame.display.flip()

    def render_debug_info(self, player: Player):
        """Draws the debug information on the screen."""
        pos_text = (
            f"Position: ({player.pos.x:.2f}, {player.pos.y:.2f}, {player.pos.z:.2f})"
        )
        yaw_text = f"Yaw: {player.yaw:.2f}°"
        pitch_text = f"Pitch: {player.pitch:.2f}°"

        pos_surf = font.render(pos_text, True, (255, 255, 255))
        yaw_surf = font.render(yaw_text, True, (255, 255, 255))
        pitch_surf = font.render(pitch_text, True, (255, 255, 255))

        # Display in top-right corner
        self.surface.blit(
            pos_surf, (self.surface.get_width() - pos_surf.get_width() - 10, 10)
        )
        self.surface.blit(
            yaw_surf, (self.surface.get_width() - yaw_surf.get_width() - 10, 40)
        )
        self.surface.blit(
            pitch_surf, (self.surface.get_width() - pitch_surf.get_width() - 10, 70)
        )

    def denormalize(self, x, y):
        """convert normalized screen coordinates to screen coordinates by scaling by screen width"""
        return (
            int((x + 1) * 0.5 * self.surface.get_width()),
            int((1 - y) * 0.5 * self.surface.get_width()),
        )

    def render_point(self, *pts3d: Coordinate, color=(255, 255, 255)):
        for pt3d in pts3d:
            pt = self.camera.project(pt3d)
            if pt is not None:
                scrn = self.denormalize(*pt)
                pygame.draw.circle(self.surface, color, scrn, 5)

        """
        HEYYY WHEN I OCME BACK!!
        gpt ignore this vvv
        make culling acc work like
        dont render things ouside of frustrum, backface culling, etc
        maybe work on perspectives like 1st and 3rd
        collision!!
        """

    def render_face(self, face: Face, outline=False):
        """render a Face onto screen"""

        if face is None:
            return

        proj_verts = self.camera.project_face(face)

        # if any of the vertices are None, don't render the face
        if None in proj_verts:
            return

        scrn_verts = [
            self.denormalize(*pt) for pt in proj_verts
        ]  # denormalize vertices to screen coords
        # then draw vertices
        pygame.draw.polygon(self.surface, face.color, scrn_verts)  # draw face
        if outline:
            pygame.draw.aalines(
                self.surface, (0, 0, 0), True, scrn_verts, 1
            )  # draw antialiased lines around face

        if self.options.visual_debug["normals"]:  # draw face normals
            face_center = face.get_center()
            face_normal = face.get_normal()
            normal_end = Coordinate(
                face_center.x + face_normal[0] / 2,
                face_center.y + face_normal[1] / 2,
                face_center.z + face_normal[2] / 2,
            )
            proj_center = self.camera.project(face_center)
            proj_normal_end = self.camera.project(normal_end)
            if proj_center and proj_normal_end:
                scrn_center = self.denormalize(*proj_center)
                scrn_normal_end = self.denormalize(*proj_normal_end)
                pygame.draw.line(
                    self.surface, (255, 0, 0), scrn_center, scrn_normal_end, 2
                )

    def render_block(self, block: GenericBlock, outline=False):
        """render a Block onto screen"""

        faces = block.get_faces()
        if not block.transparent:  # don't cull transparent blockfaces
            # backface culling
            culled_faces = []
            for face in faces:
                if face is None:
                    continue
                face_center = face.get_center()
                cam_to_face = face_center - self.camera.pos
                fn = face.get_normal()
                # dot prod of normals
                dn = (
                    fn[0] * cam_to_face.x
                    + fn[1] * cam_to_face.y
                    + fn[2] * cam_to_face.z
                )
                if dn < 0:
                    culled_faces.append(face)
            faces = culled_faces
        # z-order faces and render
        faces.sort(
            key=lambda x: 0 if x is None else self.camera.get_zdist(x.get_center()),
            reverse=True,
        )
        for face in faces:
            self.render_face(face, outline=outline)

        if self.options.visual_debug["hitbox-dots"]:
            hitbox = block.hitbox
            start = hitbox.get_start()
            end = hitbox.get_end()
            self.render_point(start, end, color=(0, 255, 0))
            # proj_start = self.camera.project(start)
            # proj_end = self.camera.project(end)
            # if proj_start and proj_end:
            #     scrn_start = self.denormalize(*proj_start)
            #     scrn_end = self.denormalize(*proj_end)
            #     pygame.draw.rect(self.surface, (255, 0, 0), (scrn_start, scrn_end), 2)

    def render_model(self, model: BlockModel, outline=False):
        """render a BlockModel onto screen"""
        self.render_block(model, outline=outline)

    def render(self, world: World, points, update=False):
        self.render_point(*points)
        blocks = world.blocks.values()
        blocks = sorted(
            blocks, key=lambda x: self.camera.get_zdist(x.get_center()), reverse=True
        )
        for block in blocks:
            self.render_block(block, outline=True)
        for entity in world.entities.values():
            if self.options.visual_debug["player-hitbox"]:
                hitbox = entity.hitbox
                start = hitbox.get_start()
                end = hitbox.get_end()
                self.render_point(start, end, color=(0, 255, 0))
            if self.options.visual_debug["player-model"]:
                model = BlockModel(
                    entity.get_pos(),
                    (255, 0, 0, 0.1),
                    [
                        (2, 1, 0),
                        (0, 3, 2),
                        (4, 2, 3),
                        (3, 5, 4),
                        (6, 4, 5),
                        (5, 7, 6),
                        (7, 6, 1),
                        (1, 0, 7),
                        (3, 0, 7),
                        (7, 5, 3),
                        (1, 2, 4),
                        (4, 6, 1),
                    ],
                    [
                        Coordinate(0.3, 1.8, 0.3),
                        Coordinate(0.3, 0.0, 0.3),
                        Coordinate(0.3, 0.0, -0.3),
                        Coordinate(0.3, 1.8, -0.3),
                        Coordinate(-0.3, 0.0, -0.3),
                        Coordinate(-0.3, 1.8, -0.3),
                        Coordinate(-0.3, 0.0, 0.3),
                        Coordinate(-0.3, 1.8, 0.3),
                    ],
                    transparent=True,
                )
                self.render_block(model, outline=True)
        if update:
            pygame.display.flip()


world = World()
user = Player(Coordinate(0, 2, 0), world)
options = GameOptions()
screen = Screen(screen_surf, user.cam, options)
world.add_entity(user)

points = [
    Coordinate(0, 0, 0),
    Coordinate(1, 0, 0),
    Coordinate(1, 1, 0),
    Coordinate(0, 1, 0),
    Coordinate(0, 0, 1),
    Coordinate(1, 0, 1),
    Coordinate(1, 1, 1),
    Coordinate(0, 1, 1),
]
world.add_block(Block(Coordinate(0, 0, 0), (255, 0, 0)))
world.add_block(Block(Coordinate(1, 3, 5), (100, 150, 255)))

for i in range(-8, 10):
    for j in range(-10, 8):
        world.add_block(Block(Coordinate(i, 0, j), (112, 168, 101)))

world.add_block(BlockSlab(Coordinate(0, 2, 2), (112, 168, 101)))
world.add_block(BlockSlab(Coordinate(1, 2, 0), (112, 168, 101), bottom=False))
world.add_block(BlockStairs(Coordinate(4, 2, 0), (112, 168, 101)))
world.add_block(BlockStairs(Coordinate(6, 2, 0), (190, 168, 50), bottom=False))
world.add_block(BlockStairs(Coordinate(8, 2, 0), (190, 168, 50), direction="s"))
world.add_block(BlockStairs(Coordinate(10, 2, 0), (190, 168, 50), direction="e"))
world.add_block(BlockStairs(Coordinate(12, 2, 0), (190, 168, 50), direction="w"))
world.add_block(BlockVerticalSlab(Coordinate(14, 2, 0), (190, 168, 50)))
world.add_block(BlockVerticalSlab(Coordinate(16, 2, 0), (190, 168, 50), left=False))
world.add_block(BlockVerticalSlab(Coordinate(16, 2, 3), (190, 168, 50, 0), left=False))


running = True
while running:
    # GAME INPUT!!
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F3:
                options.toggle_debug_info()
            if event.key == pygame.K_F11:
                # pygame.display.toggle_fullscreen()
                # if pygame.display.is_fullscreen():
                screen_surf = pygame.display.set_mode(
                    (1920, 1080),
                    pygame.FULLSCREEN
                    | pygame.RESIZABLE
                    | pygame.DOUBLEBUF
                    | pygame.HWSURFACE,
                )
                screen.surface = screen_surf
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_F5:
                screen.set_camera(user.cam3)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT]:
        user.move(0.1, 0, 0)
    if keys[pygame.K_LEFT]:
        user.move(-0.1, 0, 0)
    if keys[pygame.K_UP]:
        user.move(0, 0, 0.1)
    if keys[pygame.K_DOWN]:
        user.move(0, 0, -0.1)
    if keys[pygame.K_w]:
        user.walk(0.1, 0)
    if keys[pygame.K_s]:
        user.walk(-0.1, 0)
    if keys[pygame.K_a]:
        user.walk(0, -0.1)
    if keys[pygame.K_d]:
        user.walk(0, 0.1)
    if keys[pygame.K_SPACE]:
        user.move(0, 0.1, 0)
    if keys[pygame.K_LSHIFT]:
        user.move(0, -0.1, 0)
    if keys[pygame.K_r]:
        user.teleport(Coordinate(0, 2, 0))

    mouse_dx, mouse_dy = pygame.mouse.get_rel()
    user.rotate(mouse_dx * options.sensitivity, -mouse_dy * options.sensitivity)

    screen.clear()
    screen.render(world, points)
    if options.show_debug_info:
        screen.render_debug_info(user)

    # snap_pos = Coordinate(
    #     math.floor(user.pos.x), math.floor(user.pos.y), math.floor(user.pos.z)
    # )
    # surrounding = [
    #     Coordinate(0, 0, 0),
    #     Coordinate(1, 0, 0),
    #     Coordinate(-1, 0, 0),
    #     Coordinate(0, 1, 0),
    #     Coordinate(0, -1, 0),
    #     Coordinate(0, 0, 1),
    #     Coordinate(0, 0, -1),
    # ]
    # for pos in surrounding:
    #     blk = world.get_block(snap_pos + pos)
    #     # print(blk)
    #     if blk is None:
    #         pass  # world.add_block(Block(pos, (0, 255, 0)))
    #     elif blk.hitbox.collides(user.hitbox):
    #         print(f"Collided with block!!! {blk.pos.get()}")
    # below = world.get_block(snap_pos - Coordinate(0, 1, 0))
    # if below is None:
    #     pass  # print(f"No block below, current: {snap_pos.get()}, hb: {user.hitbox}")
    # elif below.hitbox.collides(user.hitbox):
    #     print("Collided with block below")
    # else:
    #     print(
    #         f"No collision with block below, current: {snap_pos.get()}, below: {below.pos.get()}"
    #     )

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
