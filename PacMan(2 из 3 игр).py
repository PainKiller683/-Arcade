import arcade
import random

from pyglet.graphics import Batch

# Параметры экрана
SCREEN_WIDTH = 270
SCREEN_HEIGHT = 360
SCREEN_TITLE = "Сапёр"
CELL_SIZE = 30
GRID_WIDTH = 9
GRID_HEIGHT = 9


class SaperGame(arcade.Window):
    def __init__(self, screen_width, screen_height, screen_title):
        super().__init__(screen_width, screen_height, screen_title)
        arcade.set_background_color(arcade.color.BLACK)
        self.tile_map = arcade.load_tilemap("Files/ForPacMan/CartaPacMan.tmx", scaling=1)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

    def setup(self):
        self.map = self.tile_map.sprite_lists["Cart"]

    def on_draw(self):
        self.scene.draw()

    def on_update(self, delta_time):
        pass
    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_key_press(self, key, modifiers):
        pass


def main():
    game = SaperGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()