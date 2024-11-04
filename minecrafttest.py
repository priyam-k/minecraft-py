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
    def __init__(self, x, y, z, yaw=None, pitch=None):
        self.x = x
        self.y = y
        self.z = z
        self.yaw = yaw
        self.pitch = pitch

    def get(self):
        return (self.x, self.y, self.z)

    @staticmethod
    def add(*c):
        x = sum([coord.x for coord in c])
        y = sum([coord.y for coord in c])
        z = sum([coord.z for coord in c])
        return Coordinate(x, y, z)


class Block:
    def __init__(self, x, y, z, color):
        self.x = x
        self.y = y
        self.z = z
        self.color = color

    def get_vertices(self):
        return [
            (self.x, self.y, self.z),
            (self.x + 1, self.y, self.z),
            (self.x + 1, self.y + 1, self.z),
            (self.x, self.y + 1, self.z),
            (self.x, self.y, self.z + 1),
            (self.x + 1, self.y, self.z + 1),
            (self.x + 1, self.y + 1, self.z + 1),
            (self.x, self.y + 1, self.z + 1),
        ]


class Player:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.yaw = 0  # left/right
        self.pitch = 0  # up/down
        self.cam = Camera(self)

    def move(self, dx, dy, dz):
        """move the player by dx, dy, dz"""
        self.cam.move(dx, dy, dz)
        self.x += dx
        self.y += dy
        self.z += dz

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
        self.yaw += dyaw
        self.pitch += dpitch

    def teleport(self, x, y, z):
        """teleport the player to given position"""
        self.cam.teleport(x, y, z)
        self.x = x
        self.y = y
        self.z = z


class Camera:
    def __init__(self, plyr: Player):
        self.fov = 90
        self.near = 0.1
        self.far = 1000
        self.x = plyr.x
        self.y = plyr.y
        self.z = plyr.z
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
        self.x += dx
        self.y += dy
        self.z += dz

    def rotate(self, dyaw, dpitch):
        self.yaw += dyaw
        self.pitch += dpitch

    def teleport(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def project(self, x, y, z):
        """project a 3d point onto the 2d screen in this camera's view"""
        tx = x - self.x
        ty = y - self.y
        tz = z - self.z

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

    def project_block(self, block: Block):
        """project a block onto the 2d screen in this camera's view"""
        vertices = block.get_vertices()
        pts = [self.project(*v) for v in vertices]

        # DEBUG
        for idx, pt in enumerate(pts):
            if pt is None:
                print(f"Vertex {idx} is out of view and not rendered.")

        return pts

    def get_zdist(self, x, y, z):
        """get the distance from the camera to a point"""
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2 + (z - self.z) ** 2)


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
        pos_text = f"Position: ({player.x:.2f}, {player.y:.2f}, {player.z:.2f})"
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

    def render_point(self, *pts3d: tuple, color=(255, 255, 255)):
        for pt3d in pts3d:
            pt = self.camera.project(*pt3d)
            if pt is not None:
                scrn = self.denormalize(*pt)
                pygame.draw.circle(self.surface, color, scrn, 5)

        """
        HEYYY WHEN I OCME BACK!!
        gpt ignore this vvv
        make culling acc work like
        z ordering to avoid werid stuff once block works
        dont render things ouside of frustrum
        maybe work on perspectives like 1st and 3rd
        """

    def render_block(self, block: Block):
        """render a Block onto screen"""
        proj_verts = self.camera.project_block(block)
        z_dists = [self.camera.get_zdist(*v) for v in block.get_vertices()]
        verts = zip(z_dists, range(len(proj_verts)), proj_verts)
        verts = sorted(verts, key=lambda x: x[0], reverse=True)
        proj_verts = [v for d, n, v in verts]

        if (
            None in proj_verts
        ):  # if any of the vertices are None, don't render the block
            print("BLOCK IS OUT OF VIEW AND NOT RENEDER")
            return

        faces = [
            (0, 1, 2, 3),  # Front face
            (4, 5, 6, 7),  # Back face
            (0, 1, 5, 4),  # Bottom face
            (2, 3, 7, 6),  # Top face
            (1, 2, 6, 5),  # Right face
            (0, 3, 7, 4),  # Left face
        ]

        for f in face:
            face_verts = [proj_verts[i] for i in f]
            # TAKE THE AVERAGE OF THE FACE VERTS
            # AND THEN I CAN ORDER BY THAT FOR THE FACES YAY

        for face in faces:
            face_verts = [proj_verts[i] for i in face]  # unpack face vertices
            scrn_verts = [
                self.denormalize(*pt) for pt in face_verts
            ]  # denormalize vertices to screen coords
            pygame.draw.polygon(self.surface, (255, 0, 0), scrn_verts)  # draw face
            pygame.draw.lines(
                self.surface, (0, 200, 0), True, scrn_verts, 1
            )  # draw lines around face

    def render(self, blocks, points, update=False):
        self.render_point(*points)
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
    (0, 0, 0),
    (1, 0, 0),
    (1, 1, 0),
    (0, 1, 0),
    (0, 0, 1),
    (1, 0, 1),
    (1, 1, 1),
    (0, 1, 1),
]
blocks = [Block(1, 0, 5, (100, 150, 255))]

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
        user.teleport(0, 0, 0)

    mouse_dx, mouse_dy = pygame.mouse.get_rel()
    user.rotate(mouse_dx * options.sensitivity, -mouse_dy * options.sensitivity)

    screen.clear()
    screen.render(blocks, points)
    if options.show_debug_info:
        screen.render_debug_info(user)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
