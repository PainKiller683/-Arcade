import arcade
from arcade import Sound
import random

from pyglet.graphics import Batch

# Параметры экрана
SCREEN_WIDTH = 16 * 16
SCREEN_HEIGHT = 464 - 15 * 16
SCREEN_TITLE = "Супер Марио"
CELL_SIZE = 16
DEAD_ZONE_W = int(SCREEN_WIDTH * 0.35)
DEAD_ZONE_H = int(SCREEN_HEIGHT * 0.45)

class SaperGame(arcade.Window):
    def __init__(self, screen_width, screen_height, screen_title):
        super().__init__(screen_width, screen_height, screen_title)
        arcade.set_background_color(arcade.color.BLACK)
        self.world_camera = arcade.camera.Camera2D()
        self.all_sprites = arcade.SpriteList()

    def setup(self):
        self.player_texture = arcade.load_texture(":resources:images/enemies/slimeBlue.png")
        self.player = arcade.Sprite(self.player_texture, scale=0.2)
        tile_map = arcade.load_tilemap("Files/ForMario/World 1.1 SuperMario.tmx", scaling=1)
        self.scene = arcade.Scene.from_tilemap(tile_map)
        self.wall_list = tile_map.sprite_lists["Walls"]
        self.player.center_x = 16 * 8
        self.player.center_y = 300
        self.music = arcade.load_sound("Files/ForMario/music for mario/01. Ground Theme.mp3", False)
        self.all_sprites.append(self.player)
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.wall_list)

    def on_draw(self):
        self.world_camera.use()
        self.scene.draw()
        self.wall_list.draw()
        self.all_sprites.draw()

    def on_update(self, delta_time):
        arcade.play_sound(self.music,1.0, -1,True)
        self.physics_engine.update()
        position = (
            self.player.center_x,
            self.player.center_y
        )
        self.world_camera.position = arcade.math.lerp_2d(self.world_camera.position, position, 0.14,)

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.player.change_y = 5
        elif key == arcade.key.DOWN:
            self.player.change_y = -5
        elif key == arcade.key.LEFT:
            self.player.change_x = -5
        elif key == arcade.key.RIGHT:
            self.player.change_x = 5

    def on_key_release(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player.change_y = 0
        elif key == arcade.key.LEFT or arcade.key.RIGHT:
            self.player.change_x = 0


def main():
    game = SaperGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()