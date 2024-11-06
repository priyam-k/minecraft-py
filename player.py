from camera import Camera
from coordinate import Coordinate
from utils import cos, sin, tan


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
