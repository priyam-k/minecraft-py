import pygame
import math

pygame.init()
screen_surf = pygame.display.set_mode(
    (800, 600), pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.HWSURFACE
)
pygame.display.set_caption("3D thingies")

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
        """get the normal of the face"""
        # get two vectors on the face
        v1 = self.vertices[1] - self.vertices[0]
        v2 = self.vertices[2] - self.vertices[0]
        # cross product of the two vectors is the normal
        return (
            v1.y * v2.z - v1.z * v2.y,
            v1.z * v2.x - v1.x * v2.z,
            v1.x * v2.y - v1.y * v2.x,
        )


class Block:
    def __init__(self, pos: Coordinate, color, transparent=False):
        self.pos = pos
        self.color = color
        self.transparent = transparent
        self.verts = self._calc_verts()
        self.facemap = [
            (0, 1, 2, 3),  # Front face
            (4, 5, 6, 7),  # Back face
            (0, 1, 5, 4),  # Bottom face
            (2, 3, 7, 6),  # Top face
            (1, 2, 6, 5),  # Right face
            (0, 3, 7, 4),  # Left face
        ]
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

    def _calc_faces(self):
        """calculate faces of block for caching"""
        return [
            Face([self.verts[i] for i in face], color=self.color)
            for face in self.facemap
        ]

    def get_vertices(self) -> list[Coordinate]:
        """get cached vertices of block"""
        return self.verts

    def get_center(self) -> Coordinate:
        """get center of block"""
        return Coordinate(self.pos.x + 0.5, self.pos.y + 0.5, self.pos.z + 0.5)

    def get_faces(self):
        """get cached faces of block"""
        return self.faces


class Player:
    def __init__(self, pos=Coordinate(0, 0, 0)):
        self.pos = pos
        self.yaw = 0  # left/right
        self.pitch = 0  # up/down
        self.cam = Camera(self)

    def move(self, dx, dy, dz):
        """move the player by dx, dy, dz"""
        self.cam.move(dx, dy, dz)
        self.pos.x += dx
        self.pos.y += dy
        self.pos.z += dz

    def walk(self, f, r):
        """walk in the direction of the player's yaw, f units forward, r units right"""
        self.move(
            f * sin(self.yaw) + r * cos(self.yaw),
            0,
            f * cos(self.yaw) - r * sin(self.yaw),
        )

    def rotate(self, dyaw, dpitch):
        """rotate the player by dyaw, dpitch"""
        self.cam.rotate(dyaw, dpitch)
        self.yaw = (self.yaw + dyaw) % 360
        self.pitch = max(min(self.pitch + dpitch, 90), -90)

    def teleport(self, pos: Coordinate):
        """teleport the player to given position"""
        self.cam.teleport(pos)
        self.pos = pos


class Camera:
    def __init__(self, plyr: Player):
        self.fov = 90
        self.near = 0.1
        self.far = 1000
        self.pos = plyr.pos
        self.yaw = plyr.yaw
        self.pitch = plyr.pitch

    # def __init__(self, fov=90, near=0.1, far=1000, x=0, y=0, z=0, yaw=0, pitch=0):
    #     self.fov = fov
    #     self.near = near
    #     self.far = far
    #     self.x = x
    #     self.y = y
    #     self.z = z
    #     self.yaw = yaw
    #     self.pitch = pitch

    def move(self, dx, dy, dz):
        self.pos.x += dx
        self.pos.y += dy
        self.pos.z += dz

    def rotate(self, dyaw, dpitch):
        self.yaw = (self.yaw + dyaw) % 360
        self.pitch = max(min(self.pitch + dpitch, 90), -90)

    def teleport(self, pos: Coordinate):
        self.pos = pos

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
        normx = rx / rz * tan(self.fov / 2)
        normy = ry / rz * tan(self.fov / 2)

        return (normx, normy)

    def project_face(self, face: Face):
        """project a face onto the 2d screen in this camera's view"""
        return [self.project(v) for v in face.get_vertices()]

    def project_block(self, block: Block):
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


class Screen:
    def __init__(self, surface: pygame.Surface, camera: Camera):
        self.surface = surface
        self.camera = camera

    def set_camera(self, camera: Camera):
        """change camera view"""
        self.camera = camera

    def clear(self, update=False):
        self.surface.fill((0, 0, 0))
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

    def render_face(self, face: Face):
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
        pygame.draw.lines(
            self.surface, (0, 200, 0), True, scrn_verts, 1
        )  # draw lines around face

    def render_block(self, block: Block):
        """render a Block onto screen"""

        faces = block.get_faces()
        culled_faces = []
        for face in faces:
            if face is None:
                continue
            fn = face.get_normal()
            cn = self.camera.get_normal()
            dn = fn[0]*cn[0] + fn[1]*cn[1] + fn[2]*cn[2]
            if dn < 0:
                culled_faces.append(face)
        faces = culled_faces
        # z-order faces and render
        faces.sort(key=lambda x: 0 if x is None else self.camera.get_zdist(x.get_center()), reverse=True)
        for face in faces:
            self.render_face(face)

        # proj_verts = self.camera.project_block(block)

        # # if any of the vertices are None, don't render the block
        # if None in proj_verts:
        #     return

        # faces = [
        #     (0, 1, 2, 3),  # Front face
        #     (4, 5, 6, 7),  # Back face
        #     (0, 1, 5, 4),  # Bottom face
        #     (2, 3, 7, 6),  # Top face
        #     (1, 2, 6, 5),  # Right face
        #     (0, 3, 7, 4),  # Left face
        # ]

        # # z-ordering the faces
        # f_ord = []
        # bv = block.get_vertices()
        # for f in faces:  # for each face
        #     face_verts = [bv[i] for i in f]  # get the vertices of the face
        #     avg = Coordinate.add(*face_verts) / len(face_verts)
        #     f_ord.append((avg, f))  # zip avg with face
        # f_ord = sorted(f_ord, key=lambda x: self.camera.get_zdist(x[0]), reverse=True)
        # faces = [f for a, f in f_ord]  # unpack the faces

        # for face in faces:
        #     face_verts = [
        #         proj_verts[i] for i in face
        #     ]  # unpack face vertices -> list of 2d points for a face
        #     scrn_verts = [
        #         self.denormalize(*pt) for pt in face_verts
        #     ]  # denormalize vertices to screen coords
        #     pygame.draw.polygon(self.surface, block.color, scrn_verts)  # draw face
        #     pygame.draw.lines(
        #         self.surface, (0, 200, 0), True, scrn_verts, 1
        #     )  # draw lines around face

    def render(self, blocks: list[Block], points, update=False):
        self.render_point(*points)
        blocks = sorted(
            blocks, key=lambda x: self.camera.get_zdist(x.get_center()), reverse=True
        )
        for block in blocks:
            self.render_block(block)
        if update:
            pygame.display.flip()


class GameOptions:
    def __init__(self):
        self.show_debug_info = True
        self.sensitivity = 0.2

    def toggle_debug_info(self):
        self.show_debug_info = not self.show_debug_info


user = Player()
screen = Screen(screen_surf, user.cam)
options = GameOptions()

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
blocks = [Block(Coordinate(1, 3, 5), (100, 150, 255))]

for i in range(-10, 10):
    for j in range(-10, 10):
        blocks.append(Block(Coordinate(i, 0, j), (112, 168, 101)))

running = True
while running:
    # GAME INPUT!!
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F3:
                options.toggle_debug_info()
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
        user.teleport(Coordinate(0, 0, 0))

    mouse_dx, mouse_dy = pygame.mouse.get_rel()
    user.rotate(mouse_dx * options.sensitivity, -mouse_dy * options.sensitivity)

    screen.clear()
    screen.render(blocks, points)
    if options.show_debug_info:
        screen.render_debug_info(user)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
