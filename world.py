from coordinate import Coordinate
from genericblock import GenericBlock


class World:
    def __init__(self):
        self.blocks = {}

    def set_block(self, block: GenericBlock):
        self.blocks[block.pos] = block

    def add_block(self, block: GenericBlock):
        if block.pos not in self.blocks:
            self.set_block(block)
        else:
            print("Block already exists at position.")

    def remove_block(self, pos: Coordinate):
        if pos in self.blocks:
            del self.blocks[pos]

    def get_block(self, pos: Coordinate):
        return self.blocks.get(pos, None)
