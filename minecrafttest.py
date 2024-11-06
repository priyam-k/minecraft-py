import math

import pygame
from blocks import Block, BlockSlab, BlockStairs, BlockVerticalSlab, Model
from camera import Camera
from coordinate import Coordinate
from face import Face
from genericblock import GenericBlock
from player import Player
from world import World

pygame.init()
screen_surf = pygame.display.set_mode(
    (800, 600), pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.HWSURFACE
)
pygame.display.set_caption("3D thingies")
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)


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
                self.surface, (0, 0, 0), True, scrn_verts, 1
            )  # draw lines around face

        if debug_normals:  # draw face normals
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

    def render_block(self, block: GenericBlock, outline=False, debug_normals=False):
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

    def render(self, world: World, points, update=False, debug_normals=False):
        self.render_point(*points)
        blocks = world.blocks.values()
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
world = World()

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

for i in range(-3, 6):
    for j in range(3, 8):
        world.add_block(Block(Coordinate(i, 0, j), (112, 168, 101)))

world.add_block(BlockSlab(Coordinate(0, 2, 0), (112, 168, 101)))
world.add_block(BlockSlab(Coordinate(1, 2, 0), (112, 168, 101), bottom=False))
world.add_block(BlockStairs(Coordinate(4, 2, 0), (112, 168, 101)))
world.add_block(BlockStairs(Coordinate(6, 2, 0), (190, 168, 50), bottom=False))
world.add_block(BlockStairs(Coordinate(8, 2, 0), (190, 168, 50), direction="s"))
world.add_block(BlockStairs(Coordinate(10, 2, 0), (190, 168, 50), direction="e"))
world.add_block(BlockStairs(Coordinate(12, 2, 0), (190, 168, 50), direction="w"))
world.add_block(BlockVerticalSlab(Coordinate(14, 2, 0), (190, 168, 50)))
world.add_block(BlockVerticalSlab(Coordinate(16, 2, 0), (190, 168, 50), left=False))
# world.add_block(
#     Model(
#         Coordinate(18, 2, 0),
#         (150, 75, 0),
#         [(2, 1, 0, ), # Face 0
# (0, 3, 2, ), # Face 1
# (3, 2, 4, ), # Face 2
# (4, 5, 3, ), # Face 3
# (5, 4, 6, ), # Face 4
# (6, 7, 5, ), # Face 5
# (1, 6, 7, ), # Face 6
# (7, 0, 1, ), # Face 7
# (5, 3, 0, ), # Face 8
# (0, 7, 5, ), # Face 9
# (4, 6, 1, ), # Face 10
# (1, 2, 4, ), # Face 11
# ], [Coordinate(1.0, 0.33, 0.0),
# Coordinate(1.0, 0.0, 0.0),
# Coordinate(0.0, 0.0, 0.0),
# Coordinate(0.0, 0.33, 0.0),
# Coordinate(5.55112e-17, 0.0, 1.0),
# Coordinate(5.55112e-17, 0.33, 1.0),
# Coordinate(1.0, 0.0, 1.0),
# Coordinate(1.0, 0.33, 1.0), ],
#     )
# )


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
                    (800, 600),
                    pygame.FULLSCREEN
                    | pygame.RESIZABLE
                    | pygame.DOUBLEBUF
                    | pygame.HWSURFACE,
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
    screen.render(world, points, debug_normals=options.debug_normals)
    if options.show_debug_info:
        screen.render_debug_info(user)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
