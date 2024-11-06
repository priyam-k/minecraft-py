import pygame
import math

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
    def __init__(self, pos: Coordinate, color, direction="n" ,bottom=True, transparent=False):
        super().__init__(pos, color, transparent)
        self.facemap = [
            (0, 1, 2, 3), # back
            (1, 4, 5, 2), # bottom
            (4, 7, 6, 5), # front of step1
            (8, 9, 3, 2, 5, 6), # left side
            (10, 7, 4, 1, 0, 11), # right side
            (8, 6, 7, 10), # top of step1
            (8, 10, 11, 9), # front of step2
            (3, 9, 11, 0) # top of step2
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
            pass # default, facing +z
        elif self.direction == "e":
            # facing +x
            self.currentoffsets = [Coordinate(c.z, c.y, 1-c.x) for c in self.baseoffsets]
        elif self.direction == "s":
            # facing -z
            self.currentoffsets = [Coordinate(1-c.x, c.y, 1-c.z) for c in self.baseoffsets]
        elif self.direction == "w":
            # facing -x
            self.currentoffsets = [Coordinate(1-c.z, c.y, c.x) for c in self.baseoffsets]
        if not self.bottom: # flip the block
            self.currentoffsets = [Coordinate(1-c.x, 1-c.y, c.z) for c in self.baseoffsets]
        return [self.pos + offset for offset in self.currentoffsets]

    def get_center(self): # varies based on direction/top/bottom
        return Coordinate(self.pos.x + 0.5, self.pos.y + 0.5, self.pos.z + 0.5)

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

    def render_face(self, face: Face, outline=False, debug_normals=False):
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
            pygame.draw.lines(
                self.surface, (0, 200, 0), True, scrn_verts, 1
            )  # draw lines around face
        
        if debug_normals: # draw face normals
            face_center = face.get_center()
            face_normal = face.get_normal()
            normal_end = Coordinate(
                face_center.x + face_normal[0]/2,
                face_center.y + face_normal[1]/2,
                face_center.z + face_normal[2]/2,
            )
            proj_center = self.camera.project(face_center)
            proj_normal_end = self.camera.project(normal_end)
            if proj_center and proj_normal_end:
                scrn_center = self.denormalize(*proj_center)
                scrn_normal_end = self.denormalize(*proj_normal_end)
                pygame.draw.line(self.surface, (255, 0, 0), scrn_center, scrn_normal_end, 2)

    def render_block(self, block: Block, outline=False, debug_normals=False):
        """render a Block onto screen"""

        faces = block.get_faces()
        # Temporarily remove backface culling
        culled_faces = []
        for face in faces:
            if face is None:
                continue
            face_center = face.get_center()
            cam_to_face = face_center - self.camera.pos

            # cn = self.camera.get_normal()
            fn = face.get_normal()
            dn = fn[0] * cam_to_face.x + fn[1] * cam_to_face.y + fn[2] * cam_to_face.z
            if dn < 0:
                culled_faces.append(face)
        faces = culled_faces
        # z-order faces and render
        faces.sort(
            key=lambda x: 0 if x is None else self.camera.get_zdist(x.get_center()),
            reverse=True,
        )
        for face in faces:
            self.render_face(face, outline=outline, debug_normals=debug_normals)

    def render(self, blocks: list[Block], points, update=False, debug_normals=False):
        self.render_point(*points)
        blocks = sorted(
            blocks, key=lambda x: self.camera.get_zdist(x.get_center()), reverse=True
        )
        for block in blocks:
            self.render_block(block, outline=True, debug_normals=debug_normals)
        if update:
            pygame.display.flip()


class GameOptions:
    def __init__(self):
        self.show_debug_info = True
        self.sensitivity = 0.2
        self.show_fps = True
        self.debug_normals = True

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

for i in range(-3, 6):
    for j in range(3, 8):
        blocks.append(Block(Coordinate(i, 0, j), (112, 168, 101)))

blocks.append(BlockSlab(Coordinate(0, 2, 0), (112, 168, 101)))
blocks.append(BlockSlab(Coordinate(1, 2, 0), (112, 168, 101), bottom=False))
blocks.append(BlockStairs(Coordinate(4, 2, 0), (112, 168, 101)))
blocks.append(BlockStairs(Coordinate(6, 2, 0), (190, 168, 50), bottom=False))
blocks.append(BlockStairs(Coordinate(8, 2, 0), (190, 168, 50), direction="s"))
blocks.append(BlockStairs(Coordinate(10, 2, 0), (190, 168, 50), direction="e"))
blocks.append(BlockStairs(Coordinate(12, 2, 0), (190, 168, 50), direction="w"))


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
                    (800, 600), pygame.FULLSCREEN | pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.HWSURFACE
                )                
                screen.surface = screen_surf
            if event.key == pygame.K_ESCAPE:
                running = False
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
    screen.render(blocks, points, debug_normals=options.debug_normals)
    if options.show_debug_info:
        screen.render_debug_info(user)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
