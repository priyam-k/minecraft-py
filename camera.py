import math

from coordinate import Coordinate
from face import Face
from genericblock import GenericBlock

# from player import Player
from utils import cos, sin, tan


class Camera:
    def __init__(self, plyr: "Player"):
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
