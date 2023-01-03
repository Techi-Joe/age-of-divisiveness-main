import unittest
from math import sqrt

from game_screens.logic import GameLogic
from game_screens.logic import City, Tile

CIV_ONE = "The Great Northern"
CIV_TWO = "Mixtec"


class MovementTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tiles = []
        # these have to be added in the order of bottom to top, left to right in order for get_tile(x, y) to work
        # so (0, 0), (1, 0), .... (COLUMNS_NUMBER-1, 0), (0, 1), (1, 1), ...
        # this is a linear map with, from left to right, a column of water, plains, hills, plains, mountains
        for y in range(5):
            self.tiles.append(Tile(0, y, 1, 0))
            self.tiles.append(Tile(1, y, 1, 1))
            self.tiles.append(Tile(2, y, 1, 2))
            self.tiles.append(Tile(3, y, 1, 1))
            self.tiles.append(Tile(4, y, 1, 3))
        self.game_logic = GameLogic(self.tiles, 5, 5, players=[("one", CIV_ONE, "gray"), ("two", CIV_TWO, "red")],
                                    my_nick="one")
        self.game_logic.add_unit(2, 2, "one", 'Settler', 1)
        self.settler = self.game_logic.get_tile(2, 2).occupant

        self.area = []
        self.area.append(Tile(0, 1, 1, 0))
        self.area.append(Tile(1, 1, 1, 0))
        self.area.append(Tile(2, 1, 1, 1))
        self.area.append(Tile(2, 2, 1, 2))
        self.area.append(Tile(0, 0, 1, 2))
        self.area.append(Tile(1, 2, 1, 3))

    def test_city_building(self):
        # a city is created
        # the settler should be deleted and the tile unoccupied
        # the city should be owned by the owner of the settler
        # and should have a proper name and tile set
        player = self.settler.owner
        self.game_logic.build_city(self.settler, "test_name")
        tile = self.settler.tile
        self.assertNotIn(self.settler, player.units)
        self.assertFalse(tile.occupied())
        city = tile.city
        self.assertIsNotNone(city)
        self.assertEqual(city.owner, player)
        self.assertEqual(city.name, "test_name")

    def test_city_area(self):
        # a city is created
        # if all tiles around it are not owned, it gets a 3x3 area where the middle point is the city
        self.game_logic.build_city(self.settler, "test_name")
        player = self.settler.owner
        tile = self.settler.tile
        city = tile.city
        expected_area = {(x, y) for x in range(1, 4) for y in range(1, 4)}
        real_area = {t.coords for t in city.area}
        self.assertEqual(expected_area, real_area)
        for x, y in expected_area:
            self.assertEqual(self.game_logic.get_tile(x, y).owner, player)

    def test_two_cities_area(self):
        # two cities are created, and the second one is so close that the 3x3 square around it contains
        # the territory of the first one
        # we'll make sure that this territory won't be taken by the new city
        self.game_logic.add_unit(2, 0, "two", 'Settler', 1)
        self.game_logic.build_city(self.settler, "one_city")
        self.game_logic.build_opponents_city(2, 0, "two_city")
        expected_area = {(1, 0), (2, 0), (3, 0)}
        city = self.game_logic.get_tile(2, 0).city
        player = city.owner
        real_area = {t.coords for t in city.area}
        self.assertEqual(expected_area, real_area)
        for x, y in expected_area:
            self.assertEqual(self.game_logic.get_tile(x, y).owner, player)

    def test_simple_border(self):
        # a city is created
        # since the basic area for a city is a 3x3 square, it's borders are all it's tiles except the middle point
        self.game_logic.build_city(self.settler, "one_city")
        expected_border = {(x, y) for x in range(1, 4) for y in range(1, 4) if not x == y == 2}
        player = self.settler.owner
        real_border = {border.tile.coords for border in player.borders}
        self.assertEqual(expected_border, real_border)

    def test_separated_border(self):
        # two cities whose borders don't touch
        # and they are on screen edges, so their areas are 2x3, which means all their tiles should be borders
        self.game_logic.add_unit(1, 0, "one", 'Settler', 1)
        self.game_logic.build_opponents_city(1, 0, "city1")
        self.game_logic.add_unit(3, 4, "one", 'Settler', 1)
        self.game_logic.build_opponents_city(3, 4, "city2")
        city1 = self.game_logic.get_tile(1, 0).city
        city2 = self.game_logic.get_tile(3, 4).city
        player = city1.owner
        expected_border = {tile.coords for city in [city1, city2] for tile in city.area}
        real_border = {border.tile.coords for border in player.borders}
        self.assertEqual(expected_border, real_border)

    def test_border_update(self):
        # we will create two cities so that their borders connect
        # some tiles should stop being borders then
        player = self.settler.owner
        self.game_logic.build_city(self.settler, "city1")
        self.assertIn((2, 1), [border.tile.coords for border in player.borders])
        # another city that's very close so the borders touch
        self.game_logic.add_unit(2, 0, "one", 'Settler', 1)
        self.game_logic.build_opponents_city(2, 0, "city2")
        expected_border = {(x, y) for x in range(1, 4) for y in range(0, 4) if not (x == 2 and 0 < y < 3)}  # no (2, 1)!
        real_border = {border.tile.coords for border in player.borders}
        self.assertEqual(expected_border, real_border)

    def test_calculating_goods_no_city(self):
        # just check based on known output
        self.assertEqual({'gold': 2, 'wood': 25, 'stone': 5, 'food': 27}, City.calculate_goods_no_city(self.area))

    def test_calculating_goods_based_on_city(self):
        # building city and calculating based on his area.
        self.game_logic.build_city(self.settler, "test_name")
        city = self.settler.tile.city
        assert city is not None
        city.set_area(self.area)
        self.assertEqual({'gold': 2, 'wood': 25, 'stone': 5, 'food': 27}, city.calculate_goods())

    def test_city_capture(self):
        # player two's forces have made it to the players one's stub_city and are ready to capture it
        self.setUp()
        x, y = self.settler.tile.coords
        player1 = self.settler.owner
        player2 = self.game_logic.players['two']
        self.game_logic.build_city(self.settler, "stub_city")
        city = player1.cities[0]

        self.assertNotIn(city, player2.cities)
        self.game_logic.give_opponents_city(x, y, 'two')
        self.assertNotIn(city, player1.cities)
        self.assertIn(city, player2.cities)
        for t in city.area:
            self.assertEqual(t.owner, player2)

        # fortunately, it was just player one's sneaky trap and he immediately recovered his city

        self.game_logic.give_opponents_city(x, y, 'one')
        for t in city.area:
            self.assertEqual(t.owner, player1)


class CityAreaTest(unittest.TestCase):
    def setUp_bigger(self):
        self.tiles = []
        for x in range(20):
            for y in range(20):
                self.tiles.append(Tile(x, y, 1, 1))
        self.game_logic = GameLogic(self.tiles, 20, 20, players=[("one", CIV_ONE, "gray"), ("two", CIV_TWO, "red")],
                                    my_nick="one")
        self.game_logic.add_unit(10, 10, "one", 'Settler', 1)
        settler = self.game_logic.get_tile(10, 10).occupant
        self.game_logic.build_city(settler, "stub")

    def test_city_resize(self):
        self.setUp_bigger()
        x_c, y_c = 10, 10
        city = self.game_logic.get_tile(x_c, y_c).city
        owner = city.owner
        for r in range(2, 9):
            self.game_logic.increase_area(x_c, y_c)
            self.assertEqual(city.current_radius, r)
            for x in range(x_c - r, x_c + r + 1):
                for y in range(y_c - r, y_c + r + 1):
                    tile = self.game_logic.get_tile(x, y)
                    if sqrt((x_c - x) ** 2 + (y_c - y) ** 2) <= r:
                        self.assertIn(tile, city.area)
                        self.assertEqual(tile.owner, owner)
                    else:
                        self.assertNotIn(tile, city.area)
                        self.assertIsNone(tile.owner)
