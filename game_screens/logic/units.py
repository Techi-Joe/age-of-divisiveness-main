import arcade

from game_screens.logic.city import City
from game_screens.logic.tiles import Tile


class Unit(arcade.sprite.Sprite):
    def __init__(self, tile, owner, sprite_name):
        super().__init__(f"resources/sprites/units/{sprite_name}.png")
        self.owner = owner
        self.color = owner.color
        self.tile = tile
        self.width = tile.width
        self.height = tile.height
        self.health = 100
        self.max_movement = self.movement = 5
        self.move_to(tile, 0)

    def __str__(self):
        return f"{self.owner.short_civ.capitalize()} Unit"

    def move_to(self, tile: Tile, cost: int):
        """
        Moves a unit to the specified tile at a specified cost.
        :param tile: tile to move the unit to
        :param cost: the cost of the move
        """
        self.tile.occupant = None
        self.tile = tile
        self.tile.occupant = self
        self.center_x = tile.center_x
        self.center_y = tile.center_y
        self.movement -= cost

    def reset_movement(self):
        self.movement = self.max_movement


class Settler(Unit):
    def __init__(self, tile, owner):
        # if tile is not None:
        super().__init__(tile, owner, 'settler')
        self.type = 'Settler'
        self.count = 1

    def __str__(self):
        return f"{self.owner.short_civ.capitalize()} Settlers"

    def build_city(self, name, surroundings: list):
        # TODO not on the same tile as another city!! Not on another player's territory too
        self.tile.occupant = None
        city = City(self, name, surroundings)
        return city
