import arcade

from game_screens.ui import GameView

SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720


class Game(arcade.Window):
    """
    The window containing game screens.
    """

    def __init__(self, width: int, height: int, tiles: list, client, cheats_enabled: bool, server_thread=None):
        """
        :param width: Window width.
        :param height: Window height.
        :param tiles: A 2D list of integer values representing tile types.
        :param client: A client object for server communication.
        """
        super().__init__(width, height, "Age of Divisiveness")
        self.client = client
        self.server_thread = server_thread
        self.game_view = GameView(width, height, tiles, client, cheats_enabled)
        self.back_to_game()

    def back_to_game(self):
        """
        Returns the window to the map view.
        """
        self.show_view(self.game_view)

    def run(self):
        arcade.run()

    def on_close(self):
        if self.server_thread:
            self.client.end_game_by_host()
            self.server_thread.join()
        else:
            try:
                self.client.disconnect()
            except BrokenPipeError:
                pass
        self.close()

